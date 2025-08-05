from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import re
import ast
import logging
from collections import defaultdict
from .code_language_handler import LanguageHandler

logger = logging.getLogger(__name__)

class PythonHandler(LanguageHandler):
    def extract_functions_from_diff(self, diff: str, file_map: Dict[str, str]) -> List[str]:
        """
        Extracts modified function definitions from full source using AST and diff line tracking.
        Only returns functions that were touched by the diff (added/deleted lines).
        """
        functions = []

        file_diffs = re.split(r'diff --git a/(.+?) b/\1\n', diff)[1:]
        file_chunks = list(zip(file_diffs[::2], file_diffs[1::2]))

        for filename, chunk in file_chunks:
            if not filename.endswith(".py"):
                logger.info(f"Skipping non-Python file: {filename}")
                continue

            full_source = file_map.get(filename)
            if not full_source:
                logger.warning(f"Missing full source for file: {filename}")
                continue

            # Collect modified line numbers from diff
            modified_lines = set()
            current_new_line = 0

            for line in chunk.splitlines():
                if line.startswith('@@'):
                    match = re.match(r'@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@', line)
                    if match:
                        current_new_line = int(match.group(1))
                        span = int(match.group(2) or 1)
                        current_hunk_line = current_new_line
                elif line.startswith('+') and not line.startswith('+++'):
                    modified_lines.add(current_new_line)
                    current_new_line += 1
                elif line.startswith(' ') or line.startswith('-'):
                    current_new_line += 1

            # Parse AST and filter functions by line range
            try:
                tree = ast.parse(full_source)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        start = node.lineno
                        end = getattr(node, 'end_lineno', start)  # Python 3.8+ provides end_lineno
                        if any(start <= line <= end for line in modified_lines):
                            functions.append({
                                "filename": filename,
                                "function_name": node.name
                            })
            except SyntaxError as e:
                logger.warning(f"AST parsing failed for {filename}: {e}")

        return functions

    def get_call_graph(self, file_map: Dict[str, str]) -> Dict[str, List[str]]:
        """
        Parses all Python files to build a call graph mapping each function
        to the functions it calls. Assumes file_map contains Python code.
        """
        call_graph = {}

        for filename, content in file_map.items():
            try:
                tree = ast.parse(content)
                func_defs = {node.name: node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}

                for func_name, func_node in func_defs.items():
                    calls = []
                    for node in ast.walk(func_node):
                        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                            calls.append(node.func.id)
                    full_name = f"{filename}:{func_name}"
                    call_graph[full_name] = calls

            except Exception as e:
                print(f"Skipping {filename} due to parse error: {e}")
                continue

        return call_graph

    def fetch_function_context(self, fn: dict, file_map: Dict[str, str], call_graph: Dict[str, List[str]]) -> str:
        """
        Given a function full name like 'file.py:func', extract its source code,
        along with basic context from its callers and callees if available.
        """

        try:
            filename = fn["filename"]
            func_name = fn["function_name"]
            content = file_map.get(filename)
            if not content:
                return f"# Source not found for {fn}"

            tree = ast.parse(content)
            source_lines = content.splitlines()
            context_blocks = []

            # Extract target function's code
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == func_name:
                    start_line = node.lineno - 1
                    end_line = max([n.lineno for n in ast.walk(node) if hasattr(n, "lineno")], default=start_line + 1)
                    func_code = "\n".join(source_lines[start_line:end_line])
                    context_blocks.append(f"# Function: {fn}\n{func_code}")
                    break

            # Add callees (functions this function calls)
            callees = call_graph.get(f"{filename}:{func_name}", [])
            for callee_name in callees:
                # Try to find the function definition in the same file
                callee_fn = f"{filename}:{callee_name}"
                if callee_fn in call_graph:
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef) and node.name == callee_name:
                            start = node.lineno - 1
                            end = max([n.lineno for n in ast.walk(node) if hasattr(n, "lineno")], default=start + 1)
                            callee_code = "\n".join(source_lines[start:end])
                            context_blocks.append(f"# Callee: {callee_fn}\n{callee_code}")
                            break

            return "\n\n".join(context_blocks)

        except Exception as e:
            return f"# Failed to extract function context for {fn}: {e}"
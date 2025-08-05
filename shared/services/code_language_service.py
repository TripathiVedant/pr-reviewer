from typing import Dict, List, Any, Optional
import re
import ast
import logging
from collections import defaultdict
from .code_language_handlers.code_language_handler import LanguageHandler
from .code_language_handlers.python_code_language_handler import PythonHandler


logger = logging.getLogger(__name__)

class LanguageService:
    """
    Registry + dispatcher that routes requests to the appropriate LanguageHandler.
    """
    def __init__(self):
        self._registry: Dict[str, LanguageHandler] = {}
        # register default handlers
        self.register_handler("py", PythonHandler())

    def register_handler(self, ext_or_lang: str, handler: LanguageHandler):
        """Register by extension (without dot) or language key."""
        self._registry[ext_or_lang.lower()] = handler

    def _get_handler_for_filename(self, filename: str) -> Optional[LanguageHandler]:
        # quick extension-based lookup
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        return self._registry.get(ext)

    def get_handler(self, filename: Optional[str] = None, language: Optional[str] = None) -> LanguageHandler:
        if language:
            h = self._registry.get(language.lower())
            if h:
                return h
            raise ValueError(f"No handler registered for language: {language}")

        if filename:
            h = self._get_handler_for_filename(filename)
            if h:
                return h
            raise ValueError(f"No handler registered for file extension of {filename}")

        raise ValueError("Either filename or language must be provided to select handler")

    # convenience methods that delegate to the handler
    def extract_functions_from_diff(self, diff: str, file_map: Dict[str, str]) -> List[Dict[str, str]]:
        # We assume diff may contain multiple files possibly of different languages.
        # We'll group files by ext and call the appropriate handler for each subset.
        functions: List[Dict[str, str]] = []

        # cheap split to identify file names in diff (reuse same regex you had)
        file_diffs = re.split(r'diff --git a/(.+?) b/\1\n', diff)[1:]
        file_chunks = list(zip(file_diffs[::2], file_diffs[1::2]))

        # group chunks by extension and call handlers per-language
        by_ext: Dict[str, List[tuple]] = defaultdict(list)
        for filename, chunk in file_chunks:
            ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
            by_ext[ext].append((filename, chunk))

        for ext, chunks in by_ext.items():
            handler = self._registry.get(ext)
            if not handler:
                logger.debug("No handler for extension %s, skipping %s files", ext, [f for f, _ in chunks])
                continue

            # construct a mini-diff string per-language to reuse handler logic
            mini_diff = ""
            local_file_map = {}
            for filename, chunk in chunks:
                mini_diff += f"diff --git a/{filename} b/{filename}\n{chunk}\n"
                if filename in file_map:
                    local_file_map[filename] = file_map[filename]

            functions.extend(handler.extract_functions_from_diff(mini_diff, local_file_map))

        return functions

    def get_call_graph(self, file_map: Dict[str, str]) -> Dict[str, List[str]]:
        # Merge call graphs from different handlers
        overall: Dict[str, List[str]] = {}
        # group by extension
        files_by_ext: Dict[str, Dict[str,str]] = defaultdict(dict)
        for fname, content in file_map.items():
            ext = fname.rsplit(".", 1)[-1].lower() if "." in fname else ""
            files_by_ext[ext][fname] = content

        for ext, fm in files_by_ext.items():
            handler = self._registry.get(ext)
            if not handler:
                logger.debug("No handler for ext %s; skipping", ext)
                continue
            overall.update(handler.get_call_graph(fm))
        return overall

    def fetch_function_context(self, fn: Dict[str, str], file_map: Dict[str, str], call_graph: Dict[str, List[str]]) -> str:
        filename = fn.get("filename")
        handler = self.get_handler(filename=filename)
        return handler.fetch_function_context(fn, file_map, call_graph)
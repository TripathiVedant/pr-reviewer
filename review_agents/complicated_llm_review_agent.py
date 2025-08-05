import asyncio
import json
import ast
import re
import logging
from typing import List, Dict, Any

from review_agents.chains.complicated_llm_chain import ComplicatedLLMChainExecutor
from shared.models.enums import ErrorCode
from shared.models.payloads import ErrorResult, Issue, FileResult, AnalysisResults, Summary, ReviewFactor
from shared.exceptions.agent_exceptions import AgentOutputParseException
from shared.utils.parse_llm_output import parse_review_result, parse_pr_analysis_result_for_complicated_agent_raw_result
from shared.services.code_language_service import LanguageService

logger = logging.getLogger(__name__)

class ComplicatedLLMPrReviewAgent:
    def __init__(self):
        self.executor = ComplicatedLLMChainExecutor()
        self.language_service = LanguageService()

    async def review(self, code_diff: str, files: List[Dict[str, Any]], file_map: Dict[str, str], factors: List[str]) -> AnalysisResults:
        logger.info("event: review, msg: Starting advanced review with function-level granularity")

        diff_summary = self.summarize_diff(code_diff)
        functions_to_review =  self.language_service.extract_functions_from_diff(code_diff, file_map)
        call_graph =  self.language_service.get_call_graph(file_map)

        enriched_functions = []
        for fn in functions_to_review:
            context =  self.language_service.fetch_function_context(fn, file_map, call_graph)
            enriched_functions.append({
                "function": fn,
                "context": context,
                "diff_summary": diff_summary,
            })

        tasks = []
        for factor in factors:
            for func_data in enriched_functions:
                tasks.append(self._review_function(factor, func_data))

        # Todo: Same line can be reviewed multiple time, add duplicate remover.
        raw_results = await asyncio.gather(*tasks)
        return parse_pr_analysis_result_for_complicated_agent_raw_result(raw_results, factors)

    def summarize_diff(self, diff: str) -> str:
        result = self.executor.summarize_diff().invoke({"diff": diff})
        return result.content

    async def _review_function(self, factor: str, func_data: Dict[str, Any]) -> Dict[str, Any]:
        fn = func_data.get("function", {})
        filename = fn.get("filename", fn.get("name", "<unknown>"))

        try:
            logger.info(f"event: _review_function, msg: Reviewing {fn} for factor={factor}")
            result = await asyncio.wait_for(
                self.executor.run_chain(factor, func_data),
                timeout=180
            )
            # Normalize and extract issues robustly
            issues = []

            if result is None:
                issues = []
            elif isinstance(result, dict):
                # Case A: chain returned an `issues` top-level (legacy)
                if "issues" in result and isinstance(result["issues"], list):
                    issues = result["issues"]

                # Case B: expected schema: result["files"] -> list of {name, issues}
                elif "files" in result and isinstance(result["files"], list):
                    # try to find the file that matches our filename
                    matched = None
                    for f in result["files"]:
                        # accept either 'name' or 'filename' keys depending on LLM output
                        f_name = f.get("name") or f.get("filename") or ""
                        if f_name and f_name == filename:
                            matched = f
                            break
                    if matched is None and result["files"]:
                        # fallback to first file if no exact match
                        matched = result["files"][0]
                    if matched:
                        issues = matched.get("issues", [])
                else:
                    # Unexpected shape: leave issues empty but log
                    logger.warning("Unexpected chain result shape for %s: %s", filename, type(result))
            else:
                logger.warning("Unexpected result type from chain for %s: %s", filename, type(result))

            # ensure issues is a list
            if issues is None:
                issues = []
            return {"factor": factor, "file": filename, "issues": issues}

        except asyncio.TimeoutError:
            logger.error(f"event: _review_function, msg: Timeout for {fn} - factor={factor}")
            return ErrorResult(
                error=f"Timeout during function review for factor {factor} in {fn}",
                error_code=ErrorCode.AGENT_TIMEOUT
            ).model_dump()

        except ValueError as e:
            logger.error(f"event: _review_function, msg: Prompt error for {fn} - factor={factor}: {str(e)}")
            return ErrorResult(
                error=f"Prompt error for factor {factor} in {fn}: {str(e)}",
                error_code=ErrorCode.AGENT_PROMPT_ERROR
            ).model_dump()

        except Exception as e:
            msg = str(e).lower()
            if "rate limit" in msg or "429" in msg or "quota" in msg:
                logger.error(f"event: _review_function, msg: Rate limit error for {fn} - factor={factor}: {str(e)}")
                return ErrorResult(
                    error=f"Rate limit error for factor {factor} in {fn}: {str(e)}",
                    error_code=ErrorCode.AGENT_RATE_LIMIT
                ).model_dump()
            logger.error(f"event: _review_function, msg: LLM error for {fn} - factor={factor}: {str(e)}")
            return ErrorResult(
                error=f"LLM error for factor {factor} in {fn}: {str(e)}",
                error_code=ErrorCode.AGENT_LLM_ERROR
            ).model_dump()






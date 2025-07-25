import asyncio
import json
import logging
from typing import List, Dict, Any

from review_agents.chains.simple_llm_chain import SimpleLLMChainExecutor
from shared.models.enums import ErrorCode
from shared.models.payloads import ErrorResult, Issue, FileResult, AnalysisResults, Summary
from shared.exceptions.agent_exceptions import AgentOutputParseException
from shared.utils.parse_llm_output import parse_review_result

logger = logging.getLogger(__name__)


class SimpleLLMPrReviewAgent:
    def __init__(self):
        self.executor = SimpleLLMChainExecutor()

    async def _review_factor(self, factor: str, code: str) -> Dict[str, Any]:
        try:
            chain = self.executor.build_chain(factor)
            result = await asyncio.wait_for(chain.ainvoke({"code": code}), timeout=180)
            logger.info(f"Reviewed for factor {factor}: {result}")
            return {"factor": factor, "review": result}
        except asyncio.TimeoutError:
            return ErrorResult(
                error=f"Timeout during review for factor {factor}",
                error_code=ErrorCode.AGENT_TIMEOUT
            ).model_dump()
        except ValueError as e:
            return ErrorResult(
                error=f"Prompt error for factor {factor}: {str(e)}",
                error_code=ErrorCode.AGENT_PROMPT_ERROR
            ).model_dump()
        except Exception as e:
            msg = str(e).lower()
            if "rate limit" in msg or "429" in msg or "quota" in msg:
                return ErrorResult(
                    error=f"Rate limit error for factor {factor}: {str(e)}",
                    error_code=ErrorCode.AGENT_RATE_LIMIT
                ).model_dump()
            return ErrorResult(
                error=f"LLM/runtime error for factor {factor}: {str(e)}",
                error_code=ErrorCode.AGENT_LLM_ERROR
            ).model_dump()

    async def review(self, code_diff: str, files: List[Dict[str, Any]], factors: List[str]) -> AnalysisResults:
        tasks = [self._review_factor(factor, code_diff) for factor in factors]
        raw_results = await asyncio.gather(*tasks)

        all_files: Dict[str, List[Issue]] = {}
        errors: List[ErrorResult] = []

        try:
            for factor, result in zip(factors, raw_results):
                if isinstance(result, dict) and "error_code" in result:
                    errors.append(ErrorResult(**result))
                    continue

                parsed_files = parse_review_result(result["review"])
                for filename, issues in parsed_files.items():
                    all_files.setdefault(filename, []).extend(issues)
        except Exception as e:
            logger.error(f"Failed to parse review result for all factors : {raw_results}", exc_info=e)
            raise AgentOutputParseException(f"Failed to parse result. Error {str(e)}")

        file_results = [FileResult(name=filename, issues=sorted(issues, key=lambda issue: issue.line)) for filename, issues in all_files.items()]
        summary = Summary(
            total_files=len(file_results),
            total_issues=sum(len(f.issues) for f in file_results),
            critical_issues=sum(
                1 for f in file_results for i in f.issues if i.type.lower() == "critical"
            )
        )

        return AnalysisResults(
            files=file_results,
            summary=summary,
            errors=errors
        )

        

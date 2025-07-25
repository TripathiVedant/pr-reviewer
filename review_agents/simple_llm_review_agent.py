import asyncio
from typing import List, Dict, Any
from review_agents.chains.simple_llm_chain import SimpleLLMChainExecutor
from shared.models.enums import ErrorCode
from shared.models.payloads import ErrorResult

class SimpleLLMPrReviewAgent:
    def __init__(self):
        self.executor = SimpleLLMChainExecutor()

    async def _review_factor(self, factor: str, code: str) -> Dict[str, Any]:
        try:
            chain = self.executor.build_chain(factor)
            result = await asyncio.wait_for(chain.ainvoke({"code": code}), timeout=60)
            return {"factor": factor, "review": result.content}
        except asyncio.TimeoutError as e:
            return ErrorResult(error=f"Timeout during review for factor {factor}", error_code=ErrorCode.AGENT_TIMEOUT).model_dump()
        except ValueError as e:
            # Likely a prompt error
            return ErrorResult(error=f"Prompt error for factor {factor}: {str(e)}", error_code=ErrorCode.AGENT_PROMPT_ERROR).model_dump()
        except Exception as e:
            # Detect rate limit errors from LLM API
            msg = str(e).lower()
            if "rate limit" in msg or "429" in msg or "quota" in msg:
                return ErrorResult(error=f"Rate limit error for factor {factor}: {str(e)}", error_code=ErrorCode.AGENT_RATE_LIMIT).model_dump()
            # Could be LLM or runtime error
            return ErrorResult(error=f"LLM/runtime error for factor {factor}: {str(e)}", error_code=ErrorCode.AGENT_LLM_ERROR).model_dump()

    async def review(self, code_diff: str, files: List[Dict[str, Any]], factors: List[str]) -> Dict[str, Any]:
        tasks = [self._review_factor(f, code_diff) for f in factors]
        results = await asyncio.gather(*tasks)
        return {"reviews": results}

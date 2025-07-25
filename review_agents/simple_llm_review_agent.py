import asyncio
from typing import List, Dict, Any
from review_agents.chains.simple_llm_chain import SimpleLLMChainExecutor
from shared.models.enums import ErrorCode
from shared.models.payloads import ErrorResult

class AgentException(Exception):
    def __init__(self, message: str, error_code: ErrorCode = ErrorCode.AGENT_RUNTIME_ERROR):
        super().__init__(message)
        self.error_code = error_code

class AgentPromptException(AgentException):
    def __init__(self, message: str):
        super().__init__(message, ErrorCode.AGENT_PROMPT_ERROR)

class AgentLLMException(AgentException):
    def __init__(self, message: str):
        super().__init__(message, ErrorCode.AGENT_LLM_ERROR)

class AgentTimeoutException(AgentException):
    def __init__(self, message: str):
        super().__init__(message, ErrorCode.AGENT_TIMEOUT)

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
            # Could be LLM or runtime error
            return ErrorResult(error=f"LLM/runtime error for factor {factor}: {str(e)}", error_code=ErrorCode.AGENT_LLM_ERROR).model_dump()

    async def review(self, code_diff: str, files: List[Dict[str, Any]], factors: List[str]) -> Dict[str, Any]:
        tasks = [self._review_factor(f, code_diff) for f in factors]
        results = await asyncio.gather(*tasks)
        return {"reviews": results}

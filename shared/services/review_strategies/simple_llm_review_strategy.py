from shared.services.review_strategies.base import PRReviewStrategy
from shared.models.payloads import SimpleLLMReviewStrategyContext
from review_agents.simple_llm_review_agent import SimpleLLMPrReviewAgent
from typing import Dict, Any, List

class SimpleLLMReviewStrategy(PRReviewStrategy):
    def __init__(self):
        self.agent = SimpleLLMPrReviewAgent()

    async def review(self, code_diff: str, files: List[Dict[str, Any]], metadata: SimpleLLMReviewStrategyContext) -> Dict[str, Any]:
        factors = [f.value for f in metadata.factors]
        return await self.agent.review(code_diff, files, factors)
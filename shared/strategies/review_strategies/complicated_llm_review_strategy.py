from review_agents.complicated_llm_review_agent import ComplicatedLLMPrReviewAgent
from shared.strategies.review_strategies.base import PRReviewStrategy
from shared.models.payloads import SimpleLLMReviewStrategyContext, ComplicatedLLMReviewStrategyContext
from review_agents.simple_llm_review_agent import SimpleLLMPrReviewAgent
from shared.integrations.platform_factory import PlatformFetcherFactory

from typing import Dict, Any, List

class ComplicatedLLMReviewStrategy(PRReviewStrategy):
    def __init__(self):
        self.agent = ComplicatedLLMPrReviewAgent()

    async def review(self, code_diff: str, files: List[Dict[str, Any]], metadata: ComplicatedLLMReviewStrategyContext) -> Dict[str, Any]:

        # Fetch Entire file tree for repo and given branch
        fetcher = PlatformFetcherFactory.get_fetcher(metadata.platform)
        file_map = fetcher.fetch_entire_code_for_branch(repo_url=metadata.repo_url, pr_number=metadata.pr_number, token=metadata.token)
        factors = [f.value for f in metadata.factors]

        return await self.agent.review(code_diff, files, file_map, factors)
from shared.models.enums import ReviewStrategyName
from shared.models.payloads import ReviewStrategyContext
from shared.services.review_strategies.simple_llm_review_strategy import SimpleLLMReviewStrategy
from shared.services.review_strategies.base import PRReviewStrategy

class ReviewStrategyFactory:
    @staticmethod
    def get_strategy(context: ReviewStrategyContext) -> PRReviewStrategy:
        if context.strategy_name == ReviewStrategyName.SIMPLE_LLM:
            return SimpleLLMReviewStrategy()
        raise ValueError(f"Unsupported strategy: {context.strategy_name}")

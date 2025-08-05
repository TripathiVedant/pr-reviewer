from shared.models.enums import ReviewStrategyName
from shared.models.payloads import ReviewStrategyContext
from shared.strategies.review_strategies.simple_llm_review_strategy import SimpleLLMReviewStrategy
from shared.strategies.review_strategies.complicated_llm_review_strategy import ComplicatedLLMReviewStrategy
from shared.models.payloads import SimpleLLMReviewStrategyContext, ComplicatedLLMReviewStrategyContext
from shared.strategies.review_strategies.base import PRReviewStrategy
from typing import Dict, Tuple, Type, Any
import inspect


STRATEGY_REGISTRY: Dict[str, Tuple[Type[PRReviewStrategy], Type[ReviewStrategyContext]]] = {
    "simple_llm_strategy": (SimpleLLMReviewStrategy, SimpleLLMReviewStrategyContext),
    "simple": (SimpleLLMReviewStrategy, SimpleLLMReviewStrategyContext),
    "complicated_llm_strategy": (ComplicatedLLMReviewStrategy, ComplicatedLLMReviewStrategyContext),
    "complicated": (ComplicatedLLMReviewStrategy, ComplicatedLLMReviewStrategyContext),
}


class ReviewStrategyFactory:
    @staticmethod
    def get_strategy_by_name(strategy_name: str, *, context_kwargs: Dict[str, Any]) -> Tuple[PRReviewStrategy, ReviewStrategyContext]:
        """
        Look up the strategy by string, build the context using context_kwargs,
        and return (strategy_instance, context_instance).
        """
        if not strategy_name:
            raise ValueError("strategy_name must be provided")

        key = strategy_name.strip().lower()
        mapping = STRATEGY_REGISTRY.get(key)
        if mapping is None:
            raise ValueError(f"Unsupported strategy: {strategy_name!r}. "
                             f"Supported: {', '.join(sorted(STRATEGY_REGISTRY.keys()))}")

        StrategyCls, ContextCls = mapping

        # Construct context instance (will throw a TypeError if required args are missing)
        try:
            sig = inspect.signature(ContextCls)
            accepted_params = set(sig.parameters.keys())
            filtered_kwargs = {k: v for k, v in context_kwargs.items() if k in accepted_params}

            context = ContextCls(**filtered_kwargs)
        except TypeError as e:
            raise TypeError(f"Failed to construct context for strategy {strategy_name!r}: {e}")

        # Instantiate strategy (no args assumed; adapt if your strategies need args)
        strategy = StrategyCls()
        return strategy, context

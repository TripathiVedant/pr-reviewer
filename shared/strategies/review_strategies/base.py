from abc import ABC, abstractmethod
from typing import Dict, Any, List
from shared.models.payloads import ReviewStrategyContext

class PRReviewStrategy(ABC):
    @abstractmethod
    async def review(self, code_diff: str, files: List[Dict[str, Any]], metadata: ReviewStrategyContext) -> Dict[str, Any]:
        ...
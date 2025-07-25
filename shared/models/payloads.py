from pydantic import BaseModel
from typing import List, Optional
from .enums import PlatformType, TaskStatus, ReviewStrategyName, ReviewFactor, ErrorCode, ReviewFactor

class AnalyzePRRequest(BaseModel):
    platformType: PlatformType
    repo_url: str
    pr_number: int
    token: Optional[str] = None

class PRReviewStatusRequest(BaseModel):
    platformType: PlatformType
    repo_url: str
    pr_number: int
    token: Optional[str] = None

class AnalyzePRTaskPayload(BaseModel):
    task_id: str
    platformType: PlatformType
    repo_url: str
    pr_number: int
    token: Optional[str] = None
    status: TaskStatus

class AnalyzePRResponse(BaseModel):
    task_id: str
    status: TaskStatus

# Renamed for clarity
class TaskStatusResponse(BaseModel):
    task_id: str
    status: TaskStatus

class Issue(BaseModel):
    type: ReviewFactor
    subtype: str
    line: int
    description: str
    suggestion: str

class ErrorResult(BaseModel):
    error: str
    error_code: ErrorCode = ErrorCode.UNKNOWN

class FileResult(BaseModel):
    name: str
    issues: List[Issue]

class Summary(BaseModel):
    total_files: int
    total_issues: int
    critical_issues: int

class AnalysisResults(BaseModel):
    files: List[FileResult]
    summary: Summary
    errors: Optional[List[ErrorResult]] = []

# For unified PR review status & result
class PRReviewStatusResponse(BaseModel):
    task_id: str
    status: TaskStatus
    results: Optional[AnalysisResults | ErrorResult] = None

class ErrorResponse(BaseModel):
    error: str
    status_code: int

class ReviewStrategyContext:
    def __init__(self, strategy_name: ReviewStrategyName):
        self.strategy_name = strategy_name


class SimpleLLMReviewStrategyContext(ReviewStrategyContext):
    def __init__(self, factors: List[ReviewFactor]):
        super().__init__(strategy_name=ReviewStrategyName.SIMPLE_LLM)
        self.factors = factors
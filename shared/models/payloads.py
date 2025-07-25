from pydantic import BaseModel
from typing import List, Optional
from .enums import PlatformType, TaskStatus

class AnalyzePRRequest(BaseModel):
    platformType: PlatformType
    repo_url: str
    pr_number: int
    github_token: Optional[str] = None

class PRReviewStatusRequest(BaseModel):
    platformType: PlatformType
    repo_url: str
    pr_number: int
    github_token: Optional[str] = None

class AnalyzePRTaskPayload(BaseModel):
    task_id: str
    platformType: PlatformType
    repo_url: str
    pr_number: int
    github_token: Optional[str] = None
    status: TaskStatus

class AnalyzePRResponse(BaseModel):
    task_id: str
    status: TaskStatus

# Renamed for clarity
class TaskStatusResponse(BaseModel):
    task_id: str
    status: TaskStatus

class Issue(BaseModel):
    type: str
    line: int
    description: str
    suggestion: str

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

# For unified PR review status & result
class PRReviewStatusResponse(BaseModel):
    task_id: str
    status: TaskStatus
    results: Optional[AnalysisResults] = None

class ErrorResponse(BaseModel):
    error: str
    status_code: int
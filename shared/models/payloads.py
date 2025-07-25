from pydantic import BaseModel
from typing import Optional
from .enums import PlatformType

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
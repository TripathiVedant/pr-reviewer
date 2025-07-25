from enum import Enum

class PlatformType(str, Enum):
    GITHUB = "GITHUB"
    GITLAB = "GITLAB"
    BITBUCKET = "BITBUCKET"

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class CeleryTaskNames(str, Enum):
    EXAMPLE_TASK = "celery_worker.tasks.example_task"
    ANALYZE_PR_TASK = "celery_worker.tasks.analyze_pr_task"

class ErrorCode(str, Enum):
    UNKNOWN = "UNKNOWN"
    GITHUB_PERMISSION_DENIED = "GITHUB_PERMISSION_DENIED"
    INVALID_REPO = "INVALID_REPO"
    REPO_NOT_FOUND = "REPO_NOT_FOUND"
    GITHUB_RATE_LIMIT = "GITHUB_RATE_LIMIT"
    GITHUB_TOKEN_INVALID = "GITHUB_TOKEN_INVALID"  # Or TOKEN_INVALID if you want to generalize
    PR_NOT_FOUND = "PR_NOT_FOUND"
    GITHUB_API_ERROR = "GITHUB_API_ERROR" 
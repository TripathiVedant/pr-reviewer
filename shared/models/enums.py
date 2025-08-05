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

class ReviewFactor(str, Enum):
    CODE_STYLE = "code_style"
    BUGS = "bugs"
    PERFORMANCE = "performance"
    BEST_PRACTICES = "best_practices"

class ReviewStrategyName(str, Enum):
    SIMPLE_LLM_STRATEGY = "simple_llm_strategy"
    COMPLICATED_LLM_STRATEGY = "complicated_llm_strategy"
    # Add more as needed

class ErrorCode(str, Enum):
    UNKNOWN = "UNKNOWN"
    GITHUB_PERMISSION_DENIED = "GITHUB_PERMISSION_DENIED"
    INVALID_REPO = "INVALID_REPO"
    REPO_NOT_FOUND = "REPO_NOT_FOUND"
    GITHUB_RATE_LIMIT = "GITHUB_RATE_LIMIT"
    GITHUB_TOKEN_INVALID = "GITHUB_TOKEN_INVALID"  # Or TOKEN_INVALID if you want to generalize
    PR_NOT_FOUND = "PR_NOT_FOUND"
    GITHUB_API_ERROR = "GITHUB_API_ERROR"
    AGENT_RUNTIME_ERROR = "AGENT_RUNTIME_ERROR"
    AGENT_TIMEOUT = "AGENT_TIMEOUT"
    AGENT_PROMPT_ERROR = "AGENT_PROMPT_ERROR"
    AGENT_LLM_ERROR = "AGENT_LLM_ERROR"
    AGENT_RATE_LIMIT = "AGENT_RATE_LIMIT"
    AGENT_OUTPUT_PARSE_ERROR = "AGENT_OUTPUT_PARSE_ERROR"
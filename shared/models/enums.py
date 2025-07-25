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
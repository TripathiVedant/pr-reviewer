from shared.models.requests import AnalyzePRRequest
from shared.domains.domains import Task, TaskResult
from shared.models.enums import TaskStatus
from datetime import datetime

# Mapper: Pydantic AnalyzePRRequest -> ORM Task

def analyze_pr_request_to_task(request: AnalyzePRRequest) -> Task:
    return Task(
        platformType=request.platformType,
        repo_url=request.repo_url,
        pr_number=request.pr_number,
        status=TaskStatus.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

# Mapper: ORM TaskResult <-> Pydantic (add as needed) 
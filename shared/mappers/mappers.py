from shared.domains.domains import Task
from shared.models.payloads import AnalyzePRRequest
import uuid
from datetime import datetime, UTC


def map_analyze_pr_request_to_task(request: AnalyzePRRequest) -> Task:
    """Map an AnalyzePRRequest to a Task entity."""
    return Task(
        task_id=str(uuid.uuid4()),
        platformType=request.platformType,
        repo_url=request.repo_url,
        pr_number=request.pr_number,
        status="PENDING",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
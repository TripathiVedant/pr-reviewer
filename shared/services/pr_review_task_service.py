from shared.dao.task_dao import TaskDAO
from shared.dao.task_result_dao import TaskResultDAO
from shared.models.payloads import AnalyzePRRequest
from shared.models.enums import TaskStatus
from shared.models.payloads import PRReviewStatusResponse, AnalyzePRTaskPayload
from pr_review_app.config.celery_config import celery_app
from shared.mappers.mappers import map_analyze_pr_request_to_task
import logging

logger = logging.getLogger("pr_review_service")


class PRReviewTaskService:
    @staticmethod
    def enqueue_analysis_task(request: AnalyzePRRequest) -> str:
        """Create a new task, persist it, and enqueue it for processing."""
        # Map request to Task entity
        task = map_analyze_pr_request_to_task(request)

        # Persist the task in the database
        TaskDAO.create(task)

        # Create the Celery payload DTO
        payload = AnalyzePRTaskPayload(
            task_id=task.task_id,
            platformType=task.platformType,
            repo_url=task.repo_url,
            pr_number=task.pr_number,
            github_token=request.github_token,
            status=TaskStatus.PENDING,
        )

        # Send payload to Celery worker
        logger.info(f"Payload sent to Celery: {payload.dict()}")  
        celery_app.send_task("celery_worker.tasks.analyze_pr_task", args=[payload.dict()], task_id=task.task_id)

        logger.info(f"Enqueued Celery task with task_id={task.task_id}")
        return task.task_id

    @staticmethod
    def fetch_task_status(task_id: str) -> TaskStatus | None:
        """Fetch the status of a task."""
        task = TaskDAO.get_by_id(task_id)
        return task.status if task else None

    @staticmethod
    def fetch_task_results(task_id: str):
        """Fetch results of a completed task."""
        result = TaskResultDAO.get_by_task_id(task_id)
        return result.results if result else None

    @staticmethod
    def fetch_task_details(task_id: str):
        """Fetch both the status and results of a task."""
        status = PRReviewTaskService.fetch_task_status(task_id)
        results = PRReviewTaskService.fetch_task_results(task_id)
        return status, results

    @staticmethod
    def find_task_by_repo_pr(repo_url: str, pr_number: int):
        """Find a task based on repository URL and PR number."""
        return TaskDAO.get_by_repo_pr(repo_url, pr_number)
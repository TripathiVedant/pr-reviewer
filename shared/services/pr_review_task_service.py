from shared.dao.task_dao import TaskDAO
from shared.dao.task_result_dao import TaskResultDAO
from shared.models.payloads import AnalyzePRRequest
from shared.models.enums import TaskStatus
from shared.models.payloads import PRReviewStatusResponse, AnalyzePRTaskPayload
from pr_review_app.config.celery_config import celery_app
from shared.mappers.mappers import map_analyze_pr_request_to_task
import logging

logger = logging.getLogger(__name__)


class PRReviewTaskService:
    @staticmethod
    def enqueue_analysis_task(request: AnalyzePRRequest) -> str:
        """Create a new task, persist it, and enqueue it for processing."""
        # Map request to Task entity
        task = map_analyze_pr_request_to_task(request)

        # Persist the task in the database
        TaskDAO.create(task)

        # Create the Celery payload DTO, will be polymorphic in future.
        payload = AnalyzePRTaskPayload(
            task_id=task.task_id,
            platformType=task.platformType,
            repo_url=task.repo_url,
            pr_number=task.pr_number,
            token=request.token,
            status=TaskStatus.PENDING,
        )

        # Send payload to Celery worker
        logger.info(f"Payload sent to Celery: {payload.model_dump()}")
        celery_app.send_task("celery_worker.tasks.analyze_pr_task", args=[payload.model_dump()], task_id=task.task_id)

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

    @staticmethod
    def find_task_by_repo_pr_and_status(repo_url: str, pr_number: int, status: TaskStatus):
        """Find a task based on repository URL, PR number, and status."""
        return TaskDAO.get_by_repo_pr_and_status(repo_url, pr_number, status)

    @staticmethod
    def find_completed_task_by_repo_pr(repo_url: str, pr_number: int):
        """Find a completed task based on repository URL and PR number."""
        return TaskDAO.get_completed_by_repo_pr(repo_url, pr_number)

    @staticmethod
    def analyze_pr_with_cache_logic(request: AnalyzePRRequest, cached: bool = False):
        """
        Implements the logic for analyze_pr:
        - If cached=true and a COMPLETED report exists, return it.
        - If a PENDING or PROCESSING task exists, return it.
        - Otherwise, enqueue a new task.
        Returns (task_id, status)
        """
        if cached:
            completed_task = PRReviewTaskService.find_completed_task_by_repo_pr(request.repo_url, request.pr_number)
            if completed_task:
                logger.info(f"Found completed task with task_id={completed_task.task_id}")
                return completed_task.task_id, completed_task.status

        for status in [TaskStatus.PENDING, TaskStatus.PROCESSING]:
            existing_task = PRReviewTaskService.find_task_by_repo_pr_and_status(request.repo_url, request.pr_number, status)
            if existing_task:
                logger.info(f"Found {status} task with task_id={existing_task.task_id}")
                return existing_task.task_id, existing_task.status

        logger.info(f"No pending/Procesing task with request={request}")
        task_id = PRReviewTaskService.enqueue_analysis_task(request)
        return task_id, TaskStatus.PENDING
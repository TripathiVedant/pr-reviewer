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
        logger.info(f"event: enqueue_analysis_task, msg: Starting for Identifier: repo={request.repo_url}, pr={request.pr_number}")
        try:
            task = map_analyze_pr_request_to_task(request)
            TaskDAO.create(task)
            payload = AnalyzePRTaskPayload(
                task_id=task.task_id,
                platformType=task.platformType,
                repo_url=task.repo_url,
                pr_number=task.pr_number,
                token=request.token,
                status=TaskStatus.PENDING,
            )
            logger.info(f"event: enqueue_analysis_task, msg: Payload sent to Celery for Identifier: task_id={task.task_id}")
            celery_app.send_task("celery_worker.tasks.analyze_pr_task", args=[payload.model_dump()], task_id=task.task_id)
            logger.info(f"event: enqueue_analysis_task, msg: Returning for Identifier: task_id={task.task_id}")
            return task.task_id
        except Exception as e:
            logger.error(f"event: enqueue_analysis_task, msg: Error for Identifier: repo={request.repo_url}, pr={request.pr_number}, error={e}")
            raise

    @staticmethod
    def fetch_task_status(task_id: str) -> TaskStatus | None:
        logger.info(f"event: fetch_task_status, msg: Starting for Identifier: task_id={task_id}")
        status = TaskDAO.get_by_id(task_id).status if TaskDAO.get_by_id(task_id) else None
        logger.info(f"event: fetch_task_status, msg: Returning for Identifier: task_id={task_id}, status={status}")
        return status

    @staticmethod
    def fetch_task_results(task_id: str):
        logger.info(f"event: fetch_task_results, msg: Starting for Identifier: task_id={task_id}")
        result = TaskResultDAO.get_by_task_id(task_id)
        return result.results if result else None

    @staticmethod
    def fetch_task_details(task_id: str):
        logger.info(f"event: fetch_task_details, msg: Starting for Identifier: task_id={task_id}")
        status = PRReviewTaskService.fetch_task_status(task_id)
        results = PRReviewTaskService.fetch_task_results(task_id)
        return status, results

    @staticmethod
    def find_task_by_repo_pr(repo_url: str, pr_number: int):
        """Find a task based on repository URL and PR number."""
        
        logger.info(f"event: find_task_by_repo_pr, msg: Starting for Identifier: repo={repo_url}, pr={pr_number}")
        task = TaskDAO.get_by_repo_pr(repo_url, pr_number)
        logger.info(f"event: find_task_by_repo_pr, msg: Returning for Identifier: repo={repo_url}, pr={pr_number}, found={task is not None}")
        return task

    @staticmethod
    def find_task_by_repo_pr_and_status(repo_url: str, pr_number: int, status: TaskStatus):
        """Find a task based on repository URL, PR number, and status."""
        logger.info(f"event: find_task_by_repo_pr_and_status, msg: Starting for Identifier: repo={repo_url}, pr={pr_number}, status={status}")
        task = TaskDAO.get_by_repo_pr_and_status(repo_url, pr_number, status)
        logger.info(f"event: find_task_by_repo_pr_and_status, msg: Returning for Identifier: repo={repo_url}, pr={pr_number}, status={status}, found={task is not None}")
        return task

    @staticmethod
    def find_completed_task_by_repo_pr(repo_url: str, pr_number: int):
        """Find a task based on repository URL, PR number"""
        logger.info(f"event: find_completed_task_by_repo_pr, msg: Starting for Identifier: repo={repo_url}, pr={pr_number}")
        task = TaskDAO.get_completed_by_repo_pr(repo_url, pr_number)
        logger.info(f"event: find_completed_task_by_repo_pr, msg: Returning for Identifier: repo={repo_url}, pr={pr_number}, found={task is not None}")
        return task

    @staticmethod
    def analyze_pr_with_cache_logic(request: AnalyzePRRequest, cached: bool = False):
        """
        Implements the logic for analyze_pr:
        - If cached=true and a COMPLETED report exists, return it.
        - If a PENDING or PROCESSING task exists, return it.
        - Otherwise, enqueue a new task.
        Returns (task_id, status)
        """
        logger.info(f"event: analyze_pr_with_cache_logic, msg: Starting for Identifier: request={request}")
        try:
            if cached:
                completed_task = PRReviewTaskService.find_completed_task_by_repo_pr(request.repo_url, request.pr_number)
                if completed_task:
                    logger.info(f"event: analyze_pr_with_cache_logic, msg: Returning cached for Identifier: task_id={completed_task.task_id}")
                    return completed_task.task_id, completed_task.status
            for status in [TaskStatus.PENDING, TaskStatus.PROCESSING]:
                existing_task = PRReviewTaskService.find_task_by_repo_pr_and_status(request.repo_url, request.pr_number, status)
                if existing_task:
                    logger.info(f"event: analyze_pr_with_cache_logic, msg: Returning existing for Identifier: task_id={existing_task.task_id}, status={status}")
                    return existing_task.task_id, existing_task.status
            logger.info(f"event: analyze_pr_with_cache_logic, msg: No pending/processing task, enqueuing new for Identifier: repo={request.repo_url}, pr={request.pr_number}")
            task_id = PRReviewTaskService.enqueue_analysis_task(request)
            logger.info(f"event: analyze_pr_with_cache_logic, msg: Returning new for Identifier: task_id={task_id}")
            return task_id, TaskStatus.PENDING
        except Exception as e:
            logger.error(f"event: analyze_pr_with_cache_logic, msg: Error for Identifier: repo={request.repo_url}, pr={request.pr_number}, error={e}")
            raise
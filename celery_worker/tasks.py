from shared.dao.task_dao import TaskDAO
from shared.models.enums import TaskStatus, PlatformType, ErrorCode
from shared.models.payloads import ErrorResult
from .celery_app import celery_app
import logging
from shared.integrations.github_fetcher import GitHubPRFetcher
from shared.integrations.platform_factory import PlatformFetcherFactory
from shared.exceptions.fetcher_exceptions import FetcherException

logger = logging.getLogger(__name__)


@celery_app.task(name="celery_worker.tasks.analyze_pr_task")
def analyze_pr_task(request_data):
    """
    Celery task for analyzing a Pull Request.

    Args:
        request_data (dict): The payload for the task, including task_id and PR details.

    Process:
        1. Fetch task from DB.
        2. Update task status to PROCESSING.
        3. Fetch PR data from GitHub.
        4. Run AI code analysis.
        5. Store results and update task status in a single DAO method.
    """
    logger.info(f"Received analyze_pr_task with data: {request_data}")

    # Step 1: Validate payload
    task_id = request_data.get("task_id")
    if not task_id:
        logger.error("Task ID is missing in the payload")
        return

    # Step 2: Fetch task from DB
    task = TaskDAO.get_by_id(task_id)
    if not task:
        logger.error(f"Task with ID {task_id} not found in the database")
        return

    try:
        # Step 3: Update task status to PROCESSING
        TaskDAO.update_status(task_id=task_id, status=TaskStatus.PROCESSING)
        logger.info(f"Task {task_id} status updated to PROCESSING")

        # Step 4: Fetch PR data using platform abstraction, 
        # Todo: can be moved to inside fetcher class and turned into polymorphic dto.
        platform_type = getattr(task, 'platformType', None)
        repo_url = getattr(task, 'repo_url', None)
        pr_number = getattr(task, 'pr_number', None)
        token = request_data.get('token', None)

        fetcher = PlatformFetcherFactory.get_fetcher(platform_type)
        pr_data = fetcher.fetch_pr_data(repo_url, pr_number, token)
        logger.info(f"Fetched PR data for repo {repo_url} and PR {pr_number}, data: {pr_data}")

        # Step 5: Run AI code analysis (mocked for now)
        results = {
            "summary": {
                "total_files": len(pr_data.get("files", [])),
                "total_issues": 10,
                "critical_issues": 2,
            },
            "files": [
                {"name": f.get("filename", "file.py"), "issues": []} for f in pr_data.get("files", [])
            ],
            "diff": pr_data.get("diff", "")
        }
        logger.info(f"Code analysis completed for task {task_id}")

        # Step 6: Store results and update task status using DAO
        TaskDAO.store_results_and_update_status(task_id=task_id, results=results, status=TaskStatus.COMPLETED)

    except FetcherException as fetch_exception:
        logger.error(f"Fetcher exception: {fetch_exception}")
        error_result = ErrorResult(error=str(fetch_exception), error_code=fetch_exception.error_code).model_dump()
        TaskDAO.store_results_and_update_status(task_id=task_id, results=error_result, status=TaskStatus.FAILED)
    except Exception as e:
        logger.error(f"Error processing task {task_id}: {e}")
        error_result = ErrorResult(error=str(e), error_code=ErrorCode.UNKNOWN).model_dump()
        TaskDAO.store_results_and_update_status(task_id=task_id, results=error_result, status=TaskStatus.FAILED)
import asyncio
from shared.dao.task_dao import TaskDAO
from shared.models.enums import TaskStatus, ErrorCode
from shared.models.payloads import ErrorResult
from shared.strategies.review_strategies.complicated_llm_review_strategy import ComplicatedLLMReviewStrategy
from .celery_app import app
import logging
from shared.integrations.platform_factory import PlatformFetcherFactory
from shared.models.enums import ReviewFactor
from shared.models.payloads import SimpleLLMReviewStrategyContext, ComplicatedLLMReviewStrategyContext
from shared.strategies.review_strategies.review_strategy_factory import ReviewStrategyFactory
from shared.exceptions.fetcher_exceptions import FetcherException

logger = logging.getLogger(__name__)


@app.task(name="celery_worker.tasks.analyze_pr_task")
def analyze_pr_task(request_data):
    logger.info(f"event: analyze_pr_task, msg: Starting for Identifier: request_data={request_data}")
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
    try:
        # Step 1: Validate payload
        task_id = request_data.get("task_id")
        if not task_id:
            logger.error("event: analyze_pr_task, msg: Error for Identifier: task_id=None, error=Task ID is missing in the payload")
            return

        # Step 2: Fetch task from DB
        task = TaskDAO.get_by_id(task_id)
        if not task:
            logger.error(f"event: analyze_pr_task, msg: Error for Identifier: task_id={task_id}, error=Task with ID not found in the database")
            return

        # Step 3: Update task status to PROCESSING
        TaskDAO.update_status(task_id=task_id, status=TaskStatus.PROCESSING)
        logger.info(f"Task {task_id} status updated to PROCESSING")

        # Step 4: Fetch PR data using platform abstraction, 
        # Todo: can be moved to inside fetcher class and turned into polymorphic dto.
        platform_type = getattr(task, 'platformType', None)
        repo_url = getattr(task, 'repo_url', None)
        pr_number = getattr(task, 'pr_number', None)
        pr_review_strategy = request_data.get('pr_review_strategy', "complicated")
        token = request_data.get('token', None)

        fetcher = PlatformFetcherFactory.get_fetcher(platform_type)
        pr_data = fetcher.fetch_pr_data(repo_url, pr_number, token)
        logger.info(f"Fetched PR data for repo {repo_url} and PR {pr_number}")

        # Step 5: Run AI code analysis
        # Hardcoded review factors for now — can be made configurable per task/request in the future
        factors = [
            ReviewFactor.CODE_STYLE,
            ReviewFactor.BUGS,
            ReviewFactor.PERFORMANCE,
            ReviewFactor.BEST_PRACTICES,
        ]

        # Can use other strategies as well, based on different factors/requests.
        context_kwargs = {
            "factors": factors,
            "repo_url": repo_url,
            "pr_number": pr_number,
            "platform": platform_type,
            "token": token,
            # include any other fields required by the context class
        }

        review_strategy, context = ReviewStrategyFactory.get_strategy_by_name(pr_review_strategy, context_kwargs=context_kwargs)

        review_output = asyncio.run(review_strategy.review(pr_data["diff"], pr_data["files"], context))
        result = review_output.model_dump()
        
        logger.info(f"Code analysis completed for task {task_id}")

        # Step 6: Store results and update task status using DAO
        TaskDAO.store_results_and_update_status(task_id=task_id, results=result, status=TaskStatus.COMPLETED)
        logger.info(f"event: analyze_pr_task, msg: Returning for Identifier: task_id={task_id}")
    except FetcherException as fetch_exception:
        logger.error(f"Fetcher exception: {fetch_exception}")
        error_result = ErrorResult(error=str(fetch_exception), error_code=fetch_exception.error_code).model_dump()
        TaskDAO.store_results_and_update_status(task_id=task_id, results=error_result, status=TaskStatus.FAILED)
    except Exception as e:
        logger.error(f"event: analyze_pr_task, msg: Error for Identifier: task_id={request_data.get('task_id', None)}, error={e}")
        error_result = ErrorResult(error=str(e), error_code=ErrorCode.UNKNOWN).model_dump()
        TaskDAO.store_results_and_update_status(task_id=task_id, results=error_result, status=TaskStatus.FAILED)
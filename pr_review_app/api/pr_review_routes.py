from fastapi import APIRouter, HTTPException, Query
from shared.models.enums import CeleryTaskNames, TaskStatus
from shared.models.payloads import AnalyzePRRequest, PRReviewStatusRequest,  AnalyzePRResponse, TaskStatusResponse, PRReviewStatusResponse, ErrorResponse


from shared.services.pr_review_task_service import PRReviewTaskService

import logging

# Route paths
ROUTE_HEALTH = "/health"
ROUTE_ANALYZE_PR = "/analyze-pr"
ROUTE_STATUS = "/status/{task_id}"
ROUTE_RESULTS = "/results/{task_id}"
ROUTE_PR_REVIEW_STATUS = "/pr-review-status/latest"

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get(ROUTE_HEALTH)
def health_check():
    logger.info(f"event: health_check, msg: Starting")
    result = {"status": "ok"}
    logger.info(f"event: health_check, msg: Returning: {result}")
    return result


@router.post(
    ROUTE_ANALYZE_PR,
    response_model=AnalyzePRResponse,
    responses={400: {"model": ErrorResponse}},
)
def analyze_pr(request: AnalyzePRRequest, cached: bool = Query(False, description="Return cached result if available")):
    logger.info(f"event: analyze_pr, msg: Starting for Identifier: request={request}")
    try:
        task_id, status = PRReviewTaskService.analyze_pr_with_cache_logic(request, cached)
        logger.info(f"event: analyze_pr, msg: Returning for Identifier: task_id={task_id}, status={status}")
        return AnalyzePRResponse(task_id=task_id, status=status)
    except Exception as e:
        logger.error(f"event: analyze_pr, msg: Error for Identifier: repo={request.repo_url}, pr={request.pr_number}, error={e}")
        raise


@router.get(
    ROUTE_STATUS,
    response_model=TaskStatusResponse,
    responses={404: {"model": ErrorResponse}},
)
def get_task_status(task_id: str):
    logger.info(f"event: get_task_status, msg: Starting for Identifier: task_id={task_id}")
    status = PRReviewTaskService.fetch_task_status(task_id)
    if status is None:
        logger.error(f"event: get_task_status, msg: Error for Identifier: task_id={task_id}, error=Task not found")
        raise HTTPException(status_code=404, detail="Task not found")
    logger.info(f"event: get_task_status, msg: Returning for Identifier: task_id={task_id}, status={status}")
    return TaskStatusResponse(task_id=task_id, status=status)
    

@router.get(
    ROUTE_RESULTS,
    response_model=PRReviewStatusResponse,
    responses={404: {"model": ErrorResponse}},
)
def get_task_results(task_id: str):
    logger.info(f"event: get_task_results, msg: Starting for Identifier: task_id={task_id}")
    status, results = PRReviewTaskService.fetch_task_details(task_id)
    if results is None:
        logger.error(f"event: get_task_results, msg: Error for Identifier: task_id={task_id}, error=Task not found or not completed")
        raise HTTPException(status_code=404, detail="Task not found or not completed")
    logger.info(f"event: get_task_results, msg: Returning for Identifier: task_id={task_id}, status={status}")
    return PRReviewStatusResponse(task_id=task_id, status=status, results=results)

@router.post(
    ROUTE_PR_REVIEW_STATUS,
    response_model=PRReviewStatusResponse,
    responses={404: {"model": ErrorResponse}},
)
def get_pr_review_status(request: PRReviewStatusRequest):
    logger.info(f"event: get_pr_review_status, msg: Starting for Identifier: repo={request.repo_url}, pr={request.pr_number}")
    task = PRReviewTaskService.find_task_by_repo_pr(request.repo_url, request.pr_number)
    if not task:
        logger.error(f"event: get_pr_review_status, msg: Error for Identifier: repo={request.repo_url}, pr={request.pr_number}, error=No analysis task found for the given PR")
        raise HTTPException(status_code=404, detail="No analysis task found for the given PR")
    results = PRReviewTaskService.fetch_task_results(task.task_id)
    logger.info(f"event: get_pr_review_status, msg: Returning for Identifier: task_id={task.task_id}, status={task.status}")
    return PRReviewStatusResponse(task_id=task.task_id, status=task.status, results=results)
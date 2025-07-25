from fastapi import APIRouter, HTTPException
from shared.models.enums import CeleryTaskNames, TaskStatus
from shared.models.payloads import AnalyzePRRequest, PRReviewStatusRequest,  AnalyzePRResponse, TaskStatusResponse, PRReviewStatusResponse, ErrorResponse


from shared.services.pr_review_task_service import PRReviewTaskService

import logging

# Route paths
ROUTE_HEALTH = "/health"
ROUTE_ANALYZE_PR = "/analyze-pr"
ROUTE_STATUS = "/status/{task_id}"
ROUTE_RESULTS = "/results/{task_id}"
ROUTE_PR_REVIEW_STATUS = "/pr-review-status"

logger = logging.getLogger("pr_review_app")
print(logger.getEffectiveLevel())  # Should print 20 (INFO level)
print(logger.handlers)  # Check if any handlers are attached

router = APIRouter()

@router.get(ROUTE_HEALTH)
def health_check():
    logger.info("Health check endpoint called.")
    return {"status": "ok"}


@router.post(
    ROUTE_ANALYZE_PR,
    response_model=AnalyzePRResponse,
    responses={400: {"model": ErrorResponse}},
)
def analyze_pr(request: AnalyzePRRequest):
    logger.info(f"Received analyze-pr request for repo {request.repo_url} and PR {request.pr_number}")
    task_id = PRReviewTaskService.enqueue_analysis_task(request)
    return AnalyzePRResponse(task_id=task_id, status="PENDING")


@router.get(
    ROUTE_STATUS,
    response_model=TaskStatusResponse,
    responses={404: {"model": ErrorResponse}},
)
def get_task_status(task_id: str):
    logger.info(f"Fetching task status for task_id={task_id}")
    status = PRReviewTaskService.fetch_task_status(task_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskStatusResponse(task_id=task_id, status=status)


@router.get(
    ROUTE_RESULTS,
    response_model=PRReviewStatusResponse,
    responses={404: {"model": ErrorResponse}},
)
def get_task_results(task_id: str):
    logger.info(f"Fetching task results for task_id={task_id}")
    status, results = PRReviewTaskService.fetch_task_details(task_id)
    if results is None:
        raise HTTPException(status_code=404, detail="Task not found or not completed")
    return PRReviewStatusResponse(task_id=task_id, status=status, results=results)


@router.post(
    ROUTE_PR_REVIEW_STATUS,
    response_model=PRReviewStatusResponse,
    responses={404: {"model": ErrorResponse}},
)
def get_pr_review_status(request: PRReviewStatusRequest):
    logger.info(f"Fetching PR review status for repo {request.repo_url} and PR {request.pr_number}")
    task = PRReviewTaskService.find_task_by_repo_pr(request.repo_url, request.pr_number)
    if not task:
        raise HTTPException(status_code=404, detail="No analysis task found for the given PR")
    results = PRReviewTaskService.fetch_task_results(task.task_id)
    return PRReviewStatusResponse(task_id=task.task_id, status=task.status, results=results)
from fastapi import APIRouter, HTTPException
from shared.config import settings
from shared.models.enums import CeleryTaskNames, TaskStatus
from shared.models.requests import AnalyzePRRequest, PRReviewStatusRequest
from shared.models.responses import (
    AnalyzePRResponse, StatusResponse, ResultsResponse, ErrorResponse, PRReviewStatusResponse
)
import logging
from fastapi_app.config.celery_config import celery_app

# Route paths
ROUTE_HEALTH = "/health"
ROUTE_ANALYZE_PR = "/analyze-pr"
ROUTE_STATUS = "/status/{task_id}"
ROUTE_RESULTS = "/results/{task_id}"
ROUTE_PR_REVIEW_STATUS = "/pr-review-status"

# Status values
STATUS_QUEUED = "QUEUED"

logger = logging.getLogger("pr_review_api")

router = APIRouter()

@router.get(ROUTE_HEALTH)
def health_check():
    logger.info("Health check endpoint called.")
    return {"status": "ok"}

@router.post(ROUTE_ANALYZE_PR, response_model=AnalyzePRResponse, responses={400: {"model": ErrorResponse}})
def analyze_pr(request: AnalyzePRRequest):
    logger.info(f"Received analyze-pr request: {request}")
    # Todo: Validate repo_url, check PR existence, etc.
    result = celery_app.send_task(CeleryTaskNames.ANALYZE_PR_TASK.value, args=[request.dict()])
    logger.info(f"Task queued with id: {result.id}")
    return AnalyzePRResponse(task_id=result.id, status=STATUS_QUEUED)

@router.get(ROUTE_STATUS, response_model=StatusResponse, responses={404: {"model": ErrorResponse}})
def get_status(task_id: str):
    logger.info(f"Status check for task_id: {task_id}")
    # Todo: Query task status from Celery/Redis
    return StatusResponse(task_id=task_id, status=TaskStatus.PENDING)

@router.get(ROUTE_RESULTS, response_model=ResultsResponse, responses={404: {"model": ErrorResponse}})
def get_results(task_id: str):
    logger.info(f"Results requested for task_id: {task_id}")
    # Todo: Fetch results from DB or cache
    return ResultsResponse(task_id=task_id, status=TaskStatus.COMPLETED, results=None)

@router.post(ROUTE_PR_REVIEW_STATUS, response_model=PRReviewStatusResponse, responses={404: {"model": ErrorResponse}})
def pr_review_status(request: PRReviewStatusRequest):
    logger.info(f"PR review status requested: {request}")
    # Todo: Lookup task by PR details and return status/results
    return PRReviewStatusResponse(task_id="dummy", status=TaskStatus.COMPLETED, results=None) 
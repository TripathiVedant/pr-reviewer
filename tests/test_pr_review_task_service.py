import pytest
from unittest.mock import patch, MagicMock
from shared.services.pr_review_task_service import PRReviewTaskService
from shared.models.payloads import AnalyzePRRequest, AnalyzePRTaskPayload
from shared.models.enums import PlatformType, TaskStatus

@pytest.fixture
def analyze_pr_request():
    return AnalyzePRRequest(
        platformType=PlatformType.GITHUB,
        repo_url="https://github.com/user/repo",
        pr_number=1,
        token="dummy_token"
    )

def test_enqueue_analysis_task(analyze_pr_request):
    """DOD: Tests that enqueue_analysis_task creates a task, persists it, and enqueues it for processing via Celery."""
    with patch("shared.services.pr_review_task_service.TaskDAO.create") as mock_create, \
         patch("shared.services.pr_review_task_service.celery_app.send_task") as mock_send_task, \
         patch("shared.services.pr_review_task_service.map_analyze_pr_request_to_task") as mock_map:
        mock_task = MagicMock()
        mock_task.task_id = "test-task-id"
        mock_task.platformType = PlatformType.GITHUB
        mock_task.repo_url = "https://github.com/user/repo"
        mock_task.pr_number = 1
        mock_map.return_value = mock_task
        task_id = PRReviewTaskService.enqueue_analysis_task(analyze_pr_request)
        assert task_id == "test-task-id"
        mock_create.assert_called_once()
        mock_send_task.assert_called_once()

def test_analyze_pr_with_cache_logic_cached(analyze_pr_request):
    """DOD: Tests that analyze_pr_with_cache_logic returns a completed task if cached=True and a completed report exists."""
    with patch.object(PRReviewTaskService, "find_completed_task_by_repo_pr", return_value=MagicMock(task_id="tid", status=TaskStatus.COMPLETED)) as mock_find_completed:
        task_id, status = PRReviewTaskService.analyze_pr_with_cache_logic(analyze_pr_request, cached=True)
        assert task_id == "tid"
        assert status == TaskStatus.COMPLETED
        mock_find_completed.assert_called_once()

def test_analyze_pr_with_cache_logic_pending(analyze_pr_request):
    """DOD: Tests that analyze_pr_with_cache_logic returns a pending task if one exists and no completed report is found."""
    with patch.object(PRReviewTaskService, "find_completed_task_by_repo_pr", return_value=None), \
         patch.object(PRReviewTaskService, "find_task_by_repo_pr_and_status", side_effect=[MagicMock(task_id="tid2", status=TaskStatus.PENDING), None]), \
         patch.object(PRReviewTaskService, "enqueue_analysis_task") as mock_enqueue:
        task_id, status = PRReviewTaskService.analyze_pr_with_cache_logic(analyze_pr_request, cached=True)
        assert task_id == "tid2"
        assert status == TaskStatus.PENDING

def test_analyze_pr_with_cache_logic_new(analyze_pr_request):
    """DOD: Tests that analyze_pr_with_cache_logic enqueues a new task if no completed or pending task exists."""
    with patch.object(PRReviewTaskService, "find_completed_task_by_repo_pr", return_value=None), \
         patch.object(PRReviewTaskService, "find_task_by_repo_pr_and_status", return_value=None), \
         patch.object(PRReviewTaskService, "enqueue_analysis_task", return_value="tid3") as mock_enqueue:
        task_id, status = PRReviewTaskService.analyze_pr_with_cache_logic(analyze_pr_request, cached=True)
        assert task_id == "tid3"
        assert status == TaskStatus.PENDING
        mock_enqueue.assert_called_once() 
import pytest
from unittest.mock import patch, MagicMock
from celery_worker.tasks import analyze_pr_task
from shared.models.enums import TaskStatus, PlatformType, ErrorCode
from shared.models.payloads import AnalyzePRTaskPayload, ErrorResult
from shared.exceptions.fetcher_exceptions import FetcherException, PermissionDeniedException

def make_request_data():
    return {
        "task_id": "tid",
        "platformType": PlatformType.GITHUB,
        "repo_url": "https://github.com/user/repo",
        "pr_number": 1,
        "token": "dummy_token",
        "status": TaskStatus.PENDING,
    }

def test_analyze_pr_task_success():
    """DOD: Tests that analyze_pr_task stores COMPLETED status and results when fetcher returns successfully."""
    request_data = make_request_data()
    with patch("celery_worker.tasks.TaskDAO.get_by_id", return_value=MagicMock(**request_data)), \
         patch("celery_worker.tasks.TaskDAO.update_status"), \
         patch("celery_worker.tasks.PlatformFetcherFactory.get_fetcher") as mock_factory, \
         patch("celery_worker.tasks.TaskDAO.store_results_and_update_status") as mock_store:
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_pr_data.return_value = {"files": [], "diff": ""}
        mock_factory.return_value = mock_fetcher
        analyze_pr_task(request_data)
        call_args = mock_store.call_args
        if call_args.args:
            assert call_args.args[2] == TaskStatus.COMPLETED
        else:
            assert call_args.kwargs["status"] == TaskStatus.COMPLETED

def test_analyze_pr_task_fetcher_exception():
    """DOD: Tests that analyze_pr_task stores FAILED status and error result with correct error_code when fetcher raises a FetcherException."""
    request_data = make_request_data()
    with patch("celery_worker.tasks.TaskDAO.get_by_id", return_value=MagicMock(**request_data)), \
         patch("celery_worker.tasks.TaskDAO.update_status"), \
         patch("celery_worker.tasks.PlatformFetcherFactory.get_fetcher") as mock_factory, \
         patch("celery_worker.tasks.TaskDAO.store_results_and_update_status") as mock_store:
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_pr_data.side_effect = PermissionDeniedException("No access")
        mock_factory.return_value = mock_fetcher
        analyze_pr_task(request_data)
        call_args = mock_store.call_args
        if call_args.args:
            error_result = call_args.args[1]
            status = call_args.args[2]
        else:
            error_result = call_args.kwargs["results"]
            status = call_args.kwargs["status"]
        assert error_result["error_code"] == ErrorCode.GITHUB_PERMISSION_DENIED
        assert status == TaskStatus.FAILED

def test_analyze_pr_task_generic_exception():
    """DOD: Tests that analyze_pr_task stores FAILED status and error result with UNKNOWN error_code when an unexpected exception is raised."""
    request_data = make_request_data()
    with patch("celery_worker.tasks.TaskDAO.get_by_id", return_value=MagicMock(**request_data)), \
         patch("celery_worker.tasks.TaskDAO.update_status"), \
         patch("celery_worker.tasks.PlatformFetcherFactory.get_fetcher") as mock_factory, \
         patch("celery_worker.tasks.TaskDAO.store_results_and_update_status") as mock_store:
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_pr_data.side_effect = Exception("Some error")
        mock_factory.return_value = mock_fetcher
        analyze_pr_task(request_data)
        call_args = mock_store.call_args
        if call_args.args:
            error_result = call_args.args[1]
            status = call_args.args[2]
        else:
            error_result = call_args.kwargs["results"]
            status = call_args.kwargs["status"]
        assert error_result["error_code"] == ErrorCode.UNKNOWN
        assert status == TaskStatus.FAILED 
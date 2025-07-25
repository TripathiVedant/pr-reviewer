import pytest
from requests import HTTPError
from utils.github_errors_utils import handle_http_error
from shared.exceptions.fetcher_exceptions import (
    TokenInvalidException,
    PermissionDeniedException,
    RepoNotFoundException,
    RateLimitException,
    GitHubAPIException,
)
from unittest.mock import MagicMock

def make_http_error(status_code=None, text="error text"):
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.text = text
    return HTTPError(response=mock_resp)

def test_handle_http_error_token_invalid():
    """DOD: Raises TokenInvalidException for 401 status code."""
    with pytest.raises(TokenInvalidException):
        handle_http_error(make_http_error(401))

def test_handle_http_error_permission_denied():
    """DOD: Raises PermissionDeniedException for 403 status code."""
    with pytest.raises(PermissionDeniedException):
        handle_http_error(make_http_error(403))

def test_handle_http_error_repo_not_found():
    """DOD: Raises RepoNotFoundException for 404 status code."""
    with pytest.raises(RepoNotFoundException):
        handle_http_error(make_http_error(404))

def test_handle_http_error_rate_limit():
    """DOD: Raises RateLimitException for 429 status code."""
    with pytest.raises(RateLimitException):
        handle_http_error(make_http_error(429))

def test_handle_http_error_github_api_error():
    """DOD: Raises GitHubAPIException for other status codes."""
    with pytest.raises(GitHubAPIException):
        handle_http_error(make_http_error(500))

def test_handle_http_error_no_response():
    """DOD: Raises GitHubAPIException if HTTPError has no response."""
    err = HTTPError("no response")
    err.response = None
    with pytest.raises(GitHubAPIException):
        handle_http_error(err) 
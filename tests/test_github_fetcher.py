import pytest
from unittest.mock import patch, MagicMock
from shared.integrations.github_fetcher import GitHubPRFetcher
from shared.exceptions.fetcher_exceptions import (
    InvalidRepoException, RepoNotFoundException, PermissionDeniedException, TokenInvalidException, RateLimitException, GitHubAPIException, FetcherException
)
from requests.exceptions import HTTPError

@pytest.fixture
def fetcher():
    return GitHubPRFetcher()

def test_invalid_repo_url(fetcher):
    """DOD: Tests that fetch_pr_data raises InvalidRepoException for an invalid repo URL."""
    with pytest.raises(InvalidRepoException):
        fetcher.fetch_pr_data("invalid-url", 1, "token")


def test_fetch_pr_data_propagates_custom_exceptions(fetcher):
    """DOD: Tests that fetch_pr_data propagates custom exceptions raised by the client (no wrapping)."""
    custom_exceptions = [
        RepoNotFoundException("repo not found"),
        PermissionDeniedException("no permission"),
        TokenInvalidException("token invalid"),
        RateLimitException("rate limit"),
        GitHubAPIException("api error"),
    ]
    for exc in custom_exceptions:
        with patch.object(fetcher, "client") as mock_client:
            mock_client.get_pr_files.side_effect = exc
            mock_client.get_pr_diff.return_value = "diff"
            with pytest.raises(type(exc)):
                fetcher.fetch_pr_data("https://github.com/user/repo", 1, "token")

def test_success_path(fetcher):
    """DOD: Tests that fetch_pr_data returns the correct files and diff when the client returns successfully."""
    with patch.object(fetcher, "client") as mock_client:
        mock_client.get_pr_files.return_value = [{"filename": "file.py"}]
        mock_client.get_pr_diff.return_value = "diff"
        result = fetcher.fetch_pr_data("https://github.com/user/repo", 1, "token")
        assert result["files"] == [{"filename": "file.py"}]
        assert result["diff"] == "diff" 
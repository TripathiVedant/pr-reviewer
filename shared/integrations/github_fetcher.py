import requests
from typing import Any, Dict
from .platform_pr_fetcher import PlatformPRFetcher
from .clients.github_client import GitHubClient
from shared.exceptions.fetcher_exceptions import FetcherException, InvalidRepoException, RepoNotFoundException, PermissionDeniedException, PRNotFoundException, RateLimitException, TokenInvalidException, GitHubAPIException

class GitHubPRFetcher(PlatformPRFetcher):
    def __init__(self):
        self.client = GitHubClient()

    def fetch_pr_data(self, repo_url: str, pr_number: int, token: str) -> Dict[str, Any]:
        """
        Fetch PR data (files, diffs, etc.) from GitHub using GitHubClient.
        """
        try:
            parts = repo_url.rstrip('/').split('/')
            owner, repo = parts[-2], parts[-1]
        except Exception:
            raise InvalidRepoException("Invalid GitHub repo URL")

        try:
            files = self.client.get_pr_files(owner, repo, pr_number, token)
            diff = self.client.get_pr_diff(owner, repo, pr_number, token)
        except (
            TokenInvalidException,
            PermissionDeniedException,
            RepoNotFoundException,
            RateLimitException,
            GitHubAPIException,
        ) as known_exc:
            raise known_exc
        except Exception as e:
            raise FetcherException(f"Unexpected error while fetching PR: {str(e)}")

        return {
            "files": files,
            "diff": diff,
        }

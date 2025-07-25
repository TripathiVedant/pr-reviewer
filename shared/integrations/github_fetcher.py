import requests
from typing import Any, Dict
from .platform_pr_fetcher import PlatformPRFetcher
from .clients.github_client import GitHubClient

class GitHubPRFetcher(PlatformPRFetcher):
    def fetch_pr_data(self, repo_url: str, pr_number: int, token: str | None = None) -> Dict[str, Any]:
        """
        Fetch PR data (files, diffs, etc.) from GitHub using GitHubClient.
        """
        # Extract owner and repo from URL
        try:
            parts = repo_url.rstrip('/').split('/')
            owner, repo = parts[-2], parts[-1]
        except Exception:
            raise ValueError("Invalid GitHub repo URL")

        client = GitHubClient(token)
        files = client.get_pr_files(owner, repo, pr_number)
        diff = client.get_pr_diff(owner, repo, pr_number)

        return {
            "files": files,
            "diff": diff,
        } 
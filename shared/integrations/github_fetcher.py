import requests
from typing import Any, Dict
from .platform_base import PlatformPRFetcher

class GitHubPRFetcher(PlatformPRFetcher):
    def fetch_pr_data(self, repo_url: str, pr_number: int, token: str | None = None) -> Dict[str, Any]:
        """
        Fetch PR data (files, diffs, etc.) from GitHub.
        """
        # Extract owner and repo from URL
        # Example: https://github.com/user/repo
        try:
            parts = repo_url.rstrip('/').split('/')
            owner, repo = parts[-2], parts[-1]
        except Exception:
            raise ValueError("Invalid GitHub repo URL")

        headers = {"Accept": "application/vnd.github.v3+json"}
        if token:
            headers["Authorization"] = f"token {token}"

        # Get PR files
        files_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
        files_resp = requests.get(files_url, headers=headers)
        files_resp.raise_for_status()
        files = files_resp.json()

        # Get PR diff
        diff_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
        diff_headers = headers.copy()
        diff_headers["Accept"] = "application/vnd.github.v3.diff"
        diff_resp = requests.get(diff_url, headers=diff_headers)
        diff_resp.raise_for_status()
        diff = diff_resp.text

        return {
            "files": files,
            "diff": diff,
        } 
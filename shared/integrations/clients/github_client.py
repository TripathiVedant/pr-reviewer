import requests
from typing import Any, Dict, Optional

class GitHubClient:
    def __init__(self, token: Optional[str] = None):
        self.base_url = "https://api.github.com"
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if token:
            self.headers["Authorization"] = f"token {token}"

    def get_pr_files(self, owner: str, repo: str, pr_number: int) -> Any:
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def get_pr_diff(self, owner: str, repo: str, pr_number: int) -> str:
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        diff_headers = self.headers.copy()
        diff_headers["Accept"] = "application/vnd.github.v3.diff"
        resp = requests.get(url, headers=diff_headers)
        resp.raise_for_status()
        return resp.text 
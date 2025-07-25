import requests
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class GitHubClient:
    """
    Client for GitHub API.
    """
    def __init__(self, token: Optional[str] = None):
        logger.info(f"[DEBUG] Token in GitHubClient.__init__: {token}")
        self.base_url = "https://api.github.com"
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if token:
            self.headers["Authorization"] = f"token {token}"

    def get_pr_files(self, owner: str, repo: str, pr_number: int) -> Any:
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        try:
            resp = requests.get(url, headers=self.headers)
            resp.raise_for_status()
            return resp.json()
        except requests.HTTPError as e:
            logger.error(f"Status code: {resp.status_code}, Response: {resp.text}, Headers: {resp.headers}")
            raise


    def get_pr_diff(self, owner: str, repo: str, pr_number: int) -> str:
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        diff_headers = self.headers.copy()
        diff_headers["Accept"] = "application/vnd.github.v3.diff"
        try:
            resp = requests.get(url, headers=diff_headers)
            resp.raise_for_status()
            return resp.text
        except requests.HTTPError as e:
            logger.error(f"Status code: {resp.status_code}, Response: {resp.text}, Headers: {resp.headers}")
            raise 
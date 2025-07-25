import logging
import requests
from typing import Optional, Any
from shared.utils.github_errors_utils import handle_http_error

logger = logging.getLogger(__name__)


class GitHubClient:
    """
    Client for GitHub API.
    """
    def __init__(self):
        self.base_url = "https://api.github.com"

    def _make_headers(self, token: Optional[str], accept: str = "application/vnd.github.v3+json") -> dict:
        headers = {"Accept": accept}
        if token:
            headers["Authorization"] = f"token {token}"
        return headers

    def get_pr_files(self, owner: str, repo: str, pr_number: int, token: Optional[str]) -> Any:
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        headers = self._make_headers(token)
        try:
            resp = requests.get(url, headers=headers)
            resp.raise_for_status()
            return resp.json()
        except requests.HTTPError as e:
            logger.error(
                f"[GitHub API Error] | repos: {repo} | owner: {owner} | pr_number: {pr_number} | URL: {url} | HTTPError: {e}"
            )
            handle_http_error(e)

    def get_pr_diff(self, owner: str, repo: str, pr_number: int, token: Optional[str]) -> str:
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        headers = self._make_headers(token, accept="application/vnd.github.v3.diff")
        try:
            resp = requests.get(url, headers=headers)
            resp.raise_for_status()
            return resp.text
        except requests.HTTPError as e:
            logger.error(
                f"[GitHub API Error] | repos: {repo} | owner: {owner} | pr_number: {pr_number} | URL: {url} | HTTPError: {e}"
            )
            handle_http_error(e)

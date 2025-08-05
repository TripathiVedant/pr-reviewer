import logging
import requests
from typing import Optional, Any, Dict
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

    def get_all_files_by_branch(self, owner: str, repo: str, token: Optional[str], branch: str) -> Dict[str, str]:
        """
        Recursively fetch all files and their contents from a specific branch using the GitHub Contents API.

        Args:
            owner (str): Repository owner.
            repo (str): Repository name.
            token (Optional[str]): GitHub token.
            branch (str): Branch name to fetch files from.

        Returns:
            Dict[str, str]: Mapping of file paths to their decoded contents.
        """
        headers = self._make_headers(token)
        base_contents_url = f"{self.base_url}/repos/{owner}/{repo}/contents"
        file_contents: Dict[str, str] = {}

        def fetch_directory(path: str):
            url = f"{base_contents_url}/{path}?ref={branch}" if path else f"{base_contents_url}?ref={branch}"
            try:
                resp = requests.get(url, headers=headers)
                resp.raise_for_status()
                items = resp.json()

                if not isinstance(items, list):  # It's a file, not a directory
                    items = [items]

                for item in items:
                    if item["type"] == "file":
                        try:
                            file_resp = requests.get(item["download_url"], headers=headers)
                            file_resp.raise_for_status()
                            file_contents[item["path"]] = file_resp.text
                        except requests.HTTPError as e:
                            logger.warning(f"[GitHub API Warning] | Skipping file: {item['path']} | HTTPError: {e}")
                            continue

                    elif item["type"] == "dir":
                        fetch_directory(item["path"])

            except requests.HTTPError as e:
                logger.error(f"[GitHub API Error] | Fetching path: {path} | URL: {url} | HTTPError: {e}")
                handle_http_error(e)

        fetch_directory("")  # Start from the root
        return file_contents


    def get_all_files(self, owner: str, repo: str, pr_number: int, token: Optional[str]) -> Dict[str, str]:
        """
        Fetch all files in the head branch of a PR.

        Args:
            owner (str): Repo owner.
            repo (str): Repo name.
            pr_number (int): Pull Request number.
            token (Optional[str]): GitHub access token.

        Returns:
            Dict[str, str]: Mapping from file path to file content in the PR branch.
        """
        headers = self._make_headers(token)

        # Step 1: Get the PR metadata to extract the head branch
        pr_url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        try:
            pr_resp = requests.get(pr_url, headers=headers)
            pr_resp.raise_for_status()
            pr_data = pr_resp.json()
            branch = pr_data["head"]["ref"]
        except requests.HTTPError as e:
            logger.error(f"[GitHub API Error] | Could not get PR metadata | URL: {pr_url} | HTTPError: {e}")
            handle_http_error(e)

        # Step 2: Use the branch to fetch all files
        return self.get_all_files_by_branch(owner, repo, token, branch)
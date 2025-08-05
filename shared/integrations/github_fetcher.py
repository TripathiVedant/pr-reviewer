import requests
import logging
from typing import Any, Dict
from .platform_pr_fetcher import PlatformPRFetcher
from .clients.github_client import GitHubClient
from shared.exceptions.fetcher_exceptions import FetcherException, InvalidRepoException, RepoNotFoundException, PermissionDeniedException, PRNotFoundException, RateLimitException, TokenInvalidException, GitHubAPIException

logger = logging.getLogger(__name__)

class GitHubPRFetcher(PlatformPRFetcher):
    def __init__(self):
        self.client = GitHubClient()

    def fetch_pr_data(self, repo_url: str, pr_number: int, token: str) -> Dict[str, Any]:
        """
            Fetch PR data (files, diffs, and full file tree) from GitHub using GitHubClient.

            Returns:
                Dict[str, Any]: {
                    "files": [...],    # Changed files with metadata
                    "diff": "...",     # Unified diff as string
                }
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

        logger.debug(f"Files: {files}")
        logger.debug(f"Diff: {diff}")

        return {
            "files": files,
            "diff": diff
        }

    def fetch_entire_code_for_branch(self, repo_url: str, pr_number: int, token: str) -> Dict[str, Any]:
        """
            Fetch all full file tree from GitHub using GitHubClient.

            Returns:
               "all_files": {...} # Full repo files mapping {path: content}

        """
        try:
            parts = repo_url.rstrip('/').split('/')
            owner, repo = parts[-2], parts[-1]
        except Exception:
            raise InvalidRepoException("Invalid GitHub repo URL")

        try:
            all_files = self.client.get_all_files(owner, repo, pr_number, token)
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

        logger.debug(f"Total Repo Files: {len(all_files)}")

        return all_files

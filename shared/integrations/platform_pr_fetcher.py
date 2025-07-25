from abc import ABC, abstractmethod
from typing import Any, Dict

class PlatformPRFetcher(ABC):
    """
    Abstract base class for platform PR fetcher. (platform can be github, gitlab, bitbucket, etc.)
    """
    @abstractmethod
    def fetch_pr_data(self, repo_url: str, pr_number: int, token: str | None = None) -> Dict[str, Any]:
        """
        Fetch PR data (diffs, files, etc.) from the platform.
        Args:
            repo_url (str): Repository URL
            pr_number (int): Pull request number
            token (str | None): Optional authentication token
        Returns:
            Dict[str, Any]: PR data (should be standardized for analysis)
        """
        pass 
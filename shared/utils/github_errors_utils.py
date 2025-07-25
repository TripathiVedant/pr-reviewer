import logging
from requests import HTTPError

from shared.exceptions.fetcher_exceptions import (
    TokenInvalidException,
    PermissionDeniedException,
    RepoNotFoundException,
    RateLimitException,
    GitHubAPIException,
)

logger = logging.getLogger(__name__)


def handle_http_error(e: HTTPError) -> None:
    resp = e.response
    if resp is not None:
        status_code = resp.status_code
        if status_code == 401:
            raise TokenInvalidException(resp.text)
        elif status_code == 403:
            raise PermissionDeniedException(resp.text)
        elif status_code == 404:
            raise RepoNotFoundException(resp.text)
        elif status_code == 429:
            raise RateLimitException(resp.text)
        else:
            raise GitHubAPIException(resp.text)
    else:
        raise GitHubAPIException(f"Unknown error occurred Error: {str(e)})")

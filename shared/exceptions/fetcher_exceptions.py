from shared.models.enums import ErrorCode

class FetcherException(Exception):
    def __init__(self, message: str, error_code: ErrorCode = ErrorCode.UNKNOWN):
        super().__init__(message)
        self.error_code = error_code

class InvalidRepoException(FetcherException):
    def __init__(self, message: str):
        super().__init__(message, ErrorCode.INVALID_REPO)

class RepoNotFoundException(FetcherException):
    def __init__(self, message: str):
        super().__init__(message, ErrorCode.REPO_NOT_FOUND)

class PermissionDeniedException(FetcherException):
    def __init__(self, message: str):
        super().__init__(message, ErrorCode.GITHUB_PERMISSION_DENIED)

class PRNotFoundException(FetcherException):
    def __init__(self, message: str):
        super().__init__(message, ErrorCode.PR_NOT_FOUND)

class RateLimitException(FetcherException):
    def __init__(self, message: str):
        super().__init__(message, ErrorCode.GITHUB_RATE_LIMIT)

class TokenInvalidException(FetcherException):
    def __init__(self, message: str):
        super().__init__(message, ErrorCode.GITHUB_TOKEN_INVALID)

class GitHubAPIException(FetcherException):
    def __init__(self, message: str):
        super().__init__(message, ErrorCode.GITHUB_API_ERROR) 
from shared.models.enums import PlatformType
from .github_fetcher import GitHubPRFetcher
# from .gitlab_fetcher import GitLabPRFetcher  # For future
# from .bitbucket_fetcher import BitbucketPRFetcher  # For future

class PlatformFetcherFactory:
    @staticmethod
    def get_fetcher(platform_type: PlatformType):
        if platform_type == PlatformType.GITHUB:
            return GitHubPRFetcher()
        # elif platform_type == PlatformType.GITLAB:
        #     return GitLabPRFetcher()
        # elif platform_type == PlatformType.BITBUCKET:
        #     return BitbucketPRFetcher()
        else:
            raise NotImplementedError(f"Platform {platform_type} not supported yet.") 
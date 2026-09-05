class GitHubApiError(Exception):
    """Error returned by the GitHub API."""

    def __init__(
        self,
        status_code: int,
        message: str,
    ) -> None:
        self.status_code = status_code
        self.message = message

        super().__init__(
            f"GitHub API error ({status_code}): {message}"
        )
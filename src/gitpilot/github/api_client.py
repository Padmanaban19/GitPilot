import httpx

from gitpilot.github.auth import get_github_token
from gitpilot.github.errors import GitHubApiError


class GitHubApiClient:
    """GitHub REST API client."""

    def __init__(self, token: str | None = None) -> None:
        if token is None:
            token = get_github_token()

        if not token.strip():
            raise ValueError("GitHub token cannot be empty.")

        self._client = httpx.Client(
            base_url="https://api.github.com",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )

    def branch_exists(
        self,
        owner: str,
        repository: str,
        branch: str,
    ) -> bool:
        """Check whether a branch exists."""

        response = self._client.get(
            f"/repos/{owner}/{repository}/git/ref/heads/{branch}"
        )

        if response.status_code == 404:
            return False

        self._raise_for_status(response)

        return True
    def create_branch(
        self,
        owner: str,
        repository: str,
        source: str,
        target: str,
    ) -> None:
        """Create a branch from an existing source branch."""

        if self.branch_exists(owner, repository, target):
            raise GitHubApiError(
                status_code=422,
                message=f"Branch '{target}' already exists.",
            )

        response = self._client.get(
            f"/repos/{owner}/{repository}/git/ref/heads/{source}"
        )
        self._raise_for_status(response)

        source_sha = response.json()["object"]["sha"]

        response = self._client.post(
            f"/repos/{owner}/{repository}/git/refs",
            json={
                "ref": f"refs/heads/{target}",
                "sha": source_sha,
            },
        )
        self._raise_for_status(response)

    def get_repository(
        self,
        owner: str,
        repository: str,
    ) -> dict:
        """Get repository information."""

        response = self._client.get(
            f"/repos/{owner}/{repository}"
        )
        self._raise_for_status(response)

        return response.json()

    def _raise_for_status(
        self,
        response: httpx.Response,
    ) -> None:
        """Raise a GitHub-specific error for unsuccessful responses."""

        if response.is_success:
            return

        try:
            data = response.json()
            message = data.get("message", response.text)
        except ValueError:
            message = response.text

        raise GitHubApiError(
        status_code=response.status_code,
        message=message,
        )

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()
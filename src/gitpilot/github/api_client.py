import time
from types import TracebackType
from typing import Self
from urllib.parse import quote

import httpx

from gitpilot.github.auth import get_github_token
from gitpilot.github.errors import GitHubApiError

RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
MAX_RETRIES = 3
RETRY_DELAY = 1.0


class GitHubApiClient:
    """GitHub REST API client."""

    def __init__(
        self,
        token: str | None = None,
        retry_delay: float = RETRY_DELAY,
    ) -> None:
        if token is None:
            token = get_github_token()

        if not token.strip():
            raise ValueError("GitHub token cannot be empty.")

        self._retry_delay = retry_delay

        self._client = httpx.Client(
            base_url="https://api.github.com",
            timeout=10.0,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )

    def _request(
        self,
        method: str,
        url: str,
        **kwargs: object,
    ) -> httpx.Response:
        """Make an HTTP request with retries for transient failures."""

        for attempt in range(MAX_RETRIES + 1):
            response = self._client.request(method, url, **kwargs)

            if response.status_code not in RETRYABLE_STATUS_CODES:
                return response

            if attempt == MAX_RETRIES:
                return response

            time.sleep(self._retry_delay)

        raise RuntimeError("Unexpected retry state.")

    def branch_exists(
        self,
        owner: str,
        repository: str,
        branch: str,
    ) -> bool:
        """Check whether a branch exists."""

        response = self._request(
            "GET", f"/repos/{owner}/{repository}/git/ref/heads/{branch}"
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

        response = self._request(
            "GET", f"/repos/{owner}/{repository}/git/ref/heads/{source}"
        )
        self._raise_for_status(response)

        source_sha = response.json()["object"]["sha"]

        response = self._request(
            "POST",
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

        response = self._request("GET", f"/repos/{owner}/{repository}")
        self._raise_for_status(response)

        return response.json()

    def get_repository_variable(
        self,
        owner: str,
        repository: str,
        name: str,
    ) -> dict | None:
        """Get a repository variable by name."""
        response = self._request(
            "GET",
            f"/repos/{owner}/{repository}/actions/variables/{name}",
        )

        if response.status_code == 404:
            return None

        self._raise_for_status(response)
        return response.json()

    def set_repository_variable(
        self,
        owner: str,
        repository: str,
        name: str,
        value: str,
    ) -> None:
        """Create or update a repository variable."""
        response = self._request(
            "POST",
            f"/repos/{owner}/{repository}/actions/variables",
            json={
                "name": name,
                "value": value,
            },
        )

        if response.status_code == 201:
            return

        if response.status_code == 422:
            response = self._request(
                "PATCH",
                f"/repos/{owner}/{repository}/actions/variables/{name}",
                json={
                    "name": name,
                    "value": value,
                },
            )

        self._raise_for_status(response)

    def get_repository_secret_public_key(
        self,
        owner: str,
        repository: str,
    ) -> dict:
        """Get the public key used to encrypt repository secrets."""
        response = self._request(
            "GET",
            f"/repos/{owner}/{repository}/actions/secrets/public-key",
        )
        self._raise_for_status(response)
        return response.json()

    def get_repository_secret(
        self,
        owner: str,
        repository: str,
        name: str,
    ) -> dict | None:
        """Get a repository secret by name."""
        response = self._request(
            "GET",
            f"/repos/{owner}/{repository}/actions/secrets/{name}",
        )
        if response.status_code == 404:
            return None
        self._raise_for_status(response)
        return response.json()

    def set_repository_secret(
        self,
        owner: str,
        repository: str,
        name: str,
        encrypted_value: str,
        key_id: str,
    ) -> None:
        """Create or update a repository secret."""
        response = self._request(
            "PUT",
            f"/repos/{owner}/{repository}/actions/secrets/{name}",
            json={
                "encrypted_value": encrypted_value,
                "key_id": key_id,
            },
        )

        if response.status_code not in {201, 204}:
            self._raise_for_status(response)

    def get_environment(
        self,
        owner: str,
        repository: str,
        environment: str,
    ) -> dict | None:
        environment_path = quote(environment, safe="")

        response = self._request(
            "GET",
            f"/repos/{owner}/{repository}/environments/{environment_path}",
        )

        if response.status_code == 404:
            return None

        self._raise_for_status(response)
        return response.json()


    def create_environment(
        self,
        owner: str,
        repository: str,
        environment: str,
    ) -> None:
        environment_path = quote(environment, safe="")

        response = self._request(
            "PUT",
            f"/repos/{owner}/{repository}/environments/{environment_path}",
        )

        self._raise_for_status(response)


    def delete_environment(
        self,
        owner: str,
        repository: str,
        environment: str,
    ) -> None:
        environment_path = quote(environment, safe="")
        
        response = self._request(
            "DELETE",
            f"/repos/{owner}/{repository}/environments/{environment_path}",
        )

        if response.status_code == 404:
            return

        self._raise_for_status(response)

    def get_environment_variable(
        self,
        owner: str,
        repository: str,
        environment: str,
        name: str,
    ) -> dict | None:
        environment_path = quote(environment, safe="")

        response = self._request(
            "GET",
            f"/repos/{owner}/{repository}/environments/"
            f"{environment_path}/variables/{name}",
        )

        if response.status_code == 404:
            return None

        self._raise_for_status(response)
        return response.json()


    def set_environment_variable(
        self,
        owner: str,
        repository: str,
        environment: str,
        name: str,
        value: str,
    ) -> None:
        environment_path = quote(environment, safe="")

        response = self._request(
            "POST",
            f"/repos/{owner}/{repository}/environments/"
            f"{environment_path}/variables",
            json={
                "name": name,
                "value": value,
            },
        )

        if response.status_code == 201:
            return

        if response.status_code == 422:
            response = self._request(
                "PATCH",
                f"/repos/{owner}/{repository}/environments/"
                f"{environment_path}/variables/{name}",
                json={
                    "name": name,
                    "value": value,
                },
            )

        self._raise_for_status(response)

    def get_environment_secret_public_key(
        self,
        owner: str,
        repository: str,
        environment: str,
    ) -> dict:
        environment_path = quote(environment, safe="")

        response = self._request(
            "GET",
            f"/repos/{owner}/{repository}/environments/"
            f"{environment_path}/secrets/public-key",
        )

        self._raise_for_status(response)
        return response.json()

    def get_environment_secret(
        self,
        owner: str,
        repository: str,
        environment: str,
        name: str,
    ) -> dict | None:
        environment_path = quote(environment, safe="")

        response = self._request(
            "GET",
            f"/repos/{owner}/{repository}/environments/"
            f"{environment_path}/secrets/{name}",
        )

        if response.status_code == 404:
            return None

        self._raise_for_status(response)
        return response.json()

    def set_environment_secret(
        self,
        owner: str,
        repository: str,
        environment: str,
        name: str,
        encrypted_value: str,
        key_id: str,
    ) -> None:
        environment_path = quote(environment, safe="")

        response = self._request(
            "PUT",
            f"/repos/{owner}/{repository}/environments/"
            f"{environment_path}/secrets/{name}",
            json={
                "encrypted_value": encrypted_value,
                "key_id": key_id,
            },
        )

        if response.status_code not in {201, 204}:
            self._raise_for_status(response)

    def delete_environment_variable(
        self,
        owner: str,
        repository: str,
        environment: str,
        name: str,
    ) -> None:
        environment_path = quote(environment, safe="")

        response = self._request(
            "DELETE",
            f"/repos/{owner}/{repository}/environments/"
            f"{environment_path}/variables/{name}",
        )

        if response.status_code == 404:
            return

        self._raise_for_status(response)


    def delete_environment_secret(
        self,
        owner: str,
        repository: str,
        environment: str,
        name: str,
    ) -> None:
        environment_path = quote(environment, safe="")

        response = self._request(
            "DELETE",
            f"/repos/{owner}/{repository}/environments/"
            f"{environment_path}/secrets/{name}",
        )

        if response.status_code == 404:
            return

        self._raise_for_status(response)

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

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

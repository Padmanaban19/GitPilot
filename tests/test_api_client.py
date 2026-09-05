import json

import httpx
import pytest

from gitpilot.github.api_client import GitHubApiClient
from gitpilot.github.errors import GitHubApiError


def test_get_repository_success():
    client = GitHubApiClient(token="test-token")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/repos/company/repoA"
        assert request.headers["Authorization"] == "Bearer test-token"

        return httpx.Response(
            200,
            json={
                "name": "repoA",
                "private": False,
            },
        )

    client._client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://api.github.com",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer test-token",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )

    repository = client.get_repository(
        "company",
        "repoA",
    )

    assert repository["name"] == "repoA"
    assert repository["private"] is False

    client.close()


def test_get_repository_raises_api_error():
    client = GitHubApiClient(token="test-token")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            404,
            json={"message": "Not Found"},
        )

    client._client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://api.github.com",
    )

    with pytest.raises(
        GitHubApiError,
        match="GitHub API error \\(404\\): Not Found",
    ):
        client.get_repository(
            "company",
            "does-not-exist",
        )

    client.close()


def test_branch_exists_returns_true():
    client = GitHubApiClient(token="test-token")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/repos/company/repoA/git/ref/heads/main"

        return httpx.Response(
            200,
            json={
                "ref": "refs/heads/main",
            },
        )

    client._client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://api.github.com",
    )

    assert client.branch_exists(
        "company",
        "repoA",
        "main",
    ) is True

    client.close()


def test_branch_exists_returns_false_for_missing_branch():
    client = GitHubApiClient(token="test-token")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            404,
            json={"message": "Not Found"},
        )

    client._client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://api.github.com",
    )

    assert client.branch_exists(
        "company",
        "repoA",
        "does-not-exist",
    ) is False

    client.close()

def test_create_branch_success():
    client = GitHubApiClient(token="test-token")

    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)

        if request.method == "GET":
            if request.url.path.endswith("/git/ref/heads/dev/test"):
                return httpx.Response(
                    404,
                    json={"message": "Not Found"},
                )

            if request.url.path.endswith("/git/ref/heads/main"):
                return httpx.Response(
                    200,
                    json={
                        "object": {
                            "sha": "abc123",
                        },
                    },
                )

            raise AssertionError(
                f"Unexpected GET path: {request.url.path}"
            )

        if request.method == "POST":
            assert request.url.path == "/repos/company/repoA/git/refs"

            assert json.loads(request.content) == {
                "ref": "refs/heads/dev/test",
                "sha": "abc123",
            }

            return httpx.Response(
                201,
                json={
                    "ref": "refs/heads/dev/test",
                },
            )

        raise AssertionError(f"Unexpected request: {request.method}")

    client._client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://api.github.com",
    )
        
    client.create_branch(
        owner="company",
        repository="repoA",
        source="main",
        target="dev/test",
    )

    assert len(requests) == 3
    assert requests[0].method == "GET"
    assert requests[1].method == "GET"
    assert requests[2].method == "POST"
    client.close()
import json
from unittest.mock import Mock

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


def test_client_uses_ten_second_timeout() -> None:
    client = GitHubApiClient(token="test-token")

    assert client._client.timeout.connect == 10.0
    assert client._client.timeout.read == 10.0
    assert client._client.timeout.write == 10.0
    assert client._client.timeout.pool == 10.0

    client.close()


def test_client_context_manager_closes_client() -> None:
    with GitHubApiClient(token="test-token") as client:
        assert not client._client.is_closed

    assert client._client.is_closed


def test_request_retries_transient_failures() -> None:
    client = GitHubApiClient(token="test-token", retry_delay=0)

    responses = [
        httpx.Response(503),
        httpx.Response(503),
        httpx.Response(200),
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        return responses.pop(0)

    client._client = httpx.Client(
        base_url="https://api.github.com",
        transport=httpx.MockTransport(handler),
    )

    response = client._request("GET", "/test")

    assert response.status_code == 200
    assert len(responses) == 0

    client.close()


def test_request_stops_after_max_retries() -> None:
    client = GitHubApiClient(token="test-token", retry_delay=0)

    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        return httpx.Response(503)

    client._client = httpx.Client(
        base_url="https://api.github.com",
        transport=httpx.MockTransport(handler),
    )


    response = client._request("GET", "/test")

    assert response.status_code == 503
    assert attempts == 4

    client.close()

def test_get_repository_variable_success():
    client = GitHubApiClient(token="test-token")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert (
            request.url.path
            == "/repos/company/repoA/actions/variables/APP_ENV"
        )

        return httpx.Response(
            200,
            json={
                "name": "APP_ENV",
                "value": "production",
            },
        )

    client._client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://api.github.com",
    )

    variable = client.get_repository_variable(
        owner="company",
        repository="repoA",
        name="APP_ENV",
    )

    assert variable == {
        "name": "APP_ENV",
        "value": "production",
    }

    client.close()

def test_get_repository_variable_returns_none_for_missing_variable():
    client = GitHubApiClient(token="test-token")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert (
            request.url.path
            == "/repos/company/repoA/actions/variables/DOES_NOT_EXIST"
        )

        return httpx.Response(
            404,
            json={"message": "Not Found"},
        )

    client._client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://api.github.com",
    )

    variable = client.get_repository_variable(
        owner="company",
        repository="repoA",
        name="DOES_NOT_EXIST",
    )

    assert variable is None

    client.close()

def test_set_repository_variable_success():
    client = GitHubApiClient(token="test-token")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert (
            request.url.path
            == "/repos/company/repoA/actions/variables"
        )
        assert json.loads(request.content) == {
            "name": "APP_ENV",
            "value": "production",
        }

        return httpx.Response(
            201,
            json={
                "name": "APP_ENV",
                "value": "production",
            },
        )

    client._client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://api.github.com",
    )

    client.set_repository_variable(
        owner="company",
        repository="repoA",
        name="APP_ENV",
        value="production",
    )

    client.close()

def test_set_repository_variable_updates_existing_variable():
    client = GitHubApiClient(token="test-token")

    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST":
            assert (
                request.url.path
                == "/repos/company/repoA/actions/variables"
            )
            assert json.loads(request.content) == {
                "name": "APP_ENV",
                "value": "production",
            }

            return httpx.Response(
                422,
                json={"message": "Validation Failed"},
            )

        if request.method == "PATCH":
            assert (
                request.url.path
                == "/repos/company/repoA/actions/variables/APP_ENV"
            )
            assert json.loads(request.content) == {
                "name": "APP_ENV",
                "value": "production",
            }

            return httpx.Response(204)

        raise AssertionError(f"Unexpected request: {request.method}")


    client._client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://api.github.com",
    )

    client.set_repository_variable(
        owner="company",
        repository="repoA",
        name="APP_ENV",
        value="production",
    )

    client.close()


def test_get_repository_secret_public_key_success():
    client = GitHubApiClient(token="test-token")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert (
            request.url.path
            == "/repos/company/repoA/actions/secrets/public-key"
        )

        return httpx.Response(
            200,
            json={
                "key_id": "123456",
                "key": "public-key-value",
            },
        )

    client._client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://api.github.com",
    )

    public_key = client.get_repository_secret_public_key(
        owner="company",
        repository="repoA",
    )

    assert public_key == {
        "key_id": "123456",
        "key": "public-key-value",
    }

    client.close()

def test_get_repository_secret_success():
    client = GitHubApiClient(token="test-token")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert (
            request.url.path
            == "/repos/company/repoA/actions/secrets/MY_SECRET"
        )

        return httpx.Response(
            200,
            json={
                "name": "MY_SECRET",
                "created_at": "2026-01-01T00:00:00Z",
                "updated_at": "2026-01-02T00:00:00Z",
            },
        )

    client._client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://api.github.com",
    )

    secret = client.get_repository_secret(
        owner="company",
        repository="repoA",
        name="MY_SECRET",
    )

    assert secret == {
        "name": "MY_SECRET",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-02T00:00:00Z",
    }

    client.close()

def test_get_repository_secret_missing():
    client = GitHubApiClient(token="test-token")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404)

    client._client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://api.github.com",
    )

    secret = client.get_repository_secret(
        owner="company",
        repository="repoA",
        name="MISSING_SECRET",
    )

    assert secret is None

    client.close()

def test_set_repository_secret_success():
    client = GitHubApiClient(token="test-token")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "PUT"
        assert (
            request.url.path
            == "/repos/company/repoA/actions/secrets/MY_SECRET"
        )
        assert request.read().decode() == (
            '{"encrypted_value":"encrypted-value","key_id":"123456"}'
        )

        return httpx.Response(201)

    client._client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://api.github.com",
    )

    client.set_repository_secret(
        owner="company",
        repository="repoA",
        name="MY_SECRET",
        encrypted_value="encrypted-value",
        key_id="123456",
    )

    client.close()

def test_set_repository_secret_update_success():
    client = GitHubApiClient(token="test-token")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "PUT"
        assert (
            request.url.path
            == "/repos/company/repoA/actions/secrets/MY_SECRET"
        )

        return httpx.Response(204)

    client._client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://api.github.com",
    )

    client.set_repository_secret(
        owner="company",
        repository="repoA",
        name="MY_SECRET",
        encrypted_value="encrypted-value",
        key_id="123456",
    )

    client.close()

def test_get_environment_returns_environment() -> None:
    client = GitHubApiClient(token="test-token")

    response = httpx.Response(
        200,
        json={"name": "production"},
    )

    client._client = Mock()
    client._client.request.return_value = response

    result = client.get_environment(
        owner="acme",
        repository="app",
        environment="production",
    )

    assert result == {"name": "production"}


def test_get_environment_returns_none_when_missing() -> None:
    client = GitHubApiClient(token="test-token")

    response = httpx.Response(404)

    client._client = Mock()
    client._client.request.return_value = response

    result = client.get_environment(
        owner="acme",
        repository="app",
        environment="production",
    )

    assert result is None


def test_create_environment() -> None:
    client = GitHubApiClient(token="test-token")

    response = httpx.Response(200)

    client._client = Mock()
    client._client.request.return_value = response

    client.create_environment(
        owner="acme",
        repository="app",
        environment="production",
    )

    request = client._client.request.call_args
    assert request.args == (
        "PUT",
        "/repos/acme/app/environments/production",
    )


def test_delete_environment() -> None:
    client = GitHubApiClient(token="test-token")

    response = httpx.Response(204)

    client._client = Mock()
    client._client.request.return_value = response

    client.delete_environment(
        owner="acme",
        repository="app",
        environment="production",
    )

    request = client._client.request.call_args
    assert request.args == (
        "DELETE",
        "/repos/acme/app/environments/production",
    )

def test_environment_name_is_url_encoded() -> None:
    client = GitHubApiClient(token="test-token")

    response = httpx.Response(
        200,
        json={"name": "production/release"},
    )

    client._client = Mock()
    client._client.request.return_value = response

    result = client.get_environment(
        owner="acme",
        repository="app",
        environment="production/release",
    )

    assert result == {"name": "production/release"}

    request = client._client.request.call_args
    assert request.args == (
        "GET",
        "/repos/acme/app/environments/production%2Frelease",
    )
from gitpilot.core.configuration import EnvironmentTarget
from gitpilot.core.environment_operations import create_environment_operation
from gitpilot.core.repositories import RepositoryTarget
from gitpilot.core.results import OperationStatus
from gitpilot.github.fake_client import FakeGitHubClient


def test_create_environment_operation() -> None:
    client = FakeGitHubClient()

    target = EnvironmentTarget(
        owner="acme",
        repository="app",
        name="production",
    )

    operation = create_environment_operation(
        client=client,
        target=target,
    )

    result = operation(
        RepositoryTarget(
            owner="acme",
            name="app",
        )
    )

    assert result.status == OperationStatus.SUCCESS
    assert result.message == "Created environment 'production'."
    assert client.get_environment(
        owner="acme",
        repository="app",
        environment="production",
    ) == {"name": "production"}


def test_create_environment_operation_dry_run() -> None:
    client = FakeGitHubClient()

    target = EnvironmentTarget(
        owner="acme",
        repository="app",
        name="production",
    )

    operation = create_environment_operation(
        client=client,
        target=target,
        dry_run=True,
    )

    result = operation(
        RepositoryTarget(
            owner="acme",
            name="app",
        )
    )

    assert result.status == OperationStatus.SKIPPED
    assert result.message == "Would create environment 'production'."
    assert client.environments == []
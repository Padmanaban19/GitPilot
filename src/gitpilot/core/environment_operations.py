from gitpilot.core.configuration import EnvironmentTarget
from gitpilot.core.repositories import RepositoryTarget
from gitpilot.core.results import OperationStatus, RepositoryResult
from gitpilot.github.client import GitHubClient


def create_environment_operation(
    client: GitHubClient,
    target: EnvironmentTarget,
    dry_run: bool = False,
):
    """Create an operation that creates a GitHub environment."""

    def operation(repository: RepositoryTarget) -> RepositoryResult:
        if dry_run:
            return RepositoryResult(
                owner=repository.owner,
                repository=repository.name,
                status=OperationStatus.SKIPPED,
                message=f"Would create environment '{target.name}'.",
            )

        client.create_environment(
            owner=repository.owner,
            repository=repository.name,
            environment=target.name,
        )

        return RepositoryResult(
            owner=repository.owner,
            repository=repository.name,
            status=OperationStatus.SUCCESS,
            message=f"Created environment '{target.name}'.",
        )

    return operation
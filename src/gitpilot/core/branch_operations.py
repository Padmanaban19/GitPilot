from gitpilot.core.repositories import RepositoryTarget
from gitpilot.core.results import OperationStatus, RepositoryResult
from gitpilot.github.client import GitHubClient


def create_branch_operation(
    client: GitHubClient,
    source: str,
    target: str,
    dry_run: bool = False,
):
    """Create a branch operation."""

    def operation(repository: RepositoryTarget) -> RepositoryResult:
        if dry_run:
            return RepositoryResult(
                owner=repository.owner,
                repository=repository.name,
                status=OperationStatus.SKIPPED,
                message=f"Would create '{target}' from '{source}'.",
            )

        client.create_branch(
            owner=repository.owner,
            repository=repository.name,
            source=source,
            target=target,
        )

        return RepositoryResult(
            owner=repository.owner,
            repository=repository.name,
            status=OperationStatus.SUCCESS,
            message=f"Created '{target}' from '{source}'.",
        )

    return operation
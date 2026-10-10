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


def delete_branch_operation(
    client: GitHubClient,
    branch: str,
    dry_run: bool = False,
):
    """Delete a branch while protecting the repository's default branch."""

    def operation(repository: RepositoryTarget) -> RepositoryResult:
        metadata = client.get_repository(
            owner=repository.owner,
            repository=repository.name,
        )
        default_branch = metadata.get("default_branch")

        if not default_branch:
            raise ValueError(
                f"Cannot determine the default branch for "
                f"'{repository.owner}/{repository.name}'. "
                "Refusing to delete a branch."
            )

        if branch == default_branch:
            raise ValueError(
                f"Refusing to delete default branch '{branch}' "
                f"in '{repository.owner}/{repository.name}'."
            )

        if not client.branch_exists(
            owner=repository.owner,
            repository=repository.name,
            branch=branch,
        ):
            return RepositoryResult(
                owner=repository.owner,
                repository=repository.name,
                status=OperationStatus.SKIPPED,
                message=f"Branch '{branch}' does not exist.",
            )

        if dry_run:
            return RepositoryResult(
                owner=repository.owner,
                repository=repository.name,
                status=OperationStatus.SKIPPED,
                message=f"Would delete branch '{branch}'.",
            )

        client.delete_branch(
            owner=repository.owner,
            repository=repository.name,
            branch=branch,
        )

        return RepositoryResult(
            owner=repository.owner,
            repository=repository.name,
            status=OperationStatus.SUCCESS,
            message=f"Deleted branch '{branch}'.",
        )

    return operation

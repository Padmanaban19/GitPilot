from gitpilot.core.repositories import RepositoryTarget
from gitpilot.core.results import OperationStatus, RepositoryResult


def create_branch_operation(
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

        return RepositoryResult(
            owner=repository.owner,
            repository=repository.name,
            status=OperationStatus.SUCCESS,
            message=f"Created '{target}' from '{source}'.",
        )

    return operation
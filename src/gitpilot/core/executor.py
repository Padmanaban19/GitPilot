from gitpilot.core.operations import RepositoryOperation
from gitpilot.core.repositories import RepositoryTarget
from gitpilot.core.results import OperationStatus, RepositoryResult


def execute_bulk(
    repositories: list[RepositoryTarget],
    operation: RepositoryOperation,
) -> list[RepositoryResult]:
    """Execute an operation against every repository."""

    results: list[RepositoryResult] = []

    for repository in repositories:
        try:
            result = operation(repository)
        except Exception as exc:
            result = RepositoryResult(
                owner=repository.owner,
                repository=repository.name,
                status=OperationStatus.FAILED,
                message=str(exc),
            )

        results.append(result)

    return results
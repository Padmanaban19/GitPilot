from gitpilot.core.executor import execute_bulk
from gitpilot.core.repositories import RepositoryTarget
from gitpilot.core.results import OperationStatus, RepositoryResult


def test_execute_bulk_processes_all_repositories():
    repositories = [
        RepositoryTarget("company", "repoA"),
        RepositoryTarget("company", "repoB"),
        RepositoryTarget("company", "repoC"),
    ]

    def operation(repository):
        return RepositoryResult(
            owner=repository.owner,
            repository=repository.name,
            status=OperationStatus.SUCCESS,
            message="Operation completed.",
        )

    results = execute_bulk(repositories, operation)

    assert len(results) == 3
    assert all(
        result.status == OperationStatus.SUCCESS
        for result in results
    )


def test_execute_bulk_isolates_failures():
    repositories = [
        RepositoryTarget("company", "repoA"),
        RepositoryTarget("company", "repoB"),
        RepositoryTarget("company", "repoC"),
    ]

    def operation(repository):
        if repository.name == "repoB":
            raise RuntimeError("Simulated failure")

        return RepositoryResult(
            owner=repository.owner,
            repository=repository.name,
            status=OperationStatus.SUCCESS,
            message="Operation completed.",
        )

    results = execute_bulk(repositories, operation)

    assert len(results) == 3

    assert results[0].status == OperationStatus.SUCCESS
    assert results[1].status == OperationStatus.FAILED
    assert results[1].message == "Simulated failure"
    assert results[2].status == OperationStatus.SUCCESS
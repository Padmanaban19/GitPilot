from gitpilot.core.results import (
    OperationStatus,
    RepositoryResult,
    summarize_results,
)


def test_summarize_results():
    results = [
        RepositoryResult(
            owner="company",
            repository="repoA",
            status=OperationStatus.SUCCESS,
            message="Done",
        ),
        RepositoryResult(
            owner="company",
            repository="repoB",
            status=OperationStatus.SUCCESS,
            message="Done",
        ),
        RepositoryResult(
            owner="company",
            repository="repoC",
            status=OperationStatus.SKIPPED,
            message="Skipped",
        ),
        RepositoryResult(
            owner="company",
            repository="repoD",
            status=OperationStatus.FAILED,
            message="Failed",
        ),
    ]

    summary = summarize_results(results)

    assert summary[OperationStatus.SUCCESS] == 2
    assert summary[OperationStatus.SKIPPED] == 1
    assert summary[OperationStatus.FAILED] == 1


def test_summarize_empty_results():
    summary = summarize_results([])

    assert summary[OperationStatus.SUCCESS] == 0
    assert summary[OperationStatus.SKIPPED] == 0
    assert summary[OperationStatus.FAILED] == 0
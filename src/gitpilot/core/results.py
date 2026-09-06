from dataclasses import dataclass
from enum import Enum


class OperationStatus(str, Enum):
    SUCCESS = "success"
    SKIPPED = "skipped"
    FAILED = "failed"


@dataclass(frozen=True)
class RepositoryResult:
    owner: str
    repository: str
    status: OperationStatus
    message: str


def summarize_results(
    results: list[RepositoryResult],
) -> dict[OperationStatus, int]:
    """Count repository results by status."""
    summary = {
        OperationStatus.SUCCESS: 0,
        OperationStatus.SKIPPED: 0,
        OperationStatus.FAILED: 0,
    }

    for result in results:
        summary[result.status] += 1

    return summary

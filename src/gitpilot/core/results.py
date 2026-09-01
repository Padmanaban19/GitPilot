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
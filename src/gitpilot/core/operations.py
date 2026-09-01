from collections.abc import Callable
from typing import Protocol

from gitpilot.core.repositories import RepositoryTarget
from gitpilot.core.results import RepositoryResult


class RepositoryOperation(Protocol):
    """A single operation that can be executed against a repository."""

    def __call__(
        self,
        repository: RepositoryTarget,
    ) -> RepositoryResult:
        ...


OperationFactory = Callable[[], RepositoryOperation]
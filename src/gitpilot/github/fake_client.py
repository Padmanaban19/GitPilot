from dataclasses import dataclass


@dataclass(frozen=True)
class BranchCreation:
    owner: str
    repository: str
    source: str
    target: str


class FakeGitHubClient:
    """Fake GitHub client used for testing."""

    def __init__(self) -> None:
        self.created_branches: list[BranchCreation] = []

    def create_branch(
        self,
        owner: str,
        repository: str,
        source: str,
        target: str,
    ) -> None:
        self.created_branches.append(
            BranchCreation(
                owner=owner,
                repository=repository,
                source=source,
                target=target,
            )
        )
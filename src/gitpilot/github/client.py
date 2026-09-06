from typing import Protocol


class GitHubClient(Protocol):
    """Interface for GitHub operations used by GitPilot."""

    def create_branch(
        self,
        owner: str,
        repository: str,
        source: str,
        target: str,
    ) -> None:
        """Create a branch in a repository."""
        ...

    def get_repository_variable(
        self,
        owner: str,
        repository: str,
        name: str,
    ) -> dict | None:
        """Get a repository variable by name."""
        ...

    def set_repository_variable(
        self,
        owner: str,
        repository: str,
        name: str,
        value: str,
    ) -> None:
        """Create or update a repository variable."""
        ...
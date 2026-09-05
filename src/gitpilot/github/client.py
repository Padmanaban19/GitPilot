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
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

    def get_repository_secret_public_key(
        self,
        owner: str,
        repository: str,
    ) -> dict:
        """Get the public key used to encrypt repository secrets."""
        ...

    def get_repository_secret(
        self,
        owner: str,
        repository: str,
        name: str,
    ) -> dict | None:
        """Get a repository secret by name."""
        ...

    def set_repository_secret(
        self,
        owner: str,
        repository: str,
        name: str,
        encrypted_value: str,
        key_id: str,
    ) -> None:
        """Create or update a repository secret."""
        ...

    def get_environment(
        self,
        owner: str,
        repository: str,
        environment: str,
    ) -> dict | None:
        ...

    def create_environment(
        self,
        owner: str,
        repository: str,
        environment: str,
    ) -> None:
        ...

    def delete_environment(
        self,
        owner: str,
        repository: str,
        environment: str,
    ) -> None:
        ...

    def get_environment_variable(
        self,
        owner: str,
        repository: str,
        environment: str,
        name: str,
    ) -> dict | None:
        ...

    def set_environment_variable(
        self,
        owner: str,
        repository: str,
        environment: str,
        name: str,
        value: str,
    ) -> None:
        ...

    def get_environment_secret_public_key(
        self,
        owner: str,
        repository: str,
        environment: str,
    ) -> dict:
        ...

    def get_environment_secret(
        self,
        owner: str,
        repository: str,
        environment: str,
        name: str,
    ) -> dict | None:
        ...

    def set_environment_secret(
        self,
        owner: str,
        repository: str,
        environment: str,
        name: str,
        encrypted_value: str,
        key_id: str,
    ) -> None:
        ...
from gitpilot.core.configuration import (
    ConfigurationKind,
    ConfigurationTarget,
)
from gitpilot.core.repositories import RepositoryTarget
from gitpilot.core.results import OperationStatus, RepositoryResult
from gitpilot.github.client import GitHubClient
from gitpilot.github.encryption import encrypt_secret


def set_configuration_operation(
    client: GitHubClient,
    target: ConfigurationTarget,
    value: str,
    dry_run: bool = False,
):
    """Create an operation that sets a configuration value."""
    
    if target.kind != ConfigurationKind.VARIABLE:
        raise NotImplementedError(
            f"Configuration kind '{target.kind.value}' is not supported yet."
        )

    def operation(repository: RepositoryTarget) -> RepositoryResult:
        if dry_run:
            return RepositoryResult(
                owner=repository.owner,
                repository=repository.name,
                status=OperationStatus.SKIPPED,
                message=f"Would set repository variable '{target.name}'.",
            )

        client.set_repository_variable(
            owner=repository.owner,
            repository=repository.name,
            name=target.name,
            value=value,
        )

        return RepositoryResult(
            owner=repository.owner,
            repository=repository.name,
            status=OperationStatus.SUCCESS,
            message=f"Set repository variable '{target.name}'.",
        )    

    return operation

def set_repository_secret_operation(
    client: GitHubClient,
    target: ConfigurationTarget,
    value: str,
    dry_run: bool = False,
):
    """Create an operation that sets a repository secret."""

    if target.kind != ConfigurationKind.SECRET:
        raise ValueError("Target must be a repository secret.")

    if target.environment is not None:
        raise ValueError("Environment secrets are not supported yet.")

    def operation(repository: RepositoryTarget) -> RepositoryResult:
        if dry_run:
            return RepositoryResult(
                owner=repository.owner,
                repository=repository.name,
                status=OperationStatus.SKIPPED,
                message=f"Would set repository secret '{target.name}'.",
            )

        public_key = client.get_repository_secret_public_key(
            owner=repository.owner,
            repository=repository.name,
        )

        encrypted_value = encrypt_secret(
            public_key=public_key["key"],
            secret_value=value,
        )

        client.set_repository_secret(
            owner=repository.owner,
            repository=repository.name,
            name=target.name,
            encrypted_value=encrypted_value,
            key_id=public_key["key_id"],
        )

        return RepositoryResult(
            owner=repository.owner,
            repository=repository.name,
            status=OperationStatus.SUCCESS,
            message=f"Set repository secret '{target.name}'.",
        )

    return operation

def set_environment_secret_operation(
    client: GitHubClient,
    target: ConfigurationTarget,
    value: str,
    dry_run: bool = False,
):
    """Create an operation that sets an environment secret."""

    if target.kind != ConfigurationKind.SECRET:
        raise ValueError("Target must be an environment secret.")

    if target.environment is None:
        raise ValueError("Environment is required for environment secrets.")

    def operation(repository: RepositoryTarget) -> RepositoryResult:
        if dry_run:
            return RepositoryResult(
                owner=repository.owner,
                repository=repository.name,
                status=OperationStatus.SKIPPED,
                message=(
                    f"Would set environment secret "
                    f"'{target.name}' in '{target.environment}'."
                ),
            )

        public_key = client.get_environment_secret_public_key(
            owner=repository.owner,
            repository=repository.name,
            environment=target.environment,
        )

        encrypted_value = encrypt_secret(
            public_key=public_key["key"],
            secret_value=value,
        )

        client.set_environment_secret(
            owner=repository.owner,
            repository=repository.name,
            environment=target.environment,
            name=target.name,
            encrypted_value=encrypted_value,
            key_id=public_key["key_id"],
        )

        return RepositoryResult(
            owner=repository.owner,
            repository=repository.name,
            status=OperationStatus.SUCCESS,
            message=(
                f"Set environment secret "
                f"'{target.name}' in '{target.environment}'."
            ),
        )

    return operation

def delete_environment_variable_operation(
    client: GitHubClient,
    target: ConfigurationTarget,
    dry_run: bool = False,
):
    """Create an operation that deletes an environment variable."""

    if target.kind != ConfigurationKind.VARIABLE:
        raise ValueError("Target must be an environment variable.")

    if target.environment is None:
        raise ValueError("Environment is required for environment variables.")

    def operation(repository: RepositoryTarget) -> RepositoryResult:
        if dry_run:
            return RepositoryResult(
                owner=repository.owner,
                repository=repository.name,
                status=OperationStatus.SKIPPED,
                message=(
                    f"Would delete environment variable "
                    f"'{target.name}' in '{target.environment}'."
                ),
            )

        client.delete_environment_variable(
            owner=repository.owner,
            repository=repository.name,
            environment=target.environment,
            name=target.name,
        )

        return RepositoryResult(
            owner=repository.owner,
            repository=repository.name,
            status=OperationStatus.SUCCESS,
            message=(
                f"Deleted environment variable "
                f"'{target.name}' in '{target.environment}'."
            ),
        )

    return operation


def delete_environment_secret_operation(
    client: GitHubClient,
    target: ConfigurationTarget,
    dry_run: bool = False,
):
    """Create an operation that deletes an environment secret."""

    if target.kind != ConfigurationKind.SECRET:
        raise ValueError("Target must be an environment secret.")

    if target.environment is None:
        raise ValueError("Environment is required for environment secrets.")

    def operation(repository: RepositoryTarget) -> RepositoryResult:
        if dry_run:
            return RepositoryResult(
                owner=repository.owner,
                repository=repository.name,
                status=OperationStatus.SKIPPED,
                message=(
                    f"Would delete environment secret "
                    f"'{target.name}' in '{target.environment}'."
                ),
            )

        client.delete_environment_secret(
            owner=repository.owner,
            repository=repository.name,
            environment=target.environment,
            name=target.name,
        )

        return RepositoryResult(
            owner=repository.owner,
            repository=repository.name,
            status=OperationStatus.SUCCESS,
            message=(
                f"Deleted environment secret "
                f"'{target.name}' in '{target.environment}'."
            ),
        )

    return operation
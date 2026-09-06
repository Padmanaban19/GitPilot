from gitpilot.core.configuration import (
    ConfigurationKind,
    ConfigurationTarget,
)
from gitpilot.core.repositories import RepositoryTarget
from gitpilot.core.results import OperationStatus, RepositoryResult
from gitpilot.github.client import GitHubClient


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
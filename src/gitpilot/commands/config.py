import typer

from gitpilot.core.configuration import (
    ConfigurationKind,
    ConfigurationTarget,
)
from gitpilot.core.configuration_operations import (
    delete_environment_secret_operation,
    delete_environment_variable_operation,
    delete_repository_secret_operation,
    delete_repository_variable_operation,
    set_configuration_operation,
    set_environment_secret_operation,
    set_environment_variable_operation,
    set_repository_secret_operation,
)
from gitpilot.core.executor import execute_bulk
from gitpilot.core.repositories import (
    parse_repositories,
    parse_repositories_file,
)
from gitpilot.core.results import OperationStatus, summarize_results
from gitpilot.github.api_client import GitHubApiClient

app = typer.Typer(
    help="Manage repository and environment configuration."
)


def _configuration_kind(secret: bool) -> ConfigurationKind:
    """Return the configuration kind for a CLI request."""
    return (
        ConfigurationKind.SECRET
        if secret
        else ConfigurationKind.VARIABLE
    )


def _create_set_operation(
    client: GitHubApiClient,
    target: ConfigurationTarget,
    value: str,
    environment: str | None,
    secret: bool,
    dry_run: bool,
):
    """Create the appropriate set operation."""
    if environment is not None:
        if secret:
            return set_environment_secret_operation(
                client=client,
                target=target,
                value=value,
                dry_run=dry_run,
            )

        return set_environment_variable_operation(
            client=client,
            target=target,
            value=value,
            dry_run=dry_run,
        )

    if secret:
        return set_repository_secret_operation(
            client=client,
            target=target,
            value=value,
            dry_run=dry_run,
        )

    return set_configuration_operation(
        client=client,
        target=target,
        value=value,
        dry_run=dry_run,
    )


def _create_delete_operation(
    client: GitHubApiClient,
    target: ConfigurationTarget,
    environment: str | None,
    secret: bool,
    dry_run: bool,
):
    """Create the appropriate delete operation."""
    if environment is not None:
        if secret:
            return delete_environment_secret_operation(
                client=client,
                target=target,
                dry_run=dry_run,
            )

        return delete_environment_variable_operation(
            client=client,
            target=target,
            dry_run=dry_run,
        )

    if secret:
        return delete_repository_secret_operation(
            client=client,
            target=target,
            dry_run=dry_run,
        )

    return delete_repository_variable_operation(
        client=client,
        target=target,
        dry_run=dry_run,
    )


def _get_configuration(
    client: GitHubApiClient,
    repository,
    name: str,
    environment: str | None,
    secret: bool,
):
    """Get the appropriate repository or environment configuration."""
    if environment is not None:
        if secret:
            return client.get_environment_secret(
                owner=repository.owner,
                repository=repository.name,
                environment=environment,
                name=name,
            )

        return client.get_environment_variable(
            owner=repository.owner,
            repository=repository.name,
            environment=environment,
            name=name,
        )

    if secret:
        return client.get_repository_secret(
            owner=repository.owner,
            repository=repository.name,
            name=name,
        )

    return client.get_repository_variable(
        owner=repository.owner,
        repository=repository.name,
        name=name,
    )


def _print_summary(results) -> None:
    """Print operation results and summary."""
    for result in results:
        print(f"{result.repository}: {result.message}")

    summary = summarize_results(results)

    print()
    print("Summary")
    print(f"Total:   {len(results)}")
    print(f"Success: {summary[OperationStatus.SUCCESS]}")
    print(f"Skipped: {summary[OperationStatus.SKIPPED]}")
    print(f"Failed:  {summary[OperationStatus.FAILED]}")

    if summary[OperationStatus.FAILED] > 0:
        raise typer.Exit(code=1)


@app.command()
def set(
    owner: str = typer.Option(..., help="GitHub organization or user."),
    repos: str | None = typer.Option(
        None,
        help="Comma-separated repository names.",
    ),
    repo_file: str | None = typer.Option(
        None,
        "--repo-file",
        help="Path to a file containing repository names.",
    ),
    name: str = typer.Option(..., help="Configuration name."),
    value: str | None = typer.Option(
        None,
        "--value",
        help="Configuration value.",
    ),
    environment: str | None = typer.Option(
        None,
        help="GitHub environment name.",
    ),
    secret: bool = typer.Option(
        False,
        "--secret",
        help="Treat the configuration as a secret.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would happen without making changes.",
    ),
) -> None:
    """Set a repository or environment configuration value."""
    if secret:
        value = typer.prompt(
            "Secret value",
            hide_input=True,
        )
    elif value is None:
        raise typer.BadParameter(
            "--value is required unless --secret is used."
        )

    kind = _configuration_kind(secret)
    if repos and repo_file:
        raise typer.BadParameter(
            "Use either --repos or --repo-file, not both."
        )

    if not repos and not repo_file:
        raise typer.BadParameter(
            "Either --repos or --repo-file is required."
        )

    if repo_file:
        repositories = parse_repositories_file(owner, repo_file)
    else:
        repositories = parse_repositories(owner, repos)


    target = ConfigurationTarget(
        owner=owner,
        repository=repositories[0].name,
        kind=kind,
        name=name,
        environment=environment,
    )

    with GitHubApiClient() as client:
        operation = _create_set_operation(
            client=client,
            target=target,
            value=value,
            environment=environment,
            secret=secret,
            dry_run=dry_run,
        )

        results = execute_bulk(
            repositories,
            operation,
        )

    _print_summary(results)


@app.command()
def get(
    owner: str = typer.Option(..., help="GitHub organization or user."),
    repos: str | None = typer.Option(
        None,
        help="Comma-separated repository names.",
    ),
    repo_file: str | None = typer.Option(
        None,
        "--repo-file",
        help="Path to a file containing repository names.",
    ),    name: str = typer.Option(..., help="Configuration name."),
    environment: str | None = typer.Option(
        None,
        help="GitHub environment name.",
    ),
    secret: bool = typer.Option(
        False,
        "--secret",
        help="Treat the configuration as a secret.",
    ),
) -> None:
    """Get a repository or environment configuration value."""
    if repos and repo_file:
        raise typer.BadParameter(
            "Use either --repos or --repo-file, not both."
        )

    if not repos and not repo_file:
        raise typer.BadParameter(
            "Either --repos or --repo-file is required."
        )

    if repo_file:
        repositories = parse_repositories_file(owner, repo_file)
    else:
        repositories = parse_repositories(owner, repos)

    with GitHubApiClient() as client:
        for repository in repositories:
            result = _get_configuration(
                client=client,
                repository=repository,
                name=name,
                environment=environment,
                secret=secret,
            )

            if result is None:
                print(f"{repository.name}: Not found.")
            elif secret:
                print(f"{repository.name}: Secret exists.")
            else:
                print(f"{repository.name}: {result['value']}")


@app.command()
def delete(
    owner: str = typer.Option(..., help="GitHub organization or user."),
    repos: str | None = typer.Option(
        None,
        help="Comma-separated repository names.",
    ),
    repo_file: str | None = typer.Option(
        None,
        "--repo-file",
        help="Path to a file containing repository names.",
    ),
    name: str = typer.Option(..., help="Configuration name."),
    environment: str | None = typer.Option(
        None,
        help="GitHub environment name.",
    ),
    secret: bool = typer.Option(
        False,
        "--secret",
        help="Treat the configuration as a secret.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would happen without making changes.",
    ),
) -> None:
    """Delete a repository or environment configuration value."""
    if repos and repo_file:
        raise typer.BadParameter(
            "Use either --repos or --repo-file, not both."
        )

    if not repos and not repo_file:
        raise typer.BadParameter(
            "Either --repos or --repo-file is required."
        )

    if repo_file:
        repositories = parse_repositories_file(owner, repo_file)
    else:
        repositories = parse_repositories(owner, repos)

    kind = _configuration_kind(secret)

    target = ConfigurationTarget(
        owner=owner,
        repository=repositories[0].name,
        kind=kind,
        name=name,
        environment=environment,
    )

    with GitHubApiClient() as client:
        operation = _create_delete_operation(
            client=client,
            target=target,
            environment=environment,
            secret=secret,
            dry_run=dry_run,
        )

        results = execute_bulk(
            repositories,
            operation,
        )

    _print_summary(results)
    
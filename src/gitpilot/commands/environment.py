import typer

from gitpilot.core.configuration import EnvironmentTarget
from gitpilot.core.environment_operations import (
    create_environment_operation,
    delete_environment_operation,
)
from gitpilot.core.executor import execute_bulk
from gitpilot.core.repositories import (
    parse_repositories,
    parse_repositories_file,
)
from gitpilot.core.results import OperationStatus, summarize_results
from gitpilot.github.api_client import GitHubApiClient

app = typer.Typer(help="Manage GitHub environments.")


@app.command()
def create(
    owner: str = typer.Option(
        ...,
        help="GitHub organization or user.",
    ),
    repos: str | None = typer.Option(
        None,
        help="Comma-separated repository names.",
    ),
    repos_file: str | None = typer.Option(
        None,
        "--repos-file",
        help="Path to a file containing repository names.",
    ),
    name: str = typer.Option(
        ...,
        help="Environment name.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would happen without making changes.",
    ),
) -> None:
    """Create an environment in multiple repositories."""

    if bool(repos) == bool(repos_file):
        raise typer.BadParameter(
            "Provide either --repos or --repos-file, but not both."
        )

    try:
        repositories = (
            parse_repositories(owner=owner, repos=repos)
            if repos is not None
            else parse_repositories_file(
                owner=owner,
                repos_file=repos_file,
            )
        )
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc

    target = EnvironmentTarget(
        owner=owner,
        repository="",
        name=name,
    )

    with GitHubApiClient() as client:
        operation = create_environment_operation(
            client=client,
            target=target,
            dry_run=dry_run,
        )
        results = execute_bulk(repositories, operation)

    for result in results:
        typer.echo(f"{result.repository}: {result.message}")

    summary = summarize_results(results)
    typer.echo("\nSummary")
    typer.echo(f"Total:   {len(results)}")
    typer.echo(f"Success: {summary[OperationStatus.SUCCESS]}")
    typer.echo(f"Skipped: {summary[OperationStatus.SKIPPED]}")
    typer.echo(f"Failed:  {summary[OperationStatus.FAILED]}")

    if summary[OperationStatus.FAILED]:
        raise typer.Exit(code=1)


@app.command()
def delete(
    owner: str = typer.Option(
        ...,
        help="GitHub organization or user.",
    ),
    repos: str | None = typer.Option(
        None,
        help="Comma-separated repository names.",
    ),
    repos_file: str | None = typer.Option(
        None,
        "--repos-file",
        help="Path to a file containing repository names.",
    ),
    name: str = typer.Option(
        ...,
        help="Environment name.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would happen without making changes.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        help="Skip confirmation.",
    ),
) -> None:
    """Delete an environment from multiple repositories."""

    if bool(repos) == bool(repos_file):
        raise typer.BadParameter(
            "Provide either --repos or --repos-file, but not both."
        )

    try:
        repositories = (
            parse_repositories(owner=owner, repos=repos)
            if repos is not None
            else parse_repositories_file(
                owner=owner,
                repos_file=repos_file,
            )
        )
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc

    if not dry_run and not yes:
        confirmed = typer.confirm(
            f"Delete environment '{name}' from "
            f"{len(repositories)} repositories?"
        )
        if not confirmed:
            typer.echo("Deletion cancelled.")
            raise typer.Exit()

    target = EnvironmentTarget(
        owner=owner,
        repository="",
        name=name,
    )

    with GitHubApiClient() as client:
        operation = delete_environment_operation(
            client=client,
            target=target,
            dry_run=dry_run,
        )
        results = execute_bulk(repositories, operation)

    for result in results:
        typer.echo(f"{result.repository}: {result.message}")

    summary = summarize_results(results)

    typer.echo("\nSummary")
    typer.echo(f"Total:   {len(results)}")
    typer.echo(f"Success: {summary[OperationStatus.SUCCESS]}")
    typer.echo(f"Skipped: {summary[OperationStatus.SKIPPED]}")
    typer.echo(f"Failed:  {summary[OperationStatus.FAILED]}")

    if summary[OperationStatus.FAILED]:
        raise typer.Exit(code=1)
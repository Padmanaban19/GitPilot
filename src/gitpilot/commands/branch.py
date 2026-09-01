import typer

from gitpilot.core.branch_operations import create_branch_operation
from gitpilot.core.executor import execute_bulk
from gitpilot.core.repositories import parse_repositories, parse_repositories_file
from gitpilot.core.results import OperationStatus

app = typer.Typer(help="Manage repository branches.")


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
        help="Text file containing one repository name per line.",
    ),
    source: str = typer.Option(
        ...,
        help="Source branch.",
    ),
    target: str = typer.Option(
        ...,
        help="Target branch.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would happen without making changes.",
    ),
) -> None:
    """Create a branch across multiple repositories."""

    if bool(repos) == bool(repos_file):
        raise typer.BadParameter(
            "Provide exactly one of --repos or --repos-file."
        )

    if repos:
        repositories = parse_repositories(owner, repos)
    else:
        repositories = parse_repositories_file(owner, repos_file)

    operation = create_branch_operation(
    source=source,
    target=target,
    dry_run=dry_run,
)
    results = execute_bulk(repositories, operation)

    typer.echo("")
    typer.echo("GitPilot - Branch Create")
    typer.echo("------------------------")
    typer.echo(f"Owner:  {owner}")
    typer.echo(f"Source: {source}")
    typer.echo(f"Target: {target}")
    typer.echo("")

    for result in results:
        symbol = {
            OperationStatus.SUCCESS: "✓",
            OperationStatus.SKIPPED: "→",
            OperationStatus.FAILED: "✗",
        }[result.status]

        typer.echo(
            f"{symbol} {result.repository}: {result.message}"
        )

    if dry_run:
        typer.echo("")
        typer.echo("DRY RUN - No changes were made.")
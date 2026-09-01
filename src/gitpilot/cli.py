import typer

from gitpilot.commands.branch import app as branch_app

app = typer.Typer(
    name="gitpilot",
    help="CLI toolkit for automating GitHub organization management at scale.",
)

secret_app = typer.Typer(
    help="Manage repository secrets."
)

app.add_typer(branch_app, name="branch")
app.add_typer(secret_app, name="secret")


@app.command()
def version() -> None:
    """Show the GitPilot version."""
    print("GitPilot v0.1.0")


if __name__ == "__main__":
    app()
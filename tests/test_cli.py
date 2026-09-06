from typer.testing import CliRunner

from gitpilot.cli import app
from gitpilot.github.fake_client import BranchCreation, FakeGitHubClient

runner = CliRunner()


def test_branch_create_dry_run_output(monkeypatch):
    client = FakeGitHubClient()

    class FakeClientContext:
        def __enter__(self):
            return client

        def __exit__(self, exc_type, exc_value, traceback):
            pass


    monkeypatch.setattr(
        "gitpilot.commands.branch.GitHubApiClient",
        FakeClientContext,
    )

    result = runner.invoke(
        app,
        [
            "branch",
            "create",
            "--owner",
            "company",
            "--repos",
            "repoA,repoB",
            "--source",
            "main",
            "--target",
            "dev/test",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert "repoA: Would create 'dev/test' from 'main'." in result.output
    assert "repoB: Would create 'dev/test' from 'main'." in result.output
    assert "DRY RUN - No changes were made." in result.output
    assert "Summary" in result.output
    assert "Total:   2" in result.output
    assert "Success: 0" in result.output
    assert "Skipped: 2" in result.output
    assert "Failed:  0" in result.output


def test_branch_create_failure_summary(monkeypatch):
    client = FakeGitHubClient()

    def failing_create_branch(
        owner: str,
        repository: str,
        source: str,
        target: str,
    ) -> None:
        if repository == "repoB":
            raise RuntimeError("Simulated failure")

        client.created_branches.append(
            BranchCreation(
                owner=owner,
                repository=repository,
                source=source,
                target=target,
            )
        )

    client.create_branch = failing_create_branch

    class FakeClientContext:
        def __enter__(self):
            return client

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    monkeypatch.setattr(
        "gitpilot.commands.branch.GitHubApiClient",
        FakeClientContext,
    )

    result = runner.invoke(
        app,
        [
            "branch",
            "create",
            "--owner",
            "company",
            "--repos",
            "repoA,repoB",
            "--source",
            "main",
            "--target",
            "dev/test",
        ],
    )

    assert result.exit_code == 1
    assert "repoA: Created 'dev/test' from 'main'." in result.output
    assert "repoB: Simulated failure" in result.output
    assert "Total:   2" in result.output
    assert "Success: 1" in result.output
    assert "Skipped: 0" in result.output
    assert "Failed:  1" in result.output
    
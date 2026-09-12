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

def test_config_set_variable_dry_run(monkeypatch):
    client = FakeGitHubClient()

    class FakeClientContext:
        def __enter__(self):
            return client

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    monkeypatch.setattr(
        "gitpilot.commands.config.GitHubApiClient",
        FakeClientContext,
    )

    result = runner.invoke(
        app,
        [
            "config",
            "set",
            "--owner",
            "company",
            "--repos",
            "repoA,repoB",
            "--name",
            "TEST_VAR",
            "--value",
            "hello",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert "repoA: Would set repository variable 'TEST_VAR'." in result.output
    assert "repoB: Would set repository variable 'TEST_VAR'." in result.output
    assert "Total:   2" in result.output
    assert "Success: 0" in result.output
    assert "Skipped: 2" in result.output
    assert "Failed:  0" in result.output

def test_config_set_failure_exit_code(monkeypatch):
    client = FakeGitHubClient()

    def failing_set_variable(owner, repository, name, value):
        if repository == "repoB":
            raise RuntimeError("Simulated failure")

    client.set_repository_variable = failing_set_variable

    class FakeClientContext:
        def __enter__(self):
            return client

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    monkeypatch.setattr(
        "gitpilot.commands.config.GitHubApiClient",
        FakeClientContext,
    )

    result = runner.invoke(
        app,
        [
            "config",
            "set",
            "--owner",
            "company",
            "--repos",
            "repoA,repoB",
            "--name",
            "TEST_VAR",
            "--value",
            "hello",
        ],
    )

    assert result.exit_code == 1
    assert "repoA: Set repository variable 'TEST_VAR'." in result.output
    assert "repoB: Simulated failure" in result.output
    assert "Total:   2" in result.output
    assert "Success: 1" in result.output
    assert "Skipped: 0" in result.output
    assert "Failed:  1" in result.output

def test_config_set_secret_prompt(monkeypatch):
    client = FakeGitHubClient()

    class FakeClientContext:
        def __enter__(self):
            return client

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    monkeypatch.setattr(
        "gitpilot.commands.config.GitHubApiClient",
        FakeClientContext,
    )
    monkeypatch.setattr(
        "gitpilot.commands.config.typer.prompt",
        lambda *args, **kwargs: "super-secret-value",
    )

    result = runner.invoke(
        app,
        [
            "config",
            "set",
            "--owner",
            "company",
            "--repos",
            "repoA",
            "--name",
            "TEST_SECRET",
            "--secret",
        ],
    )

    assert result.exit_code == 0
    assert "Set repository secret 'TEST_SECRET'." in result.output
    assert "super-secret-value" not in result.output

def test_config_set_environment_variable_dry_run(monkeypatch):
    client = FakeGitHubClient()

    class FakeClientContext:
        def __enter__(self):
            return client

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    monkeypatch.setattr(
        "gitpilot.commands.config.GitHubApiClient",
        FakeClientContext,
    )

    result = runner.invoke(
        app,
        [
            "config",
            "set",
            "--owner",
            "company",
            "--repos",
            "repoA,repoB",
            "--name",
            "TEST_VAR",
            "--value",
            "hello",
            "--environment",
            "prod",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert (
        "repoA: Would set environment variable "
        "'TEST_VAR' in 'prod'."
    ) in result.output
    assert (
        "repoB: Would set environment variable "
        "'TEST_VAR' in 'prod'."
    ) in result.output
    assert "Total:   2" in result.output
    assert "Success: 0" in result.output
    assert "Skipped: 2" in result.output
    assert "Failed:  0" in result.output


def test_config_set_environment_secret_dry_run(monkeypatch):
    client = FakeGitHubClient()

    class FakeClientContext:
        def __enter__(self):
            return client

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    monkeypatch.setattr(
        "gitpilot.commands.config.GitHubApiClient",
        FakeClientContext,
    )
    monkeypatch.setattr(
        "gitpilot.commands.config.typer.prompt",
        lambda *args, **kwargs: "super-secret-value",
    )

    result = runner.invoke(
        app,
        [
            "config",
            "set",
            "--owner",
            "company",
            "--repos",
            "repoA,repoB",
            "--name",
            "TEST_SECRET",
            "--secret",
            "--environment",
            "prod",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert (
        "repoA: Would set environment secret "
        "'TEST_SECRET' in 'prod'."
    ) in result.output
    assert (
        "repoB: Would set environment secret "
        "'TEST_SECRET' in 'prod'."
    ) in result.output
    assert "super-secret-value" not in result.output
    assert "Total:   2" in result.output
    assert "Success: 0" in result.output
    assert "Skipped: 2" in result.output
    assert "Failed:  0" in result.output

def test_config_get_repository_variable(monkeypatch):
    client = FakeGitHubClient()
    client.set_repository_variable(
        owner="company",
        repository="repoA",
        name="TEST_VAR",
        value="hello",
    )

    class FakeClientContext:
        def __enter__(self):
            return client

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    monkeypatch.setattr(
        "gitpilot.commands.config.GitHubApiClient",
        FakeClientContext,
    )

    result = runner.invoke(
        app,
        [
            "config",
            "get",
            "--owner",
            "company",
            "--repos",
            "repoA",
            "--name",
            "TEST_VAR",
        ],
    )

    assert result.exit_code == 0
    assert "repoA: hello" in result.output


def test_config_get_repository_secret(monkeypatch):
    client = FakeGitHubClient()
    client.set_repository_secret(
        owner="company",
        repository="repoA",
        name="TEST_SECRET",
        encrypted_value="encrypted",
        key_id="test-key",
    )

    class FakeClientContext:
        def __enter__(self):
            return client

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    monkeypatch.setattr(
        "gitpilot.commands.config.GitHubApiClient",
        FakeClientContext,
    )

    result = runner.invoke(
        app,
        [
            "config",
            "get",
            "--owner",
            "company",
            "--repos",
            "repoA",
            "--name",
            "TEST_SECRET",
            "--secret",
        ],
    )

    assert result.exit_code == 0
    assert "repoA: Secret exists." in result.output
    assert "encrypted" not in result.output


def test_config_get_environment_variable(monkeypatch):
    client = FakeGitHubClient()
    client.set_environment_variable(
        owner="company",
        repository="repoA",
        environment="prod",
        name="TEST_VAR",
        value="hello",
    )

    class FakeClientContext:
        def __enter__(self):
            return client

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    monkeypatch.setattr(
        "gitpilot.commands.config.GitHubApiClient",
        FakeClientContext,
    )

    result = runner.invoke(
        app,
        [
            "config",
            "get",
            "--owner",
            "company",
            "--repos",
            "repoA",
            "--name",
            "TEST_VAR",
            "--environment",
            "prod",
        ],
    )

    assert result.exit_code == 0
    assert "repoA: hello" in result.output


def test_config_get_environment_secret(monkeypatch):
    client = FakeGitHubClient()
    client.set_environment_secret(
        owner="company",
        repository="repoA",
        environment="prod",
        name="TEST_SECRET",
        encrypted_value="encrypted",
        key_id="test-key",
    )

    class FakeClientContext:
        def __enter__(self):
            return client

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    monkeypatch.setattr(
        "gitpilot.commands.config.GitHubApiClient",
        FakeClientContext,
    )

    result = runner.invoke(
        app,
        [
            "config",
            "get",
            "--owner",
            "company",
            "--repos",
            "repoA",
            "--name",
            "TEST_SECRET",
            "--environment",
            "prod",
            "--secret",
        ],
    )

    assert result.exit_code == 0
    assert "repoA: Secret exists." in result.output
    assert "encrypted" not in result.output

def test_config_get_not_found(monkeypatch):
    client = FakeGitHubClient()

    class FakeClientContext:
        def __enter__(self):
            return client

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    monkeypatch.setattr(
        "gitpilot.commands.config.GitHubApiClient",
        FakeClientContext,
    )

    result = runner.invoke(
        app,
        [
            "config",
            "get",
            "--owner",
            "company",
            "--repos",
            "repoA,repoB",
            "--name",
            "MISSING_VAR",
        ],
    )

    assert result.exit_code == 0
    assert "repoA: Not found." in result.output
    assert "repoB: Not found." in result.output

def test_config_delete_repository_variable_dry_run(monkeypatch):
    client = FakeGitHubClient()

    class FakeClientContext:
        def __enter__(self):
            return client

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    monkeypatch.setattr(
        "gitpilot.commands.config.GitHubApiClient",
        FakeClientContext,
    )

    result = runner.invoke(
        app,
        [
            "config",
            "delete",
            "--owner",
            "company",
            "--repos",
            "repoA,repoB",
            "--name",
            "TEST_VAR",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert "repoA: Would delete repository variable 'TEST_VAR'." in result.output
    assert "repoB: Would delete repository variable 'TEST_VAR'." in result.output
    assert "Total:   2" in result.output
    assert "Skipped: 2" in result.output


def test_config_delete_repository_secret_dry_run(monkeypatch):
    client = FakeGitHubClient()

    class FakeClientContext:
        def __enter__(self):
            return client

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    monkeypatch.setattr(
        "gitpilot.commands.config.GitHubApiClient",
        FakeClientContext,
    )

    result = runner.invoke(
        app,
        [
            "config",
            "delete",
            "--owner",
            "company",
            "--repos",
            "repoA,repoB",
            "--name",
            "TEST_SECRET",
            "--secret",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert "repoA: Would delete repository secret 'TEST_SECRET'." in result.output
    assert "repoB: Would delete repository secret 'TEST_SECRET'." in result.output
    assert "Total:   2" in result.output
    assert "Skipped: 2" in result.output


def test_config_delete_environment_variable_dry_run(monkeypatch):
    client = FakeGitHubClient()

    class FakeClientContext:
        def __enter__(self):
            return client

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    monkeypatch.setattr(
        "gitpilot.commands.config.GitHubApiClient",
        FakeClientContext,
    )

    result = runner.invoke(
        app,
        [
            "config",
            "delete",
            "--owner",
            "company",
            "--repos",
            "repoA,repoB",
            "--name",
            "TEST_VAR",
            "--environment",
            "prod",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert (
        "repoA: Would delete environment variable "
        "'TEST_VAR' in 'prod'."
    ) in result.output
    assert (
        "repoB: Would delete environment variable "
        "'TEST_VAR' in 'prod'."
    ) in result.output
    assert "Total:   2" in result.output
    assert "Skipped: 2" in result.output


def test_config_delete_environment_secret_dry_run(monkeypatch):
    client = FakeGitHubClient()

    class FakeClientContext:
        def __enter__(self):
            return client

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    monkeypatch.setattr(
        "gitpilot.commands.config.GitHubApiClient",
        FakeClientContext,
    )

    result = runner.invoke(
        app,
        [
            "config",
            "delete",
            "--owner",
            "company",
            "--repos",
            "repoA,repoB",
            "--name",
            "TEST_SECRET",
            "--environment",
            "prod",
            "--secret",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert (
        "repoA: Would delete environment secret "
        "'TEST_SECRET' in 'prod'."
    ) in result.output
    assert (
        "repoB: Would delete environment secret "
        "'TEST_SECRET' in 'prod'."
    ) in result.output
    assert "Total:   2" in result.output
    assert "Skipped: 2" in result.output

def test_config_set_repo_file_dry_run(monkeypatch, tmp_path):
    client = FakeGitHubClient()
    repos_file = tmp_path / "repos.txt"
    repos_file.write_text(
        "# Production repositories\nrepoA\nrepoB\n\n",
        encoding="utf-8",
    )

    class FakeClientContext:
        def __enter__(self):
            return client

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    monkeypatch.setattr(
        "gitpilot.commands.config.GitHubApiClient",
        FakeClientContext,
    )

    result = runner.invoke(
        app,
        [
            "config",
            "set",
            "--owner",
            "company",
            "--repo-file",
            str(repos_file),
            "--name",
            "TEST_VAR",
            "--value",
            "hello",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert "repoA: Would set repository variable 'TEST_VAR'." in result.output
    assert "repoB: Would set repository variable 'TEST_VAR'." in result.output
    assert "Total:   2" in result.output
    assert "Skipped: 2" in result.output


def test_config_get_repo_file(monkeypatch, tmp_path):
    client = FakeGitHubClient()
    client.set_repository_variable(
        owner="company",
        repository="repoA",
        name="TEST_VAR",
        value="valueA",
    )
    client.set_repository_variable(
        owner="company",
        repository="repoB",
        name="TEST_VAR",
        value="valueB",
    )

    repos_file = tmp_path / "repos.txt"
    repos_file.write_text(
        "repoA\n# ignored\nrepoB\n",
        encoding="utf-8",
    )

    class FakeClientContext:
        def __enter__(self):
            return client

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    monkeypatch.setattr(
        "gitpilot.commands.config.GitHubApiClient",
        FakeClientContext,
    )

    result = runner.invoke(
        app,
        [
            "config",
            "get",
            "--owner",
            "company",
            "--repo-file",
            str(repos_file),
            "--name",
            "TEST_VAR",
        ],
    )

    assert result.exit_code == 0
    assert "repoA: valueA" in result.output
    assert "repoB: valueB" in result.output


def test_config_delete_repo_file_dry_run(monkeypatch, tmp_path):
    client = FakeGitHubClient()
    repos_file = tmp_path / "repos.txt"
    repos_file.write_text(
        "repoA\nrepoB\n",
        encoding="utf-8",
    )

    class FakeClientContext:
        def __enter__(self):
            return client

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    monkeypatch.setattr(
        "gitpilot.commands.config.GitHubApiClient",
        FakeClientContext,
    )

    result = runner.invoke(
        app,
        [
            "config",
            "delete",
            "--owner",
            "company",
            "--repo-file",
            str(repos_file),
            "--name",
            "TEST_VAR",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert "repoA: Would delete repository variable 'TEST_VAR'." in result.output
    assert "repoB: Would delete repository variable 'TEST_VAR'." in result.output
    assert "Total:   2" in result.output
    assert "Skipped: 2" in result.output


def test_config_set_rejects_both_repos_and_repo_file(tmp_path):
    repos_file = tmp_path / "repos.txt"
    repos_file.write_text("repoA\n", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "config",
            "set",
            "--owner",
            "company",
            "--repos",
            "repoA",
            "--repo-file",
            str(repos_file),
            "--name",
            "TEST_VAR",
            "--value",
            "hello",
        ],
    )

    assert result.exit_code != 0
    assert "Use either --repos or --repo-file, not both." in result.output


def test_config_set_requires_repos_or_repo_file():
    result = runner.invoke(
        app,
        [
            "config",
            "set",
            "--owner",
            "company",
            "--name",
            "TEST_VAR",
            "--value",
            "hello",
        ],
    )

    assert result.exit_code != 0
    assert "Either --repos or --repo-file is required." in result.output
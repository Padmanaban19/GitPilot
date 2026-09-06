from gitpilot.core.branch_operations import create_branch_operation
from gitpilot.core.repositories import RepositoryTarget
from gitpilot.core.results import OperationStatus
from gitpilot.github.errors import GitHubApiError
from gitpilot.github.fake_client import FakeGitHubClient


def test_create_branch_operation():
    client = FakeGitHubClient()

    operation = create_branch_operation(
        client=client,
        source="main",
        target="dev/test",
    )

    repository = RepositoryTarget(
        owner="company",
        name="repoA",
    )

    result = operation(repository)

    assert result.status == OperationStatus.SUCCESS
    assert result.repository == "repoA"
    assert result.message == "Created 'dev/test' from 'main'."

    assert len(client.created_branches) == 1

    branch = client.created_branches[0]

    assert branch.owner == "company"
    assert branch.repository == "repoA"
    assert branch.source == "main"
    assert branch.target == "dev/test"


def test_create_branch_operation_dry_run():
    client = FakeGitHubClient()

    operation = create_branch_operation(
        client=client,
        source="main",
        target="dev/test",
        dry_run=True,
    )

    repository = RepositoryTarget(
        owner="company",
        name="repoA",
    )

    result = operation(repository)

    assert result.status == OperationStatus.SKIPPED
    assert result.message == "Would create 'dev/test' from 'main'."

    assert len(client.created_branches) == 0


def test_create_branch_operation_failure():
    client = FakeGitHubClient()

    def failing_create_branch(
        owner: str,
        repository: str,
        source: str,
        target: str,
    ) -> None:
        raise GitHubApiError(
            status_code=422,
            message="Branch already exists.",
        )

    client.create_branch = failing_create_branch

    operation = create_branch_operation(
        client=client,
        source="main",
        target="dev/test",
    )

    repository = RepositoryTarget(
        owner="company",
        name="repoA",
    )

    try:
        operation(repository)
    except GitHubApiError as exc:
        assert exc.status_code == 422
        assert exc.message == "Branch already exists."
    else:
        raise AssertionError("Expected GitHubApiError")
    
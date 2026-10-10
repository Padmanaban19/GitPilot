import pytest

from gitpilot.core.branch_operations import (
    create_branch_operation,
    delete_branch_operation,
)
from gitpilot.core.executor import execute_bulk
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


def test_delete_branch_operation_success():
    client = FakeGitHubClient()
    client.existing_branches.add(("company", "repoA", "dev/test"))

    operation = delete_branch_operation(
        client=client,
        branch="dev/test",
    )
    repository = RepositoryTarget(owner="company", name="repoA")

    result = operation(repository)

    assert result.status == OperationStatus.SUCCESS
    assert result.message == "Deleted branch 'dev/test'."
    assert len(client.deleted_branches) == 1
    assert client.deleted_branches[0].branch == "dev/test"
    assert ("company", "repoA", "dev/test") not in client.existing_branches


def test_delete_branch_operation_dry_run():
    client = FakeGitHubClient()
    client.existing_branches.add(("company", "repoA", "dev/test"))

    operation = delete_branch_operation(
        client=client,
        branch="dev/test",
        dry_run=True,
    )
    repository = RepositoryTarget(owner="company", name="repoA")

    result = operation(repository)

    assert result.status == OperationStatus.SKIPPED
    assert result.message == "Would delete branch 'dev/test'."
    assert client.deleted_branches == []
    assert ("company", "repoA", "dev/test") in client.existing_branches


def test_delete_branch_operation_skips_missing_branch():
    client = FakeGitHubClient()

    operation = delete_branch_operation(
        client=client,
        branch="dev/missing",
    )
    repository = RepositoryTarget(owner="company", name="repoA")

    result = operation(repository)

    assert result.status == OperationStatus.SKIPPED
    assert result.message == "Branch 'dev/missing' does not exist."
    assert client.deleted_branches == []


def test_delete_branch_operation_refuses_default_branch():
    client = FakeGitHubClient()
    client.repositories[("company", "repoA")] = {
        "default_branch": "main",
    }
    client.existing_branches.add(("company", "repoA", "main"))

    operation = delete_branch_operation(
        client=client,
        branch="main",
    )
    repository = RepositoryTarget(owner="company", name="repoA")

    with pytest.raises(ValueError, match="Refusing to delete default branch"):
        operation(repository)

    assert client.deleted_branches == []
    assert ("company", "repoA", "main") in client.existing_branches


def test_delete_branch_operation_fails_closed_without_default_branch():
    client = FakeGitHubClient()
    client.repositories[("company", "repoA")] = {}
    client.existing_branches.add(("company", "repoA", "dev/test"))

    operation = delete_branch_operation(
        client=client,
        branch="dev/test",
    )
    repository = RepositoryTarget(owner="company", name="repoA")

    with pytest.raises(ValueError, match="Cannot determine the default branch"):
        operation(repository)

    assert client.deleted_branches == []
    assert ("company", "repoA", "dev/test") in client.existing_branches


def test_bulk_delete_continues_after_default_branch_refusal():
    client = FakeGitHubClient()

    # repoA: dev/test is the default branch, so deletion must fail.
    client.repositories[("company", "repoA")] = {
        "default_branch": "dev/test",
    }

    # repoB: main is the default branch, so dev/test can be deleted.
    client.repositories[("company", "repoB")] = {
        "default_branch": "main",
    }

    client.existing_branches.update(
        {
            ("company", "repoA", "dev/test"),
            ("company", "repoB", "dev/test"),
        }
    )

    operation = delete_branch_operation(
        client=client,
        branch="dev/test",
    )

    repositories = [
        RepositoryTarget(owner="company", name="repoA"),
        RepositoryTarget(owner="company", name="repoB"),
    ]

    results = execute_bulk(repositories, operation)

    # Both repositories must be processed.
    assert len(results) == 2

    # repoA must fail because the target is its default branch.
    assert results[0].repository == "repoA"
    assert results[0].status == OperationStatus.FAILED
    assert "Refusing to delete default branch" in results[0].message

    # repoB must still be processed and successfully deleted.
    assert results[1].repository == "repoB"
    assert results[1].status == OperationStatus.SUCCESS
    assert results[1].message == "Deleted branch 'dev/test'."

    # Only repoB's branch should have been deleted.
    assert len(client.deleted_branches) == 1
    assert client.deleted_branches[0].repository == "repoB"

    # Confirm the actual fake-client branch state.
    assert ("company", "repoA", "dev/test") in client.existing_branches
    assert ("company", "repoB", "dev/test") not in client.existing_branches

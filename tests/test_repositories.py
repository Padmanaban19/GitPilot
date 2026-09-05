import pytest

from gitpilot.core.repositories import (
    parse_repositories,
    parse_repositories_file,
)


def test_parse_repositories():
    repositories = parse_repositories(
        "company",
        "repoA,repoB,repoC",
    )
    assert len(repositories) == 3
    assert repositories[0].owner == "company"
    assert repositories[0].name == "repoA"
    assert repositories[1].name == "repoB"
    assert repositories[2].name == "repoC"


def test_parse_repositories_removes_whitespace():
    repositories = parse_repositories(
        "company",
        " repoA, repoB ,repoC ",
    )
    assert [repo.name for repo in repositories] == [
        "repoA",
        "repoB",
        "repoC",
    ]


def test_parse_repositories_file(tmp_path):
    repos_file = tmp_path / "repos.txt"
    repos_file.write_text(
        """
        repoA
        repoB

        # comment
        repoC
        """,
        encoding="utf-8",
    )
    repositories = parse_repositories_file(
        "company",
        str(repos_file),
    )
    assert [repo.name for repo in repositories] == [
        "repoA",
        "repoB",
        "repoC",
    ]


def test_parse_repositories_rejects_empty_owner():
    with pytest.raises(ValueError, match="Owner cannot be empty"):
        parse_repositories(
            "",
            "repoA",
        )


def test_parse_repositories_rejects_empty_repositories():
    with pytest.raises(ValueError, match="At least one repository"):
        parse_repositories(
            "company",
            "   ",
        )


def test_parse_repositories_file_rejects_missing_file(tmp_path):
    repos_file = tmp_path / "does-not-exist.txt"

    with pytest.raises(ValueError, match="Repository file not found"):
        parse_repositories_file(
            "company",
            str(repos_file),
        )
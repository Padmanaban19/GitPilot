from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RepositoryTarget:
    owner: str
    name: str


def _validate_owner(owner: str) -> str:
    owner = owner.strip()

    if not owner:
        raise ValueError("Owner cannot be empty.")

    return owner


def _build_targets(
    owner: str,
    repository_names: list[str],
) -> list[RepositoryTarget]:
    owner = _validate_owner(owner)

    cleaned_names = [
        name.strip()
        for name in repository_names
        if name.strip()
    ]

    if not cleaned_names:
        raise ValueError("At least one repository must be provided.")

    return [
        RepositoryTarget(owner=owner, name=name)
        for name in cleaned_names
    ]


def parse_repositories(
    owner: str,
    repos: str,
) -> list[RepositoryTarget]:
    """Parse a comma-separated repository list."""

    return _build_targets(
        owner,
        repos.split(","),
    )


def parse_repositories_file(
    owner: str,
    repos_file: str,
) -> list[RepositoryTarget]:
    """Parse repository names from a text file."""

    path = Path(repos_file)

    if not path.exists():
        raise ValueError(f"Repository file not found: {repos_file}")

    repository_names = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    return _build_targets(owner, repository_names)
import os
import subprocess


def get_github_token() -> str:
    """Get a GitHub token from the environment or GitHub CLI."""

    token = os.getenv("GITHUB_TOKEN")
    if token:
        return token

    try:
        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        raise RuntimeError(
            "GitHub authentication required. "
            "Set GITHUB_TOKEN or authenticate with GitHub CLI."
        ) from exc

    token = result.stdout.strip()

    if not token:
        raise RuntimeError(
            "GitHub authentication required. "
            "Set GITHUB_TOKEN or authenticate with GitHub CLI."
        )

    return token
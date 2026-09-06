from gitpilot.github.fake_client import FakeGitHubClient


def test_get_repository_variable_returns_none_when_missing():
    client = FakeGitHubClient()

    result = client.get_repository_variable(
        owner="company",
        repository="repoA",
        name="APP_ENV",
    )

    assert result is None


def test_set_repository_variable_creates_variable():
    client = FakeGitHubClient()

    client.set_repository_variable(
        owner="company",
        repository="repoA",
        name="APP_ENV",
        value="production",
    )

    result = client.get_repository_variable(
        owner="company",
        repository="repoA",
        name="APP_ENV",
    )

    assert result == {
        "name": "APP_ENV",
        "value": "production",
    }


def test_set_repository_variable_updates_existing_variable():
    client = FakeGitHubClient()

    client.set_repository_variable(
        owner="company",
        repository="repoA",
        name="APP_ENV",
        value="development",
    )

    client.set_repository_variable(
        owner="company",
        repository="repoA",
        name="APP_ENV",
        value="production",
    )

    result = client.get_repository_variable(
        owner="company",
        repository="repoA",
        name="APP_ENV",
    )

    assert result == {
        "name": "APP_ENV",
        "value": "production",
    }

    assert len(client.repository_variables) == 1
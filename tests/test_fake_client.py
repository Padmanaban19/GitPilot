from gitpilot.github.fake_client import (
    FakeGitHubClient,
    RepositorySecret,
)


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

def test_get_repository_secret_public_key():
    client = FakeGitHubClient()

    public_key = client.get_repository_secret_public_key(
        owner="company",
        repository="repoA",
    )

    assert public_key["key_id"] == "fake-key-id"
    assert public_key["key"] == client._secret_public_key

def test_set_repository_secret_create():
    client = FakeGitHubClient()

    client.set_repository_secret(
        owner="company",
        repository="repoA",
        name="MY_SECRET",
        encrypted_value="encrypted-value",
        key_id="123456",
    )

    assert len(client.repository_secrets) == 1
    assert client.repository_secrets[0] == RepositorySecret(
        owner="company",
        repository="repoA",
        name="MY_SECRET",
        encrypted_value="encrypted-value",
        key_id="123456",
    )

def test_set_repository_secret_update():
    client = FakeGitHubClient()

    client.set_repository_secret(
        owner="company",
        repository="repoA",
        name="MY_SECRET",
        encrypted_value="old-value",
        key_id="123456",
    )

    client.set_repository_secret(
        owner="company",
        repository="repoA",
        name="MY_SECRET",
        encrypted_value="new-value",
        key_id="789012",
    )

    assert len(client.repository_secrets) == 1
    assert client.repository_secrets[0].encrypted_value == "new-value"
    assert client.repository_secrets[0].key_id == "789012"
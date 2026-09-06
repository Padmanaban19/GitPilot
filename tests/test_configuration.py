import pytest

from gitpilot.core.configuration import (
    ConfigurationKind,
    ConfigurationScope,
    ConfigurationTarget,
)
from gitpilot.core.configuration_operations import (
    set_configuration_operation,
    set_repository_secret_operation,
)
from gitpilot.core.repositories import RepositoryTarget
from gitpilot.core.results import OperationStatus
from gitpilot.github.fake_client import FakeGitHubClient


def test_repository_secret_target():
    target = ConfigurationTarget(
        owner="company",
        repository="repoA",
        kind=ConfigurationKind.SECRET,
        name="API_TOKEN",
    )

    assert target.owner == "company"
    assert target.repository == "repoA"
    assert target.kind == ConfigurationKind.SECRET
    assert target.name == "API_TOKEN"
    assert target.environment is None


def test_environment_variable_target():
    target = ConfigurationTarget(
        owner="company",
        repository="repoA",
        kind=ConfigurationKind.VARIABLE,
        name="APP_ENV",
        environment="production",
    )

    assert target.kind == ConfigurationKind.VARIABLE
    assert target.name == "APP_ENV"
    assert target.environment == "production"


def test_configuration_enums():
    assert ConfigurationScope.REPOSITORY.value == "repository"
    assert ConfigurationScope.ENVIRONMENT.value == "environment"
    assert ConfigurationKind.SECRET.value == "secret"
    assert ConfigurationKind.VARIABLE.value == "variable"

def test_set_repository_variable_operation_dry_run():
    client = FakeGitHubClient()

    target = ConfigurationTarget(
        owner="company",
        repository="repoA",
        kind=ConfigurationKind.VARIABLE,
        name="APP_ENV",
    )

    operation = set_configuration_operation(
        client=client,
        target=target,
        value="production",
        dry_run=True,
    )

    result = operation(
        RepositoryTarget(
            owner="company",
            name="repoA",
        )
    )

    assert result.status == OperationStatus.SKIPPED
    assert result.message == (
        "Would set repository variable 'APP_ENV'."
    )
    assert client.repository_variables == []

def test_set_repository_variable_operation():
    client = FakeGitHubClient()

    target = ConfigurationTarget(
        owner="company",
        repository="repoA",
        kind=ConfigurationKind.VARIABLE,
        name="APP_ENV",
    )

    operation = set_configuration_operation(
        client=client,
        target=target,
        value="production",
    )

    result = operation(
        RepositoryTarget(
            owner="company",
            name="repoA",
        )
    )

    assert result.status == OperationStatus.SUCCESS
    assert result.message == "Set repository variable 'APP_ENV'."

    assert client.get_repository_variable(
        owner="company",
        repository="repoA",
        name="APP_ENV",
    ) == {
        "name": "APP_ENV",
        "value": "production",
    }    

def test_set_configuration_operation_rejects_secret_for_now():
    client = FakeGitHubClient()

    target = ConfigurationTarget(
        owner="company",
        repository="repoA",
        kind=ConfigurationKind.SECRET,
        name="API_TOKEN",
    )

    with pytest.raises(
        NotImplementedError,
        match="Configuration kind 'secret' is not supported yet.",
    ):
        set_configuration_operation(
            client=client,
            target=target,
            value="secret-value",
        )

def test_set_repository_secret_operation_dry_run():
    client = FakeGitHubClient()

    target = ConfigurationTarget(
        owner="company",
        repository="repoA",
        kind=ConfigurationKind.SECRET,
        name="MY_SECRET",
    )

    operation = set_repository_secret_operation(
        client=client,
        target=target,
        value="super-secret",
        dry_run=True,
    )

    result = operation(
        RepositoryTarget(
            owner="company",
            name="repoA",
        )
    )

    assert result.status == OperationStatus.SKIPPED
    assert result.message == "Would set repository secret 'MY_SECRET'."

def test_set_repository_secret_operation_rejects_environment_secret():
    client = FakeGitHubClient()

    target = ConfigurationTarget(
        owner="company",
        repository="repoA",
        kind=ConfigurationKind.SECRET,
        name="MY_SECRET",
        environment="production",
    )

    with pytest.raises(
        ValueError,
        match="Environment secrets are not supported yet",
    ):
        set_repository_secret_operation(
            client=client,
            target=target,
            value="super-secret",
        )

def test_set_repository_secret_operation():
    client = FakeGitHubClient()

    target = ConfigurationTarget(
        owner="company",
        repository="repoA",
        kind=ConfigurationKind.SECRET,
        name="MY_SECRET",
    )

    operation = set_repository_secret_operation(
        client=client,
        target=target,
        value="super-secret",
    )

    result = operation(
        RepositoryTarget(
            owner="company",
            name="repoA",
        )
    )

    assert result.status == OperationStatus.SUCCESS
    assert result.message == "Set repository secret 'MY_SECRET'."

    assert len(client.repository_secrets) == 1
    assert client.repository_secrets[0].owner == "company"
    assert client.repository_secrets[0].repository == "repoA"
    assert client.repository_secrets[0].name == "MY_SECRET"
    assert client.repository_secrets[0].key_id == "fake-key-id"
    assert client.repository_secrets[0].encrypted_value != "super-secret"

def test_set_repository_secret_operation_encrypts_value():
    import base64

    from nacl.public import SealedBox

    client = FakeGitHubClient()

    target = ConfigurationTarget(
        owner="company",
        repository="repoA",
        kind=ConfigurationKind.SECRET,
        name="MY_SECRET",
    )

    operation = set_repository_secret_operation(
        client=client,
        target=target,
        value="super-secret",
    )

    result = operation(
        RepositoryTarget(
            owner="company",
            name="repoA",
        )
    )

    assert result.status == OperationStatus.SUCCESS

    stored_secret = client.repository_secrets[0]
    encrypted_bytes = base64.b64decode(stored_secret.encrypted_value)

    decrypted = SealedBox(client._secret_private_key).decrypt(
        encrypted_bytes
    ).decode("utf-8")

    assert decrypted == "super-secret"
import base64
from dataclasses import dataclass

from nacl.public import PrivateKey


@dataclass(frozen=True)
class BranchCreation:
    owner: str
    repository: str
    source: str
    target: str
@dataclass(frozen=True)
class RepositoryVariable:
    owner: str
    repository: str
    name: str
    value: str
@dataclass(frozen=True)
class RepositorySecret:
    owner: str
    repository: str
    name: str
    encrypted_value: str
    key_id: str
@dataclass(frozen=True)
class Environment:
    owner: str
    repository: str
    name: str
class FakeGitHubClient:
    """Fake GitHub client used for testing."""

    def __init__(self) -> None:
        self.created_branches: list[BranchCreation] = []
        self.repository_variables: list[RepositoryVariable] = []
        self.repository_secrets: list[RepositorySecret] = []

        self._secret_private_key = PrivateKey.generate()
        self._secret_public_key = base64.b64encode(
            bytes(self._secret_private_key.public_key)
        ).decode("utf-8")
        self.environments: list[Environment] = []


    def create_branch(
        self,
        owner: str,
        repository: str,
        source: str,
        target: str,
    ) -> None:
        self.created_branches.append(
            BranchCreation(
                owner=owner,
                repository=repository,
                source=source,
                target=target,
            )
        )


    def get_repository_variable(
        self,
        owner: str,
        repository: str,
        name: str,
    ) -> dict | None:
        for variable in self.repository_variables:
            if (
                variable.owner == owner
                and variable.repository == repository
                and variable.name == name
            ):
                return {
                    "name": variable.name,
                    "value": variable.value,
                }

        return None


    def set_repository_variable(
        self,
        owner: str,
        repository: str,
        name: str,
        value: str,
    ) -> None:
        self.repository_variables = [
            variable
            for variable in self.repository_variables
            if not (
                variable.owner == owner
                and variable.repository == repository
                and variable.name == name
            )
        ]

        self.repository_variables.append(
            RepositoryVariable(
                owner=owner,
                repository=repository,
                name=name,
                value=value,
            )
        )

    def get_repository_secret_public_key(
        self,
        owner: str,
        repository: str,
    ) -> dict:
        """Get the public key used to encrypt repository secrets."""
        return {
            "key_id": "fake-key-id",
            "key": self._secret_public_key,
        }
    def set_repository_secret(
        self,
        owner: str,
        repository: str,
        name: str,
        encrypted_value: str,
        key_id: str,
    ) -> None:
        """Create or update a repository secret."""
        self.repository_secrets = [
            secret
            for secret in self.repository_secrets
            if not (
                secret.owner == owner
                and secret.repository == repository
                and secret.name == name
            )
        ]

        self.repository_secrets.append(
            RepositorySecret(
                owner=owner,
                repository=repository,
                name=name,
                encrypted_value=encrypted_value,
                key_id=key_id,
            )
        )

    def get_environment(
        self,
        owner: str,
        repository: str,
        environment: str,
    ) -> dict | None:
        for item in self.environments:
            if (
                item.owner == owner
                and item.repository == repository
                and item.name == environment
            ):
                return {
                    "name": item.name,
                }

        return None

    def create_environment(
        self,
        owner: str,
        repository: str,
        environment: str,
    ) -> None:
        existing = self.get_environment(
            owner=owner,
            repository=repository,
            environment=environment,
        )

        if existing is not None:
            return

        self.environments.append(
            Environment(
                owner=owner,
                repository=repository,
                name=environment,
            )
        )

    def delete_environment(
        self,
        owner: str,
        repository: str,
        environment: str,
    ) -> None:
        self.environments = [
            item
            for item in self.environments
            if not (
                item.owner == owner
                and item.repository == repository
                and item.name == environment
            )
        ]
    
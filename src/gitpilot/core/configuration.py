from dataclasses import dataclass
from enum import Enum


class ConfigurationScope(str, Enum):
    REPOSITORY = "repository"
    ENVIRONMENT = "environment"


class ConfigurationKind(str, Enum):
    SECRET = "secret"
    VARIABLE = "variable"


@dataclass(frozen=True)
class ConfigurationTarget:
    owner: str
    repository: str
    kind: ConfigurationKind
    name: str
    environment: str | None = None

@dataclass(frozen=True)
class EnvironmentTarget:
    owner: str
    repository: str
    name: str
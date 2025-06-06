from __future__ import annotations

import os

from pydantic_settings import BaseSettings

__all__ = ["settings"]


class CommonSettings(BaseSettings):
    # Environment
    PIPES_ENV: str

    # FastAPI
    TITLE: str = "PIPES API"
    DEBUG: bool = False
    TESTING: bool = False
    ALLOW_ORIGINS: list[str] = ["*"]
    ALLOW_METHODS: list[str] = ["*"]
    ALLOW_HEADERS: list[str] = ["*"]

    # Cognito
    PIPES_REGION: str = "us-west-2"
    PIPES_COGNITO_USER_POOL_ID: str
    PIPES_COGNITO_CLIENT_ID: str

    # DocumentDB
    PIPES_DOCDB_HOST: str
    PIPES_DOCDB_PORT: str
    PIPES_DOCDB_NAME: str = "pipes"
    PIPES_DOCDB_USER: str | None
    PIPES_DOCDB_PASS: str | None

    # NeptuneDB
    PIPES_NEPTUNE_HOST: str
    PIPES_NEPTUNE_PORT: str
    PIPES_NEPTUNE_SECURE: bool = True


class DevelopmentSettings(CommonSettings):
    DEBUG: bool = True


class TestingSettings(CommonSettings):
    TESTING: bool = True


class DeploymentSettings(CommonSettings):
    DEBUG: bool = False


def get_settings(env):
    """Get settings regarding the given environment"""
    if env == "local":
        return DevelopmentSettings()

    if env == "testing":
        return TestingSettings()

    if env in ["dev", "stage", "prod"]:
        return DeploymentSettings()

    raise ValueError(
        f"Not a valid environment '{env}', please use 'local', 'dev', 'stage', or 'prod'",
    )


PIPES_ENV = os.getenv("PIPES_ENV", "local")

settings = get_settings(PIPES_ENV)

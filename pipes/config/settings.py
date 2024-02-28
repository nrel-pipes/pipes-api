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

    # DocumentDB
    PIPES_DOCDB_HOST: str
    PIPES_DOCDB_PORT: str
    PIPES_DOCDB_NAME: str
    PIPES_DOCDB_USER: str | None
    PIPES_DOCDB_PASS: str | None

    # Cognito
    PIPES_REGION: str = "us-west-2"
    PIPES_COGNITO_USER_POOL_ID: str
    PIPES_COGNITO_CLIENT_ID: str


class DevelopmentSettings(CommonSettings):
    DEBUG: bool = True


class TestingSettings(CommonSettings):
    TESTING: bool = True


class ProductionSettings(CommonSettings):
    DEBUG: bool = False


def get_settings(env):
    """Get settings regarding the given environment"""
    if env == "prod":
        return ProductionSettings()

    if env == "dev":
        return DevelopmentSettings()

    if env == "testing":
        return TestingSettings()

    raise ValueError(
        f"Not a valid environment '{env}', please use 'dev' or 'prod'",
    )


PIPES_ENV = os.getenv("PIPES_ENV", "dev")

settings = get_settings(PIPES_ENV)

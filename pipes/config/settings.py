from __future__ import annotations

from pydantic_settings import BaseSettings


class CommonSettings(BaseSettings):
    TITLE: str = "PIPES API"
    DEBUG: bool = False
    ALLOW_ORIGINS: list[str] = ["*"]
    ALLOW_METHODS: list[str] = ["*"]
    ALLOW_HEADERS: list[str] = ["*"]


class DevelopmentSettings(CommonSettings):
    DEBUG: bool = True


class ProductionSettings(CommonSettings):
    DEBUG: bool = False


def get_settings(env):
    """Get settings regarding the given environment"""
    if env == "prod":
        return ProductionSettings()

    if env == "dev":
        return DevelopmentSettings()

    raise ValueError(
        f"Not a valid environment '{env}', please use 'dev' or 'prod'",
    )

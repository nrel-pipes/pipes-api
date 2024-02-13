from pydantic_settings import BaseSettings


class CommonSettings(BaseSettings):
    TITLE: str = "PIPES API"
    DEBUG: bool = False
    ALLOW_ORIGINS: list[str] = ["*"]
    ALLOW_METHODS: list[str] = ["*"]
    ALLOW_HEADERS: list[str] = ["*"]


class DevelopmentSettings(CommonSettings):
    DEBUG: bool = True


class DeploymentSettings(CommonSettings):
    DEBUG: bool = False


def get_settings(environment):
    """Get settings regarding the given environment"""
    if environment in ["dev", "prod"]:
        return DeploymentSettings()

    if environment == "local":
        return DevelopmentSettings()

    raise ValueError(
        f"Not a valid environment '{environment}', please use 'local', 'dev', or 'prod'",
    )

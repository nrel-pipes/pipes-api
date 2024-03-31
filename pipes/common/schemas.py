from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class VersionStatus(str, Enum):
    Active = "Active"
    Inactivate = "Inactivate"
    Unresolved = "Unresolved"


class SourceCode(BaseModel):
    """Source Model Schema"""

    location: str = Field(
        title="location",
        description="The location of the source code",
    )
    branch: str | None = Field(
        title="branch",
        default="",
        description="The git branch of source code",
    )
    tag: str | None = Field(
        title="tag",
        default="",
        description="The git tag of source code",
    )
    image: str | None = Field(
        title="image",
        default="",
        description="The location of container image",
    )

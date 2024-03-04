from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class PublicModel(BaseModel):
    pub_id: str = Field(
        title="pub_id",
        max_length=8,
        min_length=8,
        description="The public id",
    )


class Milestone(BaseModel):
    name: str = Field(
        title="name",
        description="milestone name must be unique from each other.",
    )
    description: str = Field(
        title="description",
        description="description of milestone",
    )
    date: datetime = Field(
        title="date",
        description="format YYYY-MM-DD, it must be within the dates of the project.",
    )


class Scenario(BaseModel):
    name: str = Field(
        title="name",
        description="scenario name",
    )
    description: str = Field(
        title="description",
        default="",
        description="scenario description",
    )
    other: dict[str, str] = Field(
        title="other",
        default={},
        description="other properties applied to scenario",
    )


class Sensitivity(BaseModel):
    name: str = Field(
        title="name",
        description="sensitivity name",
    )
    description: str = Field(
        titleee="description",
        description="sensitivity description",
    )


class Assumption(BaseModel):
    name: str = Field(
        title="name",
        description="project assumption name",
    )
    description: str = Field(
        titleee="description",
        description="project assumption description",
    )


class Requirement(BaseModel):
    name: str = Field(
        title="name",
        description="project requirement name",
    )
    description: str = Field(
        titleee="description",
        description="project requirement description",
    )


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


class VersionStatus(str, Enum):
    Active = "Active"
    Inactivate = "Inactivate"
    Unresolved = "Unresolved"

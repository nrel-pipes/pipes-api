from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator

from pipes.common.utilities import parse_datetime


class Milestone(BaseModel):
    name: str = Field(
        title="name",
        description="milestone name must be unique from each other.",
    )
    description: list[str] = Field(
        title="description",
        description="description of milestone",
    )
    milestone_date: datetime = Field(
        title="milestone_date",
        description="format YYYY-MM-DD, it must be within the dates of the project.",
    )

    @field_validator("description", mode="before")
    @classmethod
    def validate_description(cls, value):
        if isinstance(value, str):
            return [value]
        return value

    @field_validator("milestone_date", mode="before")
    @classmethod
    def validate_milestone_date(cls, value):
        try:
            value = parse_datetime(value)
        except Exception as e:
            raise ValueError(f"Invalid milestone_date value: {value}; Error: {e}")

        return value


class Scenario(BaseModel):
    name: str = Field(
        title="name",
        description="scenario name",
    )
    description: list[str] = Field(
        title="description",
        default="",
        description="scenario description",
    )
    other: dict = Field(
        title="other",
        default={},
        description="other properties applied to scenario",
    )

    @field_validator("description", mode="before")
    @classmethod
    def convert_to_list(cls, value):
        if isinstance(value, str):
            return [value]
        return value


class Sensitivity(BaseModel):
    name: str = Field(
        title="name",
        description="sensitivity name",
    )
    description: list[str] = Field(
        titleee="description",
        description="sensitivity description",
    )

    @field_validator("description", mode="before")
    @classmethod
    def convert_string_to_list(cls, value):
        if isinstance(value, str):
            return [value]
        return value


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

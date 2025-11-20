from __future__ import annotations

from datetime import datetime

import pymongo
from pymongo import IndexModel
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field, field_validator

from pipes.common.utilities import parse_datetime
from pipes.projects.contexts import ProjectSimpleContext, ProjectObjectContext


class ProjectRunCreate(BaseModel):
    """Project run creation schema.

    Attributes:
        name: Project run name.
        description: The description of this project run.
        assumptions: Assumptions associated with project run that differ from project.
        requirements: Requirements of the project run that differ from the project.
        scenarios: The scenarios of this project run.
        scheduled_start: Schedule project run start date in YYYY-MM-DD format.
        scheduled_end: Schedule project run end date in YYYY-MM-DD format.
    """

    name: str = Field(
        title="name",
        min_length=1,
        description="Project run name",
    )
    description: str = Field(
        title="description",
        description="the description of this project run",
        default="",
    )
    assumptions: list[str] = Field(
        title="assumptions",
        description="Assumptions associated with project run that differ from project",
        default=[],
    )
    requirements: dict = Field(
        title="requirements",
        description="Requirements of the project run that differ from the project",
        default={},
    )
    scenarios: list[str] = Field(
        title="scenarios",
        description="the scenarios of this prject run",
        default=[],
    )
    scheduled_start: datetime = Field(
        title="scheduled_start",
        description="Schedule project run start date in YYYY-MM-DD format",
    )
    scheduled_end: datetime = Field(
        title="scheduled_end",
        description="Schedule project run end date in YYYY-MM-DD format",
    )
    # models: list[str] = Field(
    #     title="models",
    #     description="Model names",
    # )
    # topology: list[ModelRelation] = Field(
    #     title="topology",
    #     default=[],
    #     description="model relations within pipeline run",
    # )

    @field_validator("scheduled_start", mode="before")
    @classmethod
    def validate_scheduled_start(cls, value):
        try:
            value = parse_datetime(value)
        except Exception as e:
            raise ValueError(f"Invalid scheduled_start value: {value}; Error: {e}")
        return value

    @field_validator("scheduled_end", mode="before")
    @classmethod
    def validate_scheduled_end(cls, value):
        try:
            value = parse_datetime(value)
        except Exception as e:
            raise ValueError(f"Invalid scheduled_end value: {value}; Error: {e}")
        return value


class ProjectRunUpdate(ProjectRunCreate):
    """Project run update schema.

    Attributes:
        name: Project run name.
        description: The description of this project run.
        assumptions: Assumptions associated with project run that differ from project.
        requirements: Requirements of the project run that differ from the project.
        scenarios: The scenarios of this project run.
        scheduled_start: Schedule project run start date in YYYY-MM-DD format.
        scheduled_end: Schedule project run end date in YYYY-MM-DD format.
    """


class ProjectRunRead(ProjectRunCreate):
    """Project run read schema.

    Attributes:
        name: Project run name.
        description: The description of this project run.
        assumptions: Assumptions associated with project run that differ from project.
        requirements: Requirements of the project run that differ from the project.
        scenarios: The scenarios of this project run.
        scheduled_start: Schedule project run start date in YYYY-MM-DD format.
        scheduled_end: Schedule project run end date in YYYY-MM-DD format.
        context: Project context of team.
    """

    context: ProjectSimpleContext = Field(
        title="context",
        description="project context of team",
    )


class ProjectRunDocument(ProjectRunRead, Document):
    """Project run document.

    Attributes:
        name: Project run name.
        description: The description of this project run.
        assumptions: Assumptions associated with project run that differ from project.
        requirements: Requirements of the project run that differ from the project.
        scenarios: The scenarios of this project run.
        scheduled_start: Schedule project run start date in YYYY-MM-DD format.
        scheduled_end: Schedule project run end date in YYYY-MM-DD format.
        context: Project referenced context.
        created_at: Project creation time.
        created_by: User who created the project.
        last_modified: Last modification datetime.
        modified_by: User who modified the project.
    """

    context: ProjectObjectContext = Field(
        title="context",
        description="project referenced context",
    )

    # document information
    created_at: datetime = Field(
        title="created_at",
        description="project creation time",
    )
    created_by: PydanticObjectId = Field(
        title="created_by",
        description="user who created the project",
    )
    last_modified: datetime = Field(
        title="last_modified",
        default=datetime.now(),
        description="last modification datetime",
    )
    modified_by: PydanticObjectId = Field(
        title="modified_by",
        description="user who modified the project",
    )

    class Settings:
        name = "projectruns"
        indexes = [
            IndexModel(
                [
                    ("context", pymongo.ASCENDING),
                    ("name", pymongo.ASCENDING),
                ],
                unique=True,
            ),
        ]

from __future__ import annotations

from datetime import datetime
from uuid import UUID

import pymongo
from pymongo import IndexModel
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field, field_validator

from pipes.common.graph import VertexLabel
from pipes.common.utilities import parse_datetime
from pipes.projects.contexts import ProjectSimpleContext, ProjectObjectContext


# Project Run
class ProjectRunCreate(BaseModel):
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


class ProjectRunRead(ProjectRunCreate):
    context: ProjectSimpleContext = Field(
        title="context",
        description="project context of team",
    )


class ProjectRunVertexProperties(BaseModel):
    project: str = Field(
        title="project",
        min_length=1,
        description="project name",
    )
    name: str = Field(
        title="name",
        min_length=1,
        description="project run name",
    )


class ProjectRunVertex(BaseModel):
    id: str = Field(
        title="id",
        description="The vertex id in UUID format",
    )
    label: str = Field(
        title="label",
        default=VertexLabel.ProjectRun.value,
        description="The label for the vertex",
    )
    properties: ProjectRunVertexProperties = Field(
        title="properties",
        description="project run properties on the vertex",
    )

    @field_validator("id", mode="before")
    @classmethod
    def validate_id(cls, value):
        """Ensure the value is valid UUID string"""
        if not value:
            return None

        value = str(value)
        try:
            UUID(value)
        except ValueError as e:
            raise e

        return value


class ProjectRunDocument(ProjectRunRead, Document):
    vertex: ProjectRunVertex = Field(
        title="vertex",
        description="The project run vertex model",
    )
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
        default=datetime.utcnow(),
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

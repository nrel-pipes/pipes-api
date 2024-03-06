from __future__ import annotations

from datetime import datetime

import pymongo
from pymongo import IndexModel
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field

from pipes.common.schemas import (
    Assumption,
    Requirement,
    Sensitivity,
    Scenario,
    Milestone,
)
from pipes.models.schemas import ModelRelation


# Project
class ProjectCreate(BaseModel):
    name: str = Field(
        title="name",
        min_length=2,
        description="human-readable project id name, must be unique.",
    )
    title: str = Field(
        title="title",
        default="",
        description="Project title",
    )
    description: str = Field(
        title="description",
        default="",
        description="project description",
    )


class ProjectUpdate(ProjectCreate):
    assumptions: list[Assumption] = Field(
        title="assumptions",
        default=[],
        description="project assumptions",
    )
    requirements: list[Requirement] = Field(
        title="requirements",
        default=[],
        description="project requirements",
    )
    scenarios: list[Scenario] = Field(
        title="scenarios",
        default=[],
        description="project scenarios",
    )
    sensitivities: list[Sensitivity] = Field(
        title="sensitivities",
        default=[],
        description="project sensitivities",
    )
    milestones: list[Milestone] = Field(
        title="milestones",
        default=[],
        description="project milestones",
    )
    scheduled_start: datetime | None = Field(
        title="scheduled_start",
        default=None,
        description="project start datetime, format YYYY-MM-DD",
    )
    scheduled_end: datetime | None = Field(
        title="scheduled_end",
        default=None,
        description="format YYYY-MM-DD",
    )
    owner: PydanticObjectId | None = Field(
        title="owner",
        default=None,
        description="project owner",
    )
    leads: set[PydanticObjectId] = Field(
        title="leads",
        default=[],
        description="list of project lead",
    )
    teams: set[PydanticObjectId] = Field(
        title="teams",
        default=[],
        description="list of project teams",
    )


class ProjectBasicRead(ProjectCreate):
    pass


class ProjectDetailRead(ProjectUpdate):
    pass


class ProjectDocument(ProjectDetailRead, Document):

    created_at: datetime | None = Field(
        title="created_at",
        default=None,
        description="project creation time",
    )
    created_by: PydanticObjectId | None = Field(
        title="created_by",
        default=None,
        description="user who created the project",
    )
    last_modified: datetime = Field(
        title="last_modified",
        default=datetime.utcnow(),
        description="last modification datetime",
    )
    modified_by: PydanticObjectId | None = Field(
        title="modified_by",
        default=None,
        description="user who modified the project",
    )

    class Settings:
        name = "projects"
        indexes = [
            IndexModel(
                [("name", pymongo.ASCENDING)],
                unique=True,
            ),
        ]


# Project Run
class ProjectRunCreate(BaseModel):
    name: str = Field(
        title="name",
        min_length=2,
        description="Project run name",
    )
    description: str = Field(
        title="description",
        default="",
        description="the description of this project run",
    )
    assumptions: list[Assumption] = Field(
        title="assumptions",
        description="Assumptions associated with project run that differ from project",
        default=[],
    )
    requirements: list[Requirement] = Field(
        title="requirements",
        default=[],
        description="Requirements of the project run that differ from the project",
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
    models: list[str] = Field(
        title="models",
        description="Model names",
    )
    topology: list[ModelRelation] = Field(
        title="topology",
        default=[],
        description="model relations within pipeline run",
    )


class ProjectRunRead(ProjectRunCreate):
    pass


class ProjectRunDocument(ProjectRunRead, Document):
    models: list[PydanticObjectId] = Field(
        title="models",
        description="Models",
    )

    class Settings:
        name = "projectruns"

    def validate_scenarios(self, value):
        """Project run scenarios must be a subset of project scenarios."""
        pass

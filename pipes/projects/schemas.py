from __future__ import annotations

from datetime import datetime

import pymongo
from pymongo import IndexModel
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field, field_validator

from pipes.common.schemas import Milestone, Scenario, Sensitivity
from pipes.common.utilities import parse_datetime
from pipes.teams.schemas import TeamBasicRead
from pipes.users.schemas import UserCreate, UserRead


# Project
class ProjectCreate(BaseModel):
    name: str = Field(
        title="name",
        min_length=1,
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
    assumptions: list[str] = Field(
        title="assumptions",
        default=[],
        description="project assumptions",
    )
    requirements: dict = Field(
        title="requirements",
        default={},
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
    scheduled_start: datetime = Field(
        title="scheduled_start",
        description="project start datetime, format YYYY-MM-DD",
    )
    scheduled_end: datetime = Field(
        title="scheduled_end",
        description="format YYYY-MM-DD",
    )
    owner: UserCreate = Field(
        title="owner",
        description="project owner",
    )
    # leads: set[UserCreate] = Field(
    #     title="leads",
    #     default=[],
    #     description="list of project lead",
    # )
    # teams: set[TeamCreate] = Field(
    #     title="teams",
    #     default=[],
    #     description="list of project teams",
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


class ProjectBasicRead(BaseModel):
    name: str = Field(
        title="name",
        min_length=1,
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


class ProjectDetailRead(ProjectCreate):
    owner: UserRead = Field(
        title="owner",
        description="project owner",
    )
    leads: list[UserRead] = Field(
        title="leads",
        default=[],
        description="list of project lead",
    )
    teams: list[TeamBasicRead] = Field(
        title="teams",
        default=[],
        description="list of project teams",
    )


class ProjectDocument(ProjectDetailRead, Document):
    owner: PydanticObjectId = Field(
        title="owner",
        description="project owner",
    )
    leads: list[PydanticObjectId] = Field(
        title="leads",
        default=[],
        description="list of project lead",
    )
    teams: list[PydanticObjectId] = Field(
        title="teams",
        default=[],
        description="list of project teams",
    )
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
        name = "projects"
        indexes = [
            IndexModel(
                [("name", pymongo.ASCENDING)],
                unique=True,
            ),
        ]

from __future__ import annotations

from uuid import UUID

import pymongo
from beanie import PydanticObjectId
from pymongo import IndexModel
from beanie import Document
from pydantic import BaseModel, Field, field_validator

from pipes.common.graph import VertexLabel
from pipes.projects.contexts import ProjectSimpleContext, ProjectObjectContext
from pipes.users.schemas import UserRead, UserCreate


# Team
class TeamCreate(BaseModel):
    name: str = Field(
        title="name",
        description="The team name",
    )
    description: str | None = Field(
        title="description",
        default=None,
        description="The team description",
    )
    members: list[UserCreate] = Field(
        title="members",
        default=[],
        description="List of users",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "team1",
                    "description": "this is team one",
                    "members": [
                        {
                            "email": "user1@example.com",
                            "first_name": "User1",
                            "last_name": "Test",
                            "organization": "Org1",
                        },
                        {
                            "email": "user2@example.com",
                            "first_name": "User2",
                            "last_name": "Test",
                            "organization": "Org2",
                        },
                    ],
                },
            ],
        },
    }


class TeamUpdate(TeamCreate):
    pass


class TeamRead(TeamCreate):
    context: ProjectSimpleContext = Field(
        title="context",
        description="project context of team",
    )
    members: list[UserRead] = Field(
        title="members",
        default=[],
        description="List of users",
    )


class TeamBasicRead(BaseModel):
    name: str = Field(
        title="name",
        description="The team name",
    )
    description: str | None = Field(
        title="description",
        default=None,
        description="The team description",
    )


class TeamVertexProperties(BaseModel):
    project: str = Field(
        title="project",
        min_length=1,
        description="project name",
    )
    name: str = Field(
        title="name",
        min_length=1,
        description="team name",
    )


class TeamVertexModel(BaseModel):
    id: str = Field(
        title="id",
        description="The vertex id in UUID format",
    )
    label: str = Field(
        title="label",
        default=VertexLabel.Team.value,
        description="The label for the vertex",
    )
    properties: TeamVertexProperties = Field(
        title="properties",
        description="team properties on the vertex",
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


class TeamDocument(TeamRead, Document):
    """Team document in db"""

    vertex: TeamVertexModel = Field(
        title="vertex",
        description="The neptune vertex model",
    )
    context: ProjectObjectContext = Field(
        title="context",
        description="project referenced context",
    )
    members: list[PydanticObjectId] = Field(
        title="members",
        default=[],
        description="List of user object ids",
    )

    class Settings:
        name = "teams"
        indexes = [
            IndexModel(
                [
                    ("context", pymongo.ASCENDING),
                    ("name", pymongo.ASCENDING),
                ],
                unique=True,
            ),
        ]

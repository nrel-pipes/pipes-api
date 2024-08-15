from __future__ import annotations

import pymongo
from beanie import PydanticObjectId
from pymongo import IndexModel
from beanie import Document
from pydantic import BaseModel, Field

from pipes.graph.schemas import TeamVertex
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


class TeamDocument(TeamRead, Document):
    """Team document in db"""

    vertex: TeamVertex = Field(
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

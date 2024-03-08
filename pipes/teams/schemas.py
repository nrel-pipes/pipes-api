from __future__ import annotations

import pymongo
from pymongo import IndexModel
from beanie import Document
from pydantic import BaseModel, Field

from pipes.common.contexts import ProjectContext, ProjectRefContext
from pipes.users.schemas import UserRead


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


class TeamRead(TeamCreate):
    context: ProjectContext = Field(
        title="context",
        description="The context in string",
    )
    members: list[UserRead] = Field(
        title="members",
        default=[],
        description="List of user emails",
    )


class TeamDocument(TeamRead, Document):
    """Team document in db"""

    context: ProjectRefContext = Field(
        title="context",
        description="project referenced context",
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

from __future__ import annotations

from datetime import datetime

import pymongo
from pymongo import IndexModel
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, EmailStr, Field

from pipes.common.contexts import ProjectContext, ProjectRefContext


# User
class UserBase(BaseModel):
    """User base model"""

    email: EmailStr = Field(
        title="email",
        to_lower=True,
        description="Email address",
    )
    first_name: str | None = Field(
        title="first_name",
        default=None,
        description="First name",
    )
    last_name: str | None = Field(
        title="last_name",
        default=None,
        description="Last name",
    )
    organization: str | None = Field(
        title="organization",
        default=None,
        description="Organization name",
    )


class UserCreate(UserBase):
    """Schema for user create"""

    username: str = Field(
        title="username",
        description="Cognito username",
    )


class UserRead(UserCreate):
    """Schema for user read"""

    is_active: bool = Field(
        title="is_active",
        default=True,
        description="active or inactive user",
    )
    is_superuser: bool = Field(
        title="is_superuser",
        default=False,
        description="Is superuser or not",
    )


class UserDocument(UserRead, Document):
    """User document in db"""

    created_at: datetime = Field(
        title="created_at",
        description="User created datetime",
    )
    teams: set[PydanticObjectId] = Field(
        title="teams",
        default=set(),
        description="ObjectIds of teams",
    )

    class Settings:
        name = "users"
        indexes = [
            IndexModel(
                [("email", pymongo.ASCENDING)],
                unique=True,
            ),
        ]


# Team
class TeamBase(BaseModel):
    name: str = Field(
        title="name",
        description="The team name",
    )
    description: str | None = Field(
        title="description",
        default=None,
        description="The team description",
    )


class TeamCreate(TeamBase):
    pass


class TeamRead(TeamBase):
    context: ProjectContext = Field(
        title="context",
        description="project context",
    )
    members: set[UserRead] = Field(
        title="members",
        to_lower=True,
        description="List of user emails",
    )


class TeamDocument(TeamBase, Document):
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

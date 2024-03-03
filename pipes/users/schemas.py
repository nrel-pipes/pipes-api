from __future__ import annotations

from datetime import datetime

import pymongo
from pymongo import IndexModel
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, EmailStr, Field


# Team
class TeamCreate(BaseModel):
    name: str = Field(
        title="name",
        description="The team name",
    )
    description: str = Field(
        title="description",
        description="The team description",
    )


class TeamRead(TeamCreate):
    pass


class TeamDocument(TeamRead, Document):
    """Team document in db"""

    class Settings:
        name = "teams"
        indexes = [
            IndexModel(
                [("name", pymongo.ASCENDING)],
                unique=True,
            ),
        ]


# User
class UserCreate(BaseModel):
    """Schema for user create"""

    username: str | None = Field(
        title="username",
        default=None,
        description="Cognito username",
    )

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


class UserRead(UserCreate):
    """Schema for user read"""

    teams: set[PydanticObjectId] = Field(
        title="teams",
        default=set(),
        description="List of team names",
    )


class UserDocument(UserRead, Document):
    """User document in db"""

    is_active: bool | None = Field(
        title="is_active",
        default=None,
        description="is active or inactive",
    )
    is_superuser: bool = Field(
        title="is_superuser",
        default=False,
        description="Is superuser or not",
    )
    created_at: datetime | None = Field(
        title="created_at",
        default=None,
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


# Team Members
class TeamMembers(BaseModel):
    team: str = Field(
        title="team",
        description="Team name",
    )
    members: set[EmailStr] = Field(
        title="members",
        to_lower=True,
        description="List of user emails",
    )

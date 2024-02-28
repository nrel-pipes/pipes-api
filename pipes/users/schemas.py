from __future__ import annotations

from datetime import datetime

import pymongo
from pymongo import IndexModel
from beanie import Document, Link
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


class TeamRead(BaseModel):
    name: str = Field(
        title="name",
        description="The team name",
    )
    description: str = Field(
        title="description",
        description="The team description",
    )
    members: list[EmailStr] = Field(
        title="members",
        description="List of user email addresses",
    )


class TeamDocument(Document):
    name: str = Field(
        title="name",
        description="The team name",
    )
    description: str = Field(
        title="description",
        description="The team description",
    )

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

    teams: list[EmailStr] = Field(
        title="teams",
        default=[],
        description="Teams that user belongs to",
    )


class UserDocument(UserRead, Document):
    """PIPES User Schema"""

    username: str | None = Field(
        title="cognito:username",
        default=None,
        description="Cognito username",
    )
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
    last_login: datetime | None = Field(
        title="last_login",
        default=None,
        description="Last login datetime",
    )
    created_at: datetime | None = Field(
        title="created_at",
        default=None,
        description="User created datetime",
    )
    teams: list[Link[TeamDocument]] = Field(
        title="teams",
        default=[],
        description="Teams that user belongs to",
    )

    class Settings:
        name = "users"
        indexes = [
            IndexModel(
                [("email", pymongo.ASCENDING)],
                unique=True,
            ),
        ]

from __future__ import annotations

from datetime import datetime

import pymongo
from pymongo import IndexModel
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, EmailStr, Field


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

    pass


class CognitoUserCreate(UserBase):
    """Schema for cognito user create"""

    username: str | None = Field(
        title="username",
        default=None,
        description="Cognito username",
    )


class UserRead(CognitoUserCreate):
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

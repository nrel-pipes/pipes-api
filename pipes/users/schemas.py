from __future__ import annotations

from datetime import datetime
from uuid import UUID

import pymongo
from pymongo import IndexModel
from beanie import Document
from pydantic import BaseModel, EmailStr, Field

from pipes.common.graph import VertexLabel


# User
class UserCreate(BaseModel):
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


class CognitoUserCreate(UserCreate):
    username: UUID | None = Field(
        title="username",
        description="Cognito username in uuid",
    )


class UserRead(UserCreate):
    """Schema for user read"""

    is_active: bool = Field(
        title="is_active",
        description="Active or inactive user",
    )
    is_superuser: bool = Field(
        title="is_superuser",
        description="Is superuser or not",
    )


class UserVertexProperties(BaseModel):
    email: EmailStr = Field(
        title="email",
        to_lower=True,
        description="Email address",
    )


class UserVertexModel(BaseModel):
    id: UUID = Field(
        title="id",
        description="The Neptune vertex id",
    )
    label: VertexLabel = Field(
        title="label",
        default=VertexLabel.User.value,
        description="The Neptune vertex label",
    )
    properties: UserVertexProperties = Field(
        title="properties",
        description="The user vertex properties",
    )


class UserDocument(UserRead, Document):
    """User document in db"""

    vertex: UserVertexModel = Field(
        title="vertex",
        description="The neptune vertex model",
    )
    username: UUID | None = Field(
        title="username",
        default=None,
        description="Cognito username",
    )
    is_active: bool = Field(
        title="is_active",
        default=True,
        description="Active or inactive user",
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

    class Settings:
        name = "users"
        indexes = [
            IndexModel(
                [("email", pymongo.ASCENDING)],
                unique=True,
            ),
        ]

    def read(self) -> UserRead:
        data = self.model_dump()
        return UserRead.model_validate(data)

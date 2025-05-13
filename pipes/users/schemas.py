from __future__ import annotations

from datetime import datetime
from uuid import UUID

import pymongo
from pymongo import IndexModel
from beanie import Document
from pydantic import BaseModel, EmailStr, Field, field_validator

from pipes.graph.schemas import UserVertex


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

    @field_validator("email", mode="before")
    @classmethod
    def email_to_lowercase(cls, value):
        """Convert email to lowercase"""
        if isinstance(value, str):
            return value.lower()
        return value

class UserPasswordUpdate(BaseModel):
    """User password update model"""

    email: EmailStr = Field(
        title="email",
        to_lower=True,
        description="Email address",
    )
    old_password: str = Field(
        title="old_password",
        description="Old password",
    )
    new_password: str = Field(
        title="new_password",
        description="New password",
    )
    confirm_password: str = Field(
        title="confirm_password",
        description="Confirm new password",
    )
    @field_validator("email", mode="before")
    @classmethod
    def email_to_lowercase(cls, value):
        """Convert email to lowercase"""
        if isinstance(value, str):
            return value.lower()
        return value


class CognitoUserCreate(UserCreate):
    username: str | None = Field(
        title="username",
        description="Cognito username in uuid string",
    )

    @field_validator("username", mode="before")
    @classmethod
    def validate_username(cls, value):
        """Ensure the value is valid UUID string"""
        if not value:
            return None

        value = str(value)
        try:
            UUID(value)
        except ValueError as e:
            raise e

        return value


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


class UserDocument(UserRead, Document):
    """User document in db"""

    vertex: UserVertex = Field(
        title="vertex",
        description="The neptune vertex model",
    )
    username: str | None = Field(
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

    @field_validator("username", mode="before")
    @classmethod
    def validate_username(cls, value):
        """Ensure the value is valid UUID string"""
        if not value:
            return None

        value = str(value)
        try:
            UUID(value)
        except ValueError as e:
            raise e

        return value

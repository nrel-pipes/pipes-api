from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

import pymongo
from beanie import Document
from pydantic import BaseModel, EmailStr, Field, field_validator
from pymongo import IndexModel


# User
class UserCreate(BaseModel):
    """User base model.

    Attributes:
        email: Email address.
        first_name: First name.
        last_name: Last name.
        organization: Organization name.
    """

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
    """Cognito user creation schema.

    Attributes:
        email: Email address.
        first_name: First name.
        last_name: Last name.
        organization: Organization name.
        username: Cognito username in uuid string.
    """

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
    """Schema for user read.

    Attributes:
        email: Email address.
        first_name: First name.
        last_name: Last name.
        organization: Organization name.
        is_active: Active or inactive user.
        is_superuser: Is superuser or not.
    """

    is_active: bool = Field(
        title="is_active",
        description="Active or inactive user",
    )
    is_superuser: bool = Field(
        title="is_superuser",
        description="Is superuser or not",
    )


class UserUpdate(BaseModel):
    """Schema for updating user information.

    Attributes:
        first_name: First name.
        last_name: Last name.
        organization: Organization name.
        is_active: Active or inactive user.
        is_superuser: Is superuser or not.
        updated_at: Timestamp of when the user was last updated.
    """

    first_name: str | None = None
    last_name: str | None = None
    organization: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    updated_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of when the user was last updated",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "Jane",
                "last_name": "Doe",
                "organization": "ACME Corp",
                "is_active": True,
                "is_superuser": False,
            },
        }


class UserDocument(UserRead, Document):
    """User document in db.

    Attributes:
        email: Email address.
        first_name: First name.
        last_name: Last name.
        organization: Organization name.
        is_active: Active or inactive user.
        is_superuser: Is superuser or not.
        username: Cognito username.
        created_at: User created datetime.
    """

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

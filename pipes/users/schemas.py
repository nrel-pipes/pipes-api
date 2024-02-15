from __future__ import annotations

from datetime import datetime
from typing import Annotated

from beanie import Document
from beanie import Indexed
from beanie import Link
from pydantic import EmailStr
from pydantic import Field


class Team(Document):
    # Index team name
    name: Annotated[str, Indexed(unique=True)] = Field(
        title="name",
        description="The team name",
    )
    description: str = Field(
        title="description",
        description="The team description",
    )

    class Settings:
        name = "teams"


class User(Document):
    """PIPES User Schema"""

    # Index user email
    email: Annotated[EmailStr, Indexed()] = Field(
        title="email",
        description="Email address",
    )
    username: str | None = Field(
        title="username",
        description="Username string",
    )
    first_name: str | None = Field(
        title="first_name",
        description="First name",
    )
    last_name: str | None = Field(
        title="last_name",
        description="Last name",
    )
    organization: str | None = Field(
        title="organization",
        description="Organization name",
    )
    is_superuser: bool | None = Field(
        title="is_superuser",
        default=False,
        description="Is superuser or not",
    )
    last_login: datetime | None = Field(
        title="last_login",
        description="Last login datetime",
    )
    teams: Link[Team] | None = Field(
        title="teams",
        description="Belong to teams",
    )

    class Settings:
        name = "users"

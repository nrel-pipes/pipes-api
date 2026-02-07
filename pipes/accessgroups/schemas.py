from __future__ import annotations

from pipes.users.schemas import UserCreate, UserRead

import pymongo
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field
from pymongo import IndexModel


# AccessGroup
class AccessGroupCreate(BaseModel):
    """AccessGroup creation schema.

    Attributes:
        name: The access group name.
        description: The access group description.
        members: List of users.
    """

    name: str = Field(
        title="name",
        description="The access group name",
    )
    description: str | None = Field(
        title="description",
        default=None,
        description="The access group description",
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
                    "name": "accessgroup1",
                    "description": "this is access group one",
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


class AccessGroupUpdate(AccessGroupCreate):
    """AccessGroup update schema.

    Attributes:
        name: The access group name.
        description: The access group description.
        members: List of users.
    """

    pass


class AccessGroupRead(AccessGroupCreate):
    """AccessGroup read schema.

    Attributes:
        name: The access group name.
        description: The access group description.
        members: List of users.
        context: Project context of access group.
    """

    members: list[UserRead] = Field(
        title="members",
        default=[],
        description="List of users",
    )


class AccessGroupDocument(AccessGroupRead, Document):
    """AccessGroup document in db.

    Attributes:
        name: The access group name.
        description: The access group description.
        members: List of user object ids.
        context: Project referenced context.
    """

    members: list[PydanticObjectId] = Field(
        title="members",
        default=[],
        description="List of user object ids",
    )

    class Settings:
        name = "accessgroups"
        indexes = [
            IndexModel(
                [
                    ("context", pymongo.ASCENDING),
                    ("name", pymongo.ASCENDING),
                ],
                unique=True,
            ),
        ]

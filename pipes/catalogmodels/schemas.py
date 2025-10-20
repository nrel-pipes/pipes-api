from __future__ import annotations

from datetime import datetime
from pydantic import EmailStr

import pymongo
from pymongo import IndexModel
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field, field_validator

from pipes.users.schemas import UserRead, UserCreate


class ModelingTeam(BaseModel):
    name: str = Field(
        title="name",
        description="Name of the modeling team",
    )
    members: list[UserCreate] = Field(
        title="members",
        description="List of team members",
    )


class CatalogModelCreate(BaseModel):
    """Model schema for catalog"""

    name: str = Field(
        title="model_catalog",
        min_length=1,
        description="the model name",
    )
    display_name: str | None = Field(
        title="display_name",
        default=None,
        description="Display name for this model vertex.",
    )
    type: str = Field(
        title="type",
        description="Type of model to use in graphic headers (e.g, 'Capacity Expansion')",
    )
    description: list[str] = Field(
        title="description",
        description="Description of the model",
    )
    assumptions: list[str] = Field(
        title="assumptions",
        description="List of model assumptions",
        default=[],
    )
    requirements: dict = Field(
        title="requirements",
        default={},
        description="Model specific requirements (if different from Project and Project-Run)",
    )
    expected_scenarios: list[str] = Field(
        title="expected_scenarios",
        description="List of expected model scenarios",
        default=[],
    )
    modeling_team: ModelingTeam | None = Field(
        title="modeling_team",
        description="Information about the modeling team",
        default=None,
    )
    other: dict = Field(
        title="other",
        default={},
        description="other metadata info about the model in dictionary",
    )
    access_group: list[EmailStr] = Field(
        title="access_group",
        default=[],
        description="A group of users that has access to this model",
    )

    @field_validator("description", mode="before")
    @classmethod
    def validate_description(cls, value):
        if isinstance(value, str):
            return [value]
        return value


class CatalogModelUpdate(CatalogModelCreate):
    access_group: list[EmailStr] = Field(
        title="access_group",
        default=[],
        description="A group of users' emails that has access to this model",
    )


class CatalogModelRead(CatalogModelCreate):

    access_group: list[EmailStr] = Field(
        title="access_group",
        default=[],
        description="A group of users' emails that has access to this model",
    )
    created_at: datetime = Field(
        title="created_at",
        description="catalog model creation time",
    )
    created_by: UserRead = Field(
        title="created_by",
        description="user who created the model in catalog",
    )


class CatalogModelDocument(CatalogModelCreate, Document):
    created_at: datetime = Field(
        title="created_at",
        description="catalog model creation time",
    )
    created_by: PydanticObjectId = Field(
        title="created_by",
        description="user who created the model in catalog",
    )
    last_modified: datetime = Field(
        title="last_modified",
        default=datetime.now(),
        description="last modification datetime",
    )
    modified_by: PydanticObjectId = Field(
        title="modified_by",
        description="user who modified the project",
    )
    access_group: list[PydanticObjectId] = Field(
        title="access_group",
        default=[],
        description="A group of users that has access to this model",
    )

    class Settings:
        name = "catalogmodels"
        indexes = [
            IndexModel(
                [
                    ("name", pymongo.ASCENDING),
                ],
                unique=True,
            ),
        ]

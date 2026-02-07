from __future__ import annotations

from datetime import datetime

import pymongo
from pymongo import IndexModel
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field, field_validator

from pipes.users.schemas import UserRead, UserCreate
from pipes.accessgroups.schemas import AccessGroupRead


class ModelingTeam(BaseModel):
    """Modeling team information.

    Attributes:
        name: Name of the modeling team.
        members: List of team members.
    """

    name: str = Field(
        title="name",
        description="Name of the modeling team",
    )
    members: list[UserCreate] = Field(
        title="members",
        description="List of team members",
    )


class CatalogModelCreate(BaseModel):
    """Model schema for catalog.

    Attributes:
        name: The model name.
        display_name: Display name for this model vertex.
        type: Type of model to use in graphic headers (e.g, 'Capacity Expansion').
        description: Description of the model.
        assumptions: List of model assumptions.
        requirements: Model specific requirements (if different from Project and Project-Run).
        expected_scenarios: List of expected model scenarios.
        modeling_team: Information about the modeling team.
        other: Other metadata info about the model in dictionary.
        access_group: A group of users that has access to this model.
    """

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
    access_group: list[str] = Field(
        title="access_group",
        default=[],
        description="List of access group names that have access to this model",
    )

    @field_validator("description", mode="before")
    @classmethod
    def validate_description(cls, value):
        if isinstance(value, str):
            return [value]
        return value


class CatalogModelUpdate(CatalogModelCreate):
    """Model update schema.

    Attributes:
        name: The model name.
        display_name: Display name for this model vertex.
        type: Type of model to use in graphic headers (e.g, 'Capacity Expansion').
        description: Description of the model.
        assumptions: List of model assumptions.
        requirements: Model specific requirements (if different from Project and Project-Run).
        expected_scenarios: List of expected model scenarios.
        modeling_team: Information about the modeling team.
        other: Other metadata info about the model in dictionary.
        access_group: A group of users that has access to this model.
    """

    pass


class CatalogModelRead(CatalogModelCreate):
    """Model read schema.

    Attributes:
        name: The model name.
        display_name: Display name for this model vertex.
        type: Type of model to use in graphic headers (e.g, 'Capacity Expansion').
        description: Description of the model.
        assumptions: List of model assumptions.
        requirements: Model specific requirements (if different from Project and Project-Run).
        expected_scenarios: List of expected model scenarios.
        modeling_team: Information about the modeling team.
        other: Other metadata info about the model in dictionary.
        access_group: List of access groups that have access to this model.
        created_at: Catalog model creation time.
        created_by: User who created the model in catalog.
    """

    access_group: list[AccessGroupRead] = Field(
        title="access_group",
        default=[],
        description="List of access groups that have access to this model",
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
    """Catalog model document.

    Attributes:
        name: The model name.
        display_name: Display name for this model vertex.
        type: Type of model to use in graphic headers (e.g, 'Capacity Expansion').
        description: Description of the model.
        assumptions: List of model assumptions.
        requirements: Model specific requirements (if different from Project and Project-Run).
        expected_scenarios: List of expected model scenarios.
        modeling_team: Information about the modeling team.
        other: Other metadata info about the model in dictionary.
        access_group: List of access group object IDs that have access to this model.
        created_at: Catalog model creation time.
        created_by: User who created the model in catalog.
        last_modified: Last modification datetime.
        modified_by: User who modified the project.
    """

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
        description="List of access group object IDs that have access to this model",
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

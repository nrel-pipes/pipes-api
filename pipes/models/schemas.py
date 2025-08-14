from __future__ import annotations

from datetime import datetime

import pymongo
from beanie import PydanticObjectId
from pymongo import IndexModel
from beanie import Document
from pydantic import BaseModel, Field, field_validator, ConfigDict

from pipes.common.utilities import parse_datetime
from pipes.projectruns.contexts import ProjectRunSimpleContext, ProjectRunObjectContext
from pipes.teams.schemas import TeamRead


# Model
class ScenarioMapping(BaseModel):
    """Mapping model scenario to project scenarios"""

    model_scenario: str = Field(
        title="model_scenario",
        description="The model scenario name",
    )
    project_scenarios: list[str] = Field(
        title="project_scenarios",
        description="List of project scenario names that the model scenario maps to",
    )
    description: list[str] = Field(
        title="description",
        default=[],
        description="Model scenario description",
    )
    other: dict = Field(
        title="other",
        default={},
        description="other metadata info about the model scenario mapping in dictionary",
    )

    model_config = ConfigDict(protected_namespaces=())

    @field_validator("description", mode="before")
    @classmethod
    def validate_description(cls, value):
        if isinstance(value, str):
            return [value]
        return value


class ModelCreate(BaseModel):
    """Model schema"""

    name: str = Field(
        title="model",
        min_length=1,
        description="the model name",
    )
    display_name: str | None = Field(
        title="display_name",
        default=None,
        description="Display name for this model.",
    )
    type: str = Field(
        title="type",
        description="Type of model to use in graphic headers (e.g, 'Capacity Expansion')",
    )
    description: str | list[str] = Field(
        title="description",
        description="Description of the model",
    )
    modeling_team: str = Field(
        title="modeling_team",
        description="Which modeling team to link this model to.",
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
    scheduled_start: datetime = Field(
        title="scheduled_start",
        description="Schedule model start date in YYYY-MM-DD format",
    )
    scheduled_end: datetime = Field(
        title="scheduled_end",
        description="Schedule model end date in YYYY-MM-DD format",
    )
    # TODO: if missing from TOML, populate with project-run or project scenarios
    expected_scenarios: list[str] = Field(
        title="expected_scenarios",
        description="List of expected model scenarios",
        default=[],  # TODO: default to the list from project or project run
    )
    scenario_mappings: list[ScenarioMapping] = Field(
        title="scenario_mappings",
        description="Model scenarios (if different) and how they map to the project scenarios",
        default=[],
    )
    other: dict = Field(
        title="other",
        default={},
        description="other metadata info about the model in dictionary",
    )

    @field_validator("description", mode="before")
    @classmethod
    def validate_description(cls, value):
        if isinstance(value, str):
            return [value]
        return value

    @field_validator("scheduled_start", mode="before")
    @classmethod
    def validate_scheduled_start(cls, value):
        try:
            value = parse_datetime(value)
        except Exception as e:
            raise ValueError(f"Invalid scheduled_start value: {value}; Error: {e}")
        return value

    @field_validator("scheduled_end", mode="before")
    @classmethod
    def validate_scheduled_end(cls, value):
        try:
            value = parse_datetime(value)
        except Exception as e:
            raise ValueError(f"Invalid scheduled_end value: {value}; Error: {e}")
        return value


class ModelUpdate(ModelCreate): ...


class ModelRead(ModelCreate):
    context: ProjectRunSimpleContext = Field(
        title="context",
        description="project run context",
    )
    modeling_team: TeamRead = Field(
        title="model",
        description="The modeling team object",
    )


class ModelDocument(ModelRead, Document):
    context: ProjectRunObjectContext = Field(
        title="context",
        description="the project run object id",
    )
    modeling_team: PydanticObjectId = Field(
        title="modeling_team",
        description="the modeling team object id",
    )

    # document information
    created_at: datetime = Field(
        title="created_at",
        description="project creation time",
    )
    created_by: PydanticObjectId = Field(
        title="created_by",
        description="user who created the project",
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

    class Settings:
        name = "models"
        indexes = [
            IndexModel(
                [
                    ("context", pymongo.ASCENDING),
                    ("name", pymongo.ASCENDING),
                ],
                unique=True,
            ),
        ]

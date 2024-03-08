from __future__ import annotations

from datetime import datetime

import pymongo
from pymongo import IndexModel
from beanie import Document
from pydantic import BaseModel, Field


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
    description: str = Field(
        title="description",
        default="",
        description="Model scenario description",
    )
    other: dict[str, str] = Field(
        title="other",
        default={},
        description="other metadata info about the model scenario mapping in dictionary",
    )


class ModelCreate(BaseModel):
    """Model schema"""

    model: str = Field(
        title="model",
        min_length=2,
        description="the model name",
    )
    modeling_team: str | None = Field(
        title="modeling_team",
        description="Which modeling team to link this model to.",
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
    description: str = Field(
        title="description",
        description="Description of the model",
    )
    assumptions: list[str] = Field(
        title="assumptions",
        description="List of model assumptions",
        required=False,
        default=[],
    )
    # TODO: if missing from TOML, populate with project-run or project scenarios
    expected_scenarios: list[str] = Field(
        title="assumptions",
        description="List of expected model scenarios",
        default=[],  # TODO: default to the list from project or project run
    )
    scheduled_start: datetime = Field(
        title="scheduled_start",
        description="Schedule model start date in YYYY-MM-DD format",
    )
    scheduled_end: datetime = Field(
        title="scheduled_end",
        description="Schedule model end date in YYYY-MM-DD format",
    )
    requirements: dict = Field(
        title="requirements",
        default={},
        description="Model specific requirements (if different from Project and Project-Run)",
    )
    scenario_mappings: list[ScenarioMapping] = Field(
        title="scenario_mappings",
        description="Model scenarios (if different) and how they map to the project scenarios",
        default=[],
    )
    other: dict[str, str] = Field(
        title="other",
        default={},
        description="other metadata info about the model in dictionary",
    )


class ModelRead(ModelCreate):
    pass


class ModelDocument(ModelRead, Document):

    class Settings:
        name = "models"
        # TODO: should model names unique globally?
        indexes = [
            IndexModel(
                [("name", pymongo.ASCENDING)],
                unique=True,
            ),
        ]


class ModelRelation(BaseModel):
    """Model Connection Schema"""

    from_model: str = Field(
        title="from_model",
        description="the from_model name",
    )
    to_model: str = Field(
        title="to_model",
        description="the to_model name",
    )
    # handoffs: list[Handoff] = Field(
    #     title="handoffs",
    #     description="The handoffs from model to model",
    #     default=[],
    # )

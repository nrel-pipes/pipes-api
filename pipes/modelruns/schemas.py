from __future__ import annotations

from datetime import datetime

import pymongo
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field, field_validator
from pymongo import IndexModel

from pipes.common.schemas import SourceCode
from pipes.models.contexts import ModelSimpleContext, ModelObjectContext
from pipes.datasets.schemas import DatasetSchedule


# Model Run
class ModelRunCreate(BaseModel):
    """Model Run Schema.

    Attributes:
        name: Model run name.
        description: The description of the model run.
        version: The version of model code.
        assumptions: List of model run assumptions.
        notes: Model run notes.
        source_code: The source code of the model run.
        config: Model run config.
        env_deps: Model run environment dependencies.
        datasets: Output datasets for handoff.
    """

    name: str = Field(
        title="name",
        min_length=1,
        description="Model run name",
    )
    description: list[str] = Field(
        title="description",
        default="The description of the model run",
    )
    version: str = Field(
        title="version",
        description="The version of model code",
    )
    assumptions: list[str] = Field(
        title="assumptions",
        description="List of model run assumptions",
        default=[],
    )
    notes: str = Field(
        title="notes",
        description="Model run notes",
        default="",
    )
    source_code: SourceCode | None = Field(
        title="source_code",
        default=None,
        description="The source code of the model run",
    )
    config: dict = Field(
        title="config",
        description="Model run config",
        default={},
    )
    env_deps: dict = Field(
        title="env_deps",
        description="Model run environment dependencies",
        default={},
    )
    datasets: list[DatasetSchedule] = Field(
        title="datasets",
        default=[],
        description="Output datasets for handoff",
    )
    # TODO:
    # handoffs =

    @field_validator("description", mode="before")
    @classmethod
    def validate_description(cls, value):
        if isinstance(value, str):
            return [value]
        return value


class ModelRunRead(ModelRunCreate):
    """Model run read schema.

    Attributes:
        name: Model run name.
        description: The description of the model run.
        version: The version of model code.
        assumptions: List of model run assumptions.
        notes: Model run notes.
        source_code: The source code of the model run.
        config: Model run config.
        env_deps: Model run environment dependencies.
        datasets: Output datasets for handoff.
        context: Project run context.
    """

    context: ModelSimpleContext = Field(
        title="context",
        description="project run context",
    )


class ModelRunDocument(ModelRunRead, Document):
    """Model run document.

    Attributes:
        name: Model run name.
        description: The description of the model run.
        version: The version of model code.
        assumptions: List of model run assumptions.
        notes: Model run notes.
        source_code: The source code of the model run.
        config: Model run config.
        env_deps: Model run environment dependencies.
        datasets: Output datasets for handoff.
        context: Model context.
        created_at: Project creation time.
        created_by: User who created the project.
        last_modified: Last modification datetime.
        modified_by: User who modified the project.
    """

    context: ModelObjectContext = Field(
        title="context",
        description="model context",
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
        name = "modelruns"
        indexes = [
            IndexModel(
                [
                    ("context", pymongo.ASCENDING),
                    ("name", pymongo.ASCENDING),
                ],
                unique=True,
            ),
        ]

from __future__ import annotations

from datetime import datetime

import pymongo
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field, field_validator, ConfigDict
from pymongo import IndexModel

from pipes.common.utilities import parse_datetime
from pipes.graph.schemas import FeedsEdge
from pipes.projectruns.contexts import ProjectRunSimpleContext, ProjectRunObjectContext


# Handoffs
class HandoffCreate(BaseModel):
    """Handoff schema between models"""

    from_model: str = Field(
        title="from_model",
        description="the from_model name",
    )
    to_model: str = Field(
        title="to_model",
        description="the to_model name",
    )
    from_modelrun: str | None = Field(
        title="from_modelrun",
        default=None,
        description="The model run name that generates the handoff",
    )
    name: str = Field(
        title="name",
        description="Unique handoff identifier",
    )
    description: str = Field(
        title="description",
        description="Description of this handoff",
    )
    scheduled_start: datetime | None = Field(
        title="scheduled_start",
        default=None,
        description="scheduled start date",
    )
    scheduled_end: datetime | None = Field(
        title="scheduled_end",
        default=None,
        description="scheduled end date",
    )
    submission_date: datetime | None = Field(
        title="submission_date",
        default=None,
        description="scheduled end date",
    )
    notes: str = Field(
        title="notes",
        description="Handoff notes",
        default="",
    )

    @field_validator("scheduled_start", mode="before")
    @classmethod
    def validate_scheduled_start(cls, value):
        if value is None:
            return value

        try:
            value = parse_datetime(value)
        except Exception as e:
            raise ValueError(f"Invalid scheduled_start value: {value}; Error: {e}")
        return value

    @field_validator("scheduled_end", mode="before")
    @classmethod
    def validate_scheduled_end(cls, value):
        if value is None:
            return value

        try:
            value = parse_datetime(value)
        except Exception as e:
            raise ValueError(f"Invalid scheduled_end value: {value}; Error: {e}")
        return value

    @field_validator("submission_date", mode="before")
    @classmethod
    def validate_submission_date(cls, value):
        if value is None:
            return value

        try:
            value = parse_datetime(value)
        except Exception as e:
            raise ValueError(f"Invalid submission_date value: {value}; Error: {e}")
        return value


class HandoffRead(HandoffCreate):
    context: ProjectRunSimpleContext = Field(
        title="context",
        description="project run context",
    )


class HandoffDocument(HandoffRead, Document):
    edge: FeedsEdge = Field(
        title="edge",
        description="the edge in the graph db",
    )
    context: ProjectRunObjectContext = Field(
        title="context",
        description="the project run object id",
    )

    # document references
    from_model: PydanticObjectId = Field(
        title="from_model",
        description="the from_model object id",
    )
    to_model: PydanticObjectId = Field(
        title="to_model",
        description="the to_model object id",
    )
    from_modelrun: PydanticObjectId | None = Field(
        title="from_modelrun",
        description="the modelrun object id",
        default=None,
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
    model_config = ConfigDict(protected_namespaces=())

    class Settings:
        name = "handoffs"
        indexes = [
            IndexModel(
                [
                    ("context", pymongo.ASCENDING),
                    ("name", pymongo.ASCENDING),
                ],
                unique=True,
            ),
        ]

from __future__ import annotations

from datetime import datetime
from enum import Enum

import pymongo
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field
from pymongo import IndexModel

from pipes.common.schemas import SourceCode
from pipes.graph.schemas import TaskVertex
from pipes.modelruns.contexts import ModelRunObjectContext, ModelRunSimpleContext


class TaskStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class TaskType(str, Enum):
    Transformation = "Transformation"
    QAQC = "QAQC"
    Visualization = "Visualization"


class TaskActionCreate(BaseModel):
    name: str = Field(
        title="name",
        description="task action name",
    )
    datasets: list[str] = Field(
        title="datasets",
        description="List of datasets within this Model Run that the task applies to.",
    )
    description: str = Field(
        title="description",
        default="",
        description="Description of task process",
    )
    assignee: str = Field(
        title="assignee",
        description="The user who will be responsible for performing this task",
    )
    inputs: list[str] = Field(
        title="inputs",
        description="handoff datasets to use, if empty this task will apply to all registered handoff datasets.",
        default=[],
    )
    scheduled_start: datetime | None = Field(
        title="scheduled_start",
        description="scheduled start date",
        default=None,
    )
    scheduled_end: datetime | None = Field(
        title="scheduled_end",
        description="scheduled end date",
        defualt=None,
    )
    notes: str = Field(
        title="notes",
        description="Notes about this task",
        default="",
    )


class TaskActionRead(TaskActionCreate):
    status: TaskStatus = Field(
        title="status",
        description="PASS/FAIL flag for the task action.",
    )


class TaskCreate(BaseModel):

    name: str = Field(
        title="name",
        description="task name, must be unique to this model run.",
    )
    type: str = Field(
        title="type",
        description="task type, like be QAQC, Transformation, or Visualization",
    )
    description: str = Field(
        title="description",
        description="description of task process",
    )
    notes: str = Field(
        title="notes",
        description="notes and additional information",
        default="",
    )
    actions: list[TaskActionCreate] = Field(
        title="actions",
        description="List of actions under this task",
    )
    source_code: SourceCode = Field(
        title="script",
        description="Scripts used to perform the task process",
    )
    outputs: list[dict] = Field(
        title="outputs",
        description="Free form dictionary, store outputs information",
        default=[],
    )


class TaskRead(TaskCreate):
    context: ModelRunSimpleContext = Field(
        title="context",
        description="model run context",
    )


class TaskDocument(TaskRead, Document):
    vertex: TaskVertex = Field(
        title="vertex",
        description="The task vertex pydantic model",
    )
    context: ModelRunObjectContext = Field(
        title="context",
        description="model run context reference",
    )
    status: TaskStatus = Field(
        title="task_status",
        description="PASS/FAIL flag for the task. ",
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
        name = "datasets"
        indexes = [
            IndexModel(
                [
                    ("context", pymongo.ASCENDING),
                    ("name", pymongo.ASCENDING),
                ],
                unique=True,
            ),
        ]

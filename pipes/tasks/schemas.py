from __future__ import annotations

from datetime import datetime
from enum import Enum

import pymongo
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, EmailStr, Field
from pymongo import IndexModel

from pipes.common.schemas import SourceCode
from pipes.graph.schemas import TaskVertex
from pipes.modelruns.contexts import ModelRunObjectContext, ModelRunSimpleContext
from pipes.users.schemas import UserCreate, UserRead


class TaskStatus(str, Enum):
    Pending = "Pending"
    Running = "Running"
    Success = "Success"
    Failed = "Failed"


class TaskType(str, Enum):
    Transformation = "Transformation"
    QAQC = "QAQC"
    Visualization = "Visualization"


class SubTask(BaseModel):
    name: str = Field(
        title="name",
        description="task action name",
    )
    description: str = Field(
        title="description",
        default="",
        description="Description of task process",
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
        default="",
        description="description of task process",
    )
    assignee: UserCreate | EmailStr | None = Field(
        title="assignee",
        default=None,
        description="The user who conducts this task",
    )
    status: TaskStatus = Field(
        title="status",
        default=TaskStatus.Pending,
        description="The task status - Pending, Running, Success, or Failed",
    )
    # Each task should have at least one subtask
    subtasks: list[SubTask] = Field(
        title="subtasks",
        description="List of actions under this task",
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
    completion_date: datetime | None = Field(
        title="completion_date",
        description="task completion date",
        default=None,
    )
    source_code: SourceCode | None = Field(
        title="script",
        description="Scripts used to perform the task process",
        default=None,
    )
    input_datasets: list[str] = Field(
        title="input_datasets",
        description="List of datasets that the task applies to.",
        default=[],
    )
    input_parameters: dict = Field(
        title="input_parameters",
        description="Non-dataset inputs, i.e. parameters in dictionary",
        default={},
    )
    output_datasets: list[str] = Field(
        title="output_datasts",
        description="List of datasets produced from this task",
        default=[],
    )
    output_values: dict = Field(
        title="output_values",
        description="non-dataset outputs, i.e. values in dictionary",
        default={},
    )
    logs: str = Field(
        title="logs",
        description="task log location",
        default="",
    )
    notes: str = Field(
        title="notes",
        description="notes and additional information",
        default="",
    )


class TaskRead(TaskCreate):
    context: ModelRunSimpleContext = Field(
        title="context",
        description="model run context",
    )
    assignee: UserRead | None = Field(
        title="assignee",
        description="Assignee in user read schema",
    )
    # input_datasets: list[DatasetRead] = Field(
    #     title="input_datasets",
    #     description="List of input datasets in read schema",
    # )
    # output_datasets: list[DatasetRead] = Field(
    #     title="output_datasets",
    #     description="List of output datasets in read schema",
    #     default=[],
    # )


class TaskDocument(TaskRead, Document):
    vertex: TaskVertex = Field(
        title="vertex",
        description="The task vertex pydantic model",
    )
    context: ModelRunObjectContext = Field(
        title="context",
        description="model run context reference",
    )
    assignee: PydanticObjectId | None = Field(
        title="assignee",
        description="The assignee user object id",
        default=None,
    )
    input_datasets: list[PydanticObjectId] = Field(
        title="input_datasets",
        description="List of input dataset object ids",
    )
    output_datasets: list[PydanticObjectId] = Field(
        title="output_datasets",
        default=[],
        description="List of output dataset object ids",
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
        name = "tasks"
        indexes = [
            IndexModel(
                [
                    ("context", pymongo.ASCENDING),
                    ("name", pymongo.ASCENDING),
                ],
                unique=True,
            ),
        ]

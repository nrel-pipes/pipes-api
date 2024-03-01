from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"


class TaskCreate(BaseModel):
    name: str = Field(
        title="name",
        description="task name",
    )
    label: str = Field(
        title="label",
        to_lower=True,
        description="e.g. transformation, qaqc, visualization",
    )
    status: TaskStatus = Field(
        title="status",
        description="PASS/FAIL flag for the task. ",
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

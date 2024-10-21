from __future__ import annotations

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field

class TaskContext(BaseModel):
    project: Document = Field(
        title="project",
        description="project document",
    )
    projectrun: Document = Field(
        title="projectrun",
        description="projectrun document",
    )
    model: Document = Field(
        title="model",
        description="model document",
    )
    modelrun: Document = Field(
        title="modelrun",
        description="modelrun document",
    )
    task: Document = Field(
        title="modelrun",
        description="modelrun document",
    )
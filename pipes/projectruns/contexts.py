from __future__ import annotations

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field


# context
class ProjectRunSimpleContext(BaseModel):
    project: str = Field(
        title="project",
        min_length=1,
        description="project name",
    )
    projectrun: str = Field(
        title="projectrun",
        min_length=1,
        description="projectrun name",
    )


class ProjectRunDocumentContext(BaseModel):
    project: Document = Field(
        title="project",
        description="project document",
    )
    projectrun: Document = Field(
        title="projectrun",
        description="projectrun document",
    )


class ProjectRunObjectContext(BaseModel):
    project: PydanticObjectId = Field(title="project", description="project name")
    projectrun: PydanticObjectId = Field(
        title="projectrun",
        description="projectrun object id",
    )

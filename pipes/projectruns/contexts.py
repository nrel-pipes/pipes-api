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

    def __str__(self):
        return "{" f"project: {self.project}," f"projectrun: {self.projectrun}" "}"


class ProjectRunDocumentContext(BaseModel):
    project: Document = Field(
        title="project",
        description="project document",
    )
    projectrun: Document = Field(
        title="projectrun",
        description="projectrun document",
    )

    def __str__(self):
        return (
            "{"
            f"project: {self.project.name},"
            f"projectrun: {self.projectrun.name}"
            "}"
        )


class ProjectRunObjectContext(BaseModel):
    project: PydanticObjectId = Field(title="project", description="project name")
    projectrun: PydanticObjectId = Field(
        title="projectrun",
        description="projectrun object id",
    )

    def __str__(self):
        return "{" f"project: {self.project}," f"projectrun: {self.projectrun}" "}"

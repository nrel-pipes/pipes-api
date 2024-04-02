from __future__ import annotations

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field


# Contexts
class ProjectSimpleContext(BaseModel):
    project: str = Field(
        title="project",
        min_length=1,
        description="project name",
    )

    def __str__(self):
        return "{" f"project: {self.project}" "}"


class ProjectDocumentContext(BaseModel):
    # NOTE: use Document type here, avoid circular import
    project: Document = Field(
        title="project",
        description="project document",
    )

    def __str__(self):
        return "{" f"project: {self.project.name}" "}"


class ProjectObjectContext(BaseModel):
    project: PydanticObjectId = Field(
        title="project",
        description="project object id",
    )

    def __str__(self):
        return "{" f"project: {self.project}" "}"

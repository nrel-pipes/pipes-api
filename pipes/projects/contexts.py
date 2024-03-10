from __future__ import annotations

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field


# Contexts
class ProjectSimpleContext(BaseModel):
    project: str = Field(
        title="project",
        min_length=2,
        description="project name",
    )


class ProjectDocumentContext(BaseModel):
    # NOTE: use Document type here, avoid circular import
    project: Document = Field(
        title="project",
        description="project document",
    )


class ProjectObjectContext(BaseModel):
    project: PydanticObjectId = Field(
        title="project",
        description="project object id",
    )

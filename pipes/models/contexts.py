from __future__ import annotations

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field


class ModelSimpleContext(BaseModel):
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
    model: str = Field(
        title="model",
        min_length=1,
        description="model name",
    )

    def __str__(self):
        return (
            "{"
            f"project: {self.project},"
            f"projectrun: {self.projectrun},"
            f"model: {self.model}"
            "}"
        )


class ModelDocumentContext(BaseModel):
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

    def __str__(self):
        return (
            "{"
            f"project: {self.project.name},"
            f"projectrun: {self.projectrun.name},"
            f"model: {self.model.name}"
            "}"
        )


class ModelObjectContext(BaseModel):
    project: PydanticObjectId = Field(
        title="project",
        description="project id",
    )
    projectrun: PydanticObjectId = Field(
        title="projectrun",
        description="projectrun id",
    )
    model: PydanticObjectId = Field(
        title="model",
        description="model id",
    )

    def __str__(self):
        return (
            "{"
            f"project: {self.project},"
            f"projectrun: {self.projectrun},"
            f"model: {self.model}"
            "}"
        )

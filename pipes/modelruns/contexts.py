from __future__ import annotations

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field


# Contexts
class ModelRunSimpleContext(BaseModel):
    project: str = Field(
        title="project",
        description="project name",
    )
    projectrun: str = Field(
        title="projectrun",
        description="projectrun name",
    )
    model: str = Field(
        title="model",
        description="model name",
    )
    modelrun: str = Field(
        title="modelrun",
        description="modelrun name",
    )
    status: str = Field(
        title="status",
        description="""Status of model run -- []""",
    )

    def __str__(self) -> str:
        return f"[project:{self.project} | projectrun:{self.projectrun} | model:{self.model} | modelrun:{self.modelrun}]"  # noqa: E501


class ModelRunDocumentContext(BaseModel):
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

    def __str__(self) -> str:
        return f"[project:{self.project.name} | projectrun:{self.projectrun.name} | model:{self.model.name} | modelrun:{self.modelrun.name}]"  # noqa: E501


class ModelRunObjectContext(BaseModel):
    project: PydanticObjectId = Field(
        title="project",
        description="project id",
    )
    projectrun: PydanticObjectId = Field(
        title="projectrun",
        description="projectrun id",
    )
    model: PydanticObjectId = Field(title="model", description="model id")
    modelrun: PydanticObjectId = Field(
        title="modelrun",
        description="modelrun id",
    )

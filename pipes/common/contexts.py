from __future__ import annotations

from beanie import PydanticObjectId
from pydantic import Field, BaseModel


# project contexts
class ProjectContext(BaseModel):
    project: str = Field(
        title="project",
        description="project name",
    )


class ProjectRefContext(BaseModel):
    project: PydanticObjectId = Field(
        title="project",
        description="project object id",
    )


# project run contexts
class ProjectRunContext(BaseModel):
    project: str = Field(
        title="project",
        description="project name",
    )
    projectrun: str = Field(
        title="projectrun",
        description="projectrun name",
    )


class ProjectRunRefContext(BaseModel):
    project: PydanticObjectId = Field(title="project", description="project name")
    projectrun: PydanticObjectId = Field(
        title="projectrun",
        description="projectrun object id",
    )


# model contexts
class ModelContext(BaseModel):
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


class ModelRefContext(BaseModel):
    project: PydanticObjectId = Field(
        title="project",
        description="project id",
    )
    projectrun: PydanticObjectId = Field(
        title="projectrun",
        description="projectrun id",
    )
    model: str = Field(title="model", description="model id")


# model run contexts


# Input context
class ModelRunContext(BaseModel):
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


class ModelRunRefContext(BaseModel):
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

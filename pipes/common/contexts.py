from beanie import PydanticObjectId
from pydantic import BaseModel, Field

# Human readable


class ProjectContext(BaseModel):
    project: str = Field(title="project", description="project name")


class ProjectRunContext(BaseModel):
    project: str = Field(title="project", description="project name")
    projectrun: str = Field(title="projectrun", description="project run name")


class ModelContext(BaseModel):
    project: str = Field(title="project", description="project name")
    projectrun: str = Field(title="projectrun", description="project run name")
    model: str = Field(title="model", description="model name")


class ModelRunContext(BaseModel):
    project: str = Field(title="project", description="project name")
    projectrun: str = Field(title="projectrun", description="project run name")
    model: str = Field(title="model", description="model name")
    modelrun: str = Field(title="modelrun", description="model run name")


# Machine storage
class ProjectRefContext(BaseModel):
    project: PydanticObjectId = Field(title="project", description="project _id")


class ProjectRunRefContext(BaseModel):
    project: PydanticObjectId = Field(title="project", description="project _id")
    projectrun: PydanticObjectId = Field(
        title="projectrun",
        description="project run _id",
    )


class ModelRefContext(BaseModel):
    project: PydanticObjectId = Field(title="project", description="project name")
    projectrun: PydanticObjectId = Field(
        title="projectrun",
        description="project run _id",
    )
    model: PydanticObjectId = Field(title="model", description="model _id")


class ModelRunRefContext(BaseModel):
    project: PydanticObjectId = Field(title="project", description="project _id")
    projectrun: PydanticObjectId = Field(
        title="projectrun",
        description="project run _id",
    )
    model: PydanticObjectId = Field(title="model", description="model _id")
    modelrun: PydanticObjectId = Field(title="modelrun", description="model run _id")

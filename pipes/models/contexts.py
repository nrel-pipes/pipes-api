from beanie import PydanticObjectId
from pydantic import Field, BaseModel

from pipes.models.schemas import ModelDocument, ModelRunDocument
from pipes.projects.schemas import ProjectDocument, ProjectRunDocument
from pipes.users.schemas import UserDocument


# Input context
class ModelTextContext(BaseModel):
    project: str = Field(
        title="project",
        description="project name",
    )
    projectrun: str = Field(
        title="projectrun",
        description="project run name",
    )
    model: str = Field(
        title="model",
        description="model name",
    )


class ModelRunTextContext(BaseModel):
    user: UserDocument = Field(
        title="user",
        description="the user document",
    )
    project: str = Field(
        title="project",
        description="project name",
    )
    projectrun: str = Field(
        title="projectrun",
        description="project run str",
    )
    model: str = Field(
        title="model",
        description="model str",
    )
    modelrun: str = Field(
        title="modelrun",
        description="model run str",
    )


# Runtime context
class ModelDocumentContext(BaseModel):
    project: ProjectDocument = Field(
        title="project",
        description="project document",
    )
    projectrun: ProjectRunDocument = Field(
        title="projectrun",
        description="project run document",
    )
    model: ModelDocument = Field(
        title="model",
        description="model document",
    )


class ModelRunDocumentContext(BaseModel):
    project: ProjectDocument = Field(
        title="project",
        description="project document",
    )
    projectrun: ProjectRunDocument = Field(
        title="projectrun",
        description="project run document",
    )
    model: ModelDocument = Field(
        title="model",
        description="model document",
    )
    modelrun: ModelRunDocument = Field(
        title="modelrun",
        description="model run document",
    )


# Storage context
class ModelObjectContext(BaseModel):
    project: PydanticObjectId = Field(
        title="project",
        description="project id",
    )
    projectrun: PydanticObjectId = Field(
        title="projectrun",
        description="project run id",
    )
    model: str = Field(title="model", description="model id")


class ModelRunObjectContext(BaseModel):
    project: PydanticObjectId = Field(
        title="project",
        description="project id",
    )
    projectrun: PydanticObjectId = Field(
        title="projectrun",
        description="project run id",
    )
    model: PydanticObjectId = Field(title="model", description="model id")
    modelrun: PydanticObjectId = Field(
        title="modelrun",
        description="model run id",
    )

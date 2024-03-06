from beanie import PydanticObjectId
from pydantic import Field, BaseModel

from pipes.projects.schemas import ProjectDocument, ProjectRunDocument


# Input context
class ProjectTextContext(BaseModel):
    project: str = Field(
        title="project",
        description="project name",
    )


class ProjectRunTextContext(BaseModel):
    project: str = Field(
        title="project",
        description="project name",
    )
    projectrun: ProjectRunDocument = Field(
        title="projectrun",
        description="project run name",
    )


# Runtime context
class ProjectDocumentContext(BaseModel):
    project: ProjectDocument = Field(
        title="project",
        description="project document",
    )


class ProjectRunDocumentContext(BaseModel):
    project: ProjectDocument = Field(
        title="project",
        description="project document",
    )
    projectrun: ProjectRunDocument = Field(
        title="projectrun",
        description="project run document",
    )


# Storage context
class ProjectObjectContext(BaseModel):
    project: PydanticObjectId = Field(
        title="project",
        description="project object id",
    )


class ProjectRunObjectContext(BaseModel):
    project: PydanticObjectId = Field(title="project", description="project name")
    projectrun: PydanticObjectId = Field(
        title="projectrun",
        description="project run object id",
    )

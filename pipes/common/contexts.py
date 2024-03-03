from pydantic import BaseModel, Field


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

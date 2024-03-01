from pydantic import BaseModel, Field


class DataFoundrySchema(BaseModel):
    """DataFoundry location schema"""

    project: str = Field(
        title="project",
        description="Project name on DataFoundry",
    )
    folder: str = Field(
        title="folder",
        default="",
        description="The folder under DataFoundry project",
    )
    files: list[str] = Field(
        title="files",
        default=[],
        description="The files under DataFoundry project",
    )
    links: list[str] = Field(
        title="links",
        default=[],
        description="The links under DataFoundry project",
    )
    description: str = Field(
        title="description",
        default="",
        description="Description about this dataset on DataFoundry",
    )

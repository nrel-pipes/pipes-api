from uuid import UUID

from pydantic import BaseModel, Field


class ESIFRepoAPI(BaseModel):
    """ESIF Repo API Schema"""

    system: str = Field(
        title="system",
        default="ESIFRepoAPI",
        description="Data system of the location",
    )
    url: str = Field(
        title="api",
        default="https://esif.hpc.nrel.gov/esif/api/repo/files",
        description="The ESIF Repo API endpoint",
    )
    project: UUID | None = Field(
        title="project",
        default=None,
        description="The project uuid in ESIF Repo",
    )
    dataset: UUID | None = Field(
        title="dataset",
        default=None,
        description="The dataset uuid in ESIF Repo",
    )
    keyword: str = Field(
        title="keyword",
        default="",
        example="csv",
        description="Keyword (case insensitive) within filename or description.",
    )
    tag: list[str] = Field(
        title="tag",
        default=[],
        description="List of assigned tag names",
    )
    classification: list[UUID] = Field(
        title="classification",
        default=[],
        description="list of assigned classification IDs",
    )
    ids: list[UUID] = Field(
        title="ids",
        default=[],
        description="Specific list of IDs to retrieve",
    )
    description: str = Field(
        title="description",
        default="",
        description="Description of this location",
    )

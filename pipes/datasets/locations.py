from __future__ import annotations

from uuid import UUID
from pydantic import BaseModel, Field


class AmazonS3Schema(BaseModel):
    """Amazon S3 Location Schema"""

    system: str = Field(
        title="system",
        default="AmazonS3",
        description="Data system of the location",
    )
    bucket: str = Field(
        title="bucket",
        description="AWS bucket name",
    )
    keys: list[str] = Field(
        title="keys",
        default=[],
        description="List of keys to retrieve",
    )
    description: str = Field(
        title="description",
        default="",
        description="Description of this location",
    )


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


class HPCStorage(BaseModel):
    """NREL HPC Storage Schema"""

    path: str = Field(
        title="path",
        description="The directory or file path on HPC storage.",
    )
    description: str | None = Field(
        title="description",
        default="",
        description="Description about this data path",
    )

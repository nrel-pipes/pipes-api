from __future__ import annotations

from datetime import datetime

from beanie import Document
from pydantic import BaseModel, Field

from pipes.common.schemas import SourceCode, VersionStatus
from pipes.users.schemas import UserCreate


class DatasetCreate(BaseModel):
    """The expected dataset output from model run"""

    name: str = Field(
        title="name",
        description="A short name",
    )
    display_name: str | None = Field(
        title="display_name",
        default=None,
        description="The dataset display name",
    )
    description: str = Field(
        title="description",
        description="The description of the scheduled dataset",
        default="",
    )


class DatasetSchedule(DatasetCreate):
    scheduled_checkin: datetime | None = Field(
        title="scheduled_checkin",
        default=None,
        description="Scheduled checkin date in YYYY-MM-DD format",
    )


class TemporalInfo(BaseModel):
    """Dataset temporal information"""

    extent: str | None = Field(
        title="extent",
        default=None,
        description="The temporal extent of the dataset",
    )
    fidelity: str | None = Field(
        title="fidelity",
        default=None,
        description="The fidelity of the dataset in time",
    )
    other: dict = Field(
        title="other",
        default={},
        description="other info about temporal characteristics of data",
    )


class SpatialInfo(BaseModel):
    """Dataset spatial information"""

    extent: str | None = Field(
        title="extent",
        description="The spatial extent of the dataset",
    )
    fidelity: str | None = Field(
        title="fidelity",
        description="The fidelity of the dataset in space",
    )
    other: dict = Field(
        title="other",
        default={},
        description="other info about spatial characteristics of data",
    )


class DatasetCheckin(DatasetSchedule):
    """Dataset Checkin Schema"""

    checkin_date: datetime = Field(
        title="checkin_date",
        description="Scheduled checkin date in YYYY-MM-DD format",
    )
    version: str = Field(
        title="version",
        description="Dataset version",
    )
    hash_value: str = Field(
        title="hash_value",
        default="",
        description="The hash value of this dataset used for integrity check.",
    )
    version_status: VersionStatus = Field(
        title="version_status",
        description="Dataset version status",
    )
    previous_version: str | None = Field(
        title="name of previous version of dataset path",
        default=None,
        description="Previous version of this dataset",
    )
    data_format: str | None = Field(
        title="data_format",
        default=None,
        description="data format, or a list of formats separated by commas",
    )
    schema_info: str | None = Field(
        title="schema_info",
        default="",
        description="The schema description of the dataset",
    )
    location: dict = Field(  # NOTE: validate based on specific system.
        title="location",
        description="The dataset location on data system",
    )
    registration_author: UserCreate = Field(
        title="registration_author",
        description="The person who registered this dataset",
    )
    weather_years: list[int] = Field(
        title="weather_years",
        default=[],
        description="The weather year(s) of the dataset",
    )
    model_years: list[int] = Field(
        title="model_years",
        default=[],
        description="The model year(s) of the dataset",
    )
    units: list[str] = Field(
        title="units",
        default="",
        description="The units of the dataset",
    )
    temporal_info: TemporalInfo = Field(
        title="temporal_info",
        default={},
        description="The temportal metadata of the dataset",
    )
    spatial_info: SpatialInfo = Field(
        title="spatial_info",
        default={},
        description="The spatial metadata of the dataset",
    )
    scenarios: list[str] = Field(
        title="scenarios",
        description="The list of scenario names the dataset relates to",
    )
    sensitivities: list[str] = Field(
        title="sensitivities",
        default=[],
        description="The sensitivities of the dataset",
    )
    source_code: SourceCode = Field(
        title="source_code",
        description="The source code that produces the dataset",
    )
    relevant_links: list[str] = Field(
        title="relevant_links",
        default=[],
        description="Relevant links to this dataset",
    )
    description: str = Field(
        title="description",
        default="",
        description="Description about this dataset",
    )
    comments: str = Field(
        title="comments",
        default="",
        description="Registration comments about this dataset",
    )
    resource_url: str = Field(
        title="resource_url",
        default="",
        description="The resource URL for this dataset",
    )
    # input_datasets: list[str] = Field(
    #     title="input_datasets",
    #     default=[],
    #     description="List of dataset names",
    # )
    other: dict = Field(
        title="other",
        default={},
        description="other metadata info about the dataset",
    )


class DatasetRead(DatasetCreate):
    pass


class DatasetDocument(DatasetRead, Document):
    pass

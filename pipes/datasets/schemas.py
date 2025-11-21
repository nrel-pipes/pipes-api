from __future__ import annotations

from datetime import datetime

import pymongo
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, ConfigDict, Field
from pymongo import IndexModel

from pipes.common.schemas import SourceCode, VersionStatus
from pipes.modelruns.contexts import ModelRunSimpleContext, ModelRunObjectContext
from pipes.users.schemas import UserCreate, UserRead


class DatasetSchedule(BaseModel):
    """The expected dataset output from model run.

    Attributes:
        name: A short dataset name.
        display_name: The dataset display name.
        description: The description of the scheduled dataset.
        scheduled_checkin: Scheduled checkin date in YYYY-MM-DD format.
    """

    name: str = Field(
        title="name",
        description="A short dataset name",
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
    scheduled_checkin: datetime | None = Field(
        title="scheduled_checkin",
        default=None,
        description="Scheduled checkin date in YYYY-MM-DD format",
    )


class TemporalInfo(BaseModel):
    """Dataset temporal information.

    Attributes:
        extent: The temporal extent of the dataset.
        fidelity: The fidelity of the dataset in time.
        other: Other info about temporal characteristics of data.
    """

    extent: str = Field(
        title="extent",
        default="",
        description="The temporal extent of the dataset",
    )
    fidelity: str = Field(
        title="fidelity",
        default="",
        description="The fidelity of the dataset in time",
    )
    other: dict = Field(
        title="other",
        default={},
        description="other info about temporal characteristics of data",
    )


class SpatialInfo(BaseModel):
    """Dataset spatial information.

    Attributes:
        extent: The spatial extent of the dataset.
        fidelity: The fidelity of the dataset in space.
        other: Other info about spatial characteristics of data.
    """

    extent: str = Field(
        title="extent",
        default="",
        description="The spatial extent of the dataset",
    )
    fidelity: str = Field(
        title="fidelity",
        default="",
        description="The fidelity of the dataset in space",
    )
    other: dict = Field(
        title="other",
        default={},
        description="other info about spatial characteristics of data",
    )


class DatasetCreate(BaseModel):
    """Dataset Checkin Schema.

    Attributes:
        name: A short name.
        display_name: The dataset display name.
        description: The description of the scheduled dataset.
        version: Dataset version.
        hash_value: The hash value of this dataset used for integrity check.
        version_status: Dataset version status.
        previous_version: Previous version of this dataset.
        data_format: Data format, or a list of formats separated by commas.
        schema_info: The schema description of the dataset.
        location: The dataset location on data system.
        registration_author: The person who registered this dataset.
        weather_years: The weather year(s) of the dataset.
        model_years: The model year(s) of the dataset.
        units: The units of the dataset.
        temporal_info: The temportal metadata of the dataset.
        spatial_info: The spatial metadata of the dataset.
        scenarios: The list of scenario names the dataset relates to.
        sensitivities: The sensitivities of the dataset.
        source_code: The source code that produces the dataset.
        relevant_links: Relevant links to this dataset.
        comments: Registration comments about this dataset.
        resource_url: The resource URL for this dataset.
        other: Other metadata info about the dataset.
    """

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
        default=[],
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
    model_config = ConfigDict(protected_namespaces=())


class DatasetRead(DatasetCreate):
    """Dataset read schema.

    Attributes:
        name: A short name.
        display_name: The dataset display name.
        description: The description of the scheduled dataset.
        version: Dataset version.
        hash_value: The hash value of this dataset used for integrity check.
        version_status: Dataset version status.
        previous_version: Previous version of this dataset.
        data_format: Data format, or a list of formats separated by commas.
        schema_info: The schema description of the dataset.
        location: The dataset location on data system.
        registration_author: Registration author of this dataset.
        weather_years: The weather year(s) of the dataset.
        model_years: The model year(s) of the dataset.
        units: The units of the dataset.
        temporal_info: The temportal metadata of the dataset.
        spatial_info: The spatial metadata of the dataset.
        scenarios: The list of scenario names the dataset relates to.
        sensitivities: The sensitivities of the dataset.
        source_code: The source code that produces the dataset.
        relevant_links: Relevant links to this dataset.
        comments: Registration comments about this dataset.
        resource_url: The resource URL for this dataset.
        other: Other metadata info about the dataset.
        context: Model run context.
    """

    context: ModelRunSimpleContext = Field(
        title="context",
        description="model run context",
    )
    registration_author: UserRead = Field(
        title="registration_author",
        description="registration author of this dataset",
    )


class DatasetDocument(DatasetRead, Document):
    """Dataset document.

    Attributes:
        name: A short name.
        display_name: The dataset display name.
        description: The description of the scheduled dataset.
        version: Dataset version.
        hash_value: The hash value of this dataset used for integrity check.
        version_status: Dataset version status.
        previous_version: Previous version of this dataset.
        data_format: Data format, or a list of formats separated by commas.
        schema_info: The schema description of the dataset.
        location: The dataset location on data system.
        registration_author: Registration author reference.
        weather_years: The weather year(s) of the dataset.
        model_years: The model year(s) of the dataset.
        units: The units of the dataset.
        temporal_info: The temportal metadata of the dataset.
        spatial_info: The spatial metadata of the dataset.
        scenarios: The list of scenario names the dataset relates to.
        sensitivities: The sensitivities of the dataset.
        source_code: The source code that produces the dataset.
        relevant_links: Relevant links to this dataset.
        comments: Registration comments about this dataset.
        resource_url: The resource URL for this dataset.
        other: Other metadata info about the dataset.
        context: Model run context reference.
        created_at: Project creation time.
        created_by: User who created the project.
        last_modified: Last modification datetime.
        modified_by: User who modified the project.
    """

    context: ModelRunObjectContext = Field(
        title="context",
        description="model run context reference",
    )
    registration_author: PydanticObjectId = Field(
        title="registration_author",
        description="registration author reference",
    )

    # document information
    created_at: datetime = Field(
        title="created_at",
        description="project creation time",
    )
    created_by: PydanticObjectId = Field(
        title="created_by",
        description="user who created the project",
    )
    last_modified: datetime = Field(
        title="last_modified",
        default=datetime.now(),
        description="last modification datetime",
    )
    modified_by: PydanticObjectId = Field(
        title="modified_by",
        description="user who modified the project",
    )

    class Settings:
        name = "datasets"
        indexes = [
            IndexModel(
                [
                    ("context", pymongo.ASCENDING),
                    ("name", pymongo.ASCENDING),
                ],
                unique=True,
            ),
        ]

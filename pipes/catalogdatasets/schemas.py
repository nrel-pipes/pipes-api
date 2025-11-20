from __future__ import annotations

from datetime import datetime

import pymongo
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, ConfigDict, Field, EmailStr
from pymongo import IndexModel

from pipes.common.schemas import SourceCode
from pipes.users.schemas import UserRead


class TemporalInfo(BaseModel):
    """Dataset temporal information.

    Attributes:
        extent: The temporal extent of the dataset.
        fidelity: The fidelity of the dataset in time.
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


class SpatialInfo(BaseModel):
    """Dataset spatial information.

    Attributes:
        extent: The spatial extent of the dataset.
        fidelity: The fidelity of the dataset in space.
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


class DatasetLocation(BaseModel):
    """Dataset storage location information.

    Attributes:
        system_type: The data system of the dataset location.
        storage_path: The path to the dataset within the data system.
        access_info: The access information for the dataset location.
        extra_note: Any extra note about the dataset location.
    """

    system_type: str = Field(
        title="system_type",
        description="The data system of the dataset location",
    )
    storage_path: str = Field(
        title="storage_path",
        description="The path to the dataset within the data system",
    )
    access_info: str = Field(
        title="access_info",
        default=str,
        description="The access information for the dataset location",
    )
    extra_note: str = Field(
        title="extra_note",
        default="",
        description="Any extra note about the dataset location",
    )


class CatalogDatasetCreate(BaseModel):
    """Dataset Checkin Schema.

    Attributes:
        name: A short name.
        display_name: The dataset display name.
        description: The description of the scheduled dataset.
        version: Dataset version.
        previous_version: Previous version of this dataset.
        hash_value: The hash value of this dataset used for integrity check.
        data_format: Data format, or a list of formats separated by commas.
        schema_info: The schema description of the dataset.
        location: The dataset location on data system.
        weather_years: The weather year(s) of the dataset.
        model_years: The model year(s) of the dataset.
        units: The units of the dataset.
        temporal_info: The temporal metadata of the dataset.
        spatial_info: The spatial metadata of the dataset.
        scenarios: The list of scenario names the dataset relates to.
        sensitivities: The sensitivities of the dataset.
        source_code: The source code that produces the dataset.
        relevant_links: Relevant links to this dataset.
        resource_url: The resource URL for this dataset.
        access_group: A group of users that has access to this model.
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
        default="",
        description="The description of the scheduled dataset",
    )
    version: str = Field(
        title="version",
        description="Dataset version",
    )
    previous_version: str | None = Field(
        title="name of previous version of dataset path",
        default=None,
        description="Previous version of this dataset",
    )
    hash_value: str = Field(
        title="hash_value",
        default="",
        description="The hash value of this dataset used for integrity check.",
    )
    data_format: str | None = Field(
        title="data_format",
        default=None,
        description="data format, or a list of formats separated by commas",
    )
    schema_info: dict = Field(
        title="schema_info",
        default={},
        description="The schema description of the dataset",
    )
    location: DatasetLocation = Field(
        title="location",
        description="The dataset location on data system",
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
        default_factory=TemporalInfo,
        description="The temporal metadata of the dataset",
    )
    spatial_info: SpatialInfo = Field(
        title="spatial_info",
        default_factory=SpatialInfo,
        description="The spatial metadata of the dataset",
    )
    scenarios: list[str] = Field(
        title="scenarios",
        default=[],
        description="The list of scenario names the dataset relates to",
    )
    sensitivities: list[str] = Field(
        title="sensitivities",
        default=[],
        description="The sensitivities of the dataset",
    )
    source_code: SourceCode = Field(
        title="source_code",
        default_factory=SourceCode,
        description="The source code that produces the dataset",
    )
    relevant_links: list[str] = Field(
        title="relevant_links",
        default=[],
        description="Relevant links to this dataset",
    )
    resource_url: str = Field(
        title="resource_url",
        default="",
        description="The resource URL for this dataset",
    )
    access_group: list[EmailStr] = Field(
        title="access_group",
        default=[],
        description="A group of users that has access to this model",
    )
    model_config = ConfigDict(protected_namespaces=())


class CatalogDatasetUpdate(CatalogDatasetCreate):
    """Catalog Dataset Update Schema.

    Attributes:
        name: A short name.
        display_name: The dataset display name.
        description: The description of the scheduled dataset.
        version: Dataset version.
        previous_version: Previous version of this dataset.
        hash_value: The hash value of this dataset used for integrity check.
        data_format: Data format, or a list of formats separated by commas.
        schema_info: The schema description of the dataset.
        location: The dataset location on data system.
        weather_years: The weather year(s) of the dataset.
        model_years: The model year(s) of the dataset.
        units: The units of the dataset.
        temporal_info: The temporal metadata of the dataset.
        spatial_info: The spatial metadata of the dataset.
        scenarios: The list of scenario names the dataset relates to.
        sensitivities: The sensitivities of the dataset.
        source_code: The source code that produces the dataset.
        relevant_links: Relevant links to this dataset.
        resource_url: The resource URL for this dataset.
        access_group: A group of users that has access to this model.
    """

    pass


class CatalogDatasetRead(CatalogDatasetCreate):
    """Dataset read schema.

    Attributes:
        name: A short name.
        display_name: The dataset display name.
        description: The description of the scheduled dataset.
        version: Dataset version.
        previous_version: Previous version of this dataset.
        hash_value: The hash value of this dataset used for integrity check.
        data_format: Data format, or a list of formats separated by commas.
        schema_info: The schema description of the dataset.
        location: The dataset location on data system.
        weather_years: The weather year(s) of the dataset.
        model_years: The model year(s) of the dataset.
        units: The units of the dataset.
        temporal_info: The temporal metadata of the dataset.
        spatial_info: The spatial metadata of the dataset.
        scenarios: The list of scenario names the dataset relates to.
        sensitivities: The sensitivities of the dataset.
        source_code: The source code that produces the dataset.
        relevant_links: Relevant links to this dataset.
        resource_url: The resource URL for this dataset.
        access_group: A group of users that has access to this model.
        created_at: Catalog model creation time.
        created_by: User who created the model in catalog.
    """

    created_at: datetime = Field(
        title="created_at",
        description="catalog model creation time",
    )
    created_by: UserRead = Field(
        title="created_by",
        description="user who created the model in catalog",
    )


class CatalogDatasetDocument(CatalogDatasetRead, Document):
    """Catalog dataset document.

    Attributes:
        name: A short name.
        display_name: The dataset display name.
        description: The description of the scheduled dataset.
        version: Dataset version.
        previous_version: Previous version of this dataset.
        hash_value: The hash value of this dataset used for integrity check.
        data_format: Data format, or a list of formats separated by commas.
        schema_info: The schema description of the dataset.
        location: The dataset location on data system.
        weather_years: The weather year(s) of the dataset.
        model_years: The model year(s) of the dataset.
        units: The units of the dataset.
        temporal_info: The temporal metadata of the dataset.
        spatial_info: The spatial metadata of the dataset.
        scenarios: The list of scenario names the dataset relates to.
        sensitivities: The sensitivities of the dataset.
        source_code: The source code that produces the dataset.
        relevant_links: Relevant links to this dataset.
        resource_url: The resource URL for this dataset.
        access_group: A group of users that has access to this model.
        created_at: Project creation time.
        created_by: User who created the project.
        last_modified: Last modification datetime.
        modified_by: User who modified the project.
    """

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
    access_group: list[PydanticObjectId] = Field(
        title="access_group",
        default=[],
        description="A group of users that has access to this model",
    )

    class Settings:
        name = "catalogdatasets"
        indexes = [
            IndexModel(
                [
                    ("name", pymongo.ASCENDING),
                ],
                unique=True,
            ),
        ]

from __future__ import annotations

from datetime import datetime
from pydantic import EmailStr

import pymongo
from pymongo import IndexModel
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict

from pipes.users.schemas import UserRead, UserCreate


class ModelingTeam(BaseModel):
    """Modeling team information.

    Attributes:
        name: Name of the modeling team.
        members: List of team members.
    """

    name: str = Field(
        title="name",
        description="Name of the modeling team",
    )
    members: list[UserCreate] = Field(
        title="members",
        description="List of team members",
    )

from datetime import datetime
from pydantic import BaseModel,model_validator, Field
from typing import Union, Optional, List, Dict

class SpatialDimensions(BaseModel):
    extent: str = Field(
        title="extent",
        description="The spatial extent of the tool/dataset, can be general (e.g. regional, continental, utility service area, ect.) or specific (e.g. CONUS, ERCOT, ect.)",
    )
    fidelity: str = Field(
        title="fidelity",
        description="The spatial resolution/fidelity of the tool/dataset. Can be general (zonal, nodal, high voltage, distribution voltage, ect.) or specific (e.g. balancing areas, states, specific voltages).",
    )
    scope: Optional[List[str]] = Field(
        title="scope",
        default=None,
        description="The spatial scope of the tool/dataset (Generation, Transmission, Distribution, Device or Asset Level, Other).",
    )
    misc: Optional[Dict[str,str]] = Field(
        title="misc",
        default=None,
        description="Add additional spatial dimensions context.",
    )

class TemporalDimensions(BaseModel):
    extent: str = Field(
        title="extent",
        description="The temporal extent of the tool.",
    )
    resolution: str = Field(
        title="resolution",
        description="Temporal resolution of the tool. Can be a pythonic timestep string.",
    )
    years: Optional[List[int]] = Field(
        title="years",
        default=None,
        description="Tool years.",
    )
    weather_years: Optional[List[int]] = Field(
        title="weather_years",
        default=None,
        description="Weather years used in tool.",
    )
    misc: Optional[Dict[str,str]] = Field(
        title="misc",
        default=None,
        description="Add additional temporal dimensions context.",
    )

class DataSchemaSchema(BaseModel):
    format: str = Field(
        title="format",
        description="Format of the dataset.",
    )
    fields: List[str] = Field(
        title="fields",
        description="Fields/Columns in the dataset.",
    )
    misc: Optional[Dict[str,str]] = Field(
        title="misc",
        default=None,
        description="Add additional dataset schema context.",
    )

class GeneralDataDescriptionSchema(BaseModel):
    # Required
    name: str = Field(
        title="name",
        description="Name of the dataset.",
    )
    description: str = Field(
        title="description",
        description="Description of the dataset.",
    )
    # Required for General Data Description type
    priority: str = Field(
        title="priority",
        description="Priority of the dataset (Minimum Viable Dataset, Strongly Recommended, Optional).",
    )
    private: Optional[bool] = Field(
        title="private",
        default=False,
        description="Is the dataset private?",
    )
    NDA: Optional[bool] = Field(
        title="NDA",
        default=False,
        description="Does the dataset require an NDA to access?",
    )
    category: str = Field(
        title="category",
        description="Category of the dataset.",
    )
    provider: str = Field(
        title="provider",
        description="Provider of the dataset (e.g. Utility, Awardee, Client, Public Source, Other).",
    )
    # Optional for General Data Descriptions
    schema_info: Optional[DataSchemaSchema] = Field(
        title="schema_info",
        default=None,
        description="Information on data schema.",
    )
    temporal_dimensions: Optional[TemporalDimensions] = Field(
        title="temporal_dimensions",
        default=None,
        description="Temporal characteristics of the dataset.",
    )
    spatial_dimensions: Optional[SpatialDimensions] = Field(
        title="spatial_dimensions",
        default=None,
        description="Spatial characteristics of the dataset.",
    )
    years: Optional[List[int]] = Field(
        title="years",
        default=None,
        description="Years included in the dataset.",
    )
    weather_years: Optional[List[int]] = Field(
        title="weather_years",
        default=None,
        description="Weather years included in the dataset.",
    )
    tags: Optional[List[str]] = Field(
        title="tags",
        default=None,
        description="Tags associated with the dataset.",
    )
    scenarios: Optional[List[str]] = Field(
        title="scenarios",
        default=None,
        description="Scenarios in the dataset.",
    )
    units: Optional[str] = Field(
        title="units",
        default=None,
        description="Units of measurement in the dataset.",
    )

class DatasetSchema(BaseModel):
    # The dataset requirement can be a specific published dataset (2024 ATB) or a general data requirement (Load Forecasts)
    # Required
    name: str = Field(
        title="name",
        description="Name of the dataset.",
    )
    description: str = Field(
        title="description",
        description="Description of the dataset.",
    )
    # Required for Published Datasets
    author: str = Field(
        title="author",
        description="Author/owner of the dataset.",
    )
    date: datetime = Field(
        title="date",
        description="Publish date of the dataset.",
    )
    version: str = Field(
        title="version",
        description="Version of the dataset.",
    )
    location: str = Field(
        title="location",
        description="Link or location of the dataset.",
    )
    schema_info: DataSchemaSchema = Field(
        title="schema_info",
        description="Information on data schema.",
    )
    temporal_dimensions: TemporalDimensions = Field(
        title="temporal_dimensions",
        description="Temporal characteristics of the dataset.",
    )
    spatial_dimensions: SpatialDimensions = Field(
        title="spatial_dimensions",
        description="Spatial characteristics of the dataset.",
    )
    # Optional
    years: Optional[List[int]] = Field(
        title="years",
        default=None,
        description="Years included in the dataset.",
    )
    weather_years: Optional[List[int]] = Field(
        title="weather_years",
        default=None,
        description="Weather years included in the dataset.",
    )
    tags: Optional[List[str]] = Field(
        title="tags",
        default=None,
        description="Tags associated with the dataset.",
    )
    scenarios: Optional[List[str]] = Field(
        title="scenarios",
        default=None,
        description="Scenarios in the dataset.",
    )
    units: Optional[str] = Field(
        title="units",
        default=None,
        description="Units of measurement in the dataset.",
    )
    priority: Optional[str] = Field(
        title="priority",
        default=None,
        description="Priority of the dataset (Minimum Viable Dataset, Strongly Recommended, Optional).",
    )
    private: Optional[bool] = Field(
        title="private",
        default=None,
        description="Is the dataset private?",
    )
    NDA: Optional[bool] = Field(
        title="NDA",
        default=None,
        description="Does the dataset require an NDA to access?",
    )
    category: Optional[str] = Field(
        title="category",
        default=None,
        description="Category of the dataset.",
    )
    provider: Optional[str] = Field(
        title="provider",
        default=None,
        description="Provider of the dataset (e.g. Utility, Awardee, Client, Public Source, Other).",
    )

    '''@model_validator(mode="after")
    def check_type_requirements(self):
        if self.Type == "Published Dataset":
            required_fields = ['Author', 'Date', 'Version', 'Location', 'Schema', 'Temporal_Dimensions', 'Spatial_Dimensions']
            for field in required_fields:
                if getattr(self, field) is None:
                    raise ValueError(f"{field} is required for Published Dataset type")
        elif self.Type == "General Data Description":
            required_fields = ['Category','Priority']
            for field in required_fields:
                if getattr(self, field) is None:
                    raise ValueError(f"{field} is required for General Data Description type")
        else:
            raise ValueError("Type must be either 'Published Dataset' or 'General Data Description'")
        return self'''

class Tool_Maturity(BaseModel):
    # Required
    software_license: bool = Field(
        title="software_license",
        description="Is there a software license?",
    )
    publication_history: bool = Field(
        title="publication_history",
        description="Are there peer-reviewed publications describing innovation and disemination of grid science and technology that this tool has supported?",
    )
    external_validation_documented: bool = Field(
        title="external_validation_documented",
        description="Is there external validation via a publication, e.g., via comparison to results from other methodologies, real-world events, or replicated results from external users?",
    )
    application: bool = Field(
        title="application",
        description="Has this tool resulted in considerations used in deployment decisions, e.g., the analysis informed TA recipient decisions?",
    )
    external_validation_via_usage: bool = Field(
        title="external_validation_via_usage",
        description="Is there external validation via usage, i.e., have non-lab entities adopted this tool?",
    )
    input_output_interoperability: bool = Field(
        title="input_output_interoperability",
        description="Is there an API for scripted coordination with other tools?",
    )
    data_accessability_public: bool = Field(
        title="data_accessability_public",
        description="Can a study be performed using only publicly available data?",
    )
    data_accessability_proprietary: bool = Field(
        title="data_accessability_proprietary",
        description="Can a study be performed with data that a utility has access to?",
    )
    secure_for_sensitive_data_handling: bool = Field(
        title="secure_for_sensitive_data_handling",
        description="Can the tool be run in a secure environment with sensitive data?",
    )
    secure_independent_usage: bool = Field(
        title="secure_independent_usage",
        description="Can a user run the tool independently in a commonly accessible, secure environment (e.g. locally)? N/A if the tool is not intended to be run by an external user.",
    )
    usability_via_GUI: bool = Field(
        title="usability_via_GUI",
        description="Is there a GUI?",
    )
    usability_via_CLI: bool = Field(
        title="usability_via_CLI",
        description="Is there a CLI?",
    )
    accessible_for_external_users: bool = Field(
        title="accessible_for_external_users",
        description="Can this tool be transfered to an external user for independent use? N/A if the tool is not intended to be run by an external user.",
    )
    support_available: bool = Field(
        title="support_available",
        description="Is there a support team that can field requests and address bugs or concerns?",
    )
    workflow_integration_list: List[str] = Field(
        title="workflow_integration_list",
        description="List other tools this has been integrated with or used in tandem with.",
    )

class Teams(BaseModel):
    lab: str = Field(
        title="lab",
        description="National lab with a capability of using the tool.",
    )
    role: str = Field(
        title="role",
        description="Role of the lab team for the tool (developer, maintainer, user).",
    )
    contact: str = Field(
        title="contact",
        description="Contact email.",
    )

class Expected_Scenario(BaseModel):
    name: str = Field(
        title="name",
        description="Scenario name.",
    )
    description: str = Field(
        title="description",
        description="Scenario description.",
    )
    # Optional
    years: Optional[str] = Field(
        title="years",
        default=None,
        description="Scenario years.",
    )

class EnvironmentRequirement(BaseModel):
    platform: str = Field(
        title="platform",
        description="Platforms used/required to run tool (HPC, cloud, local, specific hardware, ect.).",
    )
    required_software: Optional[List[str]] = Field(
        title="required_software",
        default=None,
        description="Specific software dependencies/requirements.",
    )
    licenses: Optional[List[str]] = Field(
        title="licenses",
        default=None,
        description="Commercial software licenses needed to use the tool.",
    )
    resources: Optional[str] = Field(
        title="resources",
        default=None,
        description="Memory/CPU/GPU resource requirements.",
    )
    misc: Optional[str] = Field(
        title="misc",
        default=None,
        description="Add additional environment requirement context.",
    )

class Requirement(BaseModel):
    general_data_description: Optional[GeneralDataDescriptionSchema] = Field(
        title="general_data_description",
        default=None,
        description="The general data description requirement describes known data requirements for a tool that may need to be sourced/generated (e.g. Load Forecast Data, System Asset Data).",
    )  # 
    dataset: Optional[DatasetSchema] = Field(
        title="dataset",
        default=None,
        description="The dataset requirement is a specific published dataset with a location and author (e.g. 2024 ATB).",
    )
    spatial: Optional[SpatialDimensions] = Field(
        title="spatial",
        default=None,
        description="Spatial requirement block.",
    )
    temporal: Optional[TemporalDimensions] = Field(
        title="temporal",
        default=None,
        description="Temporal requirement block.",
    )
    environment: Optional[EnvironmentRequirement] = Field(
        title="environment",
        default=None,
        description="Environment requirement block.",
    )
    misc: Optional[Dict[str, str]] = Field(
        title="misc",
        default=None,
        description="Miscellaneous key-value requirements block.",
    )

class Output(BaseModel):
    general_data_description: Optional[GeneralDataDescriptionSchema] = Field(
        title="general_data_description",
        default=None,
        description="The general data description output describes known data produced by the tool (e.g. Load Forecast Data, System Asset Data).",
    )
    misc: Optional[Dict[str, str]] = Field(
        title="misc",
        default=None,
        description="Miscellaneous key-value output block.",
    )

class ConfigSchema(BaseModel):
    # Optional
    model_modes: Optional[List[str]] = Field(
        title="model_modes",
        default=None,
        description="Different modes of the tool.",
    )
    model_options: Optional[Dict[str, str]] = Field(
        title="model_options",
        default=None,
        description="Major configuration options.",
    )
    technologies: Optional[List[str]] = Field(
        title="technologies",
        default=None,
        description="List of supported technologies.",
    )

class IFACCatalogModelCreate(BaseModel):
    # Required
    catalog_schema: str = Field(
        title="catalog_schema",
        description="Catalog specsheet schema version.",
    )
    name: str = Field(
        title="name",
        description="The identifier/short name/acronym of the Tool.",
    )
    display_name: str = Field(
        title="display_name",
        description="Full name of the tool.",
    )
    description: List[str] = Field(
        title="description",
        description="Tool description.",
    )
    type: str = Field(
        title="type",
        description="The type/category of the Tool.",
    )
    use_cases: List[str] = Field(
        title="use_cases",
        description="List of IFAC use cases the tool can be used for.",
    )
    # Optional
    source: Optional[str] = Field(
        title="source",
        default=None,
        description="Optional link to tool code base or other source.",
    )
    documentation: Optional[str] = Field(
        title="documentation",
        default=None,
        description="Optional link to documentation.",
    )
    training: Optional[str] = Field(
        title="training",
        default=None,
        description="Optional link to training materials.",
    )
    version: Optional[float] = Field(
        title="version",
        default=None,
        description="Optional reference to tool version.",
    )
    branch: Optional[str] = Field(
        title="branch",
        default=None,
        description="Optional reference to tool feature branch.",
    )
    tags: Optional[List[str]] = Field(
        title="tags",
        default=None,
        description="List of tags for the tool, pulled from the Tools Task 3 tag list.",
    )
    assumptions: Optional[List[str]] = Field(
        title="assumptions",
        default=None,
        description="Free-form list of assumptions the tool uses.",
    )
    features: Optional[List[str]] = Field(
        title="features",
        default=None,
        description="Free-form list of tool features.",
    )

    # Required
    # Required tool maturity information for different aspects of the tool’s maturity for use in IFAC TA scoping.
    maturity: Tool_Maturity = Field(
        title="maturity",
        description="Required tool maturity information for different aspects of the tool’s maturity for use in IFAC TA scoping.",
    )

    # Required
    # Team(s) that use/develop/maintain the tool across the national labs. For tools with multiple lab users or developers, add multiple entries to the Teams list.
    teams: List[Teams] = Field(
        title="teams",
        description="Team(s) that use/develop/maintain the tool across the national labs. For tools with multiple lab users or developers, add multiple entries to the Teams list.",
    )

    # Optional
    # Default/expected scenarios the tool runs
    expected_scenarios: Optional[List[Expected_Scenario]] = Field(
        title="expected_scenarios",
        description="Default/expected scenarios the tool runs.",
    )

    # Required
    # Tool requirements. There are 5 types of requirements, Dataset, Spatial, Temporal, Environment, and Misc, and the specsheet supports multiple requirements of each type as needed to document the full set of tool requirements.
    # The top level key in each element determines the requirement type and required fields. An example of each requirement type is shown below. 
    requirements: Dict[str, Requirement] = Field(
        title="requirements",
        description="Tool requirements. There are 5 types of requirements, Dataset, Spatial, Temporal, Environment, and Misc, and the specsheet supports multiple requirements of each type as needed to document the full set of tool requirements.\
              The top level key in each element determines the requirement type and required fields. An example of each requirement type is shown below.",
    )

    # Optional
    # Outputs of the tool, specifically output general data specifications in the form of Datasets.
    outputs: Optional[List[Output]] = Field(
        title="outputs",
        default=None,
        description="Outputs of the tool, specifically output general data specifications in the form of Datasets.",
    )

    # Optional
    # Major configuration options/switches for the tool and their values.
    config: Optional[ConfigSchema] = Field(
        title="config",
        default=None,
        description="Major configuration options/switches for the tool and their values.",
    )

    # PIPES Required Fields
    other: dict = Field(
        title="other",
        default={},
        description="other metadata info about the model in dictionary",
    )
    access_group: list[EmailStr] = Field(
        title="access_group",
        default=[],
        description="A group of users that has access to this model",
    )


    @field_validator("description", mode="before")
    @classmethod
    def validate_description(cls, value):
        if isinstance(value, str):
            return [value]
        return value


class IFACCatalogModelUpdate(IFACCatalogModelCreate):
    """Model update schema.

    Attributes:
        name: The model name.
        display_name: Display name for this model vertex.
        type: Type of model to use in graphic headers (e.g, 'Capacity Expansion').
        description: Description of the model.
        assumptions: List of model assumptions.
        requirements: Model specific requirements (if different from Project and Project-Run).
        expected_scenarios: List of expected model scenarios.
        modeling_team: Information about the modeling team.
        other: Other metadata info about the model in dictionary.
        access_group: A group of users that has access to this model.
    """

    pass


class IFACCatalogModelRead(IFACCatalogModelCreate):
    """Model read schema.

    Attributes:
        name: The model name.
        display_name: Display name for this model vertex.
        type: Type of model to use in graphic headers (e.g, 'Capacity Expansion').
        description: Description of the model.
        assumptions: List of model assumptions.
        requirements: Model specific requirements (if different from Project and Project-Run).
        expected_scenarios: List of expected model scenarios.
        modeling_team: Information about the modeling team.
        other: Other metadata info about the model in dictionary.
        access_group: A group of users' emails that has access to this model.
        created_at: Catalog model creation time.
        created_by: User who created the model in catalog.
    """

    access_group: list[EmailStr] = Field(
        title="access_group",
        default=[],
        description="A group of users' emails that has access to this model",
    )
    created_at: datetime = Field(
        title="created_at",
        description="catalog model creation time",
    )
    created_by: UserRead = Field(
        title="created_by",
        description="user who created the model in catalog",
    )


class IFACCatalogModelDocument(IFACCatalogModelCreate, Document):
    """Catalog model document.

    Attributes:
        name: The model name.
        display_name: Display name for this model vertex.
        type: Type of model to use in graphic headers (e.g, 'Capacity Expansion').
        description: Description of the model.
        assumptions: List of model assumptions.
        requirements: Model specific requirements (if different from Project and Project-Run).
        expected_scenarios: List of expected model scenarios.
        modeling_team: Information about the modeling team.
        other: Other metadata info about the model in dictionary.
        access_group: A group of users that has access to this model.
        created_at: Catalog model creation time.
        created_by: User who created the model in catalog.
        last_modified: Last modification datetime.
        modified_by: User who modified the project.
    """

    created_at: datetime = Field(
        title="created_at",
        description="catalog model creation time",
    )
    created_by: PydanticObjectId = Field(
        title="created_by",
        description="user who created the model in catalog",
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
        name = "catalogmodels_ifac"
        indexes = [
            IndexModel(
                [
                    ("name", pymongo.ASCENDING),
                ],
                unique=True,
            ),
        ]

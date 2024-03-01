from datetime import datetime

from pydantic import BaseModel, Field


class ActivityCreate(BaseModel):
    """Activity Creation Schema"""

    name: str = Field(
        title="name",
        description="Event name",
    )
    event_time: datetime = Field(
        title="event_time",
        description="the time of the event",
        default=datetime.now(),
    )
    event_type: str = Field(
        title="event_type",
        description="the category of event",
        default="",
    )
    affected_identifier: str = Field(
        title="affected_identifier",
        description="The ID of the affected entity",
        default="",
    )
    source_system: str = Field(
        title="source_system",
        description="The source system",
    )
    data: str = Field(
        title="data",
        description="Related data",
        default="",
    )


class EventCreate(BaseModel):
    """Event Schema"""

    name: str = Field(
        title="name",
        description="Event name",
    )
    affected_identifier: str = Field(
        title="affected_identifier",
        description="Primary affected entity's identifier",
    )
    event_time: datetime = Field(
        title="event_time",
        description="the time of the event",
        default=datetime.now(),
    )
    event_type: str = Field(
        title="event_type",
        description="the category of event",
        default="",
    )
    source_identitifer: str = Field(
        title="source_identitifer",
        description="The ID of the source",
        default="",
    )
    source_system: str = Field(
        title="source_system",
        description="The source system",
    )
    source_type: str = Field(
        title="source_type",
        description="Source type if available",
        default="",
    )
    relationships_project_id: str = Field(
        title="relationships_project_id",
        description="Related project ID",
        default="",
    )
    relationships_project: str = Field(
        title="relationships_project",
        description="Related project name",
        default="",
    )
    relationships_project_run_id: str = Field(
        title="relationships_project_run_id",
        description="Related project run ID",
        default="",
    )
    relationships_project_run: str = Field(
        title="relationships_project_run",
        description="Related project run name",
        default="",
    )
    relationships_model_id: str = Field(
        title="relationships_model_id",
        description="Related model ID",
        default="",
    )
    relationships_model: str = Field(
        title="relationships_model",
        description="Related model name",
        default="",
    )
    relationships_model_run_id: str = Field(
        title="relationships_model_run_id",
        description="Related model run ID",
        default="",
    )
    relationships_model_run: str = Field(
        title="relationships_model_run",
        description="Related model run name",
        default="",
    )
    relationships_qa_run_id: str = Field(
        title="relationships_qa_run_id",
        description="Related QA run ID",
        default="",
    )
    relationships_qa_run: str = Field(
        title="relationships_qa_run",
        description="Related QA run name",
        default="",
    )
    relationships_transform_run_id: str = Field(
        title="relationships_transform_run_id",
        description="Related transform run ID",
        default="",
    )
    relationships_transform_run: str = Field(
        title="relationships_transform_run",
        description="Related transform run name",
        default="",
    )
    relationships_creator: str = Field(
        title="relationships_creator",
        description="Related creator of the new values",
        default="",
    )
    relationships_creator_id: str = Field(
        title="relationships_creator_id",
        description="Related creator ID of the new values",
        default="",
    )
    data: dict[str, str] = Field(
        title="data",
        description="Related data",
        default={},
    )


class ExceptionData(BaseModel):
    """Exception Data Schema"""

    traceback: str = Field(
        title="traceback",
        description="Exception traceback",
    )
    value: str = Field(
        title="value",
        description="Exception value",
        default="",
    )
    type: str = Field(
        title="type",
        description="Exception type",
    )


class ExceptionSource(BaseModel):
    """Exception Source Schema"""

    name: str = Field(
        title="name",
        description="Event name",
    )
    API: str = Field(
        title="API",
        description="the API source related to the exception",
        default="",
    )
    CLI_command: str = Field(
        title="CLI_command",
        description="the CLI_command of exception source",
        default="",
    )
    web_source: str = Field(
        title="web_source",
        description="The web_source of the exception",
        default="",
    )
    identifier: str = Field(
        title="identifier",
        description="The identifier of the source",
        default="",
    )
    type: str = Field(
        title="type",
        description="the type of source",
        default="",
    )
    user_id: str = Field(
        title="user_id",
        description="the type of source",
        default="",
    )
    ip: str = Field(
        title="ip",
        description="the ip of source",
        default="",
    )
    named_environment: str = Field(
        title="named_environment",
        description="the named_environment of source",
        default="",
    )


class ExceptionCreate(BaseModel):
    """Exception Schema"""

    name: str = Field(
        title="name",
        description="Event name",
    )
    event_type: str = Field(
        title="event_type",
        description="the category of event",
        default="",
    )
    event_time: datetime = Field(
        title="event_time",
        description="the time of the event",
        default=datetime.now(),
    )
    source: ExceptionSource = Field(
        title="source",
        description="the source of the exception",
    )
    data: ExceptionData = Field(
        title="data",
        description="Exception detail data.",
    )

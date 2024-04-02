from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from pipes.graph.constants import VertexLabel, EdgeLabel


# Graph element base model
class VertexModel(BaseModel):
    id: str = Field(
        title="id",
        description="The Neptune graph vertex id in UUID format",
    )

    @field_validator("id", mode="before")
    @classmethod
    def validate_id(cls, value):
        """Ensure the value is valid UUID string"""
        if not value:
            return None

        value = str(value)
        try:
            UUID(value)
        except ValueError as e:
            raise e

        return value


class EdgeModel(BaseModel):
    id: str = Field(
        title="id",
        description="The Neptune graph edge id in UUID format",
    )

    @field_validator("id", mode="before")
    @classmethod
    def validate_id(cls, value):
        """Ensure the value is valid UUID string"""
        if not value:
            return None

        value = str(value)
        try:
            UUID(value)
        except ValueError as e:
            raise e

        return value


# User vertex model
class UserVertexProperties(BaseModel):
    email: EmailStr = Field(
        title="email",
        to_lower=True,
        description="Email address",
    )


class UserVertex(VertexModel):
    label: VertexLabel = Field(
        title="label",
        default=VertexLabel.User.value,
        description="The Neptune vertex label",
    )
    properties: UserVertexProperties = Field(
        title="properties",
        description="The user vertex properties",
    )


# Team vertex model
class TeamVertexProperties(BaseModel):
    project: str = Field(
        title="project",
        min_length=1,
        description="project name",
    )
    name: str = Field(
        title="name",
        min_length=1,
        description="team name",
    )


class TeamVertex(VertexModel):
    label: str = Field(
        title="label",
        default=VertexLabel.Team.value,
        description="The label for the vertex",
    )
    properties: TeamVertexProperties = Field(
        title="properties",
        description="team properties on the vertex",
    )


# Project vertex model
class ProjectVertexProperties(BaseModel):
    name: str = Field(
        title="name",
        min_length=1,
        description="human-readable project id name, must be unique.",
    )


class ProjectVertex(VertexModel):
    label: VertexLabel = Field(
        title="label",
        default=VertexLabel.Project.value,
        description="The Neptune vertex label",
    )
    properties: ProjectVertexProperties = Field(
        title="properties",
        description="The project vertex properties",
    )


# Project run vertex model
class ProjectRunVertexProperties(BaseModel):
    project: str = Field(
        title="project",
        min_length=1,
        description="project name",
    )
    name: str = Field(
        title="name",
        min_length=1,
        description="project run name",
    )


class ProjectRunVertex(VertexModel):
    label: str = Field(
        title="label",
        default=VertexLabel.ProjectRun.value,
        description="The label for the vertex",
    )
    properties: ProjectRunVertexProperties = Field(
        title="properties",
        description="project run properties on the vertex",
    )


# Model vertex model
class ModelVertexProperties(BaseModel):
    project: str = Field(
        title="project",
        min_length=1,
        description="project name",
    )
    projectrun: str = Field(
        title="projectrun",
        min_length=1,
        description="project run name",
    )
    name: str = Field(
        title="name",
        min_length=1,
        description="model name",
    )


class ModelVertex(VertexModel):
    label: str = Field(
        title="label",
        default=VertexLabel.Model.value,
        description="The label for the vertex",
    )
    properties: ModelVertexProperties = Field(
        title="properties",
        description="model properties on the vertex",
    )


# Model run vertex model
class ModelRunVertexProperties(BaseModel):
    project: str = Field(
        title="project",
        min_length=1,
        description="project name",
    )
    projectrun: str = Field(
        title="projectrun",
        min_length=1,
        description="project run name",
    )
    model: str = Field(
        title="model",
        min_length=1,
        description="model name",
    )
    name: str = Field(
        title="name",
        min_length=1,
        description="model name",
    )


class ModelRunVertex(VertexModel):
    label: str = Field(
        title="label",
        default=VertexLabel.ModelRun.value,
        description="The label for the vertex",
    )
    properties: ModelRunVertexProperties = Field(
        title="properties",
        description="model run properties on the vertex",
    )


# Dataset vertex model
class DatasetVertexProperties(BaseModel):
    project: str | None = Field(
        title="project",
        min_length=1,
        description="project name",
    )
    projectrun: str | None = Field(
        title="projectrun",
        min_length=1,
        description="project run name",
    )
    model: str | None = Field(
        title="model",
        min_length=1,
        description="model name",
    )
    modelrun: str | None = Field(
        title="modelrun",
        min_length=1,
        description="model run name",
    )
    name: str = Field(
        title="name",
        min_length=1,
        description="dataset name",
    )


class DatasetVertex(VertexModel):
    label: str = Field(
        title="label",
        default=VertexLabel.Dataset.value,
        description="The label for the vertex",
    )
    properties: DatasetVertexProperties = Field(
        title="properties",
        description="dataset properties on the vertex",
    )


# Task vertex model


# Handoff edge model
class FeedsEdgeProperties(BaseModel):
    project: str = Field(
        title="project",
        min_length=1,
        description="project name",
    )
    projectrun: str = Field(
        title="projectrun",
        min_length=1,
        description="project run name",
    )
    handoff: str = Field(
        title="handoff",
        min_length=1,
        description="handoff name",
    )


class FeedsEdge(EdgeModel):
    label: str = Field(
        title="label",
        default=EdgeLabel.feeds.value,
        description="The label for the edge",
    )
    properties: FeedsEdgeProperties = Field(
        title="properties",
        description="handoff properties on the edge",
    )

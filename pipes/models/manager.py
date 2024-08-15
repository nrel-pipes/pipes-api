from __future__ import annotations

import logging
from datetime import datetime

from pymongo.errors import DuplicateKeyError

from pipes.common.exceptions import (
    DocumentAlreadyExists,
    DocumentDoesNotExist,
    VertexAlreadyExists,
)
from pipes.db.manager import AbstractObjectManager
from pipes.graph.constants import VertexLabel, EdgeLabel
from pipes.projects.contexts import ProjectDocumentContext
from pipes.graph.schemas import ModelVertexProperties, ModelVertex
from pipes.projects.schemas import ProjectDocument
from pipes.projectruns.contexts import (
    ProjectRunDocumentContext,
    ProjectRunObjectContext,
    ProjectRunSimpleContext,
)
from pipes.projectruns.schemas import ProjectRunDocument
from pipes.models.schemas import ModelCreate, ModelDocument, ModelRead
from pipes.models.validators import ModelDomainValidator
from pipes.teams.manager import TeamManager
from pipes.teams.schemas import TeamDocument
from pipes.users.schemas import UserDocument

logger = logging.getLogger(__name__)


class ModelManager(AbstractObjectManager):
    """Model object manager class"""

    __label__ = VertexLabel.Model.value

    def __init__(
        self,
        context: ProjectRunDocumentContext | ProjectDocumentContext,
    ) -> None:
        self.context = context

    async def create_model(
        self,
        m_create: ModelCreate,
        user: UserDocument,
    ) -> ModelDocument:
        p_doc = self.context.project
        pr_doc = self.context.projectrun

        # Validate model domain business
        domain_validator = ModelDomainValidator(self.context)
        m_create = await domain_validator.validate(m_create)

        # Create model & modeling team vertex, edge
        modeling_team_doc = await self._get_modeling_team(
            p_doc.name,
            m_create.modeling_team,
        )
        m_vertex = await self._create_model_vertex(
            p_doc.name,
            pr_doc.name,
            m_create.name,
        )
        m_vtx_id = m_vertex.id
        t_vtx_id = modeling_team_doc.vertex.id
        self.n.add_e(m_vtx_id, t_vtx_id, EdgeLabel.affiliated.value)

        # Create model document
        m_doc = await self._create_model_document(m_create, m_vertex, user)

        # Add edge: project run -(requires)- model
        pr_vtx_id = pr_doc.vertex.id
        self.n.add_e(pr_vtx_id, m_vtx_id, EdgeLabel.requires.value)

        return m_doc

    async def _get_modeling_team(self, p_name: str, modeling_team: str) -> TeamDocument:
        # Get or create team object
        team_manager = TeamManager(self.context)
        model_team_doc = await team_manager.get_team(modeling_team)
        if not model_team_doc:
            raise DocumentDoesNotExist(
                f"Modeling team '{modeling_team}' does not exist under project '{p_name}'.",
            )
        return model_team_doc

    async def _create_model_vertex(
        self,
        p_name: str,
        pr_name: str,
        m_name: str,
    ) -> ModelVertex:
        properties = {"project": p_name, "projectrun": pr_name, "name": m_name}
        if self.n.exists(self.label, **properties):
            raise VertexAlreadyExists(
                f"Model vertex '{m_name}' already exists in context: {self.context}.",
            )

        properties_model = ModelVertexProperties(**properties)
        properties = properties_model.model_dump()
        m_vtx = self.n.add_v(self.label, **properties)

        # Dcoument creation
        m_vertex_model = ModelVertex(
            id=m_vtx.id,
            label=self.label,
            properties=properties_model,
        )
        return m_vertex_model

    async def _create_model_document(
        self,
        m_create: ModelCreate,
        m_vertex: ModelVertex,
        user: UserDocument,
    ) -> ModelDocument:
        """Create a new model under given project and project run"""

        # Check if model already exists or not
        m_name = m_create.name
        p_doc = self.context.project
        pr_doc = self.context.projectrun

        m_doc_exits = await self.d.exists(
            collection=ModelDocument,
            query={
                "context.project": p_doc.id,
                "context.projectrun": pr_doc.id,
                "name": m_name,
            },
        )
        if m_doc_exits:
            raise DocumentAlreadyExists(
                f"Model '{m_name}' already exists under context: {self.context}",
            )

        # object context
        context = ProjectRunObjectContext(project=p_doc.id, projectrun=pr_doc.id)

        # modeling team
        t_name = m_create.modeling_team
        t_doc = await self.d.find_one(
            collection=TeamDocument,
            query={"context.project": p_doc.id, "name": t_name},
        )
        if not t_doc:
            raise DocumentDoesNotExist(
                f"Modeling team '{t_name}' does not exist under project '{p_doc.name}'.",
            )

        m_doc = ModelDocument(
            vertex=m_vertex,
            context=context,
            # model information
            name=m_name,
            display_name=m_create.display_name,
            type=m_create.type,
            description=m_create.description,
            modeling_team=t_doc.id,
            assumptions=m_create.assumptions,
            requirements=m_create.requirements,
            # TODO: default to the list from project or project run
            scheduled_start=m_create.scheduled_start,
            scheduled_end=m_create.scheduled_end,
            expected_scenarios=m_create.expected_scenarios,
            scenario_mappings=m_create.scenario_mappings,
            other=m_create.other,
            # document information
            created_at=datetime.now(),
            created_by=user.id,
            last_modified=datetime.now(),
            modified_by=user.id,
        )

        # Create document
        try:
            m_doc = await self.d.insert(m_doc)
        except DuplicateKeyError:
            raise DocumentAlreadyExists(
                f"Model document '{m_name}' already exists under context: {self.context}.",
            )

        logger.info(
            "New model '%s' was created successfully under context: %s",
            m_name,
            self.context,
        )
        return m_doc

    async def get_models(self) -> list[ModelRead]:
        """Get all models under given project and project run"""
        p_doc = self.context.project
        pr_doc = getattr(self.context, "projectrun", None)

        query = {
            "context.project": p_doc.id,
        }
        if pr_doc:
            query = {
                "context.project": p_doc.id,
                "context.projectrun": pr_doc.id,
            }

        m_docs = await self.d.find_all(
            collection=ModelDocument,
            query=query,
        )

        team_manager = TeamManager(self.context)
        m_reads = []
        for m_doc in m_docs:
            data = m_doc.model_dump()
            pr_doc = await self.d.get(ProjectRunDocument, m_doc.context.projectrun)
            data["context"] = ProjectRunSimpleContext(
                project=p_doc.name,
                projectrun=pr_doc.name,
            )
            modeling_team_doc = await self.d.get(
                collection=TeamDocument,
                id=m_doc.modeling_team,
            )
            data["modeling_team"] = await team_manager.read_team(modeling_team_doc)
            m_reads.append(ModelRead.model_validate(data))
        return m_reads

    async def read_model(self, m_doc: ModelDocument):
        """Read a model from given model document"""
        p_id = m_doc.context.project
        p_doc = await self.d.get(collection=ProjectDocument, id=p_id)

        pr_id = m_doc.context.projectrun
        pr_doc = await self.d.get(collection=ProjectRunDocument, id=pr_id)

        team_manager = TeamManager(context=self.context)

        data = m_doc.model_dump()
        data["context"] = ProjectRunSimpleContext(
            project=p_doc.name,
            projectrun=pr_doc.name,
        )
        modeling_team_doc = await self.d.get(
            collection=TeamDocument,
            id=m_doc.modeling_team,
        )
        data["modeling_team"] = await team_manager.read_team(modeling_team_doc)

        return ModelRead.model_validate(data)

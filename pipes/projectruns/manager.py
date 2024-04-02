from __future__ import annotations

import logging
from datetime import datetime

from pymongo.errors import DuplicateKeyError

from pipes.common.exceptions import DocumentAlreadyExists, VertexAlreadyExists
from pipes.db.manager import AbstractObjectManager
from pipes.graph.constants import VertexLabel, EdgeLabel
from pipes.graph.schemas import ProjectRunVertexProperties, ProjectRunVertex
from pipes.projects.contexts import (
    ProjectDocumentContext,
    ProjectSimpleContext,
    ProjectObjectContext,
)
from pipes.projects.schemas import ProjectDocument
from pipes.projectruns.schemas import (
    ProjectRunCreate,
    ProjectRunDocument,
    ProjectRunRead,
)
from pipes.projectruns.validators import ProjectRunDomainValidator
from pipes.users.schemas import UserDocument

logger = logging.getLogger(__name__)


class ProjectRunManager(AbstractObjectManager):
    """Project run object manager class"""

    __label__ = VertexLabel.ProjectRun.value

    def __init__(self, context: ProjectDocumentContext) -> None:
        self.context = context

    async def create_projectrun(
        self,
        pr_create: ProjectRunCreate,
        user: UserDocument,
    ) -> ProjectRunDocument:
        """Create project run vertex and document"""
        p_doc = self.context.project

        # Validate project run create
        domain_validator = ProjectRunDomainValidator(self.context)
        pr_create = await domain_validator.validate(pr_create)

        # Add project run vertex
        pr_vertex = await self._create_projectrun_vertex(p_doc.name, pr_create.name)
        pr_doc = await self._create_projectrun_document(
            pr_create,
            pr_vertex,
            user,
        )

        # Add edge: project -(runs)- project run
        p_vtx_id = p_doc.vertex.id
        pr_vtx_id = pr_vertex.id
        self.n.add_edge(p_vtx_id, pr_vtx_id, EdgeLabel.runs.value)

        return pr_doc

    async def _create_projectrun_vertex(
        self,
        p_name: str,
        pr_name: str,
    ) -> ProjectRunVertex:
        properties = {"project": p_name, "name": pr_name}
        if self.n.exists(self.label, **properties):
            raise VertexAlreadyExists(
                f"Project run vertex {properties} already exists under project {p_name}.",
            )

        properties_model = ProjectRunVertexProperties(**properties)
        properties = properties_model.model_dump()
        pr_vtx = self.n.add_v(self.label, **properties)

        # Dcoument creation
        pr_vertex_model = ProjectRunVertex(
            id=pr_vtx.id,
            label=self.label,
            properties=properties_model,
        )
        return pr_vertex_model

    async def _create_projectrun_document(
        self,
        pr_create: ProjectRunCreate,
        pr_vertex: ProjectRunVertex,
        user: UserDocument,
    ) -> ProjectRunDocument:
        """Create a new project run under given project"""
        pr_name = pr_create.name
        p_doc = self.context.project

        pr_doc_exists = await self.d.find_one(
            collection=ProjectRunDocument,
            query={"context.project": p_doc.id, "name": pr_name},
        )
        if pr_doc_exists:
            raise DocumentAlreadyExists(
                f"Project run '{pr_name}' already exists under project '{p_doc.name}'.",
            )

        pr_name = pr_create.name
        context = ProjectObjectContext(project=p_doc.id)

        # Project run document
        pr_doc = ProjectRunDocument(
            vertex=pr_vertex,
            context=context,
            # project run information
            name=pr_name,
            description=pr_create.description,
            assumptions=pr_create.assumptions,
            requirements=pr_create.requirements,
            scenarios=pr_create.scenarios,
            scheduled_start=pr_create.scheduled_start,
            scheduled_end=pr_create.scheduled_end,
            # document information
            created_at=datetime.now(),
            created_by=user.id,
            last_modified=datetime.now(),
            modified_by=user.id,
        )

        # Create document
        try:
            pr_doc = await self.d.insert(pr_doc)
        except DuplicateKeyError:
            raise DocumentAlreadyExists(
                f"Project run '{pr_name}' already exists under project '{p_doc.name}'.",
            )

        logger.info(
            "New project run '%s' of project '%s' created successfully",
            pr_create.name,
            pr_doc.name,
        )
        return pr_doc

    async def get_projectruns(self) -> list[ProjectRunRead]:
        """Return all project runs under given project"""
        p_doc = self.context.project
        pr_docs = await self.d.find_all(
            collection=ProjectRunDocument,
            query={"context.project": p_doc.id},
        )

        pr_reads = []
        for pr_doc in pr_docs:
            data = pr_doc.model_dump()
            data["context"] = ProjectSimpleContext(project=p_doc.name)
            pr_reads.append(ProjectRunRead.model_validate(data))
        return pr_reads

    async def read_projectrun(self, pr_doc: ProjectRunDocument) -> ProjectRunRead:
        """Convert ProjectRunDocument to ProjectRunRead instance"""
        p_id = pr_doc.context.project
        p_doc = await self.d.get(collection=ProjectDocument, id=p_id)

        data = pr_doc.model_dump()
        data["context"] = ProjectSimpleContext(project=p_doc.name)
        pr_read = ProjectRunRead.model_validate(data)

        return pr_read

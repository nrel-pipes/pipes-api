from __future__ import annotations

import logging
from datetime import datetime

from pymongo.errors import DuplicateKeyError

from pipes.common.exceptions import DocumentAlreadyExists, VertexAlreadyExists
from pipes.db.manager import AbstractObjectManager
from pipes.graph.constants import VertexLabel, EdgeLabel
from pipes.graph.schemas import ModelRunVertexProperties, ModelRunVertex
from pipes.projects.schemas import ProjectDocument
from pipes.projectruns.schemas import ProjectRunDocument
from pipes.models.contexts import (
    ModelDocumentContext,
    ModelSimpleContext,
    ModelObjectContext,
)
from pipes.models.schemas import ModelDocument
from pipes.modelruns.schemas import ModelRunCreate, ModelRunDocument, ModelRunRead
from pipes.modelruns.validators import ModelRunDomainValidator
from pipes.users.schemas import UserDocument

logger = logging.getLogger(__name__)


class ModelRunManager(AbstractObjectManager):

    __label__ = VertexLabel.ModelRun.value

    def __init__(self, context: ModelDocumentContext) -> None:
        self.context = context

    async def create_modelrun(
        self,
        mr_create: ModelRunCreate,
        user: UserDocument,
    ) -> ModelRunDocument:
        p_doc = self.context.project
        pr_doc = self.context.projectrun
        m_doc = self.context.model

        # Validate model run create
        domain_validator = ModelRunDomainValidator(self.context)
        mr_create = await domain_validator.validate(mr_create)

        # Create model run vertex
        mr_vertex = await self._create_modelrun_vertex(
            p_doc.name,
            pr_doc.name,
            m_doc.name,
            mr_create.name,
        )

        # Create model run document
        mr_doc = await self._create_modelrun_document(mr_create, mr_vertex, user)

        # Add edge: model -(performs)- model run
        m_vtx_id = m_doc.vertex.id
        mr_vtx_id = mr_vertex.id
        self.n.add_edge(m_vtx_id, mr_vtx_id, EdgeLabel.performs.value)

        return mr_doc

    async def _create_modelrun_vertex(
        self,
        p_name: str,
        pr_name: str,
        m_name: str,
        mr_name: str,
    ):
        properties = {
            "project": p_name,
            "projectrun": pr_name,
            "model": m_name,
            "name": mr_name,
        }
        if self.n.exists(self.label, **properties):
            raise VertexAlreadyExists(
                f"Model vertex '{m_name}' already exists in context: {self.context}.",
            )

        properties_model = ModelRunVertexProperties(**properties)
        properties = properties_model.model_dump()
        mr_vtx = self.n.add_v(self.label, **properties)

        # Dcoument creation
        mr_vertex_model = ModelRunVertex(
            id=mr_vtx.id,
            label=self.label,
            properties=properties_model,
        )
        return mr_vertex_model

    async def _create_modelrun_document(
        self,
        mr_create: ModelRunCreate,
        mr_vertex: ModelRunVertex,
        user: UserDocument,
    ):
        """Create a model run under given context"""
        p_doc = self.context.project
        pr_doc = self.context.projectrun
        m_doc = self.context.model

        mr_name = mr_create.name
        mr_doc_exists = await self.d.find_one(
            collection=ModelRunDocument,
            query={
                "context.project": p_doc.id,
                "context.projectrun": pr_doc.id,
                "context.model": m_doc,
                "name": mr_name,
            },
        )
        if mr_doc_exists:
            raise DocumentAlreadyExists(
                f"Model run document '{mr_name}' already exists under context: {self.context}.",
            )

        # context
        context = ModelObjectContext(
            project=p_doc.id,
            projectrun=pr_doc.id,
            model=m_doc.id,
        )
        mr_doc = ModelRunDocument(
            vertex=mr_vertex,
            context=context,
            # model run information
            name=mr_name,
            version=mr_create.version,
            description=mr_create.description,
            assumptions=mr_create.assumptions,
            notes=mr_create.notes,
            source_code=mr_create.source_code,
            config=mr_create.config,
            env_deps=mr_create.env_deps,
            datasets=mr_create.datasets,
            # document information
            created_at=datetime.now(),
            created_by=user.id,
            last_modified=datetime.now(),
            modified_by=user.id,
        )

        try:
            mr_doc = await self.d.insert(mr_doc)
        except DuplicateKeyError:
            raise DocumentAlreadyExists(
                f"Model run '{mr_name}' already exists under context {self.context}.",
            )

        logger.info(
            "New model run '%s' was created successfully under context: %s",
            mr_name,
            self.context,
        )
        return mr_doc

    async def get_modelruns(self) -> list[ModelRunRead]:
        """Get all model runs under given project, project run, model"""
        p_doc = self.context.project
        pr_doc = self.context.projectrun
        m_doc = self.context.model

        mr_docs = await self.d.find_all(
            collection=ModelRunDocument,
            query={
                "context.project": p_doc.id,
                "context.projectrun": pr_doc.id,
                "context.model": m_doc.id,
            },
        )

        mr_reads = []
        for m_doc in mr_docs:
            data = m_doc.model_dump()
            data["context"] = ModelSimpleContext(
                project=p_doc.name,
                projectrun=pr_doc.name,
                model=m_doc.name,
            )
            mr_reads.append(ModelRunRead.model_validate(data))
        return mr_reads

    async def read_modelrun(self, mr_doc: ModelRunDocument) -> ModelRunRead:
        p_id = mr_doc.context.project
        p_doc = await self.d.get(collection=ProjectDocument, id=p_id)

        pr_id = mr_doc.context.projectrun
        pr_doc = await self.d.get(collection=ProjectRunDocument, id=pr_id)

        m_id = mr_doc.context.model
        m_doc = await self.d.get(collection=ModelDocument, id=m_id)

        data = mr_doc.model_dump()
        data["context"] = ModelSimpleContext(
            project=p_doc.name,
            projectrun=pr_doc.name,
            model=m_doc.name,
        )

        return ModelRunRead.model_validate(data)

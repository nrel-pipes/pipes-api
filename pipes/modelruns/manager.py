from __future__ import annotations

import logging
from datetime import datetime

from pymongo.errors import DuplicateKeyError

from pipes.common.exceptions import DocumentAlreadyExists
from pipes.db.manager import AbstractObjectManager
from pipes.common.constants import NodeLabel
from pipes.projects.contexts import ProjectDocumentContext
from pipes.projects.schemas import ProjectDocument
from pipes.projectruns.contexts import ProjectRunDocumentContext
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

    __label__ = NodeLabel.ModelRun.value

    def __init__(
        self,
        context: (
            ModelDocumentContext | ProjectRunDocumentContext | ProjectDocumentContext
        ),
    ) -> None:
        self.context = context

    async def create_modelrun(
        self,
        mr_create: ModelRunCreate,
        user: UserDocument,
    ) -> ModelRunDocument:
        # Validate model run create
        domain_validator = ModelRunDomainValidator(self.context)
        mr_create = await domain_validator.validate(mr_create)

        # Create model run document
        mr_doc = await self._create_modelrun_document(mr_create, user)

        return mr_doc

    async def _create_modelrun_document(
        self,
        mr_create: ModelRunCreate,
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
        pr_doc = getattr(self.context, "projectrun", None)
        m_doc = getattr(self.context, "model", None)

        query = {
            "context.project": p_doc.id,
        }
        if pr_doc:
            query = {
                "context.project": p_doc.id,
                "context.projectrun": pr_doc.id,
            }
        if pr_doc and m_doc:
            query = {
                "context.project": p_doc.id,
                "context.projectrun": pr_doc.id,
                "context.model": m_doc.id,
            }

        mr_docs = await self.d.find_all(
            collection=ModelRunDocument,
            query=query,
        )

        mr_reads = []
        for mr_doc in mr_docs:
            data = mr_doc.model_dump()
            pr_doc = await self.d.get(ProjectRunDocument, mr_doc.context.projectrun)
            m_doc = await self.d.get(ModelDocument, mr_doc.context.model)
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

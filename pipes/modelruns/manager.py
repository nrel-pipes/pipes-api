from __future__ import annotations

import logging
from datetime import datetime

from pymongo.errors import DuplicateKeyError

from pipes.common.exceptions import DocumentAlreadyExists, DocumentDoesNotExist
from pipes.db.manager import AbstractObjectManager
from pipes.projects.schemas import ProjectDocument
from pipes.projectruns.schemas import ProjectRunDocument
from pipes.models.contexts import ModelSimpleContext, ModelObjectContext
from pipes.models.schemas import ModelDocument
from pipes.modelruns.schemas import ModelRunCreate, ModelRunDocument, ModelRunRead
from pipes.modelruns.validators import ModelRunDomainValidator
from pipes.users.schemas import UserDocument

logger = logging.getLogger(__name__)


class ModelRunManager(AbstractObjectManager):

    async def create_modelrun(
        self,
        p_doc: ProjectDocument,
        pr_doc: ProjectRunDocument,
        m_doc: ModelDocument,
        mr_create: ModelRunCreate,
        user: UserDocument,
    ):
        """Create a model run under given project/projectrun/model"""
        mr_name = mr_create.name
        mr_doc_exists = await ModelRunDocument.find_one(
            {
                "context.project": p_doc.id,
                "context.projectrun": pr_doc.id,
                "context.model": m_doc,
                "name": mr_name,
            },
        )
        if mr_doc_exists:
            raise DocumentAlreadyExists(
                f"Model run '{mr_name}' already exists with "
                f"model '{m_doc.name}' under"
                f"project run '{pr_doc.name}' in project '{p_doc.name}'.",
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
            created_at=datetime.utcnow(),
            created_by=user.id,
            last_modified=datetime.utcnow(),
            modified_by=user.id,
        )

        domain_validator = ModelRunDomainValidator()
        mr_doc = await domain_validator.validate(mr_doc)

        try:
            mr_doc = await mr_doc.insert()
        except DuplicateKeyError:
            raise DocumentAlreadyExists(
                f"Model run '{mr_name}' already exists with "
                f"Model '{m_doc.name}' under "
                f"project run '{pr_doc.name}' in project '{p_doc.name}'.",
            )

        logger.info(
            "New model run '%s' with model %s under project run '%s' in project '%s' was created successfully",
            mr_name,
            m_doc.name,
            pr_doc.name,
            p_doc.name,
        )
        return mr_doc

    async def get_modelruns(
        self,
        p_doc: ProjectDocument,
        pr_doc: ProjectRunDocument,
        m_doc: ModelDocument,
    ) -> list[ModelRunRead]:
        """Get all model runs under given project, project run, model"""
        mr_docs = ModelRunDocument.find(
            {
                "context.project": p_doc.id,
                "context.projectrun": pr_doc.id,
                "context.model": m_doc.id,
            },
        )
        mr_reads = []
        async for m_doc in mr_docs:
            data = m_doc.model_dump()
            data["context"] = ModelSimpleContext(
                project=p_doc.name,
                projectrun=pr_doc.name,
                model=m_doc.name,
            )
            mr_reads.append(ModelRunRead.model_validate(data))
        return mr_reads

    async def get_modelrun(
        self,
        p_doc: ProjectDocument,
        pr_doc: ProjectRunDocument,
        m_doc: ModelDocument,
        mr_name: str,
    ) -> ModelRunDocument:
        mr_doc = await ModelRunDocument.find_one(
            {
                "context.project": p_doc.id,
                "context.projectrun": pr_doc.id,
                "context.model": m_doc.id,
                "name": mr_name,
            },
        )
        if mr_doc:
            data = mr_doc.model_dump()
            data["context"] = ModelSimpleContext(
                project=p_doc.name,
                projectrun=pr_doc.name,
                model=m_doc.name,
            )
            print(f"Data: {data}")
            mr_read = ModelRunRead.model_validate(data)
            return mr_read
        raise DocumentDoesNotExist("Document does not exist")

    async def update_status(self, p_doc, pr_doc, m_doc, mr_name, status):
        mr_doc = await ModelRunDocument.find_one(
            {
                "context.project": p_doc.id,
                "context.projectrun": pr_doc.id,
                "context.model": m_doc.id,
                "name": mr_name,
            },
        )
        if mr_doc:
            # Update the status field
            mr_doc.status = status  # replace "new_status" with the actual status value
            await mr_doc.save()
            data = mr_doc.model_dump()
            data["context"] = ModelSimpleContext(
                project=p_doc.name,
                projectrun=pr_doc.name,
                model=m_doc.name,
            )
            mr_read = ModelRunRead.model_validate(data)
            return mr_read
        else:
            return None

    async def read_modelrun(self, mr_doc: ModelRunDocument) -> ModelRunRead:
        p_id = mr_doc.context.project
        p_doc = await ProjectDocument.get(p_id)

        pr_id = mr_doc.context.projectrun
        pr_doc = await ProjectRunDocument.get(pr_id)

        m_id = mr_doc.context.model
        m_doc = await ModelDocument.get(m_id)

        data = mr_doc.model_dump()
        data["context"] = ModelSimpleContext(
            project=p_doc.name,
            projectrun=pr_doc.name,
            model=m_doc.name,
        )

        return ModelRunRead.model_validate(data)

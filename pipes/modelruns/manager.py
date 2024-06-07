from __future__ import annotations

import logging
from datetime import datetime

from pymongo.errors import DuplicateKeyError

# from pymongo import UpdateOne
# from fastapi import HTTPException

from pipes.common.exceptions import DocumentAlreadyExists
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
        print(type(mr_doc))
        if mr_doc:
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
            data = mr_doc.model_dump()
            data["context"] = ModelSimpleContext(
                project=p_doc.name,
                projectrun=pr_doc.name,
                model=m_doc.name,
            )
            data["status"] = status  # Update the status field
            print(data)
            # Use the correct method to update the document in Motor
            await ModelRunDocument.get_motor_collection().update_one(
                {"_id": mr_doc.id},
                {"$set": data},
            )

            mr_read = ModelRunRead.model_validate(data)
            return mr_read
        else:
            return None

        # mr_doc = await ModelRunDocument.find_one(
        #     {
        #         "context.project": p_doc.id,
        #         "context.projectrun": pr_doc.id,
        #         "context.model": m_doc.id,
        #         "name": mr_name
        #     }
        # )

        # if not mr_doc:
        #     raise HTTPException(status_code=404, detail="ModelRun not found")

        # # Create the context data
        # context_data = ModelSimpleContext(
        #     project=p_doc.name,  # Assuming p_doc.name is a str
        #     projectrun=pr_doc.name,  # Assuming pr_doc.name is a str
        #     model=m_doc.name  # Assuming m_doc.name is a str
        # )

        # # Update the status and context fields
        # update_data = {"status": status, "context": context_data}

        # # Update the document in the database
        # await ModelRunDocument.get_motor_collection().update_one(
        #     {"_id": mr_doc.id},
        #     {"$set": update_data}
        # )

        # # Update the mr_doc object with the new data
        # mr_doc.status = status
        # mr_doc.context = context_data

        # # Fetch updated document
        # updated_mr_doc = await ModelRunDocument.find_one({"_id": mr_doc.id})

        # if not updated_mr_doc:
        #     raise HTTPException(status_code=404, detail="Updated ModelRun not found")

        # # Create and return ModelRunRead object with all required fields
        # return ModelRunRead(
        #     id=str(updated_mr_doc.id),
        #     name=updated_mr_doc.name,
        #     version=updated_mr_doc.version,
        #     context=ModelSimpleContext(**updated_mr_doc.context),
        #     status=updated_mr_doc.status
        # )

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

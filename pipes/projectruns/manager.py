from __future__ import annotations

import logging
from datetime import datetime

from pymongo.errors import DuplicateKeyError

from pipes.common.exceptions import DocumentAlreadyExists
from pipes.db.manager import AbstractObjectManager
from pipes.projects.contexts import ProjectSimpleContext, ProjectObjectContext
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

    async def create_projectrun(
        self,
        p_doc: ProjectDocument,
        pr_create: ProjectRunCreate,
        user: UserDocument,
    ) -> ProjectRunDocument:
        """Create a new project run under given project"""
        pr_name = pr_create.name
        pr_doc_exists = await ProjectRunDocument.find_one(
            {"context.project": p_doc.id, "name": pr_name},
        )
        if pr_doc_exists:
            raise DocumentAlreadyExists(
                f"Project run '{pr_name}' already exists under project '{p_doc.name}'.",
            )

        pr_name = pr_create.name
        context = ProjectObjectContext(project=p_doc.id)
        print(f"PR_CREATE: {pr_create}")
        # Project run document
        pr_doc = ProjectRunDocument(
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
            created_at=datetime.utcnow(),
            created_by=user.id,
            last_modified=datetime.utcnow(),
            modified_by=user.id,
            status=pr_create.status,
        )

        domain_validator = ProjectRunDomainValidator()
        pr_doc = await domain_validator.validate(pr_doc)

        # Create document
        try:
            pr_doc = await pr_doc.insert()
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

    async def change_projectrun_status(
        self,
        p_doc: ProjectDocument,
        pr_create: ProjectRunCreate,
    ):
        pr_name = pr_create.name
        pr_doc_exists = await ProjectRunDocument.find_one(
            {"context.project": p_doc.id, "name": pr_name},
        )
        if not pr_doc_exists:
            raise ValueError("Document does not exist.")
        print(pr_doc_exists.status)

    async def get_projectruns(self, p_doc: ProjectDocument) -> list[ProjectRunRead]:
        """Return all project runs under given project"""
        pr_docs = ProjectRunDocument.find({"context.project": p_doc.id})

        pr_reads = []
        async for pr_doc in pr_docs:
            data = pr_doc.model_dump()
            data["context"] = ProjectSimpleContext(project=p_doc.name)
            pr_reads.append(ProjectRunRead.model_validate(data))
        return pr_reads

    async def read_projectrun(self, pr_doc: ProjectRunDocument) -> ProjectRunRead:
        """Convert ProjectRunDocument to ProjectRunRead instance"""
        p_id = pr_doc.context.project
        p_doc = await ProjectDocument.get(p_id)

        data = pr_doc.model_dump()
        data["context"] = ProjectSimpleContext(project=p_doc.name)
        pr_read = ProjectRunRead.model_validate(data)

        return pr_read

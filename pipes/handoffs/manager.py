from __future__ import annotations

import logging
from datetime import datetime

from pymongo.errors import DuplicateKeyError

from pipes.common.exceptions import DocumentAlreadyExists, DocumentDoesNotExist
from pipes.db.manager import AbstractObjectManager
from pipes.common.constants import EdgeLabel
from pipes.handoffs.schemas import (
    HandoffCreate,
    HandoffDocument,
    HandoffRead,
    HandoffUpdate,
)
from pipes.handoffs.validators import HandoffDomainValidator
from pipes.models.schemas import ModelDocument
from pipes.models.manager import ModelManager
from pipes.modelruns.schemas import ModelRunDocument
from pipes.projects.schemas import ProjectDocument
from pipes.projectruns.contexts import (
    ProjectRunDocumentContext,
    ProjectRunSimpleContext,
    ProjectRunObjectContext,
)
from pipes.projectruns.schemas import ProjectRunDocument
from pipes.users.schemas import UserDocument

logger = logging.getLogger(__name__)


class HandoffManager(AbstractObjectManager):
    """Handoff object manager class"""

    __label__ = EdgeLabel.feeds.value

    def __init__(self, context: ProjectRunDocumentContext) -> None:
        self.context = context

    async def create_handoff(
        self,
        h_create: HandoffCreate,
        user: UserDocument,
    ) -> HandoffDocument:
        p_doc = self.context.project
        pr_doc = self.context.projectrun

        # Validate handoff domain business
        domain_validator = HandoffDomainValidator(self.context)
        h_create = await domain_validator.validate(h_create)

        # Create handoff document
        mr_doc = domain_validator.from_modelrun_doc
        _context = ProjectRunObjectContext(
            project=p_doc.id,
            projectrun=pr_doc.id,
        )
        h_doc = HandoffDocument(
            context=_context,
            from_model=domain_validator.from_model_doc.id,  # type: ignore
            to_model=domain_validator.to_model_doc.id,  # type: ignore
            from_modelrun=mr_doc.id if mr_doc else None,  # type: ignore
            name=h_create.name,
            description=h_create.description,
            # document information
            created_at=datetime.now(),
            created_by=user.id,
            last_modified=datetime.now(),
            modified_by=user.id,
        )

        try:
            h_doc = await self.d.insert(h_doc)
        except DuplicateKeyError:
            raise DocumentAlreadyExists(
                f"Handoff document '{h_doc.name}' already exists under context: {self.context}.",
            )

        return h_doc

    async def create_handoffs(
        self,
        h_creates: list[HandoffCreate],
        user: UserDocument,
    ) -> list[HandoffDocument]:
        h_docs = []
        for h_create in h_creates:
            h_doc = await self.create_handoff(h_create, user)
            h_docs.append(h_doc)
        return h_docs

    async def get_handoffs(self, model: str | None = None) -> list[HandoffRead]:
        p_doc = self.context.project
        pr_doc = getattr(self.context, "projectrun", None)
        if pr_doc:
            query = {
                "context.project": p_doc.id,
                "context.projectrun": pr_doc.id,
            }
            if model:
                m_query = query.copy()
                m_query["name"] = model
                m_doc = await self.d.find_one(ModelDocument, query=m_query)
                query["from_model"] = m_doc.id
        else:
            query = {
                "context.project": p_doc.id,
            }

        h_docs = await self.d.find_all(
            collection=HandoffDocument,
            query=query,
        )

        h_reads = []
        for h_doc in h_docs:
            h_read = await self.read_handoff(h_doc)
            h_reads.append(h_read)
        return h_reads

    async def get_handoff_by_name(self, handoff_name: str) -> HandoffDocument:
        """Get a single handoff document by name"""
        p_doc = self.context.project
        pr_doc = getattr(self.context, "projectrun", None)

        if pr_doc:
            query = {
                "context.project": p_doc.id,
                "context.projectrun": pr_doc.id,
                "name": handoff_name,
            }
        else:
            query = {
                "context.project": p_doc.id,
                "name": handoff_name,
            }

        h_doc = await self.d.find_one(
            collection=HandoffDocument,
            query=query,
        )
        return h_doc

    async def delete_handoff(
        self,
        project: str,
        projectrun: str,
        handoff: str,
    ) -> None:
        """Delete a handoff document by name"""
        query = {
            "context.project": project,
            "context.projectrun": projectrun,
            "name": handoff,
        }

        return await self.d.delete_one(
            collection=HandoffDocument,
            query=query,
        )

    async def read_handoff(self, h_doc: HandoffDocument) -> HandoffRead:
        # Read context
        p_id = h_doc.context.project
        p_doc = await self.d.get(collection=ProjectDocument, id=p_id)

        pr_id = h_doc.context.projectrun
        pr_doc = await self.d.get(collection=ProjectRunDocument, id=pr_id)

        m_from_id = h_doc.from_model
        m_from_doc = await self.d.get(collection=ModelDocument, id=m_from_id)

        m_to_id = h_doc.to_model
        m_to_doc = await self.d.get(collection=ModelDocument, id=m_to_id)

        mr_id = h_doc.from_modelrun
        if mr_id:
            mr_doc = await self.d.get(collection=ModelRunDocument, id=mr_id)
        else:
            mr_doc = None

        data = h_doc.model_dump()
        data["context"] = ProjectRunSimpleContext(
            project=p_doc.name,
            projectrun=pr_doc.name,
        )
        data["from_model"] = m_from_doc.name
        data["to_model"] = m_to_doc.name
        data["from_modelrun"] = mr_doc.name if mr_doc else None

        return HandoffRead.model_validate(data)

    async def update_handoff(
        self,
        h_doc: HandoffDocument,
        data: HandoffUpdate,
        user: UserDocument,
    ) -> HandoffDocument:
        """Update a handoff document"""
        context = self.context

        # Check if handoff exists
        if h_doc is None:
            raise DocumentDoesNotExist(
                f"Handoff does not exist in context: {context}",
            )

        # If name is changing, check for duplicate
        if data.name and data.name != h_doc.name:
            if hasattr(context, "projectrun"):
                query = {
                    "context.project": context.project.id,
                    "context.projectrun": context.projectrun.id,
                    "name": data.name,
                }
            else:
                query = {
                    "context.project": context.project.id,
                    "name": data.name,
                }
            other_h_doc = await self.d.find_one(
                collection=HandoffDocument,
                query=query,
            )
            if other_h_doc:
                raise DocumentAlreadyExists(
                    f"Handoff '{data.name}' already exists in context: {context}",
                )

        update_fields = data.model_dump(exclude_unset=True)
        model_manager = ModelManager(context=self.context)
        if "from_model" in update_fields:
            model_name = update_fields["from_model"]
            from_model_doc = await model_manager.get_model(name=model_name)
            update_fields["from_model"] = from_model_doc.id  # type: ignore

        if "to_model" in update_fields:
            model_name = update_fields["to_model"]
            to_model_doc = await model_manager.get_model(name=model_name)
            update_fields["to_model"] = to_model_doc.id  # type: ignore

        # Update the document with new values
        for k, v in update_fields.items():
            setattr(h_doc, k, v)
        h_doc.last_modified = datetime.now()
        h_doc.modified_by = user.id
        await h_doc.save()

        logger.info(
            "Handoff '%s' updated successfully under context: %s",
            h_doc.name,
            context,
        )
        return h_doc

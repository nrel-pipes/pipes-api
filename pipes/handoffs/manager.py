from __future__ import annotations

import logging
from datetime import datetime

from pipes.db.manager import AbstractObjectManager
from pipes.graph.constants import EdgeLabel
from pipes.graph.schemas import FeedsEdgeProperties, FeedsEdge
from pipes.handoffs.schemas import HandoffCreate, HandoffDocument, HandoffRead
from pipes.handoffs.validators import HandoffDomainValidator
from pipes.models.schemas import ModelDocument
from pipes.modelruns.schemas import ModelRunDocument
from pipes.projects.schemas import ProjectDocument
from pipes.projectruns.contexts import (
    ProjectRunDocumentContext,
    ProjectRunSimpleContext,
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

        # TODO: refactor edge creation
        # Create feeds edge between models for handoff
        from_m_vtx_id = domain_validator.from_model_doc.vertex.id  # type: ignore
        to_m_vtx_id = domain_validator.to_model_doc.vertex.id  # type: ignore
        properties_model = FeedsEdgeProperties(
            project=p_doc.name,
            projectrun=pr_doc.name,
            handoff=h_create.name,
        )
        properties = properties_model.model_dump()
        edge = self.n.add_edge(from_m_vtx_id, to_m_vtx_id, self.label, **properties)

        # Create handoff document
        feeds_edge_model = FeedsEdge(
            id=edge.id,
            label=EdgeLabel.feeds.value,
            properties=properties_model,
        )

        mr_doc = domain_validator.from_modelrun_doc
        h_doc = HandoffDocument(
            edge=feeds_edge_model,
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

        return h_doc

    async def get_handoffs(self, model: str | None = None) -> list[HandoffRead]:
        p_doc = self.context.project
        pr_doc = self.context.projectrun

        query = {
            "context.project": p_doc.id,
            "context.projectrun": pr_doc.id,
        }
        if model:
            query["from_model"] = model

        h_docs = await self.d.find_all(
            collection=HandoffDocument,
            query=query,
        )

        h_reads = []
        for h_doc in h_docs:
            h_read = await self.read_handoff(h_doc)
            h_reads.append(h_read)
        return h_reads

    async def read_handoff(self, h_doc: HandoffDocument) -> HandoffRead:
        # Read context
        p_id = h_doc.context.project
        p_doc = await self.d.get(collection=ProjectDocument, id=p_id)

        pr_id = h_doc.context.projectrun
        pr_doc = await self.d.get(collection=ProjectRunDocument, id=pr_id)

        m_id = h_doc.from_model
        m_doc = await self.d.get(collection=ModelDocument, id=m_id)

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
        data["from_model"] = m_doc.name
        data["to_model"] = m_doc.name if mr_doc else None

        return HandoffRead.model_validate(data)

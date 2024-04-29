from __future__ import annotations

from pipes.common.exceptions import DomainValidationError
from pipes.common.validators import DomainValidator
from pipes.db.document import DocumentDB
from pipes.models.schemas import ModelDocument
from pipes.modelruns.schemas import ModelRunDocument
from pipes.projectruns.contexts import ProjectRunDocumentContext
from pipes.handoffs.schemas import HandoffCreate


class HandoffDomainValidator(DomainValidator):

    def __init__(self, context: ProjectRunDocumentContext) -> None:
        self.context = context
        self.from_model_doc = None
        self.to_model_doc = None
        self.from_modelrun_doc = None

    async def validate_from_model(self, h_create: HandoffCreate) -> HandoffCreate:
        if self.from_model_doc:
            return h_create

        if h_create.from_model == h_create.to_model:
            raise DomainValidationError(
                f"Handoff from_model '{h_create.from_model}' could not be same as to_model '{h_create.to_model}'",
            )

        docdb = DocumentDB()
        m_doc = await docdb.find_one(
            collection=ModelDocument,
            query={
                "context.project": self.context.project.id,  # type: ignore
                "context.projectrun": self.context.projectrun.id,  # type: ignore
                "name": h_create.from_model,
            },
        )
        if m_doc is None:
            raise DomainValidationError(
                f"Handoff from_model '{h_create.from_model}' does not exist under context {self.context}.",
            )

        self.from_model_doc = m_doc

        return h_create

    async def validate_to_model(self, h_create: HandoffCreate) -> HandoffCreate:
        if self.to_model_doc:
            return h_create

        if h_create.from_model == h_create.to_model:
            raise DomainValidationError(
                f"Handoff to_model '{h_create.to_model}' could not be same as from_model '{h_create.from_model}'",
            )

        docdb = DocumentDB()
        m_doc = await docdb.find_one(
            collection=ModelDocument,
            query={
                "context.project": self.context.project.id,  # type: ignore
                "context.projectrun": self.context.projectrun.id,  # type: ignore
                "name": h_create.to_model,
            },
        )
        if m_doc is None:
            raise DomainValidationError(
                f"Handoff to_model '{h_create.to_model}' does not exist under context {self.context}.",
            )

        self.to_model_doc = m_doc

        return h_create

    async def validate_from_modelrun(self, h_create: HandoffCreate) -> HandoffCreate:
        if self.from_modelrun_doc:
            return h_create

        if not self.from_model_doc:
            await self.validate_from_model(h_create)

        if h_create.from_modelrun is None:
            return h_create

        docdb = DocumentDB()
        mr_doc = await docdb.find_one(
            collection=ModelRunDocument,
            query={
                "context.project": self.context.project.id,  # type: ignore
                "context.projectrun": self.context.projectrun.id,  # type: ignore
                "context.model": self.from_model_doc.id,  # type: ignore
                "name": h_create.from_modelrun,
            },
        )
        if mr_doc is None:
            raise DomainValidationError(
                f"Handoff from_modelrun '{h_create.from_modelrun}' does not exist "
                f"under model '{h_create.from_model}' with context {self.context}.",
            )

        self.from_modelrun_doc = mr_doc

        return h_create

    async def validate_scheduled_start(
        self,
        h_create: HandoffCreate,
    ) -> HandoffCreate:
        """Model scheduled start dates should be within project run schedules"""
        if not h_create.scheduled_start:
            return h_create

        if not h_create.scheduled_end:
            raise DomainValidationError(
                "Handoff 'scheduled_end' is required.",
            )

        if h_create.scheduled_start > h_create.scheduled_end:
            raise DomainValidationError(
                "Handoff 'scheduled_start' could not be larger than 'scheduled_end'.",
            )

        if not self.from_model_doc:
            await self.validate_from_model(h_create)

        m_doc = self.from_model_doc

        if h_create.scheduled_start < m_doc.scheduled_start:  # type: ignore
            raise DomainValidationError(
                f"Handoff 'scheduled_start' could not be early than {m_doc.scheduled_start}",  # type: ignore
            )

        if h_create.scheduled_start > m_doc.scheduled_end:  # type: ignore
            raise DomainValidationError(
                f"Handoff 'scheduled_start' could not be late than {m_doc.scheduled_end}",  # type: ignore
            )

        return h_create

    async def validate_scheduled_end(
        self,
        h_create: HandoffCreate,
    ) -> HandoffCreate:
        """Model scheduled end dates should be within project run schedules"""
        if not h_create.scheduled_start:
            return h_create

        if not h_create.scheduled_end:
            raise DomainValidationError(
                "Handoff 'scheduled_end' is required.",
            )

        if h_create.scheduled_end < h_create.scheduled_start:  # type: ignore
            raise DomainValidationError(
                "Model 'scheduled_end' could not be smaller than 'scheduled_start'.",
            )

        if not self.from_model_doc:
            await self.validate_from_model(h_create)

        m_doc = self.from_model_doc

        if h_create.scheduled_end < m_doc.scheduled_start:  # type: ignore
            raise DomainValidationError(
                f"Handoff 'scheduled_end' could not be early than {m_doc.scheduled_start}",  # type: ignore
            )

        if h_create.scheduled_end > m_doc.scheduled_end:  # type: ignore
            raise DomainValidationError(
                f"Handoff 'scheduled_end' could not be late than {m_doc.scheduled_end}",  # type: ignore
            )

        return h_create

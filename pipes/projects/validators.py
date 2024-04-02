from __future__ import annotations

from pipes.common.exceptions import (
    ContextValidationError,
    DomainValidationError,
    UserPermissionDenied,
)
from pipes.common.validators import ContextValidator, DomainValidator
from pipes.projects.contexts import ProjectSimpleContext, ProjectDocumentContext
from pipes.projects.schemas import ProjectCreate, ProjectDocument
from pipes.users.schemas import UserDocument


class ProjectContextValidator(ContextValidator):
    """Project context validator class"""

    async def validate_document(
        self,
        context: ProjectSimpleContext,
    ) -> ProjectDocumentContext:
        """Get project document through validation"""
        p_name = context.project
        p_doc = await ProjectDocument.find_one(ProjectDocument.name == p_name)

        if not p_doc:
            raise ContextValidationError(
                f"Invalid context, project '{p_name}' does not exist",
            )

        validated_context = ProjectDocumentContext(project=p_doc)
        self._validated_context = validated_context

        return validated_context

    async def validate_permission(self, user: UserDocument) -> bool:
        """Check user permission in context through validation"""
        await super().validate_permission(user)

        if not self._validated_context:
            raise ContextValidationError("Context document not been validated.")

        p_doc = self._validated_context.project

        is_superuser = user.is_superuser
        is_owner = user.id == p_doc.owner
        is_lead = user.id in p_doc.leads
        is_creator = user.id == p_doc.created_by

        if not (is_superuser or is_owner or is_lead or is_creator):
            raise UserPermissionDenied(
                f"User has no access to project '{p_doc.name}'.",
            )

        return True


class ProjectDomainValidator(DomainValidator):
    """Project run domain validator class"""

    async def validate_scheduled_start(self, p_create: ProjectCreate) -> ProjectCreate:
        """Project scheduled start <= scheduled_end"""

        if p_create.scheduled_start > p_create.scheduled_end:
            raise DomainValidationError(
                "Project 'scheduled_start' could not be larger than 'scheduled_end'.",
            )

        return p_create

    async def validate_scheduled_end(self, p_create: ProjectCreate) -> ProjectCreate:
        """Project scheduled start <= scheduled_end"""

        if p_create.scheduled_end < p_create.scheduled_start:
            raise DomainValidationError(
                "Project 'scheduled_end' could not be smaller than 'scheduled_start'.",
            )

        return p_create

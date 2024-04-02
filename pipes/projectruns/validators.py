from __future__ import annotations

from pipes.common.exceptions import (
    ContextValidationError,
    DomainValidationError,
)
from pipes.common.validators import DomainValidator
from pipes.projects.contexts import ProjectDocumentContext
from pipes.projects.validators import ProjectContextValidator
from pipes.projectruns.contexts import (
    ProjectRunSimpleContext,
    ProjectRunDocumentContext,
)
from pipes.projectruns.schemas import ProjectRunCreate, ProjectRunDocument


class ProjectRunContextValidator(ProjectContextValidator):
    """Project run context validator class"""

    async def validate_document(
        self,
        context: ProjectRunSimpleContext,
    ) -> ProjectRunDocumentContext:
        """Get project run document through validation"""
        p_context = await super().validate_document(context)
        p_doc = p_context.project

        pr_name = context.projectrun
        pr_doc = await ProjectRunDocument.find_one(ProjectRunDocument.name == pr_name)

        if not pr_doc:
            raise ContextValidationError(
                f"Invalid context, project run '{pr_name}' does not exist in project '{p_doc.name}'.",
            )

        validated_context = ProjectRunDocumentContext(
            project=p_doc,
            projectrun=pr_doc,
        )
        self._validated_context = validated_context

        return validated_context


class ProjectRunDomainValidator(DomainValidator):
    """Project run domain validator class"""

    def __init__(self, context: ProjectDocumentContext) -> None:
        self.context = context

    async def validate_scenarios(
        self,
        pr_create: ProjectRunCreate,
    ) -> ProjectRunCreate:
        """Project run scenarios should be within project scenarios"""
        p_doc = self.context.project
        p_scneario_pool = {s_obj.name for s_obj in p_doc.scenarios}

        diff = set(pr_create.scenarios).difference(p_scneario_pool)

        if diff:
            raise DomainValidationError(
                f"Invalid project run scenarions {pr_create.scenarios}, please check project scenarios configured.",
            )

        return pr_create

    async def validate_scheduled_start(
        self,
        pr_create: ProjectRunCreate,
    ) -> ProjectRunCreate:
        """Project run scheduled start dates should be within project schedules"""

        if pr_create.scheduled_start > pr_create.scheduled_end:
            raise DomainValidationError(
                "Project run 'scheduled_start' could not be larger than 'scheduled_end'.",
            )

        p_doc = self.context.project

        if pr_create.scheduled_start < p_doc.scheduled_start:
            raise DomainValidationError(
                f"Project run 'scheduled_start' could not be early than {p_doc.scheduled_start}",
            )

        if pr_create.scheduled_start > p_doc.scheduled_end:
            raise DomainValidationError(
                f"Project run 'scheduled_start' could not be late than {p_doc.scheduled_end}",
            )

        return pr_create

    async def validate_scheduled_end(
        self,
        pr_create: ProjectRunCreate,
    ) -> ProjectRunCreate:
        """Project run scheduled end dates should be within project schedules"""

        if pr_create.scheduled_end < pr_create.scheduled_start:
            raise DomainValidationError(
                "Project run 'scheduled_end' could not be smaller than 'scheduled_start'.",
            )

        p_doc = self.context.project

        if pr_create.scheduled_end < p_doc.scheduled_start:
            raise DomainValidationError(
                f"Project run 'scheduled_end' could not be early than {p_doc.scheduled_start}",
            )

        if pr_create.scheduled_end > p_doc.scheduled_end:
            raise DomainValidationError(
                f"Project run 'scheduled_end' could not be late than {p_doc.scheduled_end}",
            )

        return pr_create

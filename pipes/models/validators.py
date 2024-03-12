from __future__ import annotations

from pipes.common.exceptions import (
    ContextValidationError,
    DomainValidationError,
)
from pipes.common.validators import DomainValidator
from pipes.projectruns.validators import ProjectRunContextValidator
from pipes.models.contexts import ModelSimpleContext, ModelDocumentContext
from pipes.models.schemas import ModelDocument
from pipes.projectruns.schemas import ProjectRunDocument


class ModelContextValidator(ProjectRunContextValidator):
    """Model context validator class"""

    async def validate_document(
        self,
        context: ModelSimpleContext,
    ) -> ModelDocumentContext:
        """Get model document through validation"""
        pr_context = await super().validate_document(context)
        p_doc = pr_context.project
        pr_doc = pr_context.projectrun

        m_name = context.model
        m_doc = await ModelDocument.find_one(ModelDocument.name == m_name)

        if not m_doc:
            raise ContextValidationError(
                f"Invalid context, model '{m_name}' "
                f"does not exist in project run '{pr_doc.name}'"
                f"of project '{p_doc.name}'",
            )

        validated_context = ModelDocumentContext(
            project=p_doc,
            projectrun=pr_doc,
            model=m_doc,
        )
        self._validated_context = validated_context

        return validated_context


class ModelDomainValidator(DomainValidator):
    """Model domain validator class"""

    def __init__(self) -> None:
        self._cached_pr_doc = None

    async def _get_parent_projectrun(self, m_doc: ModelDocument) -> ProjectRunDocument:
        """Get project run document"""

        if self._cached_pr_doc:
            pr_doc = self._cached_pr_doc
        else:
            pr_id = m_doc.context.projectrun
            pr_doc = await ProjectRunDocument.get(pr_id)
            self._cached_pr_doc = pr_doc

        return pr_doc

    async def validate_scenario_mappings(
        self,
        m_doc: ModelDocument,
    ) -> ModelDocument:
        """Project run scenarios should be within project scenarios"""

        # Validate model scenarios
        m_scenario_pool = set()
        existing_m_docs = ModelDocument.find(
            {
                "context.project": m_doc.context.project,
                "context.projectrun": m_doc.context.projectrun,
            },
        )
        async for _m_doc in existing_m_docs:
            for scenario_mapping in _m_doc.scenario_mappings:
                m_s_name = scenario_mapping.model_scenario
                if m_s_name not in m_scenario_pool:
                    m_scenario_pool.add(m_s_name)
                else:
                    raise DomainValidationError(
                        f"Model scneario name '{m_s_name}' already defined in "
                        f"model '{_m_doc.name}' under same project and project run.",
                    )

        # Validate project scenarios
        pr_doc = await self._get_parent_projectrun(m_doc)
        pr_scneario_pool = set(pr_doc.scenarios)

        for scenario_mapping in m_doc.scenario_mappings:
            for p_s_name in scenario_mapping.project_scenarios:
                if p_s_name in pr_scneario_pool:
                    continue
                raise DomainValidationError(
                    "Invalid scenario mapping."
                    f"Scenario '{p_s_name}' has not been defined in project scenarios."
                    f"Valid scenarios include: {pr_scneario_pool}",
                )

        return m_doc

    async def validate_scheduled_start(
        self,
        m_doc: ModelDocument,
    ) -> ModelDocument:
        """Model scheduled start dates should be within project run schedules"""

        if m_doc.scheduled_start > m_doc.scheduled_end:
            raise DomainValidationError(
                "Model 'scheduled_start' could not be larger than 'scheduled_end'.",
            )

        pr_doc = await self._get_parent_projectrun(m_doc)

        if m_doc.scheduled_start < pr_doc.scheduled_start:
            raise DomainValidationError(
                f"Model 'scheduled_start' could not be early than {pr_doc.scheduled_start}",
            )

        if m_doc.scheduled_start > pr_doc.scheduled_end:
            raise DomainValidationError(
                f"Model 'scheduled_start' could not be late than {pr_doc.scheduled_end}",
            )

        return m_doc

    async def validate_scheduled_end(
        self,
        m_doc: ModelDocument,
    ) -> ModelDocument:
        """Model scheduled end dates should be within project run schedules"""

        if m_doc.scheduled_end < m_doc.scheduled_start:
            raise DomainValidationError(
                "Model 'scheduled_end' could not be smaller than 'scheduled_start'.",
            )

        pr_doc = await self._get_parent_projectrun(m_doc)

        if m_doc.scheduled_end < pr_doc.scheduled_start:
            raise DomainValidationError(
                f"Model 'scheduled_end' could not be early than {pr_doc.scheduled_start}",
            )

        if m_doc.scheduled_end > pr_doc.scheduled_end:
            raise DomainValidationError(
                f"Model 'scheduled_end' could not be late than {pr_doc.scheduled_end}",
            )

        return m_doc

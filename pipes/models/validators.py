from __future__ import annotations

from pipes.common.exceptions import ContextValidationError, DomainValidationError
from pipes.common.validators import DomainValidator
from pipes.db.document import DocumentDB
from pipes.projectruns.contexts import ProjectRunDocumentContext
from pipes.projectruns.validators import ProjectRunContextValidator
from pipes.models.contexts import ModelSimpleContext, ModelDocumentContext
from pipes.models.schemas import ModelCreate, ModelDocument


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
        docdb = DocumentDB()
        m_doc = await docdb.find_one(collection=ModelDocument, query={"name": m_name})

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

    def __init__(self, context: ProjectRunDocumentContext) -> None:
        self.context = context

    async def validate_scenario_mappings(
        self,
        m_create: ModelCreate,
    ) -> ModelCreate:
        """Project run scenarios should be within project scenarios"""

        # Validate model scenarios
        m_scenario_pool = set()
        docdb = DocumentDB()
        existing_m_docs = await docdb.find_all(
            collection=ModelDocument,
            query={
                "context.project": self.context.project,
                "context.projectrun": self.context.projectrun,
            },
        )
        for m_doc in existing_m_docs:
            for scenario_mapping in m_doc.scenario_mappings:
                m_scenario = scenario_mapping.model_scenario
                if m_scenario not in m_scenario_pool:
                    m_scenario_pool.add(m_scenario)
                else:
                    raise DomainValidationError(
                        f"Model scneario name '{m_scenario}' already defined in "
                        f"model '{m_doc.name}' under same project and project run.",
                    )

        # Validate project scenarios
        pr_doc = self.context.projectrun
        pr_scneario_pool = set(pr_doc.scenarios)

        for scenario_mapping in m_create.scenario_mappings:
            for p_s_name in scenario_mapping.project_scenarios:
                if p_s_name in pr_scneario_pool:
                    continue
                raise DomainValidationError(
                    "Invalid scenario mapping."
                    f"Scenario '{p_s_name}' has not been defined in project scenarios."
                    f"Valid scenarios include: {pr_scneario_pool}",
                )

        return m_create

    async def validate_scheduled_start(
        self,
        m_create: ModelCreate,
    ) -> ModelCreate:
        """Model scheduled start dates should be within project run schedules"""

        if m_create.scheduled_start > m_create.scheduled_end:
            raise DomainValidationError(
                "Model 'scheduled_start' could not be larger than 'scheduled_end'.",
            )

        pr_doc = self.context.projectrun

        if m_create.scheduled_start < pr_doc.scheduled_start:
            raise DomainValidationError(
                f"Model 'scheduled_start' could not be early than {pr_doc.scheduled_start}",
            )

        if m_create.scheduled_start > pr_doc.scheduled_end:
            raise DomainValidationError(
                f"Model 'scheduled_start' could not be late than {pr_doc.scheduled_end}",
            )

        return m_create

    async def validate_scheduled_end(
        self,
        m_create: ModelCreate,
    ) -> ModelCreate:
        """Model scheduled end dates should be within project run schedules"""

        if m_create.scheduled_end < m_create.scheduled_start:
            raise DomainValidationError(
                "Model 'scheduled_end' could not be smaller than 'scheduled_start'.",
            )

        pr_doc = self.context.projectrun

        if m_create.scheduled_end < pr_doc.scheduled_start:
            raise DomainValidationError(
                f"Model 'scheduled_end' could not be early than {pr_doc.scheduled_start}",
            )

        if m_create.scheduled_end > pr_doc.scheduled_end:
            raise DomainValidationError(
                f"Model 'scheduled_end' could not be late than {pr_doc.scheduled_end}",
            )

        return m_create

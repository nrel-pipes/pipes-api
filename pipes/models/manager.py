from __future__ import annotations

import logging
from datetime import datetime

from pymongo.errors import DuplicateKeyError

from pipes.common.exceptions import DocumentAlreadyExists
from pipes.db.manager import AbstractObjectManager
from pipes.projects.schemas import ProjectDocument
from pipes.projectruns.contexts import ProjectRunObjectContext, ProjectRunSimpleContext
from pipes.projectruns.schemas import ProjectRunDocument
from pipes.models.schemas import ModelCreate, ModelDocument, ModelRead
from pipes.models.validators import ModelDomainValidator
from pipes.teams.manager import TeamManager
from pipes.teams.schemas import TeamDocument
from pipes.users.schemas import UserDocument

logger = logging.getLogger(__name__)


class ModelManager(AbstractObjectManager):
    """Model object manager class"""

    async def create_model(
        self,
        p_doc: ProjectDocument,
        pr_doc: ProjectRunDocument,
        m_create: ModelCreate,
        user: UserDocument,
    ) -> ModelDocument:
        """Create a new model under given project and project run"""
        m_name = m_create.name
        m_doc_exists = await ModelDocument.find_one(
            {
                "context.project": p_doc.id,
                "context.projectrun": pr_doc.id,
                "name": m_name,
            },
        )
        if m_doc_exists:
            raise DocumentAlreadyExists(
                f"Model '{m_name}' already exists with "
                f"project run '{pr_doc.name}' under project '{p_doc.name}'.",
            )

        m_name = m_create.name
        context = ProjectRunObjectContext(project=p_doc.id, projectrun=pr_doc.id)
        m_doc = ModelDocument(
            context=context,
            # model information
            name=m_name,
            display_name=m_create.display_name,
            type=m_create.type,
            description=m_create.description,
            assumptions=m_create.assumptions,
            requirements=m_create.requirements,
            # TODO: default to the list from project or project run
            scheduled_start=m_create.scheduled_start,
            scheduled_end=m_create.scheduled_end,
            expected_scenarios=m_create.scenarios,
            scenario_mappings=m_create.scenario_mappings,
            other=m_create.other,
            # document information
            created_at=datetime.utcnow(),
            created_by=user.id,
            last_modified=datetime.utcnow(),
            modified_by=user.id,
        )

        domain_validator = ModelDomainValidator()
        m_doc = await domain_validator.validate(m_doc)

        # Create document
        try:
            m_doc = await m_doc.insert()
        except DuplicateKeyError:
            raise DocumentAlreadyExists(
                f"Model '{m_name}' already exists with "
                f"project run '{pr_doc.name}' under project '{p_doc.name}'.",
            )

        logger.info(
            "New model '%s' under project run '%s' of project '%s' was created successfully",
            m_name,
            pr_doc.name,
            p_doc.name,
        )
        return m_doc

    async def get_models(
        self,
        p_doc: ProjectDocument,
        pr_doc: ProjectRunDocument,
    ) -> list[ModelRead]:
        """Get all models under given project and project run"""
        m_docs = ProjectRunDocument.find(
            {
                "context.project": p_doc.id,
                "context.projectrun": pr_doc.id,
            },
        )

        team_manager = TeamManager()

        m_reads = []
        async for m_doc in m_docs:
            data = m_doc.model_dump()
            data["context"] = ProjectRunSimpleContext(
                project=p_doc.name,
                projectrun=pr_doc.name,
            )
            modeling_team_doc = await TeamDocument.get(m_doc.modeling_team)
            data["modeling_team"] = await team_manager.read_team(modeling_team_doc)
            m_reads.append(ModelRead.model_validate(data))
        return m_reads

    async def read_model(self, m_doc: ModelDocument):
        """Read a model from given model document"""
        p_id = m_doc.context.project
        p_doc = await ProjectDocument.get(p_id)

        pr_id = m_doc.context.projectrun
        pr_doc = await ProjectRunDocument.get(pr_id)

        team_manager = TeamManager()

        data = m_doc.model_dump()
        data["context"] = ProjectRunSimpleContext(
            project=p_doc.name,
            projectrun=pr_doc.name,
        )
        modeling_team_doc = await TeamDocument.get(m_doc.modeling_team)
        data["modeling_team"] = await team_manager.read_team(modeling_team_doc)

        return ModelRead.model_validate(data)

from __future__ import annotations

import logging
from datetime import datetime

from pymongo.errors import DuplicateKeyError

from pipes.common.exceptions import DocumentAlreadyExists, DocumentDoesNotExist
from pipes.db.manager import AbstractObjectManager
from pipes.common.constants import NodeLabel
from pipes.projects.contexts import ProjectDocumentContext
from pipes.projects.schemas import ProjectDocument
from pipes.projectruns.contexts import (
    ProjectRunDocumentContext,
    ProjectRunObjectContext,
    ProjectRunSimpleContext,
)
from pipes.projectruns.schemas import ProjectRunDocument
from pipes.models.schemas import (
    ModelCreate,
    ModelDocument,
    ModelRead,
    ModelUpdate,
    CatalogModelCreate,
    CatalogModelDocument,
)
from pipes.models.validators import ModelDomainValidator
from pipes.teams.manager import TeamManager
from pipes.teams.schemas import TeamDocument
from pipes.users.schemas import UserDocument

logger = logging.getLogger(__name__)


class ModelCatalogManager(AbstractObjectManager):
    async def create_model(
        self,
        m_create: CatalogModelCreate,
        user: UserDocument,
    ) -> CatalogModelDocument:

        m_doc = await self._create_model_document(m_create, user)
        return m_doc

    async def get_models(self) -> list[CatalogModelDocument]:
        """Read a model from given model document"""
        m_docs = await self.d.find_all(
            collection=CatalogModelDocument,
        )
        mc_reads = []
        for m_doc in m_docs:
            data = m_doc.model_dump()
            mc_reads.append(CatalogModelCreate.model_validate(data))
        return mc_reads

    async def read_model(
        self,
        model_name: str,
    ):
        """Retrieve a specific model from the database by name"""

        # Find the model in the database by name
        query = {"name": model_name}
        model_doc = await self.d.find_one(
            collection=CatalogModelDocument,
            query=query,
        )
        if not model_doc:
            raise ValueError(f"Model with name '{model_name}' not found")

        # Convert the document to a model document
        data = model_doc.model_dump()
        return CatalogModelDocument.model_validate(data)

    async def _create_model_document(
        self,
        m_create: CatalogModelCreate,
        user: UserDocument,
    ) -> CatalogModelDocument:
        """Create a new model under given project and project run"""

        # Check if model already exists or not
        m_name = m_create.name
        m_doc_exits = await self.d.exists(
            collection=CatalogModelDocument,
            query={
                "name": m_name,
            },
        )
        if m_doc_exits:
            raise DocumentAlreadyExists(
                f"Model '{m_name}' already exists in catalog.",
            )
        # object context
        current_time = datetime.now()
        m_doc = CatalogModelDocument(
            # model information
            name=m_name,
            display_name=m_create.display_name,
            type=m_create.type,
            description=m_create.description,
            assumptions=m_create.assumptions,
            requirements=m_create.requirements,
            expected_scenarios=m_create.expected_scenarios,
            other=m_create.other,
            created_at=current_time,
            created_by=user.id,
            last_modified=current_time,
            modified_by=user.id,
        )
        # Create document
        try:
            m_doc = await self.d.insert(m_doc)
        except DuplicateKeyError:
            raise DocumentAlreadyExists(
                f"Model document '{m_name}'.",
            )

        logger.info(
            "New model '%s' was created successfully under context: %s",
            m_name,
        )
        return m_doc


class ModelManager(AbstractObjectManager):
    """Model object manager class"""

    __label__ = NodeLabel.Model.value

    def __init__(
        self,
        context: ProjectRunDocumentContext | ProjectDocumentContext,
    ) -> None:
        self.context = context

    async def create_model(
        self,
        m_create: ModelCreate,
        user: UserDocument,
    ) -> ModelDocument:
        # Validate model domain business
        domain_validator = ModelDomainValidator(self.context)
        m_create = await domain_validator.validate(m_create)

        # Create model document
        m_doc = await self._create_model_document(m_create, user)

        return m_doc

    async def _get_modeling_team(self, p_name: str, modeling_team: str) -> TeamDocument:
        # Get or create team object
        team_manager = TeamManager(self.context)
        model_team_doc = await team_manager.get_team(modeling_team)
        if not model_team_doc:
            raise DocumentDoesNotExist(
                f"Modeling team '{modeling_team}' does not exist under project '{p_name}'.",
            )
        return model_team_doc

    async def _create_model_document(
        self,
        m_create: ModelCreate,
        user: UserDocument,
    ) -> ModelDocument:
        """Create a new model under given project and project run"""

        # Check if model already exists or not
        m_name = m_create.name
        p_doc = self.context.project
        pr_doc = self.context.projectrun

        m_doc_exits = await self.d.exists(
            collection=ModelDocument,
            query={
                "context.project": p_doc.id,
                "context.projectrun": pr_doc.id,
                "name": m_name,
            },
        )
        if m_doc_exits:
            raise DocumentAlreadyExists(
                f"Model '{m_name}' already exists under context: {self.context}",
            )

        # object context
        context = ProjectRunObjectContext(project=p_doc.id, projectrun=pr_doc.id)

        # modeling team
        t_name_or_id = m_create.modeling_team
        if isinstance(t_name_or_id, str):
            t_doc = await self.d.find_one(
                collection=TeamDocument,
                query={"context.project": p_doc.id, "name": t_name_or_id},
            )
            if not t_doc:
                raise DocumentDoesNotExist(
                    f"Modeling team '{t_name_or_id}' does not exist under project '{p_doc.name}'.",
                )
            modeling_team_id = t_doc.id
        else:
            # Assume it's already an ObjectId
            modeling_team_id = t_name_or_id

        m_doc = ModelDocument(
            context=context,
            # model information
            name=m_name,
            display_name=m_create.display_name,
            type=m_create.type,
            description=m_create.description,
            modeling_team=modeling_team_id,
            assumptions=m_create.assumptions,
            requirements=m_create.requirements,
            # TODO: default to the list from project or project run
            scheduled_start=m_create.scheduled_start,
            scheduled_end=m_create.scheduled_end,
            expected_scenarios=m_create.expected_scenarios,
            scenario_mappings=m_create.scenario_mappings,
            other=m_create.other,
            # document information
            created_at=datetime.now(),
            created_by=user.id,
            last_modified=datetime.now(),
            modified_by=user.id,
        )

        # Create document
        try:
            m_doc = await self.d.insert(m_doc)
        except DuplicateKeyError:
            raise DocumentAlreadyExists(
                f"Model document '{m_name}' already exists under context: {self.context}.",
            )

        logger.info(
            "New model '%s' was created successfully under context: %s",
            m_name,
            self.context,
        )
        return m_doc

    async def get_models(self) -> list[ModelRead]:
        """Get all models under given project and project run"""
        p_doc = self.context.project
        pr_doc = getattr(self.context, "projectrun", None)

        query = {
            "context.project": p_doc.id,
        }
        if pr_doc:
            query = {
                "context.project": p_doc.id,
                "context.projectrun": pr_doc.id,
            }

        m_docs = await self.d.find_all(
            collection=ModelDocument,
            query=query,
        )

        team_manager = TeamManager(self.context)
        m_reads = []
        for m_doc in m_docs:
            data = m_doc.model_dump()
            pr_doc = await self.d.get(ProjectRunDocument, m_doc.context.projectrun)
            data["context"] = ProjectRunSimpleContext(
                project=p_doc.name,
                projectrun=pr_doc.name,
            )
            modeling_team_doc = await self.d.get(
                collection=TeamDocument,
                id=m_doc.modeling_team,
            )
            data["modeling_team"] = await team_manager.read_team(modeling_team_doc)
            m_reads.append(ModelRead.model_validate(data))
        return m_reads

    async def read_model(self, m_doc: ModelDocument):
        """Read a model from given model document"""
        p_id = m_doc.context.project
        p_doc = await self.d.get(collection=ProjectDocument, id=p_id)

        pr_id = m_doc.context.projectrun
        pr_doc = await self.d.get(collection=ProjectRunDocument, id=pr_id)

        team_manager = TeamManager(context=self.context)

        data = m_doc.model_dump()
        data["context"] = ProjectRunSimpleContext(
            project=p_doc.name,
            projectrun=pr_doc.name,
        )
        modeling_team_doc = await self.d.get(
            collection=TeamDocument,
            id=m_doc.modeling_team,
        )
        data["modeling_team"] = await team_manager.read_team(modeling_team_doc)

        return ModelRead.model_validate(data)

    async def get_model(self, name: str) -> ModelDocument:
        """Get a specific model by name"""
        context = self.context

        if hasattr(context, "projectrun"):
            # If we have a project run context
            query = {
                "context.project": context.project.id,
                "context.projectrun": context.projectrun.id,
                "name": name,
            }
        else:
            # If we only have a project context
            query = {
                "context.project": context.project.id,
                "name": name,
            }

        model_doc = await self.d.find_one(
            collection=ModelDocument,
            query=query,
        )

        if not model_doc:
            project_name = context.project.name
            projectrun_name = context.projectrun.name

            if projectrun_name:
                raise DocumentDoesNotExist(
                    f"Model '{name}' not found in project '{project_name}', project run '{projectrun_name}'",
                )
            else:
                raise DocumentDoesNotExist(
                    f"Model '{name}' not found in project '{project_name}'",
                )

        return model_doc

    async def delete_model(
        self,
        project: ProjectDocument,
        projectrun: ProjectRunDocument,
        model: str,
    ) -> None:
        """Delete a model by name"""
        await self.d.delete_one(
            collection=ModelDocument,
            query={
                "context.project": project.id,
                "context.projectrun": projectrun.id,
                "name": model,
            },
        )

        project_name = self.context.project.name
        projectrun_name = self.context.projectrun.name

        if projectrun_name:
            logger.info(
                "Model '%s' of project '%s', project run '%s' deleted successfully",
                model,
                project_name,
                projectrun_name,
            )
        else:
            logger.info(
                "Model '%s' of project '%s' deleted successfully",
                model,
                project_name,
            )

    async def update_model(
        self,
        m_doc: ModelDocument,
        data: ModelUpdate,
        user: UserDocument,
    ) -> ModelDocument:
        """Update model document"""
        context = self.context

        # Check if model exists
        if m_doc is None:
            raise DocumentDoesNotExist(
                f"Model '{getattr(data, 'name', None)}' does not exist in context: {context}",
            )

        # If name is changing, check for duplicate
        if data.name and data.name != m_doc.name:
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
            other_m_doc = await self.d.find_one(
                collection=ModelDocument,
                query=query,
            )
            if other_m_doc:
                raise DocumentAlreadyExists(
                    f"Model '{data.name}' already exists in context: {context}",
                )

        update_fields = data.model_dump(exclude_unset=True)

        # If modeling_team is being updated, resolve to team id
        if "modeling_team" in update_fields and isinstance(
            update_fields["modeling_team"],
            str,
        ):
            p_name = context.project.name
            team_doc = await self._get_modeling_team(
                p_name,
                update_fields["modeling_team"],
            )
            update_fields["modeling_team"] = team_doc.id

        for k, v in update_fields.items():
            setattr(m_doc, k, v)
        m_doc.last_modified = datetime.now()
        m_doc.modified_by = user.id
        await m_doc.save()

        logger.info(
            "Model '%s' updated successfully under context: %s",
            m_doc.name,
            context,
        )
        return m_doc

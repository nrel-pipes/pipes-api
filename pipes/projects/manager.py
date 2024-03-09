from __future__ import annotations

import logging
from datetime import datetime
from itertools import chain

from pymongo.errors import DuplicateKeyError

from pipes.common.exceptions import (
    ContextValidationError,
    ContextPermissionDenied,
    DocumentAlreadyExists,
)
from pipes.db.manager import AbstractObjectManager
from pipes.projects.schemas import ProjectCreate, ProjectDocument
from pipes.teams.schemas import TeamDocument
from pipes.users.manager import UserManager
from pipes.users.schemas import UserDocument

logger = logging.getLogger(__name__)


class ProjectManager(AbstractObjectManager):

    async def validate_user_context(self, user: UserDocument, context: dict) -> dict:
        """Not required under project manager"""
        self._current_user = user  # type: ignore

        if "project" not in context:
            return {}

        # Validate project and convert to project document object.
        p_name = context["project"]
        p_doc = await ProjectDocument.find_one(ProjectDocument.name == p_name)

        if not p_doc:
            raise ContextValidationError(
                f"Invalid context, project '{p_name}' does not exist",
            )

        # Check user permission on p_doc
        is_superuser = self.current_user.is_superuser
        is_owner = self.current_user.id == p_doc.owner
        is_lead = self.current_user.id in p_doc.leads
        is_creator = self.current_user.id == p_doc.created_by

        if not (is_superuser or is_owner or is_lead or is_creator):
            raise ContextPermissionDenied(
                f"Invalid context, no access to project '{p_name}'.",
            )

        validated_context = dict(project=p_doc)
        self._validated_context = validated_context

        return validated_context

    async def create_project(self, p_create: ProjectCreate) -> ProjectDocument:
        """Create a new project"""
        user_manager = UserManager()
        p_owner_doc = await user_manager.get_or_create_user(p_create.owner)

        p_doc = ProjectDocument(
            # Basic information
            name=p_create.name,
            title=p_create.title,
            description=p_create.description,
            assumptions=p_create.assumptions,
            requirements=p_create.requirements,
            scenarios=p_create.scenarios,
            sensitivities=p_create.sensitivities,
            milestones=p_create.milestones,
            scheduled_start=p_create.scheduled_start,
            scheduled_end=p_create.scheduled_end,
            owner=p_owner_doc.id,
            # Record information
            created_at=datetime.utcnow(),
            created_by=self.current_user.id,
            last_modified=datetime.utcnow(),
            modified_by=self.current_user.id,
        )

        _p_doc = ProjectDocument.find_one(ProjectDocument.name == p_create.name)
        if _p_doc:
            await _p_doc.delete()

        try:
            await p_doc.insert()
        except DuplicateKeyError:
            raise DocumentAlreadyExists(f"Project '{p_create.name}' already exists.")

        logger.info("New project '%s' created successfully", p_create.name)
        return p_doc

    async def get_basic_projects(self) -> list[ProjectDocument]:
        """Get all projects of current user, basic information only."""
        # project created by current user
        p1_docs = await ProjectDocument.find(
            {"created_by": {"$eq": self.current_user.id}},
        ).to_list()

        # project owner is current user
        p2_docs = await ProjectDocument.find(
            {"owner": {"$eq": self.current_user.id}},
        ).to_list()

        # project leads containing current user
        p3_docs = await ProjectDocument.find({"leads": self.current_user.id}).to_list()

        # project team containing current user
        u_team_docs = await TeamDocument.find(
            {"members": self.current_user.id},
        ).to_list()
        p_ids = [t_doc.context.project for t_doc in u_team_docs]
        p4_docs = await ProjectDocument.find({"_id": {"$in": p_ids}}).to_list()

        # return projects
        p_docs = {}
        for p_doc in chain(p1_docs, p2_docs, p3_docs, p4_docs):
            if p_doc.id in p_docs:
                continue
            p_docs[p_doc.id] = p_doc

        return list(p_docs.values())

    async def get_project_detail(self) -> ProjectDocument:
        """Get project detail information."""
        return self.validated_context["project"]

    # async def update_project_detail(
    #     self,
    #     p_update: ProjectUpdate,
    # ) -> ProjectDocument | None:
    #     """Update project details"""
    #     p_doc = self.validated_context.project
    #     p_doc_other = await ProjectDocument.find_one(
    #         ProjectDocument.name == p_update.name,
    #     )
    #     if p_doc_other and (p_doc_other.id != p_doc.id):
    #         raise DocumentAlreadyExists(
    #             f"Project with name '{p_update.name}' already exists, use another name.",
    #         )

    #     data = p_update.model_dump()
    #     await p_doc.set(data)

    #     # await p_doc.save()
    #     logger.info("Project '%s' got updated successfully.", p_doc.name)

    #     return p_doc

    # async def get_project_detail(self) -> ProjectDocument:
    #     """Get project details"""
    #     p_doc = self.validated_context.project
    #     return p_doc

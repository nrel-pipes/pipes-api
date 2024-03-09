from __future__ import annotations

import logging

from pymongo.errors import DuplicateKeyError

from pipes.common.exceptions import (
    ContextPermissionDenied,
    ContextValidationError,
    DocumentAlreadyExists,
    DocumentDoesNotExist,
)
from pipes.db.manager import AbstractObjectManager
from pipes.projects.schemas import ProjectDocument
from pipes.teams.schemas import TeamCreate, TeamRead, TeamUpdate, TeamDocument
from pipes.users.manager import UserManager
from pipes.users.schemas import UserDocument

logger = logging.getLogger(__name__)


class TeamManager(AbstractObjectManager):
    """Manager class for team anagement"""

    async def validate_user_context(
        self,
        user: UserDocument,
        context: dict,
    ) -> dict:
        """Validate under project user context"""
        self._current_user = user

        # Check if project exists or not
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

    async def create_project_team(
        self,
        t_create: TeamCreate,
    ) -> TeamDocument:
        """Create new team"""
        p_doc = self.validated_context["project"]

        user_manager = UserManager()
        u_docs = [
            await user_manager.get_or_create_user(u_create)
            for u_create in t_create.members
        ]
        t_doc = TeamDocument(
            context={"project": p_doc.id},
            name=t_create.name,
            description=t_create.description,
            members=[u_doc.id for u_doc in u_docs],
        )

        try:
            await t_doc.insert()
        except DuplicateKeyError:
            raise DocumentAlreadyExists(
                f"Team '{t_create.name}' already exists under project '{p_doc.name}'.",
            )

        logger.info(
            "New team '%s' created successfully under project '%s'.",
            t_doc.name,
            p_doc.name,
        )
        return t_doc

    async def get_project_teams(self) -> list[TeamRead]:
        """Get all teams of given project."""
        p_doc = self.validated_context["project"]
        t_docs = await TeamDocument.find({"context.project": p_doc.id}).to_list()
        return t_docs

    async def update_project_team(
        self,
        team: str,
        data: TeamUpdate,
    ) -> TeamDocument:
        """Update team"""
        p_doc = self.validated_context["project"]

        # Validate team
        t_doc = await TeamDocument.find_one(
            {"context.project": p_doc.id, "name": team},
        )
        if t_doc is None:
            raise DocumentDoesNotExist(
                f"Team '{team}' not exist in project '{p_doc.name}'",
            )

        other_t_doc = await TeamDocument.find_one(
            {"context.project": p_doc.id, "name": data.name},
        )
        if other_t_doc and (t_doc.name == other_t_doc.name):
            raise DocumentAlreadyExists(
                f"Team '{data.name}' already exists in project '{p_doc.name}'",
            )

        user_manager = UserManager()
        member_doc_ids = set()
        for member in data.members:
            u_doc = await user_manager.get_or_create_user(member)
            member_doc_ids.add(u_doc.id)

        t_doc.name = data.name
        t_doc.description = data.description
        t_doc.members = member_doc_ids
        await t_doc.save()

        return t_doc

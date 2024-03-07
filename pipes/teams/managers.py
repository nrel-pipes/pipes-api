from __future__ import annotations

import logging

from pymongo.errors import DuplicateKeyError

from pipes.common import exceptions as E
from pipes.common.managers import AbstractObjectManager
from pipes.projects.contexts import ProjectTextContext, ProjectDocumentContext
from pipes.projects.schemas import ProjectDocument
from pipes.teams.schemas import TeamCreate, TeamDocument
from pipes.users.managers import UserManager
from pipes.users.schemas import UserCreate, UserRead, UserDocument

logger = logging.getLogger(__name__)


class TeamManager(AbstractObjectManager):
    """Manager class for team anagement"""

    def __init__(self, user: UserDocument) -> None:
        super().__init__(user)

    async def validate_context(
        self,
        context: ProjectTextContext,
    ) -> ProjectDocumentContext:
        """Validate under project user context"""
        # Check if project exists or not
        p_name = context.project
        p_doc = await ProjectDocument.find_one(ProjectDocument.name == p_name)

        if not p_doc:
            raise E.ContextValidationError(
                f"Invalid context, project '{p_name}' does not exist",
            )

        # Check user permission on p_doc
        is_superuser = self.user.is_superuser
        is_owner = self.user.id == p_doc.owner
        is_lead = self.user.id in p_doc.leads
        is_creator = self.user.id == p_doc.created_by

        if not (is_superuser or is_owner or is_lead or is_creator):
            raise E.ContextPermissionDenied(
                f"Invalid context, no access to project '{p_name}'.",
            )

        self.validated_context = ProjectDocumentContext(project=p_doc)
        return self.validated_context

    async def create_project_team(
        self,
        t_create: TeamCreate,
    ) -> TeamDocument:
        """Create new team"""
        p_doc = self.validated_context.project
        t_doc = TeamDocument(
            context={"project": p_doc.id},
            name=t_create.name,
            description=t_create.description,
        )

        try:
            await t_doc.insert()
        except DuplicateKeyError:
            raise E.DocumentAlreadyExists(
                f"Team '{t_create.name}' already exists under project '{p_doc.name}'.",
            )

        logger.info(
            "New team '%s' created successfully under project '%s'.",
            t_doc.name,
            p_doc.name,
        )
        return t_doc

    async def get_project_team_by_name(
        self,
        team: str,
    ) -> TeamDocument | None:
        """Get team by name"""
        p_doc = self.validated_context.project
        t_doc = await TeamDocument.find_one(
            {"context.project": p_doc.id, "name": team},
        )
        return t_doc

    async def update_project_team_members(
        self,
        team: str,
        u_creates: list[UserCreate],
    ) -> None:
        """Add team members"""
        p_doc = self.validated_context.project

        # Validate team
        t_doc = await TeamDocument.find_one(
            {"context.project": p_doc.id, "name": team},
        )
        if t_doc is None:
            raise E.DocumentDoesNotExist(
                f"Team '{team}' not exist under project '{p_doc.name}'",
            )

        # Validate users
        user_manager = UserManager()
        for u_create in u_creates:
            u_doc = await user_manager.get_or_create_user(u_create)
            u_doc.teams.add(t_doc.id)
            await u_doc.save()
            logger.info(
                "Add user '%s' into team '%s' under project '%s'.",
                u_doc.email,
                team,
                p_doc.name,
            )

    async def get_project_team_members(self, team: str) -> list[UserRead]:
        """Given a team, return all team members"""
        p_doc = self.validated_context.project

        t_doc = await TeamDocument.find_one(
            {"context.project": p_doc.id, "name": team},
        )
        if t_doc is None:
            raise E.DocumentDoesNotExist(
                f"Team '{team}' not exist under project '{p_doc.name}'.",
            )

        members = await UserDocument.find({"teams": t_doc.id}).to_list()
        return members

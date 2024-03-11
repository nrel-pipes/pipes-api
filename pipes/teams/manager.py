from __future__ import annotations

import logging

from pymongo.errors import DuplicateKeyError

from pipes.common.exceptions import DocumentAlreadyExists, DocumentDoesNotExist
from pipes.db.manager import AbstractObjectManager
from pipes.projects.schemas import ProjectDocument
from pipes.teams.schemas import TeamCreate, TeamRead, TeamUpdate, TeamDocument
from pipes.users.manager import UserManager
from pipes.users.schemas import UserDocument, UserRead

logger = logging.getLogger(__name__)


class TeamManager(AbstractObjectManager):
    """Manager class for team anagement"""

    async def create_project_team(
        self,
        p_doc: ProjectDocument,
        t_create: TeamCreate,
    ) -> TeamDocument:
        """Create new team"""
        t_name = t_create.name
        t_doc_exists = await TeamDocument.find_one(
            {"context.project": p_doc.id, "name": t_name}
        )
        if t_doc_exists:
            raise DocumentAlreadyExists(
                f"Team '{t_name}' already exists under project '{p_doc.name}'."
            )

        # Create tem
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
            t_doc = await t_doc.insert()
        except DuplicateKeyError:
            raise DocumentAlreadyExists(
                f"Team '{t_create.name}' already exists under project '{p_doc.name}'.",
            )

        # Update project teams reference
        p_doc.teams.append(t_doc.id)
        await p_doc.save()

        logger.info(
            "New team '%s' created successfully under project '%s'.",
            t_doc.name,
            p_doc.name,
        )
        return t_doc

    async def get_project_teams(self, p_doc: ProjectDocument) -> list[TeamRead]:
        """Get all teams of given project."""
        t_docs = TeamDocument.find({"context.project": p_doc.id})

        teams = []
        async for t_doc in t_docs:
            data = t_doc.model_dump()
            data["members"] = await self.get_team_members(t_doc)
            t_read = TeamRead.model_validate(data)
            teams.append(t_read)
        return teams

    async def get_team_members(self, t_doc: TeamDocument) -> list[UserRead]:
        u_docs = await UserDocument.find({"_id": {"$in": t_doc.members}}).to_list()
        members = [UserRead.model_validate(u_doc.model_dump()) for u_doc in u_docs]
        return members

    async def update_project_team(
        self,
        p_doc: ProjectDocument,
        team: str,
        data: TeamUpdate,
    ) -> TeamDocument:
        """Update team"""
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

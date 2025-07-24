from __future__ import annotations

import logging

from pymongo.errors import DuplicateKeyError

from pipes.common.exceptions import DocumentAlreadyExists, DocumentDoesNotExist
from pipes.db.manager import AbstractObjectManager
from pipes.common.constants import NodeLabel
from pipes.projects.contexts import ProjectDocumentContext
from pipes.teams.schemas import TeamCreate, TeamRead, TeamUpdate, TeamDocument
from pipes.users.manager import UserManager
from pipes.users.schemas import UserCreate, UserDocument, UserRead

logger = logging.getLogger(__name__)


class TeamManager(AbstractObjectManager):
    """Manager class for team management"""

    __label__ = NodeLabel.Team.value

    def __init__(self, context: ProjectDocumentContext) -> None:
        self.context = context

    async def create_team(self, t_create: TeamCreate) -> TeamDocument:
        """Create document in docdb"""
        # Add team member
        t_members = await self._add_team_members(t_create.members)
        t_doc = await self._create_team_document(t_create, t_members)
        return t_doc

    async def _add_team_members(
        self,
        t_members: list[UserCreate],
    ) -> list[UserDocument]:
        """Add user to team"""
        user_manager = UserManager()
        member_docs = []
        for u_create in t_members:
            u_doc = await user_manager.get_or_create_user(u_create)
            member_docs.append(u_doc)
        return member_docs

    async def _create_team_document(
        self,
        t_create: TeamCreate,
        t_members: list[UserDocument],
    ) -> TeamDocument:
        """Create new team"""
        t_name = t_create.name
        p_doc = self.context.project

        exists = await self.d.exists(
            collection=TeamDocument,
            query={"context.project": p_doc.id, "name": t_name},
        )
        if exists:
            raise DocumentAlreadyExists(
                f"Team document '{t_name}' already exists under project '{p_doc.name}'.",
            )

        u_doc_ids = [u_doc.id for u_doc in t_members]

        t_doc = TeamDocument(
            context={"project": p_doc.id},
            name=t_create.name,
            description=t_create.description,
            members=list(u_doc_ids),
        )

        try:
            t_doc = await self.d.insert(t_doc)
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

    # async def get_or_create_team(self, t_create: TeamCreate) -> TeamDocument:
    #     p_doc = self.context.project

    #     query = {"context.project": p_doc.id, "name": t_create.name}
    #     t_doc = await self.d.find_one(collection=TeamDocument, query=query)

    #     if not t_doc:
    #         t_doc = await self.create_team(t_create)

    #     return t_doc

    async def get_team(self, t_name: str) -> TeamDocument:
        p_doc = self.context.project
        query = {"context.project": p_doc.id, "name": t_name}
        t_doc = await self.d.find_one(collection=TeamDocument, query=query)
        return t_doc

    async def get_all_teams(self) -> list[TeamRead]:
        """Get all teams of given project."""
        p_doc = self.context.project
        t_docs = await self.d.find_all(
            collection=TeamDocument,
            query={"context.project": p_doc.id},
        )

        teams = []
        for t_doc in t_docs:
            t_read = await self.read_team(t_doc)
            teams.append(t_read)
        return teams

    async def get_team_members(self, t_doc: TeamDocument) -> list[UserRead]:
        u_docs = await self.d.find_all(
            collection=UserDocument,
            query={"_id": {"$in": t_doc.members}},
        )
        members = [UserRead.model_validate(u_doc.model_dump()) for u_doc in u_docs]
        return members

    async def update_team(
        self,
        team: str,
        data: TeamUpdate,
    ) -> TeamDocument:
        """Update team"""
        p_doc = self.context.project

        t_doc = await self.d.find_one(
            collection=TeamDocument,
            query={"context.project": p_doc.id, "name": team},
        )
        if t_doc is None:
            raise DocumentDoesNotExist(
                f"Team '{team}' not exist in project '{p_doc.name}'",
            )

        if data.name != team:
            other_t_doc = await self.d.find_one(
                collection=TeamDocument,
                query={"context.project": p_doc.id, "name": data.name},
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
        t_doc.members = list(member_doc_ids)
        await t_doc.save()

        return t_doc

    async def read_team(self, t_doc: TeamDocument) -> TeamRead:
        """Convert team document to read object"""
        data = t_doc.model_dump()
        p_doc = self.context.project
        data["context"]["project"] = p_doc.name
        data["members"] = await self.get_team_members(t_doc)
        return TeamRead.model_validate(data)

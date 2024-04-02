from __future__ import annotations

import logging

from pymongo.errors import DuplicateKeyError

from pipes.common.exceptions import (
    DocumentAlreadyExists,
    DocumentDoesNotExist,
    VertexAlreadyExists,
)
from pipes.db.manager import AbstractObjectManager
from pipes.graph.constants import VertexLabel, EdgeLabel
from pipes.graph.schemas import TeamVertexProperties, TeamVertex
from pipes.projects.contexts import ProjectDocumentContext
from pipes.teams.schemas import TeamCreate, TeamRead, TeamUpdate, TeamDocument
from pipes.users.manager import UserManager
from pipes.users.schemas import UserCreate, UserDocument, UserRead

logger = logging.getLogger(__name__)


class TeamManager(AbstractObjectManager):
    """Manager class for team anagement"""

    __label__ = VertexLabel.Team.value

    def __init__(self, context: ProjectDocumentContext) -> None:
        super().__init__(TeamDocument)
        self.context = context

    async def create_team(self, t_create: TeamCreate) -> TeamDocument:
        """Create vetex in neptune, then create document in docdb"""
        p_doc = self.context.project

        # Add team vertex
        t_vertex = await self._create_team_vertex(p_doc.name, t_create.name)

        # Add team member vertexes and edges (member to Team)
        t_members = await self._add_team_members(t_vertex, t_create.members)

        t_doc = await self._create_team_document(
            t_create,
            t_members,
            t_vertex,
        )
        return t_doc

    async def _add_team_members(
        self,
        t_vertex: TeamVertex,
        t_members: list[UserCreate],
    ) -> list[UserDocument]:
        """Create user vertexes in neptune"""
        user_manager = UserManager()
        member_docs = []
        for u_create in t_members:
            u_doc = await user_manager.get_or_create_user(u_create)
            self.n.add_edge(u_doc.vertex.id, t_vertex.id, EdgeLabel.member.value)
            member_docs.append(u_doc)
        return member_docs

    async def _create_team_vertex(
        self,
        p_name: str,
        t_name: str,
    ) -> TeamVertex:
        properties = {"project": p_name, "name": t_name}
        if self.n.exists(self.label, **properties):
            raise VertexAlreadyExists(
                f"Team vertex {properties} already exists under project {p_name}.",
            )

        properties_model = TeamVertexProperties(**properties)
        properties = properties_model.model_dump()
        t_vtx = self.n.add_v(self.label, **properties)

        # Dcoument creation
        team_vertex_model = TeamVertex(
            id=t_vtx.id,
            label=self.label,
            properties=properties_model,
        )
        return team_vertex_model

    async def _get_team_vertex(
        self,
        p_name: str,
        t_name: str,
    ) -> TeamVertex | None:
        """Create vetex in neptune"""
        properties = {"project": p_name, "name": t_name}
        vlist = self.n.get_v(self.label, **properties)
        if not vlist:
            return None

        t_vtx = vlist[0]
        properties_model = TeamVertexProperties(**properties)
        team_vertex_model = TeamVertex(
            id=t_vtx.id,
            label=self.label,
            properties=properties_model,
        )
        return team_vertex_model

    async def _create_team_document(
        self,
        t_create: TeamCreate,
        t_members: list[UserDocument],
        t_vertex: TeamVertex,
    ) -> TeamDocument:
        """Create new team"""
        t_name = t_create.name
        p_doc = self.context.project

        if await self.d.exists({"context.project": p_doc.id, "name": t_name}):
            raise DocumentAlreadyExists(
                f"Team document '{t_name}' already exists under project '{p_doc.name}'.",
            )

        u_doc_ids = [u_doc.id for u_doc in t_members]

        t_doc = TeamDocument(
            vertex=t_vertex,
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
    #     t_doc = await self.d.find_one(query)

    #     if not t_doc:
    #         t_doc = await self.create_team(t_create)

    #     return t_doc

    async def get_team(self, t_name: str) -> TeamDocument:
        p_doc = self.context.project
        query = {"context.project": p_doc.id, "name": t_name}
        t_doc = await self.d.find_one(query)
        return t_doc

    async def get_all_teams(self) -> list[TeamRead]:
        """Get all teams of given project."""
        p_doc = self.context.project
        t_docs = await self.d.find_all({"context.project": p_doc.id})

        teams = []
        for t_doc in t_docs:
            t_read = await self.read_team(t_doc)
            teams.append(t_read)
        return teams

    async def get_team_members(self, t_doc: TeamDocument) -> list[UserRead]:
        u_docs = await UserDocument.find({"_id": {"$in": t_doc.members}}).to_list()
        members = [UserRead.model_validate(u_doc.model_dump()) for u_doc in u_docs]
        return members

    async def update_team(
        self,
        team: str,
        data: TeamUpdate,
    ) -> TeamDocument:
        """Update team"""
        p_doc = self.context.project

        t_doc = await self.d.find_one({"context.project": p_doc.id, "name": team})
        if t_doc is None:
            raise DocumentDoesNotExist(
                f"Team '{team}' not exist in project '{p_doc.name}'",
            )

        other_t_doc = await self.d.find_one(
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

            # Add edge (member of Team)
            # TODO: may case duplicated edges?
            self.n.add_edge(u_doc.vertex.id, t_doc.vertex.id, EdgeLabel.member.value)

            member_doc_ids.add(u_doc.id)

        t_doc.name = data.name
        t_doc.description = data.description
        t_doc.members = list(member_doc_ids)
        await t_doc.save()

        return t_doc

    async def read_team(self, t_doc: TeamDocument) -> TeamRead:
        """Convert team document to read object"""
        data = t_doc.model_dump()
        data["members"] = await self.get_team_members(t_doc)
        return TeamRead.model_validate(data)

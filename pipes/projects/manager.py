from __future__ import annotations

import logging
from datetime import datetime
from itertools import chain

from pymongo.errors import DuplicateKeyError

from pipes.common.exceptions import DocumentAlreadyExists, VertexAlreadyExists
from pipes.db.manager import AbstractObjectManager
from pipes.graph.constants import VertexLabel, EdgeLabel
from pipes.graph.schemas import ProjectVertexProperties, ProjectVertex
from pipes.projects.schemas import ProjectCreate, ProjectDetailRead, ProjectDocument
from pipes.projects.validators import ProjectDomainValidator
from pipes.teams.schemas import TeamDocument, TeamBasicRead
from pipes.users.manager import UserManager
from pipes.users.schemas import UserCreate, UserDocument, UserRead

logger = logging.getLogger(__name__)


class ProjectManager(AbstractObjectManager):

    __label__ = VertexLabel.Project.value

    async def create_project(
        self,
        p_create: ProjectCreate,
        user: UserDocument,
    ) -> ProjectDocument:
        # Validate project domain business

        domain_validator = ProjectDomainValidator()
        p_create = await domain_validator.validate(p_create)

        # Get or create user vertex & document
        p_owner = await self._get_or_create_project_owner(p_create.owner)

        # Create project vertex & document
        p_vertex = await self._create_project_vertex(p_create.name)
        p_doc = await self._create_project_document(p_create, p_vertex, p_owner, user)

        # Add edget: user owns project
        u_vtx_id = p_owner.vertex.id
        p_vtx_id = p_vertex.id
        self.n.add_edge(u_vtx_id, p_vtx_id, EdgeLabel.owns.value)

        return p_doc

    async def _create_project_vertex(self, p_name: str) -> ProjectVertex:
        properties = {"name": p_name}
        if self.n.exists(self.label, **properties):
            raise VertexAlreadyExists(f"Project vertex {properties} already exists.")

        properties_model = ProjectVertexProperties(**properties)
        properties = properties_model.model_dump()
        p_vtx = self.n.add_v(self.label, **properties)

        # Dcoument creation
        p_vtx_model = ProjectVertex(
            id=p_vtx.id,
            label=self.label,
            properties=properties_model,
        )
        return p_vtx_model

    async def _get_or_create_project_owner(self, owner: UserCreate) -> UserDocument:
        # Get or create user object
        user_manager = UserManager()
        p_owner_doc = await user_manager.get_or_create_user(owner)
        return p_owner_doc

    async def _create_project_document(
        self,
        p_create: ProjectCreate,
        p_vertex: ProjectVertex,
        p_owner: UserDocument,
        user: UserDocument,
    ) -> ProjectDocument:
        """Create a new project"""
        # NOTE: avoid db collection issue introduced from manual operations, like db.projects.drop()
        p_name = p_create.name
        p_doc_exists = self.d.exists(collection=ProjectDocument, query={"name": p_name})
        if p_doc_exists:
            raise DocumentAlreadyExists(f"Project '{p_create.name}' already exists.")

        p_doc = ProjectDocument(
            vertex=p_vertex,
            # project information
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
            owner=p_owner.id,
            # document information
            created_at=datetime.now(),
            created_by=user.id,
            last_modified=datetime.now(),
            modified_by=user.id,
        )

        try:
            await p_doc.insert()
        except DuplicateKeyError:
            raise DocumentAlreadyExists(f"Project '{p_create.name}' already exists.")

        logger.info("New project '%s' created successfully", p_create.name)
        return p_doc

    async def get_basic_projects(self, user: UserDocument) -> list[ProjectDocument]:
        """Get all projects of current user, basic information only."""
        # project created by current user
        p1_docs = await self.d.find_all(
            collection=ProjectDocument,
            query={"created_by": {"$eq": user.id}},
        )

        # project owner is current user
        p2_docs = await self.d.find_all(
            collection=ProjectDocument,
            query={"owner": {"$eq": user.id}},
        )

        # project leads containing current user
        p3_docs = await self.d.find_all(
            collection=ProjectDocument,
            query={"leads": user.id},
        )

        # project team containing current user
        u_team_docs = await self.d.find_all(
            collection=TeamDocument,
            query={"members": user.id},
        )
        p_ids = [t_doc.context.project for t_doc in u_team_docs]
        p4_docs = await self.d.find_all(
            collection=ProjectDocument,
            query={"_id": {"$in": p_ids}},
        )

        # return projects
        p_docs = {}
        for p_doc in chain(p1_docs, p2_docs, p3_docs, p4_docs):
            if p_doc.id in p_docs:
                continue
            p_docs[p_doc.id] = p_doc

        return list(p_docs.values())

    # async def update_project_detail(
    #     self,
    #     p_update: ProjectUpdate,
    # ) -> ProjectDocument | None:
    #     """Update project details"""
    #     p_doc = self.validated_context.project
    #     p_doc_other = await self.d.find_one(
    #         collection=ProjectDocument,
    #         query={"name": p_update.name},
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

    async def read_project_detail(self, p_doc: ProjectDocument) -> ProjectDetailRead:
        """Dump project document into dictionary"""
        # owner
        owner_id = p_doc.owner
        owner_doc = await UserDocument.get(owner_id)
        owner_read = UserRead.model_validate(owner_doc.model_dump())

        # leads
        lead_docs = await self.d.find_all(
            collection=UserDocument,
            query={"_id": {"$in": p_doc.leads}},
        )
        lead_reads = []
        for lead_doc in lead_docs:
            lead_read = UserRead.model_validate(lead_doc.model_dump())
            lead_reads.append(lead_read)

        # teams
        team_docs = await self.d.find_all(
            collection=TeamDocument,
            query={"_id": {"$in": p_doc.teams}},
        )
        team_reads = []
        for team_doc in team_docs:
            team_read = TeamBasicRead(
                name=team_doc.name,
                description=team_doc.description,
            )
            team_reads.append(team_read)

        # project read
        p_data = p_doc.model_dump()
        p_data.update(
            {
                "owner": owner_read,
                "leads": lead_reads,
                "teams": team_reads,
            },
        )
        p_read = ProjectDetailRead.model_validate(p_data)

        return p_read

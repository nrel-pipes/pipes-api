from __future__ import annotations

import logging
from datetime import datetime
from itertools import chain

from pymongo.errors import DuplicateKeyError
from fastapi import HTTPException
from pipes.common.exceptions import DocumentAlreadyExists, VertexAlreadyExists
from pipes.db.manager import AbstractObjectManager
from pipes.graph.constants import VertexLabel, EdgeLabel
from pipes.graph.schemas import ProjectVertexProperties, ProjectVertex
from pipes.projects.schemas import ProjectCreate, ProjectDetailRead, ProjectDocument, ProjectUpdate
from pipes.projects.validators import ProjectDomainValidator, ProjectUpdateDomainValidator, ProjectContextValidator
from pipes.teams.schemas import TeamDocument, TeamBasicRead
from pipes.users.manager import UserManager
from pipes.users.schemas import UserCreate, UserDocument, UserRead
from pipes.common.exceptions import (
    DocumentAlreadyExists,
    VertexAlreadyExists,
    DocumentDoesNotExist
)
from pipes.projectruns.schemas import ProjectRunRead

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
        self.n.add_e(u_vtx_id, p_vtx_id, EdgeLabel.owns.value)

        return p_doc
    async def get_project(self, project: str, user: UserDocument):
        ...


    async def update_project(
        self,
        p_update: ProjectUpdate,
        projectrun_docs: list[ProjectRunRead],
        project: str,
        user: UserDocument,
    ) -> ProjectDocument:
        """
        - Get project runs. Then validate project runs against the project.
        """

        # Validate project domain business
        # Make sure to check, project exists. Also, that schedule is within bounds of children. Also, that includes all the scenarios that are found in the children.
        domain_validator = ProjectUpdateDomainValidator()
        p_update = await domain_validator.project_validate(p_update, projectrun_docs)
        p_owner = await self._get_or_create_project_owner(p_update.owner)
        p_update_doc = await self._update_project_document(p_update, p_owner, project, user)
        return p_update_doc

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

    async def _update_project_document(
        self,
        p_update: ProjectUpdate,
        p_owner: UserDocument,
        project: str,
        user: UserDocument,
    ):
        """
        Logic to function:
        - If project name does not exist, throw error.
        - If project name not equal to new name and new name does exist, throw error. 
        Overwrite the existing project. 
        """
        # Validation
        old_p_doc_exists = await self.d.exists(
            collection=ProjectDocument,
            query={"name": project},
        )
        p_doc_exists = await self.d.exists(
            collection=ProjectDocument,
            query={"name": p_update.name},
        )
        if not old_p_doc_exists:
            raise DocumentDoesNotExist(f"Project '{p_update.name}' does not exist.")
        if project != p_update.name and p_doc_exists:
            raise DocumentAlreadyExists(f"You are renaming '{project}' to an existing project, {p_update.name}.")
        
        # Get the existing document
        existing_p_doc = await self.d.find_one(
            collection=ProjectDocument,
            query={"name": project},
        )

        # Prepare update dictionary
        update_dict = {
            "$set": {
                'name': p_update.name,
                'title': p_update.title,
                'description': p_update.description,
                'assumptions': p_update.assumptions,
                'requirements': p_update.requirements,
                'scenarios': p_update.scenarios,
                'sensitivities': p_update.sensitivities,
                'milestones': p_update.milestones,
                'scheduled_start': p_update.scheduled_start,
                'scheduled_end': p_update.scheduled_end,
                'owner': p_owner.id,
                'last_modified': datetime.now(),
                'modified_by': user.id
            }
        }

        await self.d.update_one(
            collection=ProjectDocument,
            find={"name": project},
            update=update_dict
        )

        updated_doc = await self.d.find_one(
            collection=ProjectDocument,
            query={"name": p_update.name}
        )
        return updated_doc
    
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
        p_doc_exists = await self.d.exists(
            collection=ProjectDocument,
            query={"name": p_name},
        )
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
        if user.is_superuser:
            available_p_docs = await self.d.find_all(collection=ProjectDocument)
        else:
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

            # TODO: A hardcoded for all PIPES users accessing the test project.
            p5_docs = await self.d.find_all(
                collection=ProjectDocument,
                query={"name": {"$in": ["test1", "pipes101"]}},
            )

            available_p_docs = chain(p1_docs, p2_docs, p3_docs, p4_docs, p5_docs)

        # return projects
        p_docs = {}
        for p_doc in available_p_docs:
            if p_doc.id in p_docs:
                continue
            p_docs[p_doc.id] = p_doc

        return list(p_docs.values())

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

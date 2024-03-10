from __future__ import annotations

import logging
from datetime import datetime
from itertools import chain

from pymongo.errors import DuplicateKeyError

from pipes.common.exceptions import DocumentAlreadyExists
from pipes.db.manager import AbstractObjectManager
from pipes.projects.schemas import ProjectCreate, ProjectDocument, ProjectDetailRead
from pipes.teams.schemas import TeamDocument, TeamBasicRead
from pipes.users.manager import UserManager
from pipes.users.schemas import UserDocument, UserRead

logger = logging.getLogger(__name__)


class ProjectManager(AbstractObjectManager):

    async def create_project(
        self,
        p_create: ProjectCreate,
        user: UserDocument,
    ) -> ProjectDocument:
        """Create a new project"""
        user_manager = UserManager()
        p_owner_doc = await user_manager.get_or_create_user(p_create.owner)

        p_doc = ProjectDocument(
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
            owner=p_owner_doc.id,
            # document information
            created_at=datetime.utcnow(),
            created_by=user.id,
            last_modified=datetime.utcnow(),
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
        p1_docs = await ProjectDocument.find(
            {"created_by": {"$eq": user.id}},
        ).to_list()

        # project owner is current user
        p2_docs = await ProjectDocument.find(
            {"owner": {"$eq": user.id}},
        ).to_list()

        # project leads containing current user
        p3_docs = await ProjectDocument.find({"leads": user.id}).to_list()

        # project team containing current user
        u_team_docs = await TeamDocument.find({"members": user.id}).to_list()
        p_ids = [t_doc.context.project for t_doc in u_team_docs]
        p4_docs = await ProjectDocument.find({"_id": {"$in": p_ids}}).to_list()

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

    async def read_project_detail(self, p_doc: ProjectDocument) -> ProjectDetailRead:
        """Dump project document into dictionary"""
        # owner
        owner_id = p_doc.owner
        owner_doc = await UserDocument.get(owner_id)
        owner_read = UserRead.model_validate(owner_doc.model_dump())

        # leads
        lead_docs = UserDocument.find({"_id": {"$in": p_doc.leads}})
        lead_reads = []
        async for lead_doc in lead_docs:
            lead_read = UserRead.model_validate(lead_doc.model_dump())
            lead_reads.append(lead_read)

        # teams
        team_docs = TeamDocument.find({"_id": {"$in": p_doc.teams}})
        team_reads = []
        async for team_doc in team_docs:
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

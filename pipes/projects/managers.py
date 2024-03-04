from __future__ import annotations

import logging
from datetime import datetime
from itertools import chain

from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError

from pipes.common.manager import ObjectManager
from pipes.common.utilities import generate_shortuuid
from pipes.projects.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectDocument,
    ProjectRunCreate,
    ProjectRunRead,
)
from pipes.users.managers import UserManager

logger = logging.getLogger(__name__)


class ProjectManager(ObjectManager):

    async def create_project(self, p_create: ProjectCreate) -> ProjectDocument | None:
        """Create a new project"""
        p_doc = ProjectDocument(
            # Public id
            pub_id=generate_shortuuid(),
            # Basic information
            name=p_create.name,
            title=p_create.title,
            description=p_create.description,
            owner=self.current_user.id,
            leads=[self.current_user.id],
            # Record information
            created_at=datetime.utcnow(),
            created_by=self.current_user.id,
            last_modified=datetime.utcnow(),
            modified_by=self.current_user.id,
        )
        try:
            await p_doc.insert()
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Project '{p_create.name}' already exists.",
            )
        logger.info("New project '%s' created successfully", p_create.name)
        return p_doc

    async def get_projects_of_current_user(self) -> list[ProjectDocument] | None:
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
        user_manager = UserManager()
        user_team_ids = await user_manager.get_user_team_ids(self.current_user)
        p4_docs = await ProjectDocument.find({"teams": user_team_ids}).to_list()

        # return projects
        p_docs = {}
        for p_doc in chain(p1_docs, p2_docs, p3_docs, p4_docs):
            if p_doc.id in p_docs:
                continue
            p_docs[p_doc.id] = p_doc

        return list(p_docs.values())

    async def update_project_details(
        self,
        pub_id: str,
        p_update: ProjectUpdate,
    ) -> ProjectDocument | None:
        """Update project details"""
        p_doc = await ProjectDocument.find_one(ProjectDocument.pub_id == pub_id)
        if p_doc is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id '{pub_id}' not found.",
            )

        if not self.current_user_can_update(p_doc):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Forbiden. No edit permission to project '{pub_id}'.",
            )

        data = p_update.model_dump()
        await p_doc.set(data)

        # await p_doc.save()
        logger.info("Project got updated successfully.")

        return p_doc

    async def get_project_details(self, pub_id: str) -> ProjectDocument | None:
        """Get project details"""
        p_doc = await ProjectDocument.find_one(ProjectDocument.pub_id == pub_id)
        if p_doc is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id '{pub_id}' not found.",
            )
        if not self.current_user_can_read(p_doc):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbiden, no access to project '{pub_id}'.",
            )
        return p_doc

    async def current_user_can_read(self, p_doc: ProjectDocument) -> bool:
        """Validate if current user can read this project

        One of the following conditions must be met:
         - current user is the project owner
         - current user is project creator
         - current user is one of the project leads
         - current user belongs to one of the project teams
        """
        if self.current_user.id == p_doc.owner:
            return True

        if self.current_user.id == p_doc.created_by:
            return True

        if self.current_user.id in p_doc.leads:
            return True

        teams = p_doc.teams.intersection(self.current_user.teams)
        if len(teams) >= 1:
            return True

        return False

    async def current_user_can_update(self, p_doc: ProjectDocument) -> bool:
        """Validate if current user can edit this project

        One of the following conditions must be met:
         - current user is the project owner
         - current user is project creator
         - current user is one of the project leads
        """
        if self.current_user.id == p_doc.owner:
            return True

        if self.current_user.id == p_doc.created_by:
            return True

        if self.current_user.id in p_doc.leads:
            return True

        return False


class ProjectRunManager(ObjectManager):

    def create_projectrun(
        self,
        projectrun_create: ProjectRunCreate,
    ) -> ProjectRunRead | None:
        pass

    def get_projectrun_by_name(self, projectrun_name: str) -> ProjectRunRead | None:
        pass

    def get_projectruns_under_project(
        self,
        project_name: str,
    ) -> list[ProjectRunRead] | None:
        pass

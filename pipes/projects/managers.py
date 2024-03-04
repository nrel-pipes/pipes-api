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
        return None


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

from __future__ import annotations

import logging
from datetime import datetime

from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError

from pipes.db.manager import PipesObjectManager
from pipes.projects.schemas import (
    ProjectCreate,
    ProjectReadBasic,
    ProjectDocument,
    ProjectRunCreate,
    ProjectRunRead,
)

logger = logging.getLogger(__name__)


class ProjectManager(PipesObjectManager):

    async def create_project(self, p_create: ProjectCreate) -> ProjectReadBasic | None:
        """Create a new project"""
        p_doc = ProjectDocument(
            # Basic information
            name=p_create.name,
            title=p_create.title,
            description=p_create.description,
            # Record information
            created_at=datetime.utcnow(),
            created_by=self.current_user.email,
            last_modified=datetime.utcnow(),
            modified_by=self.current_user.email,
        )
        try:
            await p_doc.insert()
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Project '{p_create.name}' already exists.",
            )
        logger.info("New project '%s' created successfully", p_create.name)
        p_read_basic = p_doc  # Pydantic ignore extra fields
        return p_read_basic

    async def get_current_user_projects(self) -> list[ProjectReadBasic] | None:
        """Get all projects of current user, basic information only."""
        p_docs = await ProjectDocument.find().to_list()

        p_read_basics = p_docs
        return p_read_basics


class ProjectRunManager(PipesObjectManager):

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

from __future__ import annotations

import logging
from datetime import datetime

from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError

from pipes.db.manager import DocumentGrahpObjectManager
from pipes.projects.schemas import (
    ProjectCreate,
    ProjectRead,
    ProjectDocument,
    ProjectRunCreate,
    ProjectRunRead,
)

logger = logging.getLogger(__name__)


class ProjectManager(DocumentGrahpObjectManager):

    async def create_project(self, project_create: ProjectCreate) -> ProjectRead | None:
        """Create a new project"""
        project_doc = ProjectDocument(
            name=project_create.name,
            title=project_create.title,
            description=project_create.description,
            created_at=datetime.utcnow(),
            created_by=self.current_user.email,
            last_modified=datetime.utcnow(),
            modified_by=self.current_user.email,
        )
        try:
            await project_doc.insert()
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Project '{project_create.name}' already exists.",
            )
        logger.info("New project '%s' created successfully", project_create.name)
        project_read = ProjectRead(
            name=project_doc.name,
            title=project_doc.title,
            description=project_doc.description,
        )
        return project_read

    async def get_project_by_name(self, project_name: str) -> ProjectRead | None:
        pass


class ProjectRunManager(DocumentGrahpObjectManager):

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

from __future__ import annotations

import logging

from pipes.db.manager import DocumentGrahpObjectManager
from pipes.projects.schemas import (
    ProjectCreate,
    ProjectRead,
    ProjectRunCreate,
    ProjectRunRead,
)

logger = logging.getLogger(__name__)


class ProjectManager(DocumentGrahpObjectManager):

    def create_project(self, project_create: ProjectCreate) -> ProjectRead | None:
        pass

    def get_project_by_name(self, project_name: str) -> ProjectRead | None:
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

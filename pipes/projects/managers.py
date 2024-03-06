from __future__ import annotations

import logging
from datetime import datetime
from itertools import chain

from pymongo.errors import DuplicateKeyError

from pipes.common import exceptions as E
from pipes.common.managers import AbstractObjectManager
from pipes.projects.contexts import ProjectTextContext, ProjectDocumentContext
from pipes.projects.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectDocument,
    ProjectRunCreate,
    ProjectRunRead,
)
from pipes.users.managers import UserManager
from pipes.users.schemas import UserDocument

logger = logging.getLogger(__name__)


class ProjectManager(AbstractObjectManager):
    """Project management class"""

    def __init__(self, user: UserDocument) -> None:
        super().__init__(user)

    async def validate_context(
        self,
        context: ProjectTextContext,
    ) -> ProjectDocumentContext:
        """Not required under project manager"""
        p_name = context.project
        p_doc = await ProjectDocument.find_one(ProjectDocument.name == p_name)

        if not p_doc:
            raise E.ContextValidationError(
                f"Invalid context, project '{p_name}' does not exist",
            )

        # Check user permission on p_doc
        is_superuser = self.user.is_superuser
        is_owner = self.user.id == p_doc.owner
        is_lead = self.user.id in p_doc.leads
        is_creator = self.user.id == p_doc.created_by

        if not (is_superuser or is_owner or is_lead or is_creator):
            raise E.ContextPermissionDenied(
                f"Invalid context, no access to project '{p_name}'.",
            )

        self.validated_context = ProjectDocumentContext(project=p_doc)
        return self.validated_context

    async def create_project(self, p_create: ProjectCreate) -> ProjectDocument | None:
        """Create a new project"""
        p_doc = ProjectDocument(
            # Basic information
            name=p_create.name,
            title=p_create.title,
            description=p_create.description,
            owner=self.user.id,
            leads=[self.user.id],
            # Record information
            created_at=datetime.utcnow(),
            created_by=self.user.id,
            last_modified=datetime.utcnow(),
            modified_by=self.user.id,
        )
        try:
            await p_doc.insert()
        except DuplicateKeyError:
            raise E.DocumentAlreadyExists(f"Project '{p_create.name}' already exists.")

        logger.info("New project '%s' created successfully", p_create.name)
        return p_doc

    async def get_user_projects(self) -> list[ProjectDocument] | None:
        """Get all projects of current user, basic information only."""
        # project created by current user
        p1_docs = await ProjectDocument.find(
            {"created_by": {"$eq": self.user.id}},
        ).to_list()

        # project owner is current user
        p2_docs = await ProjectDocument.find(
            {"owner": {"$eq": self.user.id}},
        ).to_list()

        # project leads containing current user
        p3_docs = await ProjectDocument.find({"leads": self.user.id}).to_list()

        # project team containing current user
        user_manager = UserManager(user=None)
        user_team_ids = await user_manager.get_user_team_ids(self.user)
        p4_docs = await ProjectDocument.find({"teams": user_team_ids}).to_list()

        # return projects
        p_docs = {}
        for p_doc in chain(p1_docs, p2_docs, p3_docs, p4_docs):
            if p_doc.id in p_docs:
                continue
            p_docs[p_doc.id] = p_doc

        return list(p_docs.values())

    async def update_project_detail(
        self,
        p_update: ProjectUpdate,
    ) -> ProjectDocument | None:
        """Update project details"""
        p_doc = self.validated_context.project
        p_doc_other = await ProjectDocument.find_one(
            ProjectDocument.name == p_update.name,
        )
        if p_doc_other and (p_doc_other.id != p_doc.id):
            raise E.DocumentAlreadyExists(
                f"Project with name '{p_update.name}' already exists, use another name.",
            )

        data = p_update.model_dump()
        await p_doc.set(data)

        # await p_doc.save()
        logger.info("Project '%s' got updated successfully.", p_doc.name)

        return p_doc

    async def get_project_detail(self) -> ProjectDocument:
        """Get project details"""
        p_doc = self.validated_context.project
        return p_doc


class ProjectRunManager(AbstractObjectManager):

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

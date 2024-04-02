from __future__ import annotations

import logging
from datetime import datetime

from pipes.graph.constants import VertexLabel
from pipes.db.manager import AbstractObjectManager
from pipes.projects.schemas import ProjectDocument
from pipes.projectruns.schemas import ProjectRunDocument
from pipes.models.schemas import ModelDocument
from pipes.modelruns.contexts import (
    ModelRunDocumentContext,
    ModelRunSimpleContext,
    ModelRunObjectContext,
)
from pipes.modelruns.schemas import ModelRunDocument
from pipes.tasks.schemas import TaskCreate, TaskDocument, TaskRead
from pipes.tasks.validators import TaskDomainValidator
from pipes.users.schemas import UserDocument

logger = logging.getLogger(__name__)


class TaskManager(AbstractObjectManager):

    __label__ = VertexLabel.Task.value

    def __init__(self, context: ModelRunDocumentContext) -> None:
        self.context = context

    async def create_task(
        self,
        task_create: TaskCreate,
        user: UserDocument,
    ) -> TaskDocument:
        # Domain validation
        domain_validator = TaskDomainValidator(self.context)
        task_create = await domain_validator.validate(task_create)

        # Create task vertex

        # Create task action assignees

        # Add edges between task and assignee

        # Create task document
        task_doc = TaskDocument(
            # document information
            created_at=datetime.now(),
            created_by=user.id,
            last_modified=datetime.now(),
            modified_by=user.id,
        )
        return task_doc

    async def get_tasks(self) -> list[TaskRead]:
        _context = ModelRunObjectContext(
            project=self.context.project.id,
            projectrun=self.context.projectrun.id,
            model=self.context.model.id,
            modelrun=self.context.modelrun.id,
        )
        task_docs = await self.d.find_all(
            collection=TaskDocument,
            query={
                "context.project": _context.project,
                "context.projectrun": _context.projectrun,
                "context.model": _context.model,
                "context.modelrun": _context.modelrun,
            },
        )
        task_reads = []
        for task_doc in task_docs:
            task_read = await self.read_task(task_doc)
            task_reads.append(task_read)
        return task_reads

    async def read_task(self, task_doc: TaskDocument) -> TaskRead:
        # Read context
        p_id = task_doc.context.project
        p_doc = await self.d.get(collection=ProjectDocument, id=p_id)

        pr_id = task_doc.context.projectrun
        pr_doc = await self.d.get(collection=ProjectRunDocument, id=pr_id)

        m_id = task_doc.context.model
        m_doc = await self.d.get(collection=ModelDocument, id=m_id)

        mr_id = task_doc.context.modelrun
        mr_doc = await self.d.get(collection=ModelRunDocument, id=mr_id)

        data = task_doc.model_dump()
        data["context"] = ModelRunSimpleContext(
            project=p_doc.name,
            projectrun=pr_doc.name,
            model=m_doc.name,
            modelrun=mr_doc.name,
        )

        return TaskRead.model_validate(data)

from __future__ import annotations

import logging
from datetime import datetime

from pydantic import EmailStr
from pymongo.errors import DuplicateKeyError

from pipes.common.exceptions import (
    DocumentAlreadyExists,
    DocumentDoesNotExist,
    VertexAlreadyExists,
)
from pipes.datasets.manager import DatasetManager
from pipes.datasets.schemas import DatasetRead
from pipes.db.manager import AbstractObjectManager
from pipes.graph.constants import VertexLabel, EdgeLabel
from pipes.graph.schemas import TaskVertex, TaskVertexProperties
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
from pipes.users.manager import UserManager
from pipes.users.schemas import UserCreate, UserDocument, UserRead

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

        # Create task action assignees
        assignee_doc = await self._get_or_create_assignee(task_create.assignee)

        # Find and link datasets
        input_datasets = [
            await self._get_dataset(d_name) for d_name in task_create.input_datasets
        ]
        output_datasets = [
            await self._get_dataset(d_name) for d_name in task_create.output_datasets
        ]

        # Create task vertex
        task_vtx_model = await self._create_task_vertex(task_create.name)
        task_vtx_id = task_vtx_model.id

        # Add edges between task and assignee
        u_vtx_id = assignee_doc.vertex.id
        self.n.add_e(task_vtx_id, u_vtx_id, EdgeLabel.associated.value)

        # Task used datasets
        for d_doc in input_datasets:
            d_vtx_id = d_doc.vertex.id
            self.n.add_e(task_vtx_id, d_vtx_id, EdgeLabel.used.value)

        mr_vtx_id = self.context.modelrun.vertex.id
        for d_doc in output_datasets:
            d_vtx_id = d_doc.vertex.id
            # Task output dataset
            self.n.add_e(task_vtx_id, d_vtx_id, EdgeLabel.output.value)

            # Model run connected to task output dataset
            self.n.add_e(mr_vtx_id, d_vtx_id, EdgeLabel.connected.value)

        # Create task document
        _context = ModelRunObjectContext(
            project=self.context.project.id,
            projectrun=self.context.projectrun.id,
            model=self.context.model.id,
            modelrun=self.context.modelrun.id,
        )
        task_doc = TaskDocument(
            context=_context,
            vertex=task_vtx_model,
            # task properties
            name=task_create.name,
            type=task_create.type,
            description=task_create.description,
            task_assignee=assignee_doc.id,
            status=task_create.status,
            subtasks=task_create.subtasks,
            scheduled_start=task_create.scheduled_start,
            scheduled_end=task_create.scheduled_end,
            completion_date=task_create.completion_date,
            source_code=task_create.source_code,
            input_datasets=[d_doc.id for d_doc in input_datasets],
            input_parameters=task_create.input_parameters,
            output_datasets=[d_doc.id for d_doc in output_datasets],
            output_values=task_create.output_values,
            logs=task_create.logs,
            notes=task_create.notes,
            # document information
            created_at=datetime.now(),
            created_by=user.id,
            last_modified=datetime.now(),
            modified_by=user.id,
        )
        try:
            task_doc = await self.d.insert(task_doc)
        except DuplicateKeyError:
            raise DocumentAlreadyExists(
                f"Task document '{task_create.name}' already exists under context: {self.context}.",
            )

        return task_doc

    async def _create_task_vertex(self, task_name: str) -> TaskVertex:
        properties = {
            "project": self.context.project.name,
            "projectrun": self.context.projectrun.name,
            "model": self.context.model.name,
            "modelrun": self.context.modelrun.name,
            "name": task_name,
        }
        if self.n.exists(self.label, **properties):
            raise VertexAlreadyExists(
                f"Task vertex {properties} already exists under context: {self.context}",
            )

        properties_model = TaskVertexProperties(**properties)
        properties = properties_model.model_dump()
        task_vtx = self.n.add_v(self.label, **properties)

        # Dcoument creation
        task_vtx_model = TaskVertex(
            id=task_vtx.id,
            label=self.label,
            properties=properties_model,
        )
        return task_vtx_model

    async def _get_or_create_assignee(self, assignee: EmailStr | UserCreate | None):
        if not assignee:
            return None

        user_manager = UserManager()
        if isinstance(assignee, EmailStr):
            assignee_doc = await user_manager.get_user_by_email(assignee)
            if not assignee_doc:
                raise DocumentDoesNotExist("Assignee specified in task does not exist.")

        assignee_doc = await user_manager.get_or_create_user(assignee)
        return assignee_doc

    async def _get_dataset(self, d_name) -> DatasetRead:
        dataset_manager = DatasetManager(self.context)
        d_doc = await dataset_manager.get_dataset(d_name)
        if not d_doc:
            raise DocumentDoesNotExist(
                "Dataset does not exist, please checkin this dataset first.",
            )
        return d_doc

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

        # task assignee
        assignee_doc = await self.d.get(
            collection=UserDocument,
            id=task_doc.task_assignee,
        )
        assigee_read = UserRead.model_validate(assignee_doc.model_dump())
        data["task_assignee"] = assigee_read

        # task input & output datasets
        # dataset_manager = DatasetManager(self.context)
        # input_datasets = []
        # for d_id in task_doc.input_datasets:
        #     d_doc = await self.d.get(collection=DatasetDocument, id=d_id)
        #     d_read = await dataset_manager.read_dataset(d_doc)
        #     input_datasets.append(d_read)
        # data["input_datasets"] = input_datasets

        # output_datasets = []
        # for d_id in task_doc.output_datasets:
        #     d_doc = await self.d.get(collection=DatasetDocument, id=d_id)
        #     d_read = await dataset_manager.read_dataset(d_doc)
        #     output_datasets.append(d_read)
        # data["output_datasets"] = output_datasets

        return TaskRead.model_validate(data)

from __future__ import annotations

import logging
from datetime import datetime

from pymongo.errors import DuplicateKeyError

from pipes.common.exceptions import DocumentAlreadyExists, VertexAlreadyExists
from pipes.graph.constants import VertexLabel, EdgeLabel
from pipes.graph.schemas import DatasetVertexProperties, DatasetVertex
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
from pipes.datasets.schemas import DatasetCreate, DatasetDocument, DatasetRead
from pipes.datasets.validators import DatasetDomainValidator
from pipes.users.manager import UserManager
from pipes.users.schemas import UserCreate, UserDocument, UserRead

logger = logging.getLogger(__name__)


class DatasetManager(AbstractObjectManager):

    __label__ = VertexLabel.Dataset.value

    def __init__(self, context: ModelRunDocumentContext) -> None:
        self.context = context

    async def create_dataset(
        self,
        d_create: DatasetCreate,
        user: UserDocument,
    ) -> DatasetDocument:
        # Domain validation
        domain_validator = DatasetDomainValidator(self.context)
        d_create = await domain_validator.validate(d_create)

        # Get or create regiatration author
        r_author = await self._get_or_create_registration_author(
            d_create.registration_author,
        )

        # Create dataset vertex
        d_vertex = await self._create_dataset_vertex(d_create.name)

        # Add edge between dataset and registration author
        d_vtx_id = d_vertex.id
        u_vtx_id = r_author.vertex.id
        self.n.add_edge(d_vtx_id, u_vtx_id, EdgeLabel.attributed.value)

        # Create dataset document
        d_doc = await self._create_dataset_document(d_create, r_author, d_vertex, user)

        # Add edge between dataset and model run
        mr_doc = self.context.modelrun
        mr_vtx_id = mr_doc.vertex.id
        self.n.add_edge(mr_vtx_id, d_vtx_id, EdgeLabel.produced.value)

        return d_doc

    async def _create_dataset_vertex(self, d_name: str) -> DatasetVertex:
        properties = {
            "project": self.context.project.name,
            "projectrun": self.context.projectrun.name,
            "model": self.context.model.name,
            "modelrun": self.context.modelrun.name,
            "name": d_name,
        }
        if self.n.exists(self.label, **properties):
            raise VertexAlreadyExists(
                f"Dataset vertex '{d_name}' already exists in context: {self.context}.",
            )

        properties_model = DatasetVertexProperties(**properties)
        properties = properties_model.model_dump()
        d_vtx = self.n.add_v(self.label, **properties)

        # Dcoument creation
        d_vertex_model = DatasetVertex(
            id=d_vtx.id,
            label=self.label,
            properties=properties_model,
        )
        return d_vertex_model

    async def _get_or_create_registration_author(
        self,
        r_author: UserCreate,
    ) -> UserDocument:
        user_manager = UserManager()
        r_author_doc = await user_manager.get_or_create_user(r_author)
        return r_author_doc

    async def _create_dataset_document(
        self,
        d_create: DatasetCreate,
        d_r_author: UserDocument,
        d_vertex: DatasetVertex,
        user: UserDocument,
    ) -> DatasetDocument:
        """Checkin a dataset with given context"""
        d_name = d_create.name
        _context = ModelRunObjectContext(
            project=self.context.project.id,
            projectrun=self.context.projectrun.id,
            model=self.context.model.id,
            modelrun=self.context.modelrun.id,
        )
        d_doc_exists = await self.d.exists(
            collection=DatasetDocument,
            query={
                "context.project": _context.project,
                "context.projectrun": _context.projectrun,
                "context.model": _context.model,
                "context.modelrun": _context.modelrun,
                "name": d_name,
            },
        )
        if d_doc_exists:
            raise DocumentAlreadyExists(
                f"Dataset '{d_name}' already exists with context '{self.context}'.",
            )

        # dataset document
        d_doc = DatasetDocument(
            vertex=d_vertex,
            context=_context,
            # dataset information
            name=d_name,
            display_name=d_create.display_name,
            description=d_create.description,
            version=d_create.version,
            hash_value=d_create.hash_value,
            version_status=d_create.version_status,
            previous_version=d_create.previous_version,
            data_format=d_create.data_format,
            schema_info=d_create.schema_info,
            location=d_create.location,
            registration_author=d_r_author.id,
            weather_years=d_create.weather_years,
            model_years=d_create.model_years,
            units=d_create.units,
            temporal_info=d_create.temporal_info,
            spatial_info=d_create.spatial_info,
            scenarios=d_create.scenarios,
            sensitivities=d_create.sensitivities,
            source_code=d_create.source_code,
            relevant_links=d_create.relevant_links,
            comments=d_create.comments,
            resource_url=d_create.resource_url,
            other=d_create.other,
            # document information
            created_at=datetime.now(),
            created_by=user.id,
            last_modified=datetime.now(),
            modified_by=user.id,
        )

        try:
            d_doc = await self.d.insert(d_doc)
        except DuplicateKeyError:
            raise DocumentAlreadyExists(
                f"Dataset '{d_name}' already exists under context '{self.context}'.",
            )

        return d_doc

    async def get_datasets(self) -> list[DatasetRead]:
        """Get all datasets in the given context"""
        _context = ModelRunObjectContext(
            project=self.context.project.id,
            projectrun=self.context.projectrun.id,
            model=self.context.model.id,
            modelrun=self.context.modelrun.id,
        )
        d_docs = await self.d.find_all(
            collection=DatasetDocument,
            query={
                "context.project": _context.project,
                "context.projectrun": _context.projectrun,
                "context.model": _context.model,
                "context.modelrun": _context.modelrun,
            },
        )
        d_reads = []
        for d_doc in d_docs:
            d_read = await self.read_dataset(d_doc)
            d_reads.append(d_read)
        return d_reads

    async def read_dataset(
        self,
        d_doc: DatasetDocument,
    ) -> DatasetRead:
        """Convert a dataset document into dataset read"""
        # Read context
        p_id = d_doc.context.project
        p_doc = await self.d.get(collection=ProjectDocument, id=p_id)

        pr_id = d_doc.context.projectrun
        pr_doc = await self.d.get(collection=ProjectRunDocument, id=pr_id)

        m_id = d_doc.context.model
        m_doc = await self.d.get(collection=ModelDocument, id=m_id)

        mr_id = d_doc.context.modelrun
        mr_doc = await self.d.get(collection=ModelRunDocument, id=mr_id)

        data = d_doc.model_dump()
        data["context"] = ModelRunSimpleContext(
            project=p_doc.name,
            projectrun=pr_doc.name,
            model=m_doc.name,
            modelrun=mr_doc.name,
        )

        # dataset author
        author_id = d_doc.registration_author
        author_doc = await self.d.get(collection=UserDocument, id=author_id)
        author_read = UserRead.model_validate(author_doc.model_dump())
        data["registration_author"] = author_read

        return DatasetRead.model_validate(data)

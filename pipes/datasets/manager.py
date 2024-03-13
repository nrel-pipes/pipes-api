from __future__ import annotations

from datetime import datetime

from pymongo.errors import DuplicateKeyError

from pipes.common.exceptions import DocumentAlreadyExists
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
from pipes.users.schemas import UserDocument, UserRead


class DatasetManager(AbstractObjectManager):

    async def create_dataset(
        self,
        user: UserDocument,
        data: DatasetCreate,
        context: ModelRunDocumentContext,
    ) -> DatasetDocument:
        """Checkin a dataset with given context"""
        d_name = data.name
        _context = ModelRunObjectContext(
            project=context.project.id,
            projectrun=context.projectrun.id,
            model=context.model.id,
            modelrun=context.modelrun.id,
        )
        d_doc_exists = await DatasetDocument.find_one(
            {
                "context.project": _context.project,
                "context.projectrun": _context.projectrun,
                "context.model": _context.model,
                "context.modelrun": _context.modelrun,
                "name": d_name,
            },
        )
        if d_doc_exists:
            raise DocumentAlreadyExists(
                f"Dataset '{d_name}' already exists with context '{context}'.",
            )

        # dataset document
        user_manager = UserManager()
        r_author_doc = await user_manager.get_or_create_user(data.registration_author)

        d_doc = DatasetDocument(
            context=_context,
            # dataset information
            name=d_name,
            display_name=data.display_name,
            description=data.description,
            version=data.version,
            hash_value=data.hash_value,
            version_status=data.version_status,
            previous_version=data.previous_version,
            data_format=data.data_format,
            schema_info=data.schema_info,
            location=data.location,
            registration_author=r_author_doc.id,
            weather_years=data.weather_years,
            model_years=data.model_years,
            units=data.units,
            temporal_info=data.temporal_info,
            spatial_info=data.spatial_info,
            scenarios=data.scenarios,
            sensitivities=data.sensitivities,
            source_code=data.source_code,
            relevant_links=data.relevant_links,
            comments=data.comments,
            resource_url=data.resource_url,
            other=data.other,
            # document information
            created_at=datetime.utcnow(),
            created_by=user.id,
            last_modified=datetime.utcnow(),
            modified_by=user.id,
        )

        # Domain validation
        domain_validator = DatasetDomainValidator()
        d_doc = await domain_validator.validate(d_doc)

        try:
            d_doc = await d_doc.insert()
        except DuplicateKeyError:
            raise DocumentAlreadyExists(
                f"Dataset '{d_name}' already exists with context '{context}'.",
            )

        return d_doc

    async def get_datasets(
        self,
        _context: ModelRunDocumentContext,
    ) -> list[DatasetRead]:
        """Get all datasets in the given context"""
        d_docs = DatasetDocument.find(
            {
                "context.project": _context.project.id,
                "context.projectrun": _context.projectrun.id,
                "context.model": _context.model.id,
                "context.modelrun": _context.modelrun.id,
            },
        )
        d_reads = []
        async for d_doc in d_docs:
            d_read = await self.read_dataset(d_doc, _context)
            d_reads.append(d_read)
        return d_reads

    async def read_dataset(
        self,
        d_doc: DatasetDocument,
        context: ModelRunDocumentContext | None = None,
    ) -> DatasetRead:
        """Convert a dataset document into dataset read"""
        # Read context
        if context:
            p_doc = context.project
            pr_doc = context.projectrun
            m_doc = context.model
            mr_doc = context.modelrun
        else:
            p_id = d_doc.context.project
            p_doc = await ProjectDocument.get(p_id)

            pr_id = d_doc.context.projectrun
            pr_doc = await ProjectRunDocument.get(pr_id)

            m_id = d_doc.context.model
            m_doc = await ModelDocument.get(m_id)

            mr_id = d_doc.context.modelrun
            mr_doc = await ModelRunDocument.get(mr_id)

        data = d_doc.model_dump()
        data["context"] = ModelRunSimpleContext(
            project=p_doc.name,
            projectrun=pr_doc.name,
            model=m_doc.name,
            modelrun=mr_doc.name,
        )

        # dataset author
        author_id = d_doc.registration_author
        author_doc = await UserDocument.get(author_id)
        author_read = UserRead.model_validate(author_doc.model_dump())
        data["registration_author"] = author_read

        return DatasetRead.model_validate(data)

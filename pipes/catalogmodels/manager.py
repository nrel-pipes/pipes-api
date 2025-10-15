from __future__ import annotations

import logging
from datetime import datetime

from pymongo.errors import DuplicateKeyError

from pipes.common.exceptions import DocumentAlreadyExists, DocumentDoesNotExist
from pipes.db.manager import AbstractObjectManager
from pipes.catalogmodels.schemas import (
    CatalogModelCreate,
    CatalogModelDocument,
    CatalogModelRead,
    CatalogModelUpdate,
)
from pipes.users.schemas import UserDocument, UserRead

logger = logging.getLogger(__name__)


class CatalogModelManager(AbstractObjectManager):
    """Manager for catalog model operations"""

    async def create_model(
        self,
        m_create: CatalogModelCreate,
        user: UserDocument,
    ) -> CatalogModelDocument:
        m_doc = await self._create_model_document(m_create, user)
        return m_doc

    async def _create_model_document(
        self,
        m_create: CatalogModelCreate,
        user: UserDocument,
    ) -> CatalogModelDocument:
        """Create a new model under given project and project run"""

        # Check if model already exists or not
        m_name = m_create.name
        m_doc_exits = await self.d.exists(
            collection=CatalogModelDocument,
            query={
                "name": m_name,
            },
        )
        if m_doc_exits:
            raise DocumentAlreadyExists(
                f"Model '{m_name}' already exists in catalog.",
            )
        # object context
        current_time = datetime.now()
        cm_doc = CatalogModelDocument(
            # model information
            name=m_name,
            display_name=m_create.display_name,
            type=m_create.type,
            description=m_create.description,
            assumptions=m_create.assumptions,
            requirements=m_create.requirements,
            expected_scenarios=m_create.expected_scenarios,
            other=m_create.other,
            created_at=current_time,
            created_by=user.id,
            last_modified=current_time,
            modified_by=user.id,
        )
        # Create document
        try:
            cm_doc = await self.d.insert(cm_doc)
        except DuplicateKeyError:
            raise DocumentAlreadyExists(
                f"Model document '{m_name}'.",
            )

        logger.info(
            "New model '%s' was created successfully in catalog.",
            m_name,
        )
        return cm_doc

    async def get_models(self, user: UserDocument) -> list[CatalogModelDocument]:
        """Read a model from given model document"""
        cm_docs = await self.d.find_all(
            collection=CatalogModelDocument,
            query={"created_by": user.id},
        )
        cm_reads = []
        for cm_doc in cm_docs:
            data = cm_doc.model_dump()
            created_by_doc = await UserDocument.get(data["created_by"])
            data["created_by"] = created_by_doc.model_dump()
            cm_reads.append(CatalogModelRead.model_validate(data))
        return cm_reads

    async def read_model(
        self,
        cm_doc: CatalogModelDocument,
    ):
        """Retrieve a specific model from the database by name"""
        # Convert the document to a model document
        if not cm_doc:
            return None
        data = cm_doc.model_dump()
        created_by_doc = await UserDocument.get(data["created_by"])
        data["created_by"] = UserRead.model_validate(created_by_doc.model_dump())
        return CatalogModelRead.model_validate(data)

    async def get_model(
        self,
        model_name: str,
        user: UserDocument,
    ) -> CatalogModelRead:
        """Get a specific model by name"""
        query = {"name": model_name, "created_by": user.id}
        cm_doc = await self.d.find_one(
            collection=CatalogModelDocument,
            query=query,
        )
        if not cm_doc:
            raise DocumentDoesNotExist(
                f"Model '{model_name}' does not exist in catalog.",
            )

        cm_read = await self.read_model(cm_doc)
        return cm_read

    async def update_model(
        self,
        model_name: str,
        m_update: CatalogModelUpdate,
        user: UserDocument,
    ) -> CatalogModelDocument:
        """Update an existing catalog model"""
        # Find the model
        query = {"name": model_name, "created_by": user.id}
        cm_doc = await self.d.find_one(
            collection=CatalogModelDocument,
            query=query,
        )
        if not cm_doc:
            raise DocumentDoesNotExist(
                f"Model '{model_name}' does not exist in catalog.",
            )

        # Update fields
        update_data = m_update.model_dump()
        if update_data:
            update_data["last_modified"] = datetime.now()
            update_data["modified_by"] = user.id

            for key, value in update_data.items():
                setattr(cm_doc, key, value)

            cm_doc = await cm_doc.save()

            logger.info(
                "Model '%s' was updated successfully in catalog.",
                model_name,
            )

        return await self.read_model(cm_doc)

    async def delete_model(
        self,
        model_name: str,
        user: UserDocument,
    ) -> None:
        """Delete a specific model by name"""
        query = {"name": model_name, "created_by": user.id}
        cm_doc = await self.d.find_one(
            collection=CatalogModelDocument,
            query=query,
        )
        if not cm_doc:
            raise DocumentDoesNotExist(
                f"Model '{model_name}' does not exist in catalog.",
            )
        await self.d.delete_one(
            collection=CatalogModelDocument,
            query={"_id": cm_doc.id},
        )
        logger.info(
            "Model '%s' was deleted successfully from catalog.",
            model_name,
        )

from __future__ import annotations

import logging, json
from datetime import datetime

from pymongo.errors import DuplicateKeyError

from pipes.common.exceptions import DocumentAlreadyExists, DocumentDoesNotExist
from pipes.db.manager import AbstractObjectManager
from pipes.catalogmodels.schemas import (
    GeneralCatalogModelCreate,
    GeneralCatalogModelDocument,
    GeneralCatalogModelRead,
    GeneralCatalogModelUpdate,
)
from pipes.catalogmodels.ifac.schemas import (
    IFACCatalogModelCreate
)
from pipes.catalogmodels.default.schemas import (
    DefaultCatalogModelCreate
)
from pipes.users.schemas import UserDocument, UserRead

logger = logging.getLogger(__name__)

schemas = {
    "IFAC Tool Specsheet v1.0": IFACCatalogModelCreate,
    "Default": DefaultCatalogModelCreate,
}

class GeneralCatalogModelManager(AbstractObjectManager):
    """Manager for catalog model operations"""

    async def create_model(
        self,
        m_create: GeneralCatalogModelCreate,
        user: UserDocument,
    ) -> GeneralCatalogModelDocument:
        if m_create.catalog_schema is not None:
            if m_create.catalog_schema not in schemas:
                raise DocumentAlreadyExists(
                    f"Catalog schema '{m_create.catalog_schema}' does not exist.",
                )
            try: 
                schemas[m_create.catalog_schema].model_validate(m_create.model_dump())
            except Exception as e:
                raise DocumentAlreadyExists(
                    f"Model '{m_create.name}' does not conform to {m_create.catalog_schema} schema: {e}",
                )
        m_doc = await self._create_model_document(m_create, user)
        return m_doc

    async def _create_model_document(
        self,
        m_create: GeneralCatalogModelCreate,
        user: UserDocument,
    ) -> GeneralCatalogModelDocument:
        """Create a new model under given project and project run"""

        # Check if model already exists or not
        m_name = m_create.name
        m_doc_exits = await self.d.exists(
            collection=GeneralCatalogModelDocument,
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
        cm_doc = GeneralCatalogModelDocument(
            # model information
            created_at=current_time,
            created_by=user.id,
            last_modified=current_time,
            modified_by=user.id,
            **m_create.model_dump(exclude_none=True)
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

    async def get_models(self, user: UserDocument) -> list[GeneralCatalogModelDocument]:
        """Read a model from given model document"""
        cm_docs = await self.d.find_all(
            collection=GeneralCatalogModelDocument,
            query={
                "$or": [
                    {"created_by": user.id},
                    {"access_group": {"$in": [user.id]}},
                ],
            },
        )

        cm_reads = []
        for cm_doc in cm_docs:
            cm_read = await self.read_model(cm_doc)
            cm_reads.append(cm_read)
        return cm_reads

    async def read_model(
        self,
        cm_doc: GeneralCatalogModelDocument,
    ):
        """Retrieve a specific model from the database by name"""
        # Convert the document to a model document
        if not cm_doc:
            return None
        data = cm_doc.model_dump()
        created_by_doc = await UserDocument.get(data["created_by"])
        data["created_by"] = UserRead.model_validate(created_by_doc.model_dump())
        modified_by_doc = await UserDocument.get(data["modified_by"])
        data["modified_by"] = UserRead.model_validate(modified_by_doc.model_dump())

        user_emails = []
        for user_id in data["access_group"]:
            user_doc = await UserDocument.get(user_id)
            if user_doc:
                user_emails.append(user_doc.email)
        data["access_group"] = user_emails
        return GeneralCatalogModelRead.model_validate(data)

    async def get_model(
        self,
        model_name: str,
        user: UserDocument,
    ) -> GeneralCatalogModelRead:
        """Get a specific model by name"""
        query = {
            "name": model_name,
            "$or": [
                {"created_by": user.id},
                {"access_group": {"$in": [user.id]}},
            ],
        }
        cm_doc = await self.d.find_one(
            collection=GeneralCatalogModelDocument,
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
        m_update: GeneralCatalogModelUpdate,
        user: UserDocument,
    ) -> GeneralCatalogModelDocument:
        """Update an existing catalog model"""
        # Find the model
        query = {"name": model_name, "created_by": user.id}
        cm_doc = await self.d.find_one(
            collection=GeneralCatalogModelDocument,
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
            collection=GeneralCatalogModelDocument,
            query=query,
        )
        if not cm_doc:
            raise DocumentDoesNotExist(
                f"Model '{model_name}' does not exist in catalog.",
            )
        await self.d.delete_one(
            collection=GeneralCatalogModelDocument,
            query={"_id": cm_doc.id},
        )
        logger.info(
            "Model '%s' was deleted successfully from catalog.",
            model_name,
        )

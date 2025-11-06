from __future__ import annotations

import logging
from datetime import datetime

from pymongo.errors import DuplicateKeyError

from pipes.common.exceptions import DocumentAlreadyExists, DocumentDoesNotExist
from pipes.db.manager import AbstractObjectManager
from pipes.catalogdatasets.schemas import (
    CatalogDatasetCreate,
    CatalogDatasetDocument,
    CatalogDatasetRead,
    CatalogDatasetUpdate,
    DatasetLocation,
)
from pipes.users.schemas import UserDocument, UserRead

logger = logging.getLogger(__name__)


class CatalogDatasetManager(AbstractObjectManager):
    """Manager for catalog dataset operations"""

    async def create_dataset(
        self,
        d_create: CatalogDatasetCreate,
        user: UserDocument,
    ) -> CatalogDatasetDocument:
        d_doc = await self._create_dataset_document(d_create, user)
        return d_doc

    async def _create_dataset_document(
        self,
        d_create: CatalogDatasetCreate,
        user: UserDocument,
    ) -> CatalogDatasetDocument:
        """Create a new dataset in catalog"""

        # Check if dataset already exists or not
        d_name = d_create.name
        d_doc_exits = await self.d.exists(
            collection=CatalogDatasetDocument,
            query={
                "name": d_name,
            },
        )
        if d_doc_exits:
            raise DocumentAlreadyExists(
                f"Dataset '{d_name}' already exists in catalog.",
            )

        # Convert access_group emails to user IDs
        access_group_ids = []
        for email in d_create.access_group:
            user_doc = await UserDocument.find_one({"email": email})
            if user_doc:
                access_group_ids.append(user_doc.id)

        # object context
        current_time = datetime.now()
        cd_doc = CatalogDatasetDocument(
            # dataset information
            name=d_name,
            display_name=d_create.display_name,
            description=d_create.description,
            version=d_create.version,
            previous_version=d_create.previous_version,
            hash_value=d_create.hash_value,
            data_format=d_create.data_format,
            schema_info=d_create.schema_info,
            location=d_create.location,
            weather_years=d_create.weather_years,
            model_years=d_create.model_years,
            units=d_create.units,
            temporal_info=d_create.temporal_info,
            spatial_info=d_create.spatial_info,
            scenarios=d_create.scenarios,
            sensitivities=d_create.sensitivities,
            source_code=d_create.source_code,
            relevant_links=d_create.relevant_links,
            resource_url=d_create.resource_url,
            access_group=access_group_ids,
            created_at=current_time,
            created_by=user.id,
            last_modified=current_time,
            modified_by=user.id,
        )
        # Create document
        try:
            cd_doc = await self.d.insert(cd_doc)
        except DuplicateKeyError:
            raise DocumentAlreadyExists(
                f"Dataset document '{d_name}'.",
            )

        logger.info(
            "New dataset '%s' was created successfully in catalog.",
            d_name,
        )
        return cd_doc

    async def get_datasets(self, user: UserDocument) -> list[CatalogDatasetRead]:
        """Get all datasets accessible by user"""
        cd_docs = await self.d.find_all(
            collection=CatalogDatasetDocument,
            query={
                "$or": [
                    {"created_by": user.id},
                    {"access_group": {"$in": [user.id]}},
                ],
            },
        )

        cd_reads = []
        for cd_doc in cd_docs:
            cd_read = await self.read_dataset(cd_doc)
            cd_reads.append(cd_read)
        return cd_reads

    async def read_dataset(
        self,
        cd_doc: CatalogDatasetDocument,
    ) -> CatalogDatasetRead:
        """Convert dataset document to read schema"""
        data = cd_doc.model_dump()
        created_by_doc = await UserDocument.get(data["created_by"])
        data["created_by"] = UserRead.model_validate(created_by_doc.model_dump())

        user_emails = []
        for user_id in data["access_group"]:
            user_doc = await UserDocument.get(user_id)
            if user_doc:
                user_emails.append(user_doc.email)
        data["access_group"] = user_emails
        return CatalogDatasetRead.model_validate(data)

    async def get_dataset(
        self,
        dataset_name: str,
        user: UserDocument,
    ) -> CatalogDatasetRead:
        """Get a specific dataset by name"""
        query = {
            "name": dataset_name,
            "$or": [
                {"created_by": user.id},
                {"access_group": {"$in": [user.id]}},
            ],
        }
        cd_doc = await self.d.find_one(
            collection=CatalogDatasetDocument,
            query=query,
        )
        if not cd_doc:
            raise DocumentDoesNotExist(
                f"Dataset '{dataset_name}' does not exist in catalog.",
            )

        cd_read = await self.read_dataset(cd_doc)
        return cd_read

    async def update_dataset(
        self,
        dataset_name: str,
        d_update: CatalogDatasetUpdate,
        user: UserDocument,
    ) -> CatalogDatasetRead:
        """Update an existing catalog dataset"""
        # Find the dataset
        query = {"name": dataset_name, "created_by": user.id}
        cd_doc = await self.d.find_one(
            collection=CatalogDatasetDocument,
            query=query,
        )
        if not cd_doc:
            raise DocumentDoesNotExist(
                f"Dataset '{dataset_name}' does not exist in catalog.",
            )

        # Update fields
        update_data = d_update.model_dump(exclude_unset=True)
        if update_data:
            # Convert access_group emails to user IDs if present
            if "access_group" in update_data and update_data["access_group"]:
                access_group_ids = []
                for email in update_data["access_group"]:
                    user_doc = await UserDocument.find_one({"email": email})
                    if user_doc:
                        access_group_ids.append(user_doc.id)
                update_data["access_group"] = access_group_ids

            # Ensure location is a DatasetLocation object if present
            if "location" in update_data and update_data["location"] is not None:
                if isinstance(update_data["location"], dict):
                    update_data["location"] = DatasetLocation(**update_data["location"])

            update_data["last_modified"] = datetime.now()
            update_data["modified_by"] = user.id

            for key, value in update_data.items():
                setattr(cd_doc, key, value)

            cd_doc = await cd_doc.save()

            logger.info(
                "Dataset '%s' was updated successfully in catalog.",
                dataset_name,
            )

        return await self.read_dataset(cd_doc)

    async def delete_dataset(
        self,
        dataset_name: str,
        user: UserDocument,
    ) -> None:
        """Delete a specific dataset by name"""
        query = {"name": dataset_name, "created_by": user.id}
        cd_doc = await self.d.find_one(
            collection=CatalogDatasetDocument,
            query=query,
        )
        if not cd_doc:
            raise DocumentDoesNotExist(
                f"Dataset '{dataset_name}' does not exist in catalog.",
            )
        await self.d.delete_one(
            collection=CatalogDatasetDocument,
            query={"_id": cd_doc.id},
        )
        logger.info(
            "Dataset '%s' was deleted successfully from catalog.",
            dataset_name,
        )

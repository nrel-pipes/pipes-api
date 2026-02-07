from __future__ import annotations

import logging
from pipes.accessgroups.schemas import (
    AccessGroupCreate,
    AccessGroupDocument,
    AccessGroupRead,
    AccessGroupUpdate,
)
from pipes.common.exceptions import DocumentAlreadyExists, DocumentDoesNotExist
from pipes.db.manager import AbstractObjectManager
from pipes.users.manager import UserManager
from pipes.users.schemas import UserCreate, UserDocument, UserRead

from pymongo.errors import DuplicateKeyError

logger = logging.getLogger(__name__)


class AccessGroupManager(AbstractObjectManager):
    """Manager class for access group management"""

    __label__ = None

    async def create_accessgroup(
        self,
        ag_create: AccessGroupCreate,
    ) -> AccessGroupDocument:
        """Create document in docdb"""
        # Add access group members
        ag_members = await self._add_accessgroup_members(ag_create.members)
        ag_doc = await self._create_accessgroup_document(ag_create, ag_members)
        return ag_doc

    async def _add_accessgroup_members(
        self,
        ag_members: list[UserCreate],
    ) -> list[UserDocument]:
        """Add user to access group"""
        user_manager = UserManager()
        member_docs = []
        for u_create in ag_members:
            u_doc = await user_manager.get_or_create_user(u_create)
            member_docs.append(u_doc)
        return member_docs

    async def _create_accessgroup_document(
        self,
        ag_create: AccessGroupCreate,
        ag_members: list[UserDocument],
    ) -> AccessGroupDocument:
        """Create new access group"""
        ag_name = ag_create.name

        exists = await self.d.exists(
            collection=AccessGroupDocument,
            query={"name": ag_name},
        )
        if exists:
            raise DocumentAlreadyExists(
                f"AccessGroup document '{ag_name}' already exists.",
            )

        u_doc_ids = [u_doc.id for u_doc in ag_members]

        ag_doc = AccessGroupDocument(
            name=ag_create.name,
            description=ag_create.description,
            members=list(u_doc_ids),
        )

        try:
            ag_doc = await self.d.insert(ag_doc)
        except DuplicateKeyError:
            raise DocumentAlreadyExists(
                f"AccessGroup '{ag_create.name}' already exists.",
            )

        logger.info(
            "New access group '%s' created successfully.",
            ag_doc.name,
        )
        return ag_doc

    # async def get_or_create_accessgroup(self, ag_create: AccessGroupCreate) -> AccessGroupDocument:
    #     p_doc = self.context.project

    #     query = {"context.project": p_doc.id, "name": ag_create.name}
    #     ag_doc = await self.d.find_one(collection=AccessGroupDocument, query=query)

    #     if not ag_doc:
    #         ag_doc = await self.create_accessgroup(ag_create)

    #     return ag_doc

    async def get_accessgroup(self, ag_name: str) -> AccessGroupDocument:
        query = {"name": ag_name}
        ag_doc = await self.d.find_one(collection=AccessGroupDocument, query=query)

        if not ag_doc:
            raise DocumentDoesNotExist(
                f"AccessGroup '{ag_name}' not found",
            )

        return ag_doc

    async def get_all_accessgroups(self) -> list[AccessGroupRead]:
        """Get all access groups."""
        ag_docs = await self.d.find_all(
            collection=AccessGroupDocument,
            query={},
        )

        accessgroups = []
        for ag_doc in ag_docs:
            ag_read = await self.read_accessgroup(ag_doc)
            accessgroups.append(ag_read)
        return accessgroups

    async def get_accessgroup_members(
        self,
        ag_doc: AccessGroupDocument,
    ) -> list[UserRead]:
        u_docs = await self.d.find_all(
            collection=UserDocument,
            query={"_id": {"$in": ag_doc.members}},
        )
        members = [UserRead.model_validate(u_doc.model_dump()) for u_doc in u_docs]
        return members

    async def update_accessgroup(
        self,
        accessgroup: str,
        data: AccessGroupUpdate,
    ) -> AccessGroupDocument:
        """Update access group"""
        ag_doc = await self.d.find_one(
            collection=AccessGroupDocument,
            query={"name": accessgroup},
        )
        if ag_doc is None:
            raise DocumentDoesNotExist(
                f"AccessGroup '{accessgroup}' does not exist",
            )

        if data.name != accessgroup:
            other_ag_doc = await self.d.find_one(
                collection=AccessGroupDocument,
                query={"name": data.name},
            )
            if other_ag_doc and (ag_doc.name != other_ag_doc.name):
                raise DocumentAlreadyExists(
                    f"AccessGroup '{data.name}' already exists",
                )

        user_manager = UserManager()
        member_doc_ids = set()
        for member in data.members:
            u_doc = await user_manager.get_or_create_user(member)
            member_doc_ids.add(u_doc.id)

        ag_doc.name = data.name
        ag_doc.description = data.description
        ag_doc.members = list(member_doc_ids)
        await ag_doc.save()

        return ag_doc

    async def read_accessgroup(self, ag_doc: AccessGroupDocument) -> AccessGroupRead:
        """Convert access group document to read object"""
        data = ag_doc.model_dump()
        data["members"] = await self.get_accessgroup_members(ag_doc)
        return AccessGroupRead.model_validate(data)

    async def delete_accessgroup(self, name: str) -> None:
        """Delete an access group by name"""
        # Delete the access group document
        await self.d.delete_one(
            collection=AccessGroupDocument,
            query={"name": name},
        )

        logger.info(
            "AccessGroup '%s' deleted successfully",
            name,
        )

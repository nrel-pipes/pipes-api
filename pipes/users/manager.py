from __future__ import annotations

import logging
from datetime import datetime

from beanie import PydanticObjectId
from pydantic import EmailStr
from pymongo.errors import DuplicateKeyError

from pipes.db.manager import AbstractObjectManager
from pipes.common.exceptions import DocumentDoesNotExist, DocumentAlreadyExists
from pipes.users.schemas import UserCreate, UserDocument

logger = logging.getLogger(__name__)


class UserManager(AbstractObjectManager):
    """Manager class for user management"""

    async def create_user(
        self,
        u_create: UserCreate,
        u_username: str = "",
    ) -> UserDocument:
        """Admin create new user"""
        u_doc = UserDocument(
            email=u_create.email,
            first_name=u_create.first_name,
            last_name=u_create.last_name,
            organization=u_create.organization,
            created_at=datetime.utcnow(),
            is_active=True,
            is_superuser=False,
        )
        if u_username:
            u_doc.username = u_username

        try:
            await u_doc.insert()
        except DuplicateKeyError:
            raise DocumentAlreadyExists(f"User '{u_create.email}' already exists.")
        return u_doc

    async def get_or_create_user(self, u_create: UserCreate) -> UserDocument:
        """Get or create user"""
        u_doc = await UserDocument.find_one(UserDocument.email == u_create.email)
        if not u_doc:
            u_doc = UserDocument(
                email=u_create.email,
                first_name=u_create.first_name,
                last_name=u_create.last_name,
                organization=u_create.organization,
                created_at=datetime.utcnow(),
            )
            u_doc = await u_doc.insert()
        return u_doc

    async def get_users(self) -> list[UserDocument]:
        """Admin get all users db"""
        u_docs = await UserDocument.find().to_list()
        return u_docs

    async def get_user_by_email(self, email: EmailStr) -> UserDocument:
        """Get user by email"""
        email = email.lower()
        u_doc = await UserDocument.find_one(UserDocument.email == email)
        if not u_doc:
            raise DocumentDoesNotExist(f"User '{email}' not found")
        return u_doc

    async def get_user_by_username(self, username: str) -> UserDocument:
        """Get user by cognito username decoded from access token"""
        u_doc = await UserDocument.find_one(UserDocument.username == username)
        if not u_doc:
            raise DocumentDoesNotExist(f"User not found - username: {username}")
        return u_doc

    async def get_user_by_id(self, id: PydanticObjectId) -> UserDocument:
        """Get user by document id"""
        u_doc = await UserDocument.get(id)
        if not u_doc:
            raise DocumentDoesNotExist(f"User not found - user id: {id}")
        return u_doc

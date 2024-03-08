from __future__ import annotations

import logging
from datetime import datetime

from beanie import PydanticObjectId
from pydantic import EmailStr
from pymongo.errors import DuplicateKeyError

from pipes.db.manager import AbstractObjectManager
from pipes.teams.schemas import TeamDocument
from pipes.common.exceptions import DocumentDoesNotExist, DocumentAlreadyExists
from pipes.users.schemas import UserCreate, UserRead, UserDocument

logger = logging.getLogger(__name__)


class UserManager(AbstractObjectManager):
    """Manager class for user management"""

    async def validate_user_context(self, user: UserDocument, context: dict) -> dict:
        """No need to validate the context for user management"""
        # Skip, no context validation required now.
        return {}

    async def create_user(
        self,
        u_create: UserCreate,
        u_username: str = "",
    ) -> UserDocument | None:
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

    async def get_user_by_email(self, email: EmailStr) -> UserRead | None:
        """Get user by email"""
        email = email.lower()
        u_doc = await UserDocument.find_one(UserDocument.email == email)
        if not u_doc:
            raise DocumentDoesNotExist(f"User '{email}' not found")

        team_names = await self.get_user_team_names(u_doc)
        u_read = UserRead(
            username=u_doc.username,
            email=u_doc.email,
            first_name=u_doc.first_name,
            last_name=u_doc.last_name,
            organization=u_doc.organization,
            teams=team_names,
            is_active=u_doc.is_active,
            is_superuser=u_doc.is_superuser,
        )
        return u_read

    async def get_user_by_username(self, username: str) -> UserDocument | None:
        """Get user by cognito username decoded from access token"""
        u_doc = await UserDocument.find_one(UserDocument.username == username)
        if not u_doc:
            raise DocumentDoesNotExist(f"User not found - username: {username}")
        return u_doc

    async def get_user_by_id(self, id: PydanticObjectId) -> UserDocument | None:
        """Get user by document id"""
        u_doc = await UserDocument.get(id)
        if not u_doc:
            raise DocumentDoesNotExist(f"User not found - user id: {id}")
        return u_doc

    async def get_user_team_names(self, u_doc: UserDocument | None) -> list[str]:
        """Given a user, return its team names"""
        if not u_doc:
            return []

        t_docs = TeamDocument.find({"_id": {"$in": u_doc.teams}})
        return [t_doc.name async for t_doc in t_docs]

    async def get_user_team_ids(
        self,
        u_doc: UserDocument | None,
    ) -> list[PydanticObjectId]:
        """Given a user, return its team ids"""
        if not u_doc:
            return []

        t_docs = TeamDocument.find({"_id": {"$in": u_doc.teams}})
        return [t_doc.id async for t_doc in t_docs]

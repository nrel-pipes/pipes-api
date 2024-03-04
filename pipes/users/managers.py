from __future__ import annotations

import logging
from datetime import datetime

from beanie import PydanticObjectId
from fastapi import HTTPException, status
from pydantic import EmailStr
from pymongo.errors import DuplicateKeyError

from pipes.common.manager import AbstractObjectManager
from pipes.teams.schemas import TeamDocument
from pipes.users.schemas import UserCreate, CognitoUserCreate, UserRead, UserDocument

logger = logging.getLogger(__name__)


class UserManager(AbstractObjectManager):
    """Manager class for user management"""

    async def validate_context(self):
        """No need to validate the context for user management"""
        pass

    async def create_cognito_user(
        self,
        u_create: CognitoUserCreate,
    ) -> UserDocument | None:
        """Admin create new user"""
        u_doc = UserDocument(
            username=u_create.username,
            email=u_create.email,
            first_name=u_create.first_name,
            last_name=u_create.last_name,
            organization=u_create.organization,
            created_at=datetime.utcnow(),
            is_active=True,
            is_superuser=False,
        )
        try:
            await u_doc.insert()
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User '{u_create.email}' already exists.",
            )
        return u_doc

    async def get_or_create_user(self, u_create: UserCreate) -> UserDocument | None:
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

    async def get_user_by_email(self, user_email: EmailStr) -> UserRead | None:
        """Get user by email"""
        user_email = user_email.lower()
        u_doc = await UserDocument.find_one(UserDocument.email == user_email)
        if not u_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return u_doc

    async def get_user_team_names(self, user_doc: UserDocument) -> list[str]:
        """Given a user, return its team names"""
        t_docs = TeamDocument.find({"_id": {"$in": user_doc.teams}})
        return [t_doc.name async for t_doc in t_docs]

    async def get_user_team_ids(self, user_doc: UserDocument) -> list[PydanticObjectId]:
        t_docs = TeamDocument.find({"_id": {"$in": user_doc.teams}})
        return [t_doc.id async for t_doc in t_docs]

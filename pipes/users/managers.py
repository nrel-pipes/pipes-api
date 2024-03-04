from __future__ import annotations

import logging
from datetime import datetime

from beanie import PydanticObjectId
from fastapi import HTTPException, status
from pydantic import EmailStr
from pymongo.errors import DuplicateKeyError

from pipes.common.manager import ObjectManager
from pipes.users.schemas import (
    TeamCreate,
    TeamRead,
    TeamDocument,
    UserCreate,
    UserRead,
    UserDocument,
)

logger = logging.getLogger(__name__)


class TeamManager(ObjectManager):
    """Manager class for team anagement"""

    async def create_team(self, team_create: TeamCreate) -> TeamRead | None:
        """Create new team"""
        team_doc = TeamDocument(
            name=team_create.name,
            description=team_create.description,
        )
        try:
            await team_doc.insert()
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Team '{team_create.name}' already exists.",
            )
        logger.info("New team '%s' created successfully.", team_doc.name)
        team_read = TeamRead(name=team_doc.name, description=team_doc.description)
        return team_read

    async def get_team_by_name(self, team_name: str) -> TeamRead | None:
        """Get team by name"""
        team_doc = await TeamDocument.find_one(TeamDocument.name == team_name)
        if not team_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team '{team_name}' not found",
            )
        team_read = TeamRead(name=team_doc.name, description=team_doc.description)
        return team_read

    async def get_team_members(self, team_name: str) -> list[UserRead]:
        """Given a team, return all team members"""
        team_doc = await TeamDocument.find_one(TeamDocument.name == team_name)
        if team_doc is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Team '{team_name}' not exist",
            )
        members = await UserDocument.find({"teams": team_doc.id}).to_list()
        return members

    async def put_team_members(
        self,
        team_name: str,
        user_emails: list[EmailStr],
    ) -> None:
        """Add team members"""
        # Validate team
        team_doc = await TeamDocument.find_one(TeamDocument.name == team_name)
        if team_doc is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Team '{team_name}' not exist",
            )

        # Validate users
        user_docs = UserDocument.find({"email": {"$in": user_emails}})
        candidates, knowns = [], set()
        async for user_doc in user_docs:
            knowns.add(user_doc.email)
            if team_doc.id in user_doc.teams:
                logger.info(
                    "Skip! User '%s' already exists in team '%s'",
                    user_doc.email,
                    team_name,
                )
                continue
            candidates.append(user_doc)

        unknowns = set(user_emails).difference(knowns)
        if unknowns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User {unknowns} not exist",
            )

        # Update user teams
        for user_doc in candidates:
            user_doc.teams.add(team_doc.id)
            await user_doc.save()
            logger.info("Put user '%s' into team '%s'.", user_doc.email, team_name)


class UserManager(ObjectManager):
    """Manager class for user management"""

    async def create_user(self, user_create: UserCreate) -> UserDocument | None:
        user_doc = UserDocument(
            username=user_create.username,
            email=user_create.email,
            first_name=user_create.first_name,
            last_name=user_create.last_name,
            organization=user_create.organization,
            created_at=datetime.utcnow(),
            is_active=True,
            is_superuser=False,
        )
        try:
            await user_doc.insert()
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User '{user_create.email}' already exists.",
            )
        return user_doc

    async def get_user_by_email(self, user_email: EmailStr) -> UserRead | None:
        """Get user by email"""
        user_doc = await UserDocument.find_one(UserDocument.email == user_email)
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        team_names = await self.get_user_team_names(user_doc)
        user_read = UserRead(
            email=user_doc.email,
            first_name=user_doc.first_name,
            last_name=user_doc.last_name,
            organization=user_doc.organization,
            teams=team_names,
        )
        return user_read

    async def get_user_by_username(self, username: str) -> UserDocument | None:
        """Get user by cognito username decoded from access token"""
        user_doc = await UserDocument.find_one(UserDocument.username == username)
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user_doc

    async def get_user_team_names(self, user_doc: UserDocument) -> list[str]:
        """Given a user, return its team names"""
        team_docs = TeamDocument.find({"_id": {"$in": user_doc.teams}})
        return [team_doc.name async for team_doc in team_docs]

    async def get_user_team_ids(self, user_doc: UserDocument) -> list[PydanticObjectId]:
        team_docs = TeamDocument.find({"_id": {"$in": user_doc.teams}})
        return [team_doc.id async for team_doc in team_docs]

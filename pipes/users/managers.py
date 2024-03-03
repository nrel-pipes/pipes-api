from __future__ import annotations

import logging
from datetime import datetime

from fastapi import HTTPException, status
from pydantic import EmailStr
from pymongo.errors import DuplicateKeyError

from pipes.db.manager import DocumentGrahpObjectManager
from pipes.users.schemas import (
    TeamCreate,
    TeamRead,
    TeamDocument,
    TeamMembers,
    UserCreate,
    UserRead,
    UserDocument,
)

logger = logging.getLogger(__name__)


class TeamManager(DocumentGrahpObjectManager):
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

    async def get_team_members(self, team_name: str) -> TeamMembers:
        """Given a team, return all team members"""
        team_doc = await TeamDocument.find_one(TeamDocument.name == team_name)
        if team_doc is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Team '{team_name}' not exist",
            )
        members = UserDocument.find({"teams": team_doc.id})
        team_members = TeamMembers(
            team=team_name,
            members=[m.email async for m in members],
        )
        return team_members

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


class UserManager(DocumentGrahpObjectManager):
    """Manager class for user management"""

    async def create_user(self, user_create: UserCreate) -> UserRead | None:
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
        user_read = user_doc  # NOTE: FastAPI will automatically convert it
        return user_read

    async def get_user_by_email(self, user_email: EmailStr) -> UserRead | None:
        """Get user by email"""
        user_doc = await UserDocument.find_one(UserDocument.email == user_email)
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        team_names = await self._get_user_teams(user_doc)
        user_read = UserRead(
            email=user_doc.email,
            first_name=user_doc.first_name,
            last_name=user_doc.last_name,
            organization=user_doc.organization,
            teams=team_names,
        )
        return user_read

    async def get_user_by_username(self, username: str) -> UserRead | None:
        """Get user by cognito username decoded from access token"""
        print("================================uuasusuau")
        print("xjldjalfdsa: ===", username)
        user_doc = await UserDocument.find_one(UserDocument.username == username)
        print(user_doc)
        print("userdaodc===")
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user_doc

    async def _get_user_teams(self, user_doc: UserDocument):
        """Given a user, return its team names"""
        team_docs = TeamDocument.find({"_id": {"$in": user_doc.teams}})
        return [team_doc.name async for team_doc in team_docs]

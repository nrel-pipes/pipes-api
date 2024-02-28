from __future__ import annotations

import logging
from datetime import datetime

from beanie import PydanticObjectId
from fastapi import HTTPException, status
from pydantic import EmailStr
from pymongo.errors import DuplicateKeyError

from pipes.db.manager import DocumentGrahpObjectManager
from pipes.users.schemas import (
    Team,
    TeamMembers,
    TeamDocument,
    UserCreate,
    UserRead,
    UserDocument,
)

logger = logging.getLogger(__name__)


class TeamManager(DocumentGrahpObjectManager):
    """Manager class for team anagement"""

    async def create_team(self, team: Team) -> Team | None:
        """Create new team"""
        team = TeamDocument(name=team.name, description=team.description)
        try:
            await team.insert()
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Team '{team.name}' already exists.",
            )

        logger.info("New team '%s' created successfully.", team.name)
        return team

    async def get_team_by_name(self, name: str) -> Team | None:
        """Get team by name"""
        team = await TeamDocument.find_one(TeamDocument.name == name)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team '{name}' not found",
            )
        return team

    async def get_team_by_id(self, id: PydanticObjectId) -> TeamDocument | None:
        """Get team by document _id"""
        team = await TeamDocument.get(id)
        if not team:
            raise
        return team

    async def get_team_members(self, team: str) -> TeamMembers:
        """Given a team, return all team members"""
        _team = await TeamDocument.find_one(TeamDocument.name == team)
        if _team is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Team '{team}' not exist",
            )
        members = UserDocument.find({"teams": _team.id})
        team_members = TeamMembers(
            team=team,
            members=[m.email async for m in members],
        )
        return team_members

    async def put_team_members(self, team: str, emails: list[EmailStr]) -> None:
        """Add team members"""
        # Validate team
        _team = await TeamDocument.find_one(TeamDocument.name == team)
        if _team is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Team '{team}' not exist",
            )

        # Validate users
        users = UserDocument.find({"email": {"$in": emails}})
        candidates, knowns = [], set()
        async for user in users:
            knowns.add(user.email)
            if _team.id in user.teams:
                logger.info(
                    "Skip! User '%s' already exists in team '%s'",
                    user.email,
                    team,
                )
                continue
            candidates.append(user)

        unknowns = set(emails).difference(knowns)
        if unknowns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User {unknowns} not exist",
            )

        # Update user teams
        for user in candidates:
            user.teams.add(_team.id)
            await user.save()
            logger.info("Put user '%s' into team '%s'.", user.email, team)


class UserManager(DocumentGrahpObjectManager):
    """Manager class for user management"""

    async def create_user(self, user: UserCreate) -> UserRead | None:
        user = UserDocument(
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            organization=user.organization,
            created_at=datetime.utcnow(),
            is_active=True,
            is_superuser=False,
        )
        try:
            await user.insert()
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User '{user.email}' already exists.",
            )
        return user

    async def get_user_by_email(self, email: EmailStr) -> UserRead | None:
        """Get user by email"""
        user = await UserDocument.find_one(UserDocument.email == email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        teams = await self._get_user_team_names(user)
        _user = UserRead(
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            organization=user.organization,
            teams=teams,
        )
        return _user

    async def get_user_by_id(self, id: PydanticObjectId) -> UserRead | None:
        """Get team by document _id"""
        user = await UserDocument.get(id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user

    async def _get_user_team_names(self, user: UserDocument):
        teams = TeamDocument.find({"_id": {"$in": user.teams}})
        return [team.name async for team in teams]

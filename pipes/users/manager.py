from __future__ import annotations

from datetime import datetime

from beanie import PydanticObjectId
from pydantic import EmailStr

from pipes.db.manager import DocumentGrahpObjectManager
from pipes.users.schemas import TeamCreate, TeamRead, TeamDocument
from pipes.users.schemas import UserCreate, UserRead, UserDocument


class TeamManager(DocumentGrahpObjectManager):
    """Manager class for team anagement"""

    async def create_team(self, team: TeamCreate) -> TeamRead | None:
        """Create new team"""
        _team = TeamDocument(name=team.name, description=team.description)
        await _team.insert()
        team = TeamRead(
            name=_team.name,
            description=_team.description,
            members=[],
        )
        return team

    async def get_team_by_name(self, team_name: str) -> TeamRead | None:
        """Get team by name"""
        _team = await TeamDocument.find_one(TeamDocument.name == team_name)
        users = await UserDocument.find(UserDocument.teams.id == _team.id).to_list()  # type: ignore
        emails = [u.email for u in users]
        team = TeamRead(
            name=_team.name,
            description=_team.description,
            members=emails,
        )
        return team

    async def get_team_by_id(self, id: PydanticObjectId) -> TeamDocument | None:
        """Get team by document _id"""
        team = await TeamDocument.get(id)
        return team


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
        await user.insert()
        return user

    async def get_user_by_email(self, email: EmailStr) -> UserRead | None:
        """Get user by email"""
        user = await UserDocument.find_one(UserDocument.email == email)
        return user

    async def get_user_by_id(self, id: PydanticObjectId) -> TeamDocument | None:
        """Get team by document _id"""
        user = await UserDocument.get(id)
        return user

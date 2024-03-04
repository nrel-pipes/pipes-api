from __future__ import annotations

import logging
from datetime import datetime

from beanie import PydanticObjectId
from fastapi import HTTPException, status
from pydantic import EmailStr
from pymongo.errors import DuplicateKeyError

from pipes.common.contexts import ProjectUserContext
from pipes.common.manager import AbstractObjectManager
from pipes.projects.schemas import ProjectDocument
from pipes.users.schemas import (
    TeamCreate,
    TeamDocument,
    UserCreate,
    UserRead,
    UserDocument,
)

logger = logging.getLogger(__name__)


class TeamManager(AbstractObjectManager):
    """Manager class for team anagement"""

    async def validate_context(self, context: ProjectUserContext) -> dict:
        """Validate under project user context"""
        if not self.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid context, user None.",
            )

        p_name = context.get("project", None)
        if not p_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid context, project '{p_name}'.",
            )

        p_doc = await ProjectDocument.find_one(ProjectDocument.name == p_name)
        if not p_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Invalid context, project '{p_name}' not found.",
            )

        is_superuser = self.user.is_superuser
        is_owner = self.user.id == p_doc.owner
        is_lead = self.user.id in p_doc.leads
        is_creator = self.user.id == p_doc.created_by

        if not (is_superuser or is_owner or is_lead or is_creator):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Invalid context, no access to project '{p_name}'.",
            )

        validated_context = {"project": p_doc}
        return validated_context

    async def create_team(
        self,
        p_doc: ProjectDocument,
        t_create: TeamCreate,
    ) -> TeamDocument | None:
        """Create new team"""
        t_doc = TeamDocument(
            context={"project": p_doc.id},
            name=t_create.name,
            description=t_create.description,
        )
        try:
            await t_doc.insert()
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Team '{t_create.name}' already exists.",
            )
        logger.info(
            "New team '%s' created successfully under project '%s'.",
            t_doc.name,
            p_doc.name,
        )
        return t_doc

    async def get_team_by_name(self, team_name: str) -> TeamDocument | None:
        """Get team by name"""
        team_doc = await TeamDocument.find_one(TeamDocument.name == team_name)
        if not team_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team '{team_name}' not found",
            )
        return team_doc

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


class UserManager(AbstractObjectManager):
    """Manager class for user management"""

    async def validate_context(self, context):
        pass

    async def create_user(self, u_create: UserCreate) -> UserDocument | None:
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

    async def get_user_by_email(self, user_email: EmailStr) -> UserRead | None:
        """Get user by email"""
        u_doc = await UserDocument.find_one(UserDocument.email == user_email)
        if not u_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        team_names = await self.get_user_team_names(u_doc)
        u_read = UserRead(
            email=u_doc.email,
            first_name=u_doc.first_name,
            last_name=u_doc.last_name,
            organization=u_doc.organization,
            teams=team_names,
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

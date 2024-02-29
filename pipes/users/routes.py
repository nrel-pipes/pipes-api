from __future__ import annotations

from fastapi import APIRouter
from pydantic import EmailStr

from pipes.users.manager import TeamManager, UserManager
from pipes.users.schemas import TeamCreate, TeamRead, TeamMembers, UserCreate, UserRead

router = APIRouter()


# Teams
@router.post("/teams/", response_model=TeamRead)
async def create_team(team_create: TeamCreate):
    """Create a new team"""
    manager = TeamManager()
    new_team = await manager.create_team(team_create)  # type: ignore
    return new_team


@router.get("/teams/", response_model=TeamRead)
async def get_team_by_name(team_name: str):
    """Get the team by name"""
    manager = TeamManager()
    team_read = await manager.get_team_by_name(team_name)
    return team_read


@router.put("/teams/members/")
async def put_team_members(team_name: str, user_emails: list[EmailStr]):
    """Put one or more users to a team"""
    manager = TeamManager()
    await manager.put_team_members(team_name, user_emails)
    return {
        "message": f"Added users {user_emails} into team '{team_name}' successfully.",
    }


@router.get("/teams/members/", response_model=TeamMembers)
async def get_team_members(team_name: str):
    """Given team name, get the team members"""
    manager = TeamManager()
    team_members = await manager.get_team_members(team_name)
    return team_members


# Users
@router.post("/users/", response_model=UserRead)
async def create_user(user_create: UserCreate):
    """Create a new user"""
    manager = UserManager()
    user_read = await manager.create_user(user_create)  # type: ignore
    return user_read


@router.get("/users/", response_model=UserRead)
async def get_user_by_email(user_email: EmailStr):
    """Get a user by email"""
    manager = UserManager()
    user_read = await manager.get_user_by_email(user_email)
    return user_read

from __future__ import annotations

from fastapi import APIRouter
from pydantic import EmailStr

from pipes.users.manager import TeamManager, UserManager
from pipes.users.schemas import Team, TeamMembers, UserCreate, UserRead

router = APIRouter()


# Teams
@router.post("/teams/", response_model=Team)
async def create_team(team: Team):
    """Create a new team"""
    manager = TeamManager()
    new_team = await manager.create_team(team)  # type: ignore
    return new_team


@router.get("/teams/", response_model=Team)
async def get_team_by_name(name: str):
    """Get the team by name"""
    manager = TeamManager()
    team = await manager.get_team_by_name(name)
    return team


@router.get("/teams/members/", response_model=TeamMembers)
async def get_team_members(team: str):
    """Given team name, get the team members"""
    manager = TeamManager()
    team_members = await manager.get_team_members(team)
    return team_members


@router.put("/teams/members/")
async def put_team_members(team: str, emails: list[EmailStr]):
    """Put one or more users to a team"""
    manager = TeamManager()
    await manager.put_team_members(team, emails)
    return {
        "message": f"Added users {emails} into team '{team}' successfully.",
    }


# Users
@router.post("/users/", response_model=UserRead)
async def create_user(user: UserCreate):
    """Create a new user"""
    manager = UserManager()
    new_user = await manager.create_user(user)  # type: ignore
    return new_user


@router.get("/users/", response_model=UserRead)
async def get_user_by_email(email: EmailStr):
    """Get a user by email"""
    manager = UserManager()
    user = await manager.get_user_by_email(email)
    return user

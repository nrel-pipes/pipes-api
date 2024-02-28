from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from pydantic import EmailStr
from pymongo.errors import DuplicateKeyError

from pipes.users.manager import TeamManager, UserManager
from pipes.users.schemas import TeamCreate, TeamRead
from pipes.users.schemas import UserCreate, UserRead

router = APIRouter()


# Teams
@router.post("/teams/", response_model=TeamRead)
async def create_team(team: TeamCreate):
    """Create a new team"""
    manager = TeamManager()
    try:
        team = await manager.create_team(team)  # type: ignore
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Team '{team.name}' already exists.",
        )
    return team


@router.get("/teams/", response_model=TeamRead)
async def get_team_by_name(name: str):
    """Get the team by name"""
    manager = TeamManager()
    team = await manager.get_team_by_name(name)
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )
    return team


# Users
@router.post("/users/", response_model=UserRead)
async def create_user(user: UserCreate):
    """Create a new user"""
    manager = UserManager()
    try:
        user = await manager.create_user(user)  # type: ignore
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User '{user.email}' already exists.",
        )
    return user


@router.get("/users/", response_model=UserRead)
async def get_user_by_email(email: EmailStr):
    """Get a user by email"""
    manager = UserManager()
    user = await manager.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user

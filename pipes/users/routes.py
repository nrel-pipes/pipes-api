from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import EmailStr

from pipes.common.contexts import UserContext, ProjectContext
from pipes.users.auth import auth_required
from pipes.users.managers import TeamManager, UserManager
from pipes.users.schemas import TeamCreate, TeamRead, UserCreate, UserRead, UserDocument

router = APIRouter()


# Teams
@router.post("/teams/", response_model=TeamRead)
async def create_project_team(
    project_name: str,
    t_create: TeamCreate,
    user: UserDocument = Depends(auth_required),
):
    """Create a new team"""
    context = ProjectContext(project=project_name, user=user)
    manager = TeamManager(context)
    validated_context = await manager.validate_context(context)

    p_doc = validated_context.get("project")
    new_team = await manager.create_team(p_doc, t_create)  # type: ignore

    return new_team


@router.get("/teams/", response_model=TeamRead)
async def get_project_team_by_name(
    project_name: str,
    team_name: str,
    user: UserDocument = Depends(auth_required),
):
    """Get the team by name"""
    context = ProjectContext(project=project_name, user=user)
    manager = TeamManager(context)
    await manager.validate_context(context)  # TODO:

    t_doc = await manager.get_team_by_name(team_name)
    return t_doc


@router.put("/teams/members/")
async def update_project_team_members(
    project_name: str,
    team_name: str,
    user_emails: list[EmailStr],
    user: UserDocument = Depends(auth_required),
):
    """Put one or more users to a team"""
    context = ProjectContext(project=project_name, user=user)
    manager = TeamManager(context)
    await manager.validate_context(context)  # TODO:

    await manager.put_team_members(team_name, user_emails)
    return {
        "message": f"Added users {user_emails} into team '{team_name}' successfully.",
    }


@router.get("/teams/members/", response_model=list[UserRead])
async def get_project_team_members(
    project_name: str,
    team_name: str,
    user: UserDocument = Depends(auth_required),
):
    """Given team name, get the team members"""
    context = ProjectContext(project=project_name, user=user)
    manager = TeamManager(context)
    await manager.validate_context(context)  # TODO:

    team_members = await manager.get_team_members(team_name)
    return team_members


# Users
@router.post("/users/", response_model=UserRead)
async def create_user(
    user_create: UserCreate,
    user: UserDocument = Depends(auth_required),
):
    """Create a new user"""
    manager = UserManager(UserContext(user=None))
    u_read = await manager.create_user(user_create)  # type: ignore
    return u_read


@router.get("/users/", response_model=UserRead)
async def get_user_by_email(
    user_email: EmailStr,
    user: UserDocument = Depends(auth_required),
):
    """Get a user by email"""
    manager = UserManager(UserContext(user=None))
    u_read = await manager.get_user_by_email(user_email)
    return u_read

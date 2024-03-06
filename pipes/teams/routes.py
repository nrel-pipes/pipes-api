from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from pipes.common import exceptions as E
from pipes.projects.contexts import ProjectTextContext
from pipes.teams.managers import TeamManager
from pipes.teams.schemas import TeamCreate, TeamRead
from pipes.users.auth import auth_required
from pipes.users.schemas import UserCreate, UserRead, UserDocument

router = APIRouter()


# Teams
@router.post("/teams/", response_model=TeamRead)
async def create_project_team(
    project: str,
    data: TeamCreate,
    user: UserDocument = Depends(auth_required),
):
    """Create a new team"""
    context = ProjectTextContext(project=project)
    manager = TeamManager(user)
    try:
        validated_context = await manager.validate_context(context)
    except E.ContextValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except E.ContextPermissionDenied as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    p_doc = validated_context.project
    if not p_doc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid context, project None",
        )

    try:
        t_doc = await manager.create_project_team(data)
    except E.DocumentAlreadyExists as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    data = t_doc.model_dump()
    data["context"] = {"project": p_doc.name}

    t_read = TeamRead.model_validate(data)
    return t_read


@router.get("/teams/", response_model=TeamRead)
async def get_project_team_by_name(
    project: str,
    team: str,
    user: UserDocument = Depends(auth_required),
):
    """Get the team by name"""
    context = ProjectTextContext(project=project)
    try:
        manager = TeamManager(user)
        validated_context = await manager.validate_context(context)
    except E.ContextValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except E.ContextPermissionDenied as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    t_doc = await manager.get_project_team_by_name(team)
    if t_doc is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not find team '{team}' of project '{project}'.",
        )

    p_doc = validated_context.project
    u_docs = await UserDocument.find({"teams": t_doc.id}).to_list()
    t_read = TeamRead(
        name=t_doc.name,
        description=t_doc.description,
        members=u_docs,
        context=ProjectTextContext(project=p_doc.name),
    )
    return t_read


@router.put("/teams/members/")
async def update_project_team_members(
    project: str,
    team: str,
    data: list[UserCreate],
    user: UserDocument = Depends(auth_required),
):
    """Put one or more users to a team"""
    context = ProjectTextContext(project=project)

    try:
        manager = TeamManager(user)
        validated_context = await manager.validate_context(context)
    except E.ContextValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except E.ContextPermissionDenied as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    try:
        await manager.update_project_team_members(team, data)
    except E.DocumentDoesNotExist as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    emails = [u.email for u in data]
    p_doc = validated_context.project
    return {
        "message": f"Added users {emails} into team '{team}' of project '{p_doc.name}'",
    }


@router.get("/teams/members/", response_model=list[UserRead])
async def get_project_team_members(
    project: str,
    team: str,
    user: UserDocument = Depends(auth_required),
):
    """Given team name, get the team members"""
    context = ProjectTextContext(project=project)
    try:
        manager = TeamManager(user)
        await manager.validate_context(context)
    except E.ContextValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except E.ContextPermissionDenied as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    team_members = await manager.get_project_team_members(team)
    return team_members

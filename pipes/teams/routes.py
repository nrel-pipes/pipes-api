from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from pipes.common.contexts import ProjectContext
from pipes.common.exceptions import (
    ContextValidationError,
    ContextPermissionDenied,
    DocumentAlreadyExists,
    DocumentDoesNotExist,
)
from pipes.teams.manager import TeamManager
from pipes.teams.schemas import TeamCreate, TeamRead, TeamUpdate
from pipes.users.auth import auth_required
from pipes.users.schemas import UserDocument

router = APIRouter()


# Teams
@router.post("/teams/", response_model=TeamRead, status_code=201)
async def create_project_team(
    project: str,
    data: TeamCreate,
    user: UserDocument = Depends(auth_required),
):
    """Create a new team"""
    context = dict(project=project)
    manager = TeamManager()
    try:
        validated_context = await manager.validate_user_context(user, context)
    except ContextValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except ContextPermissionDenied as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    p_doc = validated_context["project"]
    if not p_doc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid context, project None",
        )

    try:
        t_doc = await manager.create_project_team(data)
    except DocumentAlreadyExists as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Query members
    u_docs = await UserDocument.find({"_id": {"$in": t_doc.members}}).to_list()

    t_read = TeamRead(
        name=t_doc.name,
        description=t_doc.description,
        context={"project": p_doc.name},
        members=u_docs,
    )

    return t_read


@router.get("/teams/", response_model=list[TeamRead])
async def get_project_teams(
    project: str,
    user: UserDocument = Depends(auth_required),
):
    """Get the teams of given project"""
    context = dict(project=project)
    try:
        manager = TeamManager()
        validated_context = await manager.validate_user_context(user, context)
    except ContextValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except ContextPermissionDenied as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    t_docs = await manager.get_project_teams()
    if not t_docs:
        return []

    t_reads = []
    p_doc = validated_context["project"]
    for t_doc in t_docs:
        u_docs = await UserDocument.find({"_id": {"$in": t_doc.members}}).to_list()
        t_reads.append(
            TeamRead(
                name=t_doc.name,
                description=t_doc.description,
                members=u_docs,
                context=ProjectContext(project=p_doc.name),
            ),
        )
    return t_reads


@router.put("/teams/detail/")
async def update_project_team(
    project: str,
    team: str,
    data: TeamUpdate,
    user: UserDocument = Depends(auth_required),
):
    """Update project team"""
    context = dict(project=project)

    try:
        manager = TeamManager()
        validated_context = await manager.validate_user_context(user, context)
    except ContextValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except ContextPermissionDenied as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    try:
        t_doc = await manager.update_project_team(team, data)
    except (DocumentDoesNotExist, DocumentAlreadyExists) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    p_doc = validated_context["project"]
    u_docs = await UserDocument.find({"_id": {"$in": t_doc.members}}).to_list()
    t_read = TeamRead(
        name=t_doc.name,
        description=t_doc.description,
        members=u_docs,
        context=ProjectContext(project=p_doc.name),
    )
    return t_read

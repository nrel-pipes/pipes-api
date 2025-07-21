from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from pipes.common.exceptions import (
    ContextValidationError,
    UserPermissionDenied,
    DocumentAlreadyExists,
    DocumentDoesNotExist,
)
from pipes.db.document import DocumentDB
from pipes.projects.contexts import ProjectSimpleContext
from pipes.projects.validators import ProjectContextValidator
from pipes.teams.manager import TeamManager
from pipes.teams.schemas import TeamCreate, TeamRead, TeamUpdate
from pipes.users.auth import auth_required
from pipes.users.schemas import UserDocument

router = APIRouter()


# Teams
@router.post("/teams", response_model=TeamRead, status_code=201)
async def create_team(
    project: str,
    data: TeamCreate,
    user: UserDocument = Depends(auth_required),
):
    """Create a new team"""
    context = ProjectSimpleContext(project=project)

    try:
        validator = ProjectContextValidator()
        validated_context = await validator.validate(user, context)
    except ContextValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except UserPermissionDenied as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    try:
        manager = TeamManager(context=validated_context)
        t_doc = await manager.create_team(data)
    except DocumentAlreadyExists as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Query members
    docdb = DocumentDB()
    u_docs = await docdb.find_all(
        collection=UserDocument,
        query={"_id": {"$in": t_doc.members}},
    )

    t_read = TeamRead(
        name=t_doc.name,
        description=t_doc.description,
        context={"project": project},
        members=u_docs,
    )

    return t_read


@router.get("/teams", response_model=list[TeamRead])
async def get_teams(
    project: str,
    user: UserDocument = Depends(auth_required),
):
    """Get the teams of given project"""
    context = ProjectSimpleContext(project=project)

    try:
        validator = ProjectContextValidator()
        validated_context = await validator.validate(user, context)
    except ContextValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except UserPermissionDenied as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    manager = TeamManager(context=validated_context)
    p_teams = await manager.get_all_teams()
    return p_teams


@router.patch("/teams/detail")
async def update_team(
    project: str,
    team: str,
    data: TeamUpdate,
    user: UserDocument = Depends(auth_required),
):
    """Update project team"""
    context = ProjectSimpleContext(project=project)

    try:
        validator = ProjectContextValidator()
        validated_context = await validator.validate(user, context)
    except ContextValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except UserPermissionDenied as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    try:
        manager = TeamManager(context=validated_context)
        t_doc = await manager.update_team(team, data)
    except (DocumentDoesNotExist, DocumentAlreadyExists) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    docdb = DocumentDB()
    u_docs = await docdb.find_all(
        collection=UserDocument,
        query={"_id": {"$in": t_doc.members}},
    )
    t_read = TeamRead(
        name=t_doc.name,
        description=t_doc.description,
        members=u_docs,
        context=ProjectSimpleContext(project=project),
    )
    return t_read

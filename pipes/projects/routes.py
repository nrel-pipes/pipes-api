from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from pipes.common.exceptions import (
    UserPermissionDenied,
    ContextValidationError,
    DocumentDoesNotExist,
    DomainValidationError,
    VertexAlreadyExists,
)
from pipes.projects.contexts import ProjectSimpleContext
from pipes.projects.manager import ProjectManager
from pipes.projects.schemas import (
    ProjectCreate,
    ProjectBasicRead,
    ProjectDetailRead,
    ProjectUpdate,
)
from pipes.projects.validators import ProjectContextValidator
from pipes.users.auth import auth_required
from pipes.users.schemas import UserDocument

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/projects/basics", response_model=list[ProjectBasicRead])
async def get_basic_projects(user: UserDocument = Depends(auth_required)):
    """Get all projects with basic information"""
    manager = ProjectManager()
    p_read_docs = await manager.get_basic_projects(user)
    return p_read_docs


@router.post("/projects", response_model=ProjectDetailRead, status_code=201)
async def create_project(
    data: ProjectCreate,
    user: UserDocument = Depends(auth_required),
):
    """Create a new project"""
    try:
        manager = ProjectManager()
        p_doc = await manager.create_project(data, user)
    except (VertexAlreadyExists, DocumentDoesNotExist, DomainValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Read referenced documents
    p_read = await manager.read_project_detail(p_doc)

    return p_read


@router.get("/projects", response_model=ProjectDetailRead)
async def get_project(
    project: str,
    user: UserDocument = Depends(auth_required),
):
    """Get project detail information"""
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

    p_doc = validated_context.project

    # Read referenced documents
    manager = ProjectManager()
    p_read = await manager.read_project_detail(p_doc)

    return p_read


@router.put("/projects", response_model=ProjectDetailRead, status_code=200)
async def update_project(
    project: str,
    data: ProjectUpdate,
    user: UserDocument = Depends(auth_required),
):
    """
    Update Project by given project name and data.
    """
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

    p_doc = validated_context.project
    try:
        p_manager = ProjectManager()
        p_doc = await p_manager.update_project(p_doc=p_doc, p_update=data, user=user)
    except (DocumentDoesNotExist, DomainValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    p_read = await p_manager.read_project_detail(p_doc)

    return p_read

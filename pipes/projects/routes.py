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
from pipes.projectruns.manager import ProjectRunManager
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


@router.put("/projects/{project}", response_model=ProjectDetailRead, status_code=200)
async def update_project(
    project: str,
    data: ProjectUpdate,
    user: UserDocument = Depends(auth_required),
):
    """
    Update Project workflow
    - Gets project runs
    - Update Project logic
    """
    # Gets all the project runs
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

    pr_manager = ProjectRunManager(context=validated_context)
    pr_docs = await pr_manager.get_projectruns()

    try:
        p_manager = ProjectManager()
        p_doc = await p_manager.update_project(
            p_update=data,
            projectrun_docs=pr_docs,
            project=project,
            user=user,
        )
    except (DocumentDoesNotExist, DomainValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    # Read referenced documents
    p_read = await p_manager.read_project_detail(p_doc)

    return p_read


@router.get("/projects", response_model=ProjectDetailRead)
async def get_project_detail(
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


@router.get("/projects/basics", response_model=list[ProjectBasicRead])
async def get_basic_projects(user: UserDocument = Depends(auth_required)):
    """Get all projects with basic information"""
    manager = ProjectManager()
    p_read_docs = await manager.get_basic_projects(user)
    return p_read_docs


@router.delete("/projects", status_code=204)
async def delete_project(
    project: str,
    user: UserDocument = Depends(auth_required),
):
    """Delete a project by given project name"""
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

    manager = ProjectManager()
    p_doc = validated_context.project
    try:
        await manager.delete_project(p_doc.name)
    except DocumentDoesNotExist as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        # Handle any unexpected errors (e.g., Neptune connection issues)
        logger.error(f"Error deleting project '{project}': {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}",
        )

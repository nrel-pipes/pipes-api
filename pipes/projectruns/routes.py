from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from pipes.common.exceptions import (
    ContextValidationError,
    UserPermissionDenied,
    DocumentAlreadyExists,
    DomainValidationError,
    DocumentDoesNotExist,
)
from pipes.projects.contexts import ProjectSimpleContext
from pipes.projects.validators import ProjectContextValidator
from pipes.projectruns.schemas import ProjectRunCreate, ProjectRunRead, ProjectRunUpdate
from pipes.projectruns.manager import ProjectRunManager
from pipes.projectruns.contexts import ProjectRunSimpleContext
from pipes.projectruns.validators import ProjectRunContextValidator
from pipes.users.auth import auth_required
from pipes.users.schemas import UserDocument
from pipes.models.manager import ModelManager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/projectruns", response_model=ProjectRunRead, status_code=201)
async def create_projectrun(
    project: str,
    data: ProjectRunCreate,
    user: UserDocument = Depends(auth_required),
):
    """Create project run under given project"""
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

    manager = ProjectRunManager(context=validated_context)
    try:
        pr_doc = await manager.create_projectrun(data, user)
    except (DocumentAlreadyExists, DomainValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    pr_read = await manager.read_projectrun(pr_doc)

    return pr_read


@router.get("/projectruns", response_model=list[ProjectRunRead] | ProjectRunRead)
async def get_projectruns(
    project: str,
    projectrun: str | None = None,
    user: UserDocument = Depends(auth_required),
):
    """Get all project runs under given project, or a specific project run if projectrun is provided"""
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

    manager = ProjectRunManager(context=validated_context)

    if projectrun is not None:
        # Return specific project run
        try:
            pr_doc = await manager.get_projectrun(projectrun)
            pr_read = await manager.read_projectrun(pr_doc)
            return pr_read
        except DocumentDoesNotExist as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )
    else:
        pr_docs = await manager.get_projectruns()
        return pr_docs


@router.delete("/projectruns", status_code=204)
async def delete_projectrun(
    project: str,
    projectrun: str,
    user: UserDocument = Depends(auth_required),
):
    """Delete project run if it doesn't have any models under it"""
    context = ProjectRunSimpleContext(project=project, projectrun=projectrun)

    try:
        validator = ProjectRunContextValidator()
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

    manager = ProjectRunManager(context=validated_context)

    try:
        try:
            await manager.get_projectrun(projectrun)
        except DocumentDoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project run '{projectrun}' not found",
            )

        # Check if there are models under this project run
        model_manager = ModelManager(context=validated_context)
        models = await model_manager.get_models()

        if models:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete project run '{projectrun}' because it has models associated with it",
            )

        # Delete the project run
        await manager.delete_projectrun(projectrun)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return None


@router.put("/projectruns", response_model=ProjectRunRead)
async def update_projectrun(
    project: str,
    projectrun: str,
    data: ProjectRunUpdate,
    user: UserDocument = Depends(auth_required),
):
    """Update project run under given project"""
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

    manager = ProjectRunManager(context=validated_context)
    try:
        pr_doc = await manager.update_projectrun(projectrun, data, user)
    except DocumentDoesNotExist as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except (DocumentAlreadyExists, DomainValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    pr_read = await manager.read_projectrun(pr_doc)

    return pr_read

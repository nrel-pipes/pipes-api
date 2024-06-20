from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from pipes.common.exceptions import (
    ContextValidationError,
    UserPermissionDenied,
    DocumentAlreadyExists,
    DomainValidationError,
)
from pipes.projects.contexts import ProjectSimpleContext
from pipes.projects.validators import ProjectContextValidator
from pipes.projectruns.schemas import ProjectRunCreate, ProjectRunRead
from pipes.projectruns.manager import ProjectRunManager
from pipes.users.auth import auth_required
from pipes.users.schemas import UserDocument

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/projectruns/", response_model=ProjectRunRead, status_code=201)
async def create_projectrun(
    project: str,
    data: ProjectRunCreate,
    user: UserDocument = Depends(auth_required),
):
    """Create project run under given project"""
    logger.info(f"User: {user} \n Data: {data} \n project: {project}")

    context = ProjectSimpleContext(project=project)
    print(context)
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
    print(f"call: {p_doc}")
    manager = ProjectRunManager()
    try:
        pr_doc = await manager.create_projectrun(p_doc, data, user)
    except (DocumentAlreadyExists, DomainValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    pr_read = await manager.read_projectrun(pr_doc)

    return pr_read


@router.get("/projectruns/", response_model=list[ProjectRunRead])
async def get_projectruns(
    project: str,
    user: UserDocument = Depends(auth_required),
):
    """Get all project runs under given project"""
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
    manager = ProjectRunManager()
    pr_docs = await manager.get_projectruns(p_doc)

    return pr_docs

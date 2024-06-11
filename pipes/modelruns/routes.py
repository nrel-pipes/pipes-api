from __future__ import annotations

import logging
from fastapi import APIRouter, Depends, HTTPException, status

from pipes.common.exceptions import (
    ContextValidationError,
    DocumentAlreadyExists,
    DocumentDoesNotExist,
    DomainValidationError,
    UserPermissionDenied,
)
from pipes.models.contexts import ModelSimpleContext
from pipes.models.validators import ModelContextValidator
from pipes.modelruns.manager import ModelRunManager
from pipes.modelruns.schemas import ModelRunCreate, ModelRunRead, ModelRunUpdate
from pipes.users.auth import auth_required
from pipes.users.schemas import UserDocument

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/modelruns/", response_model=ModelRunRead, status_code=201)
async def create_modelrun(
    project: str,
    projectrun: str,
    model: str,
    data: ModelRunCreate,
    user: UserDocument = Depends(auth_required),
):
    """Create a model run with given project/projectrun/model"""
    context = ModelSimpleContext(
        project=project,
        projectrun=projectrun,
        model=model,
    )

    try:
        validator = ModelContextValidator()
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
    pr_doc = validated_context.projectrun
    m_doc = validated_context.model

    manager = ModelRunManager()
    try:
        mr_doc = await manager.create_modelrun(p_doc, pr_doc, m_doc, data, user)
    except (DocumentAlreadyExists, DomainValidationError, DocumentDoesNotExist) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    mr_read = await manager.read_modelrun(mr_doc)

    return mr_read


@router.get("/modelruns/", response_model=list[ModelRunRead])
async def get_modelruns(
    project: str,
    projectrun: str,
    model: str,
    user: UserDocument = Depends(auth_required),
):
    """Get all model runs under the given project/projectrun/model"""
    context = ModelSimpleContext(project=project, projectrun=projectrun, model=model)

    try:
        validator = ModelContextValidator()
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

    manager = ModelRunManager()
    mr_reads = await manager.get_modelruns(
        p_doc=validated_context.project,
        pr_doc=validated_context.projectrun,
        m_doc=validated_context.model,
    )

    return mr_reads


@router.put("/modelruns/", response_model=ModelRunUpdate)
async def update_status(
    project: str,
    projectrun: str,
    model: str,
    modelrun: str,
    user: UserDocument = Depends(auth_required),
    status: str = "PENDING",
):
    context = ModelSimpleContext(
        project=project,
        projectrun=projectrun,
        model=model,
    )
    try:
        validator = ModelContextValidator()
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
    pr_doc = validated_context.projectrun
    m_doc = validated_context.model

    manager = ModelRunManager()
    mr_doc = await manager.update_status(p_doc, pr_doc, m_doc, modelrun, status)

    return mr_doc

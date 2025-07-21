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
from pipes.modelruns.schemas import ModelRunCreate, ModelRunRead
from pipes.projects.contexts import ProjectSimpleContext
from pipes.projects.validators import ProjectContextValidator
from pipes.projectruns.contexts import ProjectRunSimpleContext
from pipes.projectruns.validators import ProjectRunContextValidator
from pipes.users.auth import auth_required
from pipes.users.schemas import UserDocument

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/modelruns", response_model=ModelRunRead, status_code=201)
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

    manager = ModelRunManager(context=validated_context)
    try:
        mr_doc = await manager.create_modelrun(data, user)
    except (
        DocumentAlreadyExists,
        DomainValidationError,
        DocumentDoesNotExist,
    ) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    mr_read = await manager.read_modelrun(mr_doc)

    return mr_read


@router.get("/modelruns", response_model=list[ModelRunRead])
async def get_modelruns(
    project: str,
    projectrun: str | None = None,
    model: str | None = None,
    user: UserDocument = Depends(auth_required),
):
    """Get all model runs under the given project/projectrun/model"""
    if projectrun and model:
        context = ModelSimpleContext(
            project=project,
            projectrun=projectrun,
            model=model,
        )

        try:
            validator1 = ModelContextValidator()
            validated_context = await validator1.validate(user, context)
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

        manager = ModelRunManager(context=validated_context)
        mr_reads = await manager.get_modelruns()
        return mr_reads

    if projectrun and (not model):
        pr_context = ProjectRunSimpleContext(project=project, projectrun=projectrun)
        try:
            validator2 = ProjectRunContextValidator()
            validated_context = await validator2.validate(user, pr_context)
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
        manager = ModelRunManager(context=validated_context)
        mr_reads = await manager.get_modelruns()
        return mr_reads

    if (not projectrun) and (not model):
        p_context = ProjectSimpleContext(project=project)
        try:
            validator3 = ProjectContextValidator()
            validated_context = await validator3.validate(user, p_context)
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
        manager = ModelRunManager(context=validated_context)
        mr_reads = await manager.get_modelruns()
        return mr_reads

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from pipes.common.exceptions import (
    ContextValidationError,
    UserPermissionDenied,
    DocumentAlreadyExists,
    DocumentDoesNotExist,
    DomainValidationError,
)
from pipes.models.manager import ModelManager
from pipes.models.schemas import ModelCreate, ModelRead, ModelUpdate
from pipes.projects.contexts import ProjectSimpleContext, ProjectDocumentContext
from pipes.projects.validators import ProjectContextValidator
from pipes.projectruns.contexts import ProjectRunSimpleContext
from pipes.projectruns.validators import ProjectRunContextValidator
from pipes.modelruns.manager import ModelRunManager
from pipes.users.auth import auth_required
from pipes.users.schemas import UserDocument

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/models", response_model=ModelRead, status_code=201)
async def create_model(
    project: str,
    projectrun: str,
    data: ModelCreate,
    user: UserDocument = Depends(auth_required),
):
    """Create a new model under the given project and projectrun"""
    context = ProjectRunSimpleContext(
        project=project,
        projectrun=projectrun,
    )

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

    manager = ModelManager(context=validated_context)
    try:
        m_doc = await manager.create_model(data, user)
    except (
        DocumentAlreadyExists,
        DomainValidationError,
        DocumentDoesNotExist,
    ) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    m_read = await manager.read_model(m_doc)

    return m_read


@router.get("/models", response_model=list[ModelRead])
async def get_models(
    project: str,
    projectrun: str | None = None,
    user: UserDocument = Depends(auth_required),
):
    """Get all models with given project and projectrun"""
    m_reads = []

    if projectrun is None:
        p_context = ProjectSimpleContext(project=project)
        try:
            validator = ProjectContextValidator()
            validated_context = await validator.validate(user, p_context)
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

        # pr_manager = ProjectRunManager(context=validated_context)

        # pr_docs = await pr_manager.get_projectruns(read_docs=False)
        p_context = ProjectDocumentContext(project=validated_context.project)
        m_manager = ModelManager(context=p_context)
        _m_reads = await m_manager.get_models()
        m_reads.extend(_m_reads)

    else:
        pr_context = ProjectRunSimpleContext(project=project, projectrun=projectrun)
        try:
            validator = ProjectRunContextValidator()
            validated_context = await validator.validate(user, pr_context)
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
        manager = ModelManager(context=validated_context)
        _m_reads = await manager.get_models()
        m_reads.extend(_m_reads)

    return m_reads


@router.get("/models/detail", response_model=ModelRead)
async def get_model(
    project: str,
    projectrun: str,
    model: str,
    user: UserDocument = Depends(auth_required),
):
    """Get a specific model by project and model name"""
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

    try:
        p_context = ProjectDocumentContext(project=validated_context.project)
        manager = ModelManager(context=p_context)
        m_doc = await manager.get_model(model)
    except DocumentDoesNotExist as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    m_read = await manager.read_model(m_doc)
    return m_read


@router.delete("/models", status_code=204)
async def delete_model(
    project: str,
    projectrun: str,
    model: str,
    user: UserDocument = Depends(auth_required),
):
    """Delete model if it doesn't have any model runs under it"""
    context = ProjectRunSimpleContext(
        project=project,
        projectrun=projectrun,
    )

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

    manager = ModelManager(context=validated_context)

    try:
        try:
            await manager.get_model(model)
        except DocumentDoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model '{model}' not found",
            )

        # Check if there are any model runs under this model
        modelrun_manager = ModelRunManager(context=validated_context)
        modelruns = await modelrun_manager.get_modelruns()

        if modelruns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete model '{model}' because it has model runs associated with it",
            )

        # Delete the model
        await manager.delete_model(
            project=validated_context.project,
            projectrun=validated_context.projectrun,
            model=model,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return None


@router.patch("/models", response_model=ModelRead)
async def update_model(
    project: str,
    projectrun: str,
    model: str,
    data: ModelUpdate,
    user: UserDocument = Depends(auth_required),
):
    """Update a model by project, projectrun, and model name"""
    context = ProjectRunSimpleContext(
        project=project,
        projectrun=projectrun,
    )

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

    manager = ModelManager(context=validated_context)
    try:
        m_doc = await manager.get_model(model)
        updated_m_doc = await manager.update_model(m_doc, data, user)
    except DocumentDoesNotExist as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except DocumentAlreadyExists as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    m_read = await manager.read_model(updated_m_doc)
    return m_read

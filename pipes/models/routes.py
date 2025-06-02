from __future__ import annotations

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from pipes.common.exceptions import (
    ContextValidationError,
    UserPermissionDenied,
    DocumentAlreadyExists,
    DocumentDoesNotExist,
    DomainValidationError,
    VertexAlreadyExists,
)
from pipes.models.manager import ModelManager, ModelCatalogManager
from pipes.models.schemas import ModelCreate, ModelRead, CatalogModelCreate, ModelCatalogDocument
from pipes.projects.contexts import ProjectSimpleContext, ProjectDocumentContext
from pipes.projects.validators import ProjectContextValidator
from pipes.projectruns.contexts import ProjectRunSimpleContext
from pipes.projectruns.validators import ProjectRunContextValidator
from pipes.users.auth import auth_required
from pipes.users.schemas import UserDocument

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/model_catalog", response_model=ModelCatalogDocument, status_code=201)
async def create_catalog_model(
    data: CatalogModelCreate,
    user: UserDocument = Depends(auth_required),
):
    manager = ModelCatalogManager()
    try:
        mc_doc = await manager.create_model(data, user)
    except (
        DocumentAlreadyExists,
        DomainValidationError,
        DocumentDoesNotExist,
    ) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    mr_doc = await manager.read_model(mc_doc.name)
    return mr_doc


@router.get("/model_catalog", response_model=List[CatalogModelCreate], status_code=200)
async def get_catalog_models(
    user: UserDocument = Depends(auth_required)
):
    manager = ModelCatalogManager()
    model_catalog = await manager.get_models()
    print("model_catalog", model_catalog)
    return model_catalog


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
        VertexAlreadyExists,
        DocumentAlreadyExists,
        DomainValidationError,
        DocumentDoesNotExist,
    ) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    m_read = await manager.read_model(m_doc.name)

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

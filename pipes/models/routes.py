from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from pipes.common.exceptions import (
    ContextValidationError,
    UserPermissionDenied,
    DocumentAlreadyExists,
    DocumentDoesNotExist,
    DomainValidationError,
    VertexAlreadyExists,
)
from pipes.models.manager import ModelManager
from pipes.models.schemas import ModelCreate, ModelRead
from pipes.projects.contexts import ProjectSimpleContext
from pipes.projects.validators import ProjectContextValidator
from pipes.projectruns.contexts import (
    ProjectRunSimpleContext,
    ProjectRunDocumentContext,
)
from pipes.projectruns.manager import ProjectRunManager
from pipes.projectruns.validators import ProjectRunContextValidator
from pipes.users.auth import auth_required
from pipes.users.schemas import UserDocument

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/models/", response_model=ModelRead, status_code=201)
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

    m_read = await manager.read_model(m_doc)

    return m_read


@router.get("/models/", response_model=list[ModelRead])
async def get_models(
    project: str,
    projectrun: str | None = None,
    user: UserDocument = Depends(auth_required),
):
    """Get all models with given project and projectrun"""
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

        m_reads = []
        pr_manager = ProjectRunManager(context=validated_context)

        pr_docs = await pr_manager.get_projectruns(read_docs=False)
        for pr_doc in pr_docs:
            pr_context = ProjectRunDocumentContext(
                project=validated_context.project,
                projectrun=pr_doc,
            )
            m_manager = ModelManager(context=pr_context)
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
        m_reads = await manager.get_models()

    return m_reads

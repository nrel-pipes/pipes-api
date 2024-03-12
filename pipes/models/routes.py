import logging

from fastapi import APIRouter, Depends, HTTPException, status

from pipes.common.exceptions import (
    ContextValidationError,
    UserPermissionDenied,
    DocumentAlreadyExists,
    DomainValidationError,
)
from pipes.models.manager import ModelManager
from pipes.models.schemas import ModelCreate, ModelRead
from pipes.projectruns.contexts import ProjectRunSimpleContext
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

    p_doc = validated_context.project
    pr_doc = validated_context.projectrun

    manager = ModelManager()
    try:

        m_doc = await manager.create_model(p_doc, pr_doc, data, user)
    except (DocumentAlreadyExists, DomainValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    m_read = manager.read_model(m_doc)

    return m_read


@router.get("/models/")
async def get_models(
    project: str,
    projectrun: str,
    user: UserDocument = Depends(auth_required),
):
    """Get all models with given project and projectrun"""
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

    manager = ModelManager()
    p_doc, pr_doc = validated_context.project, validated_context.projectrun
    m_docs = await manager.get_models(p_doc, pr_doc)

    return m_docs

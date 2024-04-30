from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from pipes.common.exceptions import (
    ContextValidationError,
    UserPermissionDenied,
    DocumentAlreadyExists,
    DocumentDoesNotExist,
    DomainValidationError,
    EdgeAlreadyExists,
)
from pipes.handoffs.manager import HandoffManager
from pipes.handoffs.schemas import HandoffCreate, HandoffRead
from pipes.projectruns.contexts import ProjectRunSimpleContext
from pipes.projectruns.validators import ProjectRunContextValidator
from pipes.users.auth import auth_required
from pipes.users.schemas import UserDocument

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/handoffs/",
    response_model=HandoffRead | list[HandoffRead],
    status_code=201,
)
async def create_handoff(
    project: str,
    projectrun: str,
    data: HandoffCreate | list[HandoffCreate],
    user: UserDocument = Depends(auth_required),
):
    """Create a new handoff"""
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

    manager = HandoffManager(context=validated_context)

    if isinstance(data, HandoffCreate):
        data = [data]

    try:
        h_docs = await manager.create_handoffs(data, user)
    except (
        EdgeAlreadyExists,
        DocumentAlreadyExists,
        DomainValidationError,
        DocumentDoesNotExist,
    ) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    h_reads = []
    for h_doc in h_docs:
        h_read = await manager.read_handoff(h_doc)
        h_reads.append(h_read)

    if len(h_reads) == 1:
        return h_reads[0]

    return h_reads


@router.get("/handoffs/", response_model=list[HandoffRead])
async def get_handoffs(
    project: str,
    projectrun: str,
    model: str | None = None,
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

    manager = HandoffManager(context=validated_context)
    h_reads = await manager.get_handoffs(model)

    return h_reads

from __future__ import annotations

from pipes.common.exceptions import (
    ContextValidationError,
    DocumentAlreadyExists,
    DocumentDoesNotExist,
    DomainValidationError,
    UserPermissionDenied,
)
from pipes.datasets.manager import DatasetManager
from pipes.datasets.schemas import DatasetCreate, DatasetRead
from pipes.modelruns.contexts import ModelRunSimpleContext
from pipes.modelruns.validators import ModelRunContextValidator
from pipes.users.auth import auth_required
from pipes.users.schemas import UserDocument

from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter()


@router.post("/datasets", response_model=DatasetRead, status_code=201)
async def create_dataset(
    project: str,
    projectrun: str,
    model: str,
    modelrun: str,
    data: DatasetCreate,
    user: UserDocument = Depends(auth_required),
):
    """Create a dataset with given context"""
    context = ModelRunSimpleContext(
        project=project,
        projectrun=projectrun,
        model=model,
        modelrun=modelrun,
    )

    try:
        validator = ModelRunContextValidator()
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

    manager = DatasetManager(context=validated_context)
    try:
        d_doc = await manager.create_dataset(data, user)
    except (
        DocumentAlreadyExists,
        DomainValidationError,
        DocumentDoesNotExist,
    ) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    d_read = await manager.read_dataset(d_doc)

    return d_read


@router.get("/datasets", response_model=list[DatasetRead])
async def get_datasets(
    project: str,
    projectrun: str,
    model: str,
    modelrun: str,
    user: UserDocument = Depends(auth_required),
):
    """Get all datasets under given context"""
    context = ModelRunSimpleContext(
        project=project,
        projectrun=projectrun,
        model=model,
        modelrun=modelrun,
    )

    try:
        validator = ModelRunContextValidator()
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

    manager = DatasetManager(context=validated_context)
    d_reads = await manager.get_datasets()

    return d_reads

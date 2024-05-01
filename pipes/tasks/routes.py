from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from pipes.common.exceptions import (
    ContextValidationError,
    DocumentAlreadyExists,
    DocumentDoesNotExist,
    DomainValidationError,
    UserPermissionDenied,
    VertexAlreadyExists,
)
from pipes.modelruns.contexts import ModelRunSimpleContext
from pipes.modelruns.validators import ModelRunContextValidator
from pipes.tasks.schemas import TaskCreate, TaskRead
from pipes.tasks.manager import TaskManager
from pipes.users.auth import auth_required
from pipes.users.schemas import UserDocument

router = APIRouter()


@router.post("/tasks", response_model=TaskRead, status_code=201)
async def create_task(
    project: str,
    projectrun: str,
    model: str,
    modelrun: str,
    data: TaskCreate,
    user: UserDocument = Depends(auth_required),
):
    """Create a task with given context"""
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

    manager = TaskManager(context=validated_context)
    try:
        task_doc = await manager.create_task(data, user)
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

    task_read = await manager.read_task(task_doc)

    return task_read


@router.get("/tasks", response_model=list[TaskRead])
async def get_tasks(
    project: str,
    projectrun: str,
    model: str,
    modelrun: str,
    user: UserDocument = Depends(auth_required),
):
    """Get all tasks under given context"""
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

    manager = TaskManager(context=validated_context)
    d_reads = await manager.get_tasks()

    return d_reads

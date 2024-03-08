from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from pipes.common.exceptions import (
    ContextPermissionDenied,
    ContextValidationError,
    DocumentAlreadyExists,
)
from pipes.projects.manager import ProjectManager
from pipes.projects.schemas import ProjectCreate, ProjectBasicRead, ProjectDetailRead
from pipes.users.auth import auth_required
from pipes.users.manager import UserManager
from pipes.users.schemas import UserDocument

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/projects/detail/", response_model=ProjectDetailRead)
async def create_project(
    data: ProjectCreate,
    user: UserDocument = Depends(auth_required),
):
    """Create a new project"""
    project_manager = ProjectManager()
    await project_manager.validate_user_context(user=user, context={})

    try:
        p_doc = await project_manager.create_project(data)
    except DocumentAlreadyExists as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Convert owner object into dictionary
    user_manager = UserManager()
    p_read = p_doc.model_dump()
    owner_doc = await user_manager.get_user_by_id(p_read["owner"])
    p_read["owner"] = owner_doc.read()

    return p_read


@router.get("/projects/detail/", response_model=ProjectDetailRead)
async def get_project_detail(
    project: str,
    user: UserDocument = Depends(auth_required),
):
    """Get project detail information"""
    manager = ProjectManager()
    try:
        context = dict(project=project)
        await manager.validate_user_context(user, context)
    except ContextValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except ContextPermissionDenied as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    p_doc = await manager.get_project_detail()

    # Convert owner object into dictionary
    user_manager = UserManager()
    p_read = p_doc.model_dump()
    owner_doc = await user_manager.get_user_by_id(p_read["owner"])
    p_read["owner"] = owner_doc.read()

    return p_read


@router.get("/projects/basic/", response_model=list[ProjectBasicRead])
async def get_projects(user: UserDocument = Depends(auth_required)):
    """Get all projects with basic information"""
    manager = ProjectManager()
    try:
        await manager.validate_user_context(user, {})
    except ContextValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except ContextPermissionDenied as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    p_read_docs = await manager.list_projects_of_current_user()
    return p_read_docs


# @router.put("/projects/detail/", response_model=ProjectDetailRead)
# async def update_project_detail(
#     project: str,
#     data: ProjectUpdate,
#     user: UserDocument = Depends(auth_required),
# ):
#     """Update project detail information"""
#     context = dict(project=project)
#     manager = ProjectManager(user)
#     try:
#         await manager.validate_context(context)
#     except ContextValidationError as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(e),
#         )
#     except ContextPermissionDenied as e:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail=str(e),
#         )

#     try:
#         p_doc = await manager.update_project_detail(p_update=data)
#     except DocumentAlreadyExists as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(e),
#         )

#     return p_doc

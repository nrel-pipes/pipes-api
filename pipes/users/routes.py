from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr

from pipes.users.auth import auth_required
from pipes.common.exceptions import DocumentDoesNotExist, DocumentAlreadyExists
from pipes.users.managers import UserManager
from pipes.users.schemas import UserCreate, UserRead, UserDocument

router = APIRouter()


@router.post("/users/", response_model=UserRead)
async def create_user(
    data: UserCreate,
    user: UserDocument = Depends(auth_required),
):
    """Create a new user"""
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not permitted. Admin only.",
        )

    try:
        manager = UserManager(user)

        # NOTE: No context validation for user management now
        # await manager.validate_context(UserManagementContext())

        u_doc = await manager.create_user(data)
    except DocumentAlreadyExists as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    return u_doc


@router.get("/users/", response_model=list[UserRead])
async def get_all_users(user: UserDocument = Depends(auth_required)):
    """Get a user by email"""
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not permitted. Admin only.",
        )

    manager = UserManager(user)

    # NOTE: No context validation for user management now
    # await manager.validate_context(UserManagementContext())

    u_docs = await manager.get_users()
    return u_docs


@router.get("/users/detail/", response_model=UserRead)
async def get_user_by_email(
    email: EmailStr,
    user: UserDocument = Depends(auth_required),
):
    """
    Get a user by email
    * Admin user could query detail of any user by email
    * Regular user could query detail of their own.
    """
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not permitted. Admin only.",
        )

    try:
        manager = UserManager(user)

        # NOTE: No context validation for user management now
        # await manager.validate_context(UserManagementContext())

        u_read = await manager.get_user_by_email(email)
    except DocumentDoesNotExist as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    return u_read

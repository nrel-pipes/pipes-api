from __future__ import annotations

from pipes.common.exceptions import (
    DocumentAlreadyExists,
    DocumentDoesNotExist,
    VertexAlreadyExists,
)
from pipes.users.auth import auth_required
from pipes.users.manager import UserManager
from pipes.users.schemas import UserCreate, UserDocument, UserRead, UserUpdate

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr

router = APIRouter()


@router.post("/users", response_model=UserRead, status_code=201)
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
        manager = UserManager()
        u_doc = await manager.create_user(data)
    except (VertexAlreadyExists, DocumentAlreadyExists) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    return u_doc


@router.get("/users", response_model=list[UserRead])
async def get_all_users(user: UserDocument = Depends(auth_required)):
    """Get a user by email"""
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not permitted. Admin only.",
        )

    manager = UserManager()
    u_docs = await manager.get_all_users()
    return u_docs


@router.get("/users/detail", response_model=UserRead)
async def get_user_by_email(
    email: EmailStr,
    user: UserDocument = Depends(auth_required),
):
    """
    Get a user by email
    * Admin user could query detail of any user by email
    * Regular user could query detail of their own.
    """
    if (not user.is_superuser) and (email.lower() != user.email.lower()):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not permitted.",
        )

    try:
        manager = UserManager()
        u_doc = await manager.get_user_by_email(email)
    except DocumentDoesNotExist as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    return u_doc


@router.put("/users/update", response_model=UserRead)
async def update_user(
    email: EmailStr,
    data: UserUpdate,
    user: UserDocument = Depends(auth_required),
):
    """
    Update user information
    * Admin users can update any user's information
    * Regular users can only update their own information
    * Only admin users can update the is_superuser attribute
    """
    # Check permissions: admin can update anyone, users can only update themselves
    if (not user.is_superuser) and (email.lower() != user.email.lower()):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not permitted. You can only update your own information.",
        )
    # Only admins can grant admin privileges
    if data.is_superuser and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not permitted. Only admins can grant admin privileges.",
        )

    try:
        manager = UserManager()
        u_doc = await manager.get_user_by_email(email)

        # Update user attributes
        if data.first_name is not None:
            u_doc.first_name = data.first_name
        if data.last_name is not None:
            u_doc.last_name = data.last_name
        if data.organization is not None:
            u_doc.organization = data.organization
        if data.is_active is not None:
            u_doc.is_active = data.is_active
        # Only allow superusers to update is_superuser field
        if user.is_superuser and data.is_superuser is not None:
            u_doc.is_superuser = data.is_superuser

        await u_doc.save()
        return u_doc
    except DocumentDoesNotExist as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

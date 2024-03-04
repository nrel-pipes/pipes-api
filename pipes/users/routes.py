from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import EmailStr

from pipes.users.contexts import UserContext
from pipes.users.auth import auth_required, admin_required
from pipes.users.managers import UserManager
from pipes.users.schemas import UserCreate, UserRead, UserDocument

router = APIRouter()

# Users


@router.post("/users/", response_model=UserRead)
async def create_user(
    user_create: UserCreate,
    user: UserDocument = Depends(admin_required),
):
    """Create a new user"""
    context = UserContext(user=user)
    manager = UserManager(context)
    u_doc = await manager.create_user(user_create)
    u_read = u_doc  # FastAPI ignore extra fields automatically
    return u_read


@router.get("/users/", response_model=list[UserRead])
async def get_all_users(user: UserDocument = Depends(admin_required)):
    """Get a user by email"""
    context = UserContext(user=user)
    manager = UserManager(context)
    u_docs = await manager.get_users()
    return u_docs


@router.get("/users/profile/", response_model=UserRead)
async def get_user_by_email(
    user_email: EmailStr,
    user: UserDocument = Depends(auth_required),
):
    """Get a user by email"""
    context = UserContext(user=user)
    manager = UserManager(context)
    u_read = await manager.get_user_by_email(user_email)
    return u_read

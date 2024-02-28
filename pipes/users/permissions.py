from __future__ import annotations

from fastapi import HTTPException, Request, status

from pipes.users.authenticate import CognitoAuth


class AdminAuth(CognitoAuth):

    def authenticate(self, request):
        user = super().authenticate(request)
        if not user or not user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to perform this action.",
            )
        return user


class ManagerAuth(CognitoAuth):

    def authenticate(self, request):
        user = super().authenticate(request)
        if not user or not user.is_manager:  # TODO: Default user roles
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to perform this action.",
            )
        return user


async def auth_required(request: Request):
    """Authenticate the user and return it"""
    auth = CognitoAuth()
    user = await auth.authenticate(request)
    request.state.user = user
    return user


async def admin_required(request: Request):
    """Authenticate admin user for operations"""
    auth = AdminAuth()
    user = await auth.authenticate(request)
    request.state.user = user
    return user


async def manager_required(request: Request):
    """Authenticate manager for operations"""
    auth = ManagerAuth()
    user = await auth.authenticate(request)
    request.state.user = user
    return user

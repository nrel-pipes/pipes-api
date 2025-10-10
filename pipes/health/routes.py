from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def welcome():
    return {"message": "ok", "status": "healthy"}


@router.get("/ping")
async def ping():
    """
    Check the health status of the NREL PIPES service.
    """
    return {"message": "pong", "status": "healthy"}

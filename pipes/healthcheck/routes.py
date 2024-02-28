from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def welcome():
    return {"message": "Hello, Welcome to PIPES API!"}


@router.get("/ping/")
async def ping():
    """
    For ALB health check, need to ping Neptune regularly to avoid idle timeout - 20mins

    https://docs.aws.amazon.com/neptune/latest/userguide/limits.html#limits-websockets
    """
    return {"message": "pong"}

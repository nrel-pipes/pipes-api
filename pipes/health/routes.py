from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from pipes.db.neptune import NeptuneDB

router = APIRouter()


def get_neptune_db():
    """A dependency function for FastAPI"""
    db = NeptuneDB()
    try:
        db.connect()
        yield db
    finally:
        db.close()


@router.get("/")
async def welcome():
    return {"message": "Welcome to NREL PIPES!"}


@router.get("/ping")
async def ping(neptune: NeptuneDB = Depends(get_neptune_db)):
    """
    For ALB health check, need to ping Neptune regularly to avoid idle timeout - 20mins

    https://docs.aws.amazon.com/neptune/latest/userguide/limits.html#limits-websockets
    """
    try:
        data = neptune.ping()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    vtx = data[0] if len(data) > 0 else None
    if not vtx:
        vid = None
    else:
        vid = vtx.id
    return {"message": "pong", "vertex": vid}

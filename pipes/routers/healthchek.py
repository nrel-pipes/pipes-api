from fastapi import APIRouter


router = APIRouter()


@router.get("/ping")
def healthcheck():
    """
    For ALB health check, need to ping Neptune regularly to avoid idle timeout - 20mins

    https://docs.aws.amazon.com/neptune/latest/userguide/limits.html#limits-websockets
    """
    return {"message": "pong"}

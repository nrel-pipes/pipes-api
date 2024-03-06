from fastapi import APIRouter


router = APIRouter()


@router.post("/tasks/")
def create_task():
    pass


@router.get("/tasks/")
def get_tasks():
    pass

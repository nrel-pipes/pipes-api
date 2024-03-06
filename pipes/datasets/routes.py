from fastapi import APIRouter

router = APIRouter()


@router.post("/datasets/")
def checkin_dataset():
    pass


@router.get("/datasets/")
def get_datasets():
    pass

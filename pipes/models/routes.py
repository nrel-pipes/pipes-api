import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/models/")
def create_model():
    pass


@router.post("/models/")
def get_models():
    pass


@router.post("/models/runs/")
def create_modelrun():
    pass


@router.get("/models/runs/")
def get_modelruns():
    pass

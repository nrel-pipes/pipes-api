import logging

from fastapi import APIRouter, Depends

from pipes.projects.managers import ProjectManager
from pipes.projects.schemas import (
    ProjectCreate,
    ProjectReadBasic,
    ProjectReadDetail,
)
from pipes.users.auth import auth_required
from pipes.users.schemas import UserRead

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/projects/", response_model=ProjectReadBasic)
async def create_project(
    project_create: ProjectCreate,
    current_user: UserRead = Depends(auth_required),
):
    """Create a new project"""
    pm = ProjectManager()
    pm.set_current_user(user=current_user)
    project = await pm.create_project(project_create)
    return project


@router.get("/projects/", response_model=list[ProjectReadBasic])
async def get_projects(
    current_user: UserRead = Depends(auth_required),
):
    """Get all projects with basic information"""
    pm = ProjectManager()
    pm.set_current_user(user=current_user)
    p_read_docs = await pm.get_current_user_projects()
    return p_read_docs


@router.put("/projects/details/", response_model=ProjectReadDetail)
async def put_project_detail(
    project_name: str,
    current_user: UserRead = Depends(auth_required),
):
    pass


@router.get("/projects/details/", response_model=ProjectReadDetail)
async def get_project_detail(
    project_name: str,
    current_user: UserRead = Depends(auth_required),
):
    pass


# @router.post("/projects/runs/", response_model=ProjectRunRead)
# async def create_project_run(projectrun_create: ProjectRunCreate):
#     pass


# @router.get("/projects/runs/", response_model=ProjectRunRead)
# async def get_project_run_by_name(projectrun_name: str):
#     pass


##############################################################################
# NOTE: Remove in the future, simulate GRPC returns in MVP
##############################################################################
grpcrouter = APIRouter()


@grpcrouter.get("/projects/")
async def get_grpc_projects():
    """
    Returns all projects that the current user has been participating in.
    """
    logger.info("Listing projects...")
    # TODO:
    projects = [
        {
            "name": "test1",
            "full_name": "Test One Solar PV",
            "description": "This is the test1 project about solar PV plant",
        },
        {
            "name": "test2",
            "full_name": "Test Two Biomass Energy",
            "description": "This is the test2 project about bioenergy",
        },
        {
            "name": "test3",
            "full_name": "Test Three Geothermal Tech",
            "description": "This is the test3 project about geothermal technology",
        },
    ]
    return projects

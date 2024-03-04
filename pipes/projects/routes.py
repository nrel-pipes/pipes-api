import logging

from fastapi import APIRouter, Depends

from pipes.projects.managers import ProjectManager
from pipes.projects.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectReadBasic,
    ProjectReadDetail,
)
from pipes.users.auth import auth_required
from pipes.users.schemas import UserRead

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/projects/", response_model=ProjectReadBasic)
async def create_project(
    p_create: ProjectCreate,
    user: UserRead = Depends(auth_required),
):
    """Create a new project"""
    manager = ProjectManager()
    manager.set_current_user(user)
    p_doc = await manager.create_project(p_create)
    p_read_basic = p_doc
    return p_read_basic


@router.get("/projects/basics/", response_model=list[ProjectReadBasic])
async def get_projects(user: UserRead = Depends(auth_required)):
    """Get all projects with basic information"""
    manager = ProjectManager()
    manager.set_current_user(user)
    p_read_docs = await manager.get_projects_of_current_user()
    return p_read_docs


@router.put("/projects/details/", response_model=ProjectReadDetail)
async def put_project_detail(
    pub_id: str,
    p_update: ProjectUpdate,
    user: UserRead = Depends(auth_required),
):
    """Update project detail information"""
    manager = ProjectManager()
    manager.set_current_user(user)

    p_doc = await manager.update_project_details(pub_id=pub_id, p_update=p_update)

    p_read_detail = p_doc  # FastAPI will ignore extra fields by default
    return p_read_detail


@router.get("/projects/details/", response_model=ProjectReadDetail)
async def get_project_detail(
    pub_id: str,
    user: UserRead = Depends(auth_required),
):
    """Get project detail information"""
    manager = ProjectManager()
    manager.set_current_user(user)

    p_doc = await manager.get_project_details(pub_id=pub_id)
    p_read_detail = p_doc  # FastAPI will ignore extra fields by default
    return p_read_detail


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

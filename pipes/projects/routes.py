import logging

from fastapi import APIRouter, Depends, HTTPException, status

from pipes.common import exceptions as E
from pipes.projects.contexts import ProjectTextContext
from pipes.projects.managers import ProjectManager
from pipes.projects import schemas as S
from pipes.users.auth import auth_required
from pipes.users.schemas import UserDocument

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/projects/", response_model=S.ProjectBasicRead)
async def create_project(
    data: S.ProjectCreate,
    user: UserDocument = Depends(auth_required),
):
    """Create a new project"""
    context = ProjectTextContext(project=data.name)
    manager = ProjectManager(user)

    try:
        await manager.validate_context(context)
    except E.ContextValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except E.ContextPermissionDenied as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    try:
        p_doc = await manager.create_project(data)
    except E.DocumentAlreadyExists as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    return p_doc


@router.get("/projects/", response_model=list[S.ProjectBasicRead])
async def get_projects(user: UserDocument = Depends(auth_required)):
    """Get all projects with basic information"""
    context = ProjectTextContext(project="")
    manager = ProjectManager(user)
    try:
        await manager.validate_context(context)
    except E.ContextValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except E.ContextPermissionDenied as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    p_read_docs = await manager.get_user_projects()
    return p_read_docs


@router.put("/projects/detail/", response_model=S.ProjectDetailRead)
async def update_project_detail(
    project: str,
    data: S.ProjectUpdate,
    user: UserDocument = Depends(auth_required),
):
    """Update project detail information"""
    context = ProjectTextContext(project=project)
    manager = ProjectManager(user)
    try:
        await manager.validate_context(context)
    except E.ContextValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except E.ContextPermissionDenied as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    try:
        p_doc = await manager.update_project_detail(p_update=data)
    except E.DocumentAlreadyExists as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return p_doc


@router.get("/projects/detail/", response_model=S.ProjectDetailRead)
async def get_project_detail(
    project: str,
    user: UserDocument = Depends(auth_required),
):
    """Get project detail information"""
    context = ProjectTextContext(project=project)
    manager = ProjectManager(user)
    try:
        await manager.validate_context(context)
    except E.ContextValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except E.ContextPermissionDenied as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    p_doc = await manager.get_project_detail()
    return p_doc


@router.post("/projects/runs/", response_model=S.ProjectRunRead)
async def create_project_run(projectrun_create: S.ProjectRunCreate):
    pass


@router.get("/projects/runs/", response_model=S.ProjectRunRead)
async def get_project_run_by_name(projectrun_name: str):
    pass


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

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/projects")
async def list_projects():
    """
    Returns all projects that the current user has been participating in.
    """
    # TODO:
    projects = [
        {
            "name": "test1",
            "full_name": "Test One Solar PV",
            "description": "This is the test1 project about solar PV plant",
        },
        {
            "name": "test2",
            "full_name": "Test One Solar PV",
            "description": "This is the test1 project about solar PV plant",
        },
        {
            "name": "test3",
            "full_name": "Test One Solar PV",
            "description": "This is the test1 project about solar PV plant",
        },
    ]
    return projects

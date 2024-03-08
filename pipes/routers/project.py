from __future__ import annotations

from fastapi import APIRouter

from toml import load
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


@router.get("/overview_dropdowns")
async def overview_dropdowns(project):
    """
    Returns all the information for the dropdown menus on the overview tab.
    """
    # To change how to ingest the data
    with open("pipes/data/templates/test_project.toml") as f:
        config = load(f)
    return {
        "assumptions": config["project"]["assumptions"],
        "requirements": config["project"]["requirements"],
        "scenarios": config["project"]["scenarios"],
        "milestones": config["project"]["milestones"]
    }

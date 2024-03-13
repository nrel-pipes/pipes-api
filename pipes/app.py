from __future__ import annotations

from contextlib import asynccontextmanager

from beanie import init_beanie
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from motor.motor_asyncio import AsyncIOMotorClient

# Settings
from pipes.config.settings import settings

# Health
from pipes.health.routes import router as health_router

# Projects
from pipes.projects.schemas import ProjectDocument
from pipes.projects.routes import router as projects_router

# Projectruns
from pipes.projectruns.schemas import ProjectRunDocument
from pipes.projectruns.routes import router as projectruns_router

# Models
from pipes.models.routes import router as models_router
from pipes.models.schemas import ModelDocument

# Modelruns
from pipes.modelruns.schemas import ModelRunDocument
from pipes.modelruns.routes import router as modelruns_router

# Datasets
from pipes.datasets.schemas import DatasetDocument
from pipes.datasets.routes import router as datasets_router

# Teams
from pipes.teams.routes import router as teams_router
from pipes.teams.schemas import TeamDocument

# Users
from pipes.users.schemas import UserDocument
from pipes.users.routes import router as users_router

__version__ = "0.0.1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI application life span"""
    # Init beanie
    if settings.PIPES_ENV == "testing":
        docdb_uri = "mongodb://"  # TODO: testing docdb uri
    elif settings.PIPES_ENV == "prod":
        docdb_uri = "mongodb://"  # TODO: prod docdb uri
    else:
        docdb_uri = f"mongodb://{settings.PIPES_DOCDB_HOST}:{settings.PIPES_DOCDB_PORT}/{settings.PIPES_DOCDB_NAME}"

    motor_client = AsyncIOMotorClient(docdb_uri)

    await init_beanie(
        database=motor_client[settings.PIPES_DOCDB_NAME],
        document_models=[
            ProjectDocument,
            ProjectRunDocument,
            ModelDocument,
            ModelRunDocument,
            DatasetDocument,
            TeamDocument,
            UserDocument,
        ],
    )

    yield


app = FastAPI(
    title=settings.TITLE,
    version=__version__,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# CORS settings - https://fastapi.tiangolo.com/tutorial/cors/
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=False,  # TODO: Update later
    allow_methods=settings.ALLOW_METHODS,
    allow_headers=settings.ALLOW_HEADERS,
)

# Routers
app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(projects_router, prefix="/api", tags=["projects"])
app.include_router(projectruns_router, prefix="/api", tags=["projectruns"])
app.include_router(models_router, prefix="/api", tags=["models"])
app.include_router(modelruns_router, prefix="/api", tags=["modelruns"])
app.include_router(datasets_router, prefix="/api", tags=["datasets"])
app.include_router(teams_router, prefix="/api", tags=["teams"])
app.include_router(users_router, prefix="/api", tags=["users"])


@app.get("/")
async def welcome():
    return RedirectResponse("/api/")

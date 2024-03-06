from __future__ import annotations

from contextlib import asynccontextmanager

from beanie import init_beanie
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from motor.motor_asyncio import AsyncIOMotorClient

from pipes.config.settings import settings
from pipes.datasets.routes import router as DatasetRouter
from pipes.health.routes import router as HealthRouter
from pipes.models.routes import router as ModelRouter
from pipes.projects import schemas as ProjectsSchemas
from pipes.projects.routes import router as ProjectsRouter
from pipes.teams import schemas as TeamsSchemas
from pipes.teams.routes import router as TeamsRouter
from pipes.users import schemas as UsersSchemas
from pipes.users.routes import router as UsersRouter

# NOTE: Simulate GRPC API returns during MVP, will be removed later
from pipes.projects.routes import grpcrouter as ProjectGrpcRouter

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
            TeamsSchemas.TeamDocument,
            UsersSchemas.UserDocument,
            ProjectsSchemas.ProjectDocument,
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

# NOTE: Remove in the future
app.include_router(ProjectGrpcRouter, prefix="/grpc", tags=["[grpc] projects"])

# Routers
app.include_router(HealthRouter, prefix="/api", tags=["health"])
app.include_router(ProjectsRouter, prefix="/api", tags=["projects"])
app.include_router(ModelRouter, prefix="/api", tags=["models"])
app.include_router(DatasetRouter, prefix="/api", tags=["datasets"])
app.include_router(TeamsRouter, prefix="/api", tags=["teams"])
app.include_router(UsersRouter, prefix="/api", tags=["users"])


@app.get("/")
async def welcome():
    return RedirectResponse("/api/")

from __future__ import annotations

import os
from pipes.config.settings import get_settings
from pipes.health.routes import router as health_router
from pipes.projects.routes import router as projects_router

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


settings = get_settings(os.environ.get("PIPES_ENV", "dev"))
app = FastAPI(
    title=settings.TITLE,
    debug=settings.DEBUG,
)

# CORS settings - https://fastapi.tiangolo.com/tutorial/cors/
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=False,  # TODO: Update later
    allow_methods=settings.ALLOW_METHODS,
    allow_headers=settings.ALLOW_HEADERS,
)

app.include_router(health_router, tags=["health"], prefix="/api")
app.include_router(projects_router, tags=["project"], prefix="/api")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=settings.DEBUG)

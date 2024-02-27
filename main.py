import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pipes.config.settings import settings
from pipes.healthcheck.routes import router as healthcheck
from pipes.projects.routes import router as projects

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

app.include_router(healthcheck, prefix="/api", tags=["healthcheck"])
app.include_router(projects, prefix="/api", tags=["projects"])


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=settings.DEBUG)

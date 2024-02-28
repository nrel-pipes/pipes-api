from __future__ import annotations

import uvicorn

from pipes.config.settings import settings


if __name__ == "__main__":
    uvicorn.run("pipes.app:app", host="0.0.0.0", port=8080, reload=settings.DEBUG)

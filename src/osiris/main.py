"""Entrypoint FastAPI de osiris-menu.

Ejecutar con: `uvicorn osiris.main:app --app-dir src` (D-a).
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import api_router
from .config import settings
from .shared import models as _shared_models  # noqa: F401  (registra tablas en Base.metadata)
from .shared.errors import register_exception_handlers
from .websocket.api import ws_router


def create_app() -> FastAPI:
    app = FastAPI(title="osiris-menu API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(api_router)
    app.include_router(ws_router)

    @app.get("/health", tags=["health"])
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "osiris-menu-api", "env": settings.APP_ENV}

    return app


app = create_app()

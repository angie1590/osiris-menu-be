"""Entrypoint de la aplicación FastAPI.

Expone ``app`` (importable como ``osiris.main:app``) con el endpoint de salud
``/health``, el router base versionado ``/api/v1`` (vacío por ahora) y los
manejadores que normalizan los errores al contrato base.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from osiris.config import Settings, get_settings
from osiris.shared.exceptions import OsirisError

# Mapa de códigos HTTP a códigos de error estables del contrato público.
_HTTP_ERROR_CODES: dict[int, str] = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "method_not_allowed",
    409: "conflict",
    422: "validation_error",
    500: "internal_error",
}


def _error_response(
    status_code: int,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    """Serializa un error al contrato `{ "error": { code, message, details? } }`."""
    error: dict[str, Any] = {"code": code, "message": message}
    if details is not None:
        error["details"] = details
    return JSONResponse(status_code=status_code, content={"error": error})


def create_app(settings: Settings | None = None) -> FastAPI:
    """Construye y configura la instancia FastAPI del backend."""
    settings = settings or get_settings()

    app = FastAPI(title="Osiris Menu API", version="0.1.0")

    @app.get("/health", tags=["health"], summary="Estado del servicio")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    # Router base de la API versionada. Los módulos de negocio montarán sus
    # routers bajo este prefijo (`/api/v1`); por ahora queda vacío.
    api_v1 = APIRouter(prefix=settings.api_prefix)
    app.include_router(api_v1)

    _register_exception_handlers(app)
    return app


def _register_exception_handlers(app: FastAPI) -> None:
    """Registra los manejadores que normalizan errores al contrato base."""

    @app.exception_handler(OsirisError)
    async def _handle_domain_error(_: Request, exc: OsirisError) -> JSONResponse:
        return _error_response(exc.status_code, exc.code, exc.message, exc.details)

    @app.exception_handler(StarletteHTTPException)
    async def _handle_http_error(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = _HTTP_ERROR_CODES.get(exc.status_code, "http_error")
        message = exc.detail if isinstance(exc.detail, str) else "Error HTTP"
        return _error_response(exc.status_code, code, message)

    @app.exception_handler(RequestValidationError)
    async def _handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        return _error_response(
            422,
            "validation_error",
            "Datos de entrada inválidos",
            {"errors": jsonable_encoder(exc.errors())},
        )


app = create_app()

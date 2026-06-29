"""Router raíz `/api/v1`: agrega los routers de los módulos MVP."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from .modules.cocina_barra.api import router as cocina_barra_router
from .modules.comandas.api import router as comandas_router
from .modules.mesas.api import router as mesas_router
from .shared.idempotency import idempotency_guard

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(mesas_router)
api_router.include_router(comandas_router)
api_router.include_router(cocina_barra_router)


@api_router.post("/_internal/echo", tags=["internal"])
async def internal_echo(request_id: str = Depends(idempotency_guard)) -> dict[str, str]:
    """Endpoint interno de prueba para ejercitar la idempotencia `X-Request-Id` (D-b).

    No es un mutador de negocio; existe para validar la política de rechazo 409 mientras
    los módulos aún no exponen mutadores reales.
    """
    return {"status": "ok", "request_id": request_id}

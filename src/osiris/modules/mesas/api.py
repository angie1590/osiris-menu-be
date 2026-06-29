"""§20 — Router FastAPI (placeholder). Sólo orquesta; sin reglas de negocio."""

from __future__ import annotations

from fastapi import APIRouter

from . import service
from .schemas import ModuleInfo

router = APIRouter(prefix="/mesas", tags=["mesas"])


@router.get("", response_model=ModuleInfo)
async def get_module_info() -> ModuleInfo:
    return service.module_info()

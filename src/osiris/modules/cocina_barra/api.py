"""§22 — Router FastAPI (placeholder). Vistas operativas cocina/barra por ruteo.

Las rutas reales (`/cocina/items`, `/barra/items`, agotar/restaurar producto) y las
transiciones de ítem llegan con la propuesta funcional de §22. Aquí sólo un placeholder.
"""

from __future__ import annotations

from fastapi import APIRouter

from . import service
from .schemas import ModuleInfo

router = APIRouter(prefix="/cocina-barra", tags=["cocina_barra"])


@router.get("", response_model=ModuleInfo)
async def get_module_info() -> ModuleInfo:
    return service.module_info()

"""§20 — Lógica de negocio. Placeholder.

Las reglas REG-20-xx (transiciones de mesa/zona, grupos, traslados) se implementan en
la propuesta funcional de §20, respaldadas por spec/decisión. No codificar aquí.
"""

from __future__ import annotations

from .schemas import ModuleInfo

SECCION = "§20 Mesas y zonas"


def module_info() -> ModuleInfo:
    return ModuleInfo(module="mesas", seccion=SECCION, status="scaffolding")

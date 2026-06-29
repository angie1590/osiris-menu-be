"""§21 — Lógica de negocio. Placeholder.

Reglas REG-21-xx (precio congelado N-04, matriz D-02, inventario híbrido D-01, combos
D-03, división D-09, traslados D-08, idempotencia) se implementan en la propuesta
funcional de §21. No codificar reglas aquí.
"""

from __future__ import annotations

from .schemas import ModuleInfo

SECCION = "§21 Comandas"


def module_info() -> ModuleInfo:
    return ModuleInfo(module="comandas", seccion=SECCION, status="scaffolding")

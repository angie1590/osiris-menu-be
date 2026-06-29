"""§22 — Lógica de negocio. Placeholder.

Reglas R-22-xx (vista operativa filtrada por ruteo, consumo confirmado D-01 al pasar a
En preparación, agotamiento N-11, semáforo de tiempos) se implementan en la propuesta
funcional de §22. No codificar reglas aquí.
"""

from __future__ import annotations

from .schemas import ModuleInfo

SECCION = "§22 Cocina y barra"


def module_info() -> ModuleInfo:
    return ModuleInfo(module="cocina_barra", seccion=SECCION, status="scaffolding")

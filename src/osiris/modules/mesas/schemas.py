"""§20 — Contratos públicos (Pydantic). Placeholder de scaffolding."""

from __future__ import annotations

from pydantic import BaseModel


class ModuleInfo(BaseModel):
    """Respuesta placeholder del router del módulo."""

    module: str
    seccion: str
    status: str

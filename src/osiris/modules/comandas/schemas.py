"""§21 — Contratos públicos (Pydantic). Placeholder de scaffolding."""

from __future__ import annotations

from pydantic import BaseModel


class ModuleInfo(BaseModel):
    module: str
    seccion: str
    status: str

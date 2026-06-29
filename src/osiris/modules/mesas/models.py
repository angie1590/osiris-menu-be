"""§20 — Enums de estado (terminología canónica del glosario).

Placeholder: aquí sólo viven los enums de estado. Los modelos SQLAlchemy de Zona,
Mesa y GrupoMesas, con su migración Alembic, llegan en la propuesta funcional de §20.
"""

from __future__ import annotations

from enum import StrEnum


class EstadoZona(StrEnum):
    ACTIVA = "Activa"
    EN_CIERRE = "En cierre"
    INACTIVA = "Inactiva"


class EstadoMesa(StrEnum):
    LIBRE = "Libre"
    RESERVADA = "Reservada"
    OCUPADA = "Ocupada"
    POR_LIMPIAR = "Por limpiar"
    INACTIVA = "Inactiva"

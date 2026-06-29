"""§20 — Contratos públicos (Pydantic). Valores técnicos de estado en el contrato."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .models import EstadoMesa, EstadoZona

# ---- Zona ----


class ZonaCreate(BaseModel):
    nombre: str = Field(min_length=1)
    descripcion: str | None = None
    aforo_max: int = 0
    orden_visualizacion: int = 0


class ZonaUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1)
    descripcion: str | None = None
    aforo_max: int | None = None
    orden_visualizacion: int | None = None


class ZonaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nombre: str
    descripcion: str | None
    estado: EstadoZona
    aforo_max: int
    orden_visualizacion: int
    created_at: datetime
    updated_at: datetime


class CerrarZonaRequest(BaseModel):
    motivo: str = Field(min_length=1)


# ---- Mesa ----


class MesaCreate(BaseModel):
    # `id` NO se acepta: lo genera el backend (D-mz-6).
    zona_id: uuid.UUID
    numero_visible: str = Field(min_length=1)
    capacidad: int = 0


class MesaUpdate(BaseModel):
    zona_id: uuid.UUID | None = None
    numero_visible: str | None = Field(default=None, min_length=1)
    capacidad: int | None = None


class MesaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    zona_id: uuid.UUID
    numero_visible: str
    capacidad: int
    estado: EstadoMesa
    comanda_activa_id: uuid.UUID | None
    reserva_activa_id: uuid.UUID | None
    grupo_id: uuid.UUID | None
    activa: bool
    created_at: datetime
    updated_at: datetime


# ---- Grupo ----


class GrupoMesasCreate(BaseModel):
    mesas_ids: list[uuid.UUID] = Field(min_length=2)


class GrupoMesasUpdate(BaseModel):
    agregar: list[uuid.UUID] = Field(default_factory=list)
    quitar: list[uuid.UUID] = Field(default_factory=list)


class GrupoMesasRead(BaseModel):
    id: uuid.UUID
    comanda_id: uuid.UUID | None
    mesas_ids: list[uuid.UUID]  # derivado de Mesa.grupo_id (D-mz-5)
    created_at: datetime
    dissolved_at: datetime | None


class QrRead(BaseModel):
    mesa_id: uuid.UUID
    url: str

"""§20 — Modelos SQLAlchemy y enums de estado.

Valores técnicos snake_case en API/DB; la UI mapea a las etiquetas canónicas del
glosario (D-mz-8). La pertenencia a un grupo vive en `Mesa.grupo_id` como única fuente
de verdad; `GrupoMesas` no persiste un arreglo de mesas (D-mz-5).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, Uuid, text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from ...db import Base


class EstadoZona(StrEnum):
    ACTIVA = "activa"
    EN_CIERRE = "en_cierre"
    INACTIVA = "inactiva"


class EstadoMesa(StrEnum):
    LIBRE = "libre"
    RESERVADA = "reservada"
    OCUPADA = "ocupada"
    POR_LIMPIAR = "por_limpiar"
    INACTIVA = "inactiva"


def _estado_zona_col() -> SAEnum:
    return SAEnum(
        EstadoZona, native_enum=False, length=20, values_callable=lambda e: [m.value for m in e]
    )


def _estado_mesa_col() -> SAEnum:
    return SAEnum(
        EstadoMesa, native_enum=False, length=20, values_callable=lambda e: [m.value for m in e]
    )


def _now() -> datetime:
    return datetime.now(UTC)


class Zona(Base):
    __tablename__ = "zonas"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    estado: Mapped[EstadoZona] = mapped_column(
        _estado_zona_col(), nullable=False, default=EstadoZona.ACTIVA
    )
    aforo_max: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    orden_visualizacion: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now
    )


class GrupoMesas(Base):
    __tablename__ = "grupos_mesas"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    # FK a comandas (§21) — sin ForeignKey dura todavía (D-mz-2).
    comanda_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    dissolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Mesa(Base):
    __tablename__ = "mesas"
    # Unicidad de numero_visible por zona, case-insensitive (REG-20-15, D-h1).
    __table_args__ = (
        Index(
            "uq_mesas_zona_numero_lower",
            "zona_id",
            text("lower(numero_visible)"),
            unique=True,
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    zona_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("zonas.id"), nullable=False)
    numero_visible: Mapped[str] = mapped_column(String(50), nullable=False)
    capacidad: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estado: Mapped[EstadoMesa] = mapped_column(
        _estado_mesa_col(), nullable=False, default=EstadoMesa.LIBRE
    )
    # FKs a comandas/reservas (§21/§28) — sin ForeignKey dura todavía (D-mz-2).
    comanda_activa_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    reserva_activa_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    grupo_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("grupos_mesas.id"), nullable=True)
    activa: Mapped[bool] = mapped_column(nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now
    )

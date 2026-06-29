"""Auditoría persistente mínima (D-mz-9, Principio 1).

Tabla `audit_logs` consultable (no solo `logging.info`). `registrar_audit` agrega la fila
a la sesión; el caller hace commit con el resto de la operación.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, DateTime, String, Text, Uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


async def registrar_audit(
    session: AsyncSession,
    *,
    event_type: str,
    entity_type: str,
    entity_id: uuid.UUID,
    user_id: uuid.UUID | None = None,
    reason: str | None = None,
    payload: dict[str, Any] | None = None,
) -> AuditLog:
    """Agrega un registro de auditoría a la sesión (sin commit)."""
    entry = AuditLog(
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        user_id=user_id,
        reason=reason,
        payload=payload or {},
    )
    session.add(entry)
    return entry

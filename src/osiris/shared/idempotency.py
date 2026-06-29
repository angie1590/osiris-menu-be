"""Dependencia de idempotencia por `X-Request-Id` (D-b).

Política inicial del scaffolding: un `X-Request-Id` ya procesado (dentro del TTL) se
**rechaza** con `409 IDEMPOTENCY_KEY_REUSED`. No se reconstruye ni devuelve la
respuesta original todavía.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from fastapi import Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..db import get_session
from .exceptions import IdempotencyKeyReused, InvalidRequestId, MissingRequestId
from .models import RequestIdProcesado


def _as_utc(value: datetime) -> datetime:
    """Normaliza a UTC aware (sqlite devuelve naive; postgres aware)."""
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)


async def idempotency_guard(
    request: Request,
    x_request_id: str | None = Header(default=None, alias="X-Request-Id"),
    session: AsyncSession = Depends(get_session),
) -> str:
    """Valida y registra el `X-Request-Id`. Úsese como dependencia en todo mutador."""
    if not x_request_id:
        raise MissingRequestId("Falta el header X-Request-Id")
    try:
        uuid.UUID(x_request_id, version=4)
    except ValueError as exc:
        raise InvalidRequestId("X-Request-Id no es un UUID v4 válido") from exc

    now = datetime.now(UTC)
    existing = await session.get(RequestIdProcesado, x_request_id)
    if existing is not None and _as_utc(existing.expires_at) > now:
        raise IdempotencyKeyReused(details={"request_id": x_request_id})
    if existing is not None:
        await session.delete(existing)
        await session.flush()

    session.add(
        RequestIdProcesado(
            request_id=x_request_id,
            endpoint=request.url.path,
            created_at=now,
            expires_at=now + timedelta(seconds=settings.IDEMPOTENCY_TTL_SECONDS),
        )
    )
    await session.commit()
    return x_request_id

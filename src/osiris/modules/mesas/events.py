"""§20 — Eventos WebSocket del canal lógico `mesas` (ruta física `/ws/mesas`).

Payloads tipados (dict json-serializable) emitidos por el `ConnectionManager` compartido,
testeable. `usuario_id` es opcional hasta auth real (D-mz-7/D-mz-10).
"""

from __future__ import annotations

import uuid
from collections.abc import Iterable
from datetime import UTC, datetime

from ...websocket.manager import manager
from .models import EstadoMesa, EstadoZona

CHANNEL = "mesas"

MESA_ESTADO_CAMBIADO = "mesa.estado_cambiado"
ZONA_ESTADO_CAMBIADO = "zona.estado_cambiado"
GRUPO_CREADO = "grupo.creado"
GRUPO_ACTUALIZADO = "grupo.actualizado"
GRUPO_DISUELTO = "grupo.disuelto"


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _opt_str(value: uuid.UUID | None) -> str | None:
    return str(value) if value is not None else None


async def emit_mesa_estado_cambiado(
    *,
    mesa_id: uuid.UUID,
    estado_anterior: EstadoMesa | None,
    estado_nuevo: EstadoMesa,
    comanda_id: uuid.UUID | None = None,
    usuario_id: uuid.UUID | None = None,
) -> None:
    await manager.broadcast(
        CHANNEL,
        {
            "type": MESA_ESTADO_CAMBIADO,
            "mesa_id": str(mesa_id),
            "estado_anterior": estado_anterior.value if estado_anterior else None,
            "estado_nuevo": estado_nuevo.value,
            "comanda_id": _opt_str(comanda_id),
            "usuario_id": _opt_str(usuario_id),
            "timestamp": _now_iso(),
        },
    )


async def emit_zona_estado_cambiado(
    *,
    zona_id: uuid.UUID,
    estado_anterior: EstadoZona | None,
    estado_nuevo: EstadoZona,
    usuario_id: uuid.UUID | None = None,
) -> None:
    await manager.broadcast(
        CHANNEL,
        {
            "type": ZONA_ESTADO_CAMBIADO,
            "zona_id": str(zona_id),
            "estado_anterior": estado_anterior.value if estado_anterior else None,
            "estado_nuevo": estado_nuevo.value,
            "usuario_id": _opt_str(usuario_id),
            "timestamp": _now_iso(),
        },
    )


async def _emit_grupo(
    event_type: str,
    *,
    grupo_id: uuid.UUID,
    mesas_ids: Iterable[uuid.UUID],
    comanda_id: uuid.UUID | None = None,
    usuario_id: uuid.UUID | None = None,
) -> None:
    await manager.broadcast(
        CHANNEL,
        {
            "type": event_type,
            "grupo_id": str(grupo_id),
            "mesas_ids": [str(m) for m in mesas_ids],
            "comanda_id": _opt_str(comanda_id),
            "usuario_id": _opt_str(usuario_id),
            "timestamp": _now_iso(),
        },
    )


async def emit_grupo_creado(**kwargs: object) -> None:
    await _emit_grupo(GRUPO_CREADO, **kwargs)  # type: ignore[arg-type]


async def emit_grupo_actualizado(**kwargs: object) -> None:
    await _emit_grupo(GRUPO_ACTUALIZADO, **kwargs)  # type: ignore[arg-type]


async def emit_grupo_disuelto(**kwargs: object) -> None:
    await _emit_grupo(GRUPO_DISUELTO, **kwargs)  # type: ignore[arg-type]

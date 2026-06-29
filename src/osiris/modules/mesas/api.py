"""§20 — Routers FastAPI. Orquestan request/response; la lógica vive en `service.py`.

Mutadores: `X-Request-Id` (idempotencia) + operador actual (placeholder). El cierre de zona
exige Nivel 2 (placeholder de auth). Errores con el envelope estructurado del proyecto.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...auth.levels import NivelAutorizacion, require_nivel
from ...auth.operator import current_operator
from ...db import get_session
from ...shared.idempotency import idempotency_guard
from . import schemas, service
from .models import EstadoMesa

zonas_router = APIRouter(prefix="/zonas", tags=["zonas"])
mesas_router = APIRouter(prefix="/mesas", tags=["mesas"])
grupos_router = APIRouter(prefix="/grupos", tags=["grupos"])

# Dependencia de nivel como singleton de módulo (placeholder de auth, D-mz-4).
nivel_2_required = require_nivel(NivelAutorizacion.NIVEL_2)


# ---- Zonas ----


@zonas_router.get("", response_model=list[schemas.ZonaRead])
async def listar_zonas(session: AsyncSession = Depends(get_session)) -> list[schemas.ZonaRead]:
    zonas = await service.listar_zonas(session)
    return [schemas.ZonaRead.model_validate(z) for z in zonas]


@zonas_router.post("", response_model=schemas.ZonaRead, status_code=201)
async def crear_zona(
    data: schemas.ZonaCreate,
    session: AsyncSession = Depends(get_session),
    _request_id: str = Depends(idempotency_guard),
) -> schemas.ZonaRead:
    zona = await service.crear_zona(session, data)
    return schemas.ZonaRead.model_validate(zona)


@zonas_router.patch("/{zona_id}", response_model=schemas.ZonaRead)
async def actualizar_zona(
    zona_id: uuid.UUID,
    data: schemas.ZonaUpdate,
    session: AsyncSession = Depends(get_session),
    _request_id: str = Depends(idempotency_guard),
) -> schemas.ZonaRead:
    zona = await service.actualizar_zona(session, zona_id, data)
    return schemas.ZonaRead.model_validate(zona)


@zonas_router.post("/{zona_id}/cerrar", response_model=schemas.ZonaRead)
async def cerrar_zona(
    zona_id: uuid.UUID,
    data: schemas.CerrarZonaRequest,
    session: AsyncSession = Depends(get_session),
    _request_id: str = Depends(idempotency_guard),
    usuario_id: uuid.UUID | None = Depends(current_operator),
    _nivel: NivelAutorizacion = Depends(nivel_2_required),
) -> schemas.ZonaRead:
    zona = await service.cerrar_zona(session, zona_id, data.motivo, usuario_id=usuario_id)
    return schemas.ZonaRead.model_validate(zona)


@zonas_router.post("/{zona_id}/activar", response_model=schemas.ZonaRead)
async def activar_zona(
    zona_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _request_id: str = Depends(idempotency_guard),
    usuario_id: uuid.UUID | None = Depends(current_operator),
) -> schemas.ZonaRead:
    zona = await service.activar_zona(session, zona_id, usuario_id=usuario_id)
    return schemas.ZonaRead.model_validate(zona)


@zonas_router.post("/{zona_id}/desactivar", response_model=schemas.ZonaRead)
async def desactivar_zona(
    zona_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _request_id: str = Depends(idempotency_guard),
    usuario_id: uuid.UUID | None = Depends(current_operator),
) -> schemas.ZonaRead:
    zona = await service.desactivar_zona(session, zona_id, usuario_id=usuario_id)
    return schemas.ZonaRead.model_validate(zona)


# ---- Mesas ----


@mesas_router.get("", response_model=list[schemas.MesaRead])
async def listar_mesas(
    session: AsyncSession = Depends(get_session),
    zona_id: uuid.UUID | None = Query(default=None),
    estado: EstadoMesa | None = Query(default=None),
) -> list[schemas.MesaRead]:
    mesas = await service.listar_mesas(session, zona_id=zona_id, estado=estado)
    return [schemas.MesaRead.model_validate(m) for m in mesas]


@mesas_router.post("", response_model=schemas.MesaRead, status_code=201)
async def crear_mesa(
    data: schemas.MesaCreate,
    session: AsyncSession = Depends(get_session),
    _request_id: str = Depends(idempotency_guard),
) -> schemas.MesaRead:
    mesa = await service.crear_mesa(session, data)
    return schemas.MesaRead.model_validate(mesa)


@mesas_router.get("/{mesa_id}", response_model=schemas.MesaRead)
async def obtener_mesa(
    mesa_id: uuid.UUID, session: AsyncSession = Depends(get_session)
) -> schemas.MesaRead:
    mesa = await service.obtener_mesa(session, mesa_id)
    return schemas.MesaRead.model_validate(mesa)


@mesas_router.patch("/{mesa_id}", response_model=schemas.MesaRead)
async def actualizar_mesa(
    mesa_id: uuid.UUID,
    data: schemas.MesaUpdate,
    session: AsyncSession = Depends(get_session),
    _request_id: str = Depends(idempotency_guard),
) -> schemas.MesaRead:
    mesa = await service.actualizar_mesa(session, mesa_id, data)
    return schemas.MesaRead.model_validate(mesa)


@mesas_router.delete("/{mesa_id}", response_model=schemas.MesaRead)
async def baja_mesa(
    mesa_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _request_id: str = Depends(idempotency_guard),
    usuario_id: uuid.UUID | None = Depends(current_operator),
) -> schemas.MesaRead:
    mesa = await service.baja_mesa(session, mesa_id, usuario_id=usuario_id)
    return schemas.MesaRead.model_validate(mesa)


@mesas_router.post("/{mesa_id}/marcar-libre", response_model=schemas.MesaRead)
async def marcar_libre(
    mesa_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _request_id: str = Depends(idempotency_guard),
    usuario_id: uuid.UUID | None = Depends(current_operator),
) -> schemas.MesaRead:
    mesa = await service.marcar_libre(session, mesa_id, usuario_id=usuario_id)
    return schemas.MesaRead.model_validate(mesa)


@mesas_router.post("/{mesa_id}/qr", response_model=schemas.QrRead)
async def generar_qr(
    mesa_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _request_id: str = Depends(idempotency_guard),
    usuario_id: uuid.UUID | None = Depends(current_operator),
) -> schemas.QrRead:
    return await service.generar_qr(session, mesa_id, usuario_id=usuario_id)


# ---- Grupos ----


@grupos_router.post("", response_model=schemas.GrupoMesasRead, status_code=201)
async def crear_grupo(
    data: schemas.GrupoMesasCreate,
    session: AsyncSession = Depends(get_session),
    _request_id: str = Depends(idempotency_guard),
    usuario_id: uuid.UUID | None = Depends(current_operator),
) -> schemas.GrupoMesasRead:
    grupo = await service.crear_grupo(session, data, usuario_id=usuario_id)
    return await service.leer_grupo(session, grupo.id)


@grupos_router.patch("/{grupo_id}", response_model=schemas.GrupoMesasRead)
async def modificar_grupo(
    grupo_id: uuid.UUID,
    data: schemas.GrupoMesasUpdate,
    session: AsyncSession = Depends(get_session),
    _request_id: str = Depends(idempotency_guard),
    usuario_id: uuid.UUID | None = Depends(current_operator),
) -> schemas.GrupoMesasRead:
    grupo = await service.modificar_grupo(session, grupo_id, data, usuario_id=usuario_id)
    return await service.leer_grupo(session, grupo.id)


@grupos_router.post("/{grupo_id}/disolver", response_model=schemas.GrupoMesasRead)
async def disolver_grupo(
    grupo_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _request_id: str = Depends(idempotency_guard),
    usuario_id: uuid.UUID | None = Depends(current_operator),
) -> schemas.GrupoMesasRead:
    grupo = await service.disolver_grupo(session, grupo_id, usuario_id=usuario_id)
    return await service.leer_grupo(session, grupo.id)


# Router agregado que monta zonas, mesas y grupos bajo /api/v1 (vía osiris.api).
router = APIRouter()
router.include_router(zonas_router)
router.include_router(mesas_router)
router.include_router(grupos_router)

"""§20 — Lógica de negocio (reglas REG-20-XX).

Toda transición de estado de mesa pasa por `transicionar_mesa` (máquina de estados central,
D-mz-1). Cada mutación material registra audit log (D-mz-9) y emite evento WS (D-mz-7).
La integración real con §21/§28 queda como contrato (columnas + seams), sin implementarse.
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...shared.audit import registrar_audit
from ...shared.exceptions import DomainError
from . import events, schemas
from .models import EstadoMesa, EstadoZona, GrupoMesas, Mesa, Zona

# ---- errores de dominio ----


def _not_found(entidad: str) -> DomainError:
    return DomainError(f"{entidad} no encontrada", code="NO_ENCONTRADO", status_code=404)


def _conflict(message: str, code: str) -> DomainError:
    return DomainError(message, code=code, status_code=409)


def _invalid(message: str, code: str) -> DomainError:
    return DomainError(message, code=code, status_code=400)


# ---- carga ----


async def _load_zona(session: AsyncSession, zona_id: uuid.UUID) -> Zona:
    zona = await session.get(Zona, zona_id)
    if zona is None:
        raise _not_found("Zona")
    return zona


async def _load_mesa(session: AsyncSession, mesa_id: uuid.UUID) -> Mesa:
    mesa = await session.get(Mesa, mesa_id)
    if mesa is None:
        raise _not_found("Mesa")
    return mesa


async def _load_grupo(session: AsyncSession, grupo_id: uuid.UUID) -> GrupoMesas:
    grupo = await session.get(GrupoMesas, grupo_id)
    if grupo is None:
        raise _not_found("Grupo")
    return grupo


async def _mesas_de_grupo(session: AsyncSession, grupo_id: uuid.UUID) -> list[Mesa]:
    result = await session.execute(select(Mesa).where(Mesa.grupo_id == grupo_id))
    return list(result.scalars().all())


async def _mesas_de_zona(session: AsyncSession, zona_id: uuid.UUID) -> list[Mesa]:
    result = await session.execute(
        select(Mesa).where(Mesa.zona_id == zona_id, Mesa.activa.is_(True))
    )
    return list(result.scalars().all())


# ---- máquina de estados de mesa (D-mz-1) ----


async def transicionar_mesa(
    session: AsyncSession,
    mesa: Mesa,
    nuevo: EstadoMesa,
    *,
    usuario_id: uuid.UUID | None = None,
    reason: str | None = None,
    comanda_id: uuid.UUID | None = None,
) -> Mesa:
    anterior = mesa.estado

    if nuevo == EstadoMesa.OCUPADA:
        if anterior not in (EstadoMesa.LIBRE, EstadoMesa.RESERVADA):  # REG-20-01
            raise _invalid("Solo se puede ocupar desde Libre o Reservada", "TRANSICION_INVALIDA")
        if mesa.comanda_activa_id is not None:  # REG-20-02
            raise _conflict("La mesa ya tiene una comanda activa", "MESA_CON_COMANDA")

    if nuevo in (EstadoMesa.OCUPADA, EstadoMesa.RESERVADA):
        zona = await _load_zona(session, mesa.zona_id)
        if zona.estado == EstadoZona.INACTIVA:  # REG-20-07
            raise _invalid("La zona está Inactiva", "ZONA_INACTIVA")
        if zona.estado == EstadoZona.EN_CIERRE:  # REG-20-09
            raise _invalid("La zona está En cierre", "ZONA_EN_CIERRE")

    mesa.estado = nuevo
    await registrar_audit(
        session,
        event_type=events.MESA_ESTADO_CAMBIADO,
        entity_type="mesa",
        entity_id=mesa.id,
        user_id=usuario_id,
        reason=reason,
        payload={"estado_anterior": anterior.value, "estado_nuevo": nuevo.value},
    )
    await events.emit_mesa_estado_cambiado(
        mesa_id=mesa.id,
        estado_anterior=anterior,
        estado_nuevo=nuevo,
        comanda_id=comanda_id,
        usuario_id=usuario_id,
    )
    return mesa


# ---- Zonas ----


async def crear_zona(session: AsyncSession, data: schemas.ZonaCreate) -> Zona:
    zona = Zona(**data.model_dump())
    session.add(zona)
    await session.commit()
    await session.refresh(zona)
    return zona


async def listar_zonas(session: AsyncSession) -> Sequence[Zona]:
    result = await session.execute(select(Zona).order_by(Zona.orden_visualizacion))
    return result.scalars().all()


async def actualizar_zona(
    session: AsyncSession, zona_id: uuid.UUID, data: schemas.ZonaUpdate
) -> Zona:
    zona = await _load_zona(session, zona_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(zona, field, value)
    await session.commit()
    await session.refresh(zona)
    return zona


async def _cambiar_estado_zona(
    session: AsyncSession,
    zona: Zona,
    nuevo: EstadoZona,
    *,
    usuario_id: uuid.UUID | None,
    reason: str | None = None,
) -> None:
    anterior = zona.estado
    zona.estado = nuevo
    await registrar_audit(
        session,
        event_type=events.ZONA_ESTADO_CAMBIADO,
        entity_type="zona",
        entity_id=zona.id,
        user_id=usuario_id,
        reason=reason,
        payload={"estado_anterior": anterior.value, "estado_nuevo": nuevo.value},
    )
    await events.emit_zona_estado_cambiado(
        zona_id=zona.id, estado_anterior=anterior, estado_nuevo=nuevo, usuario_id=usuario_id
    )


async def cerrar_zona(  # REG-20-08
    session: AsyncSession, zona_id: uuid.UUID, motivo: str, *, usuario_id: uuid.UUID | None
) -> Zona:
    zona = await _load_zona(session, zona_id)
    if zona.estado != EstadoZona.ACTIVA:
        raise _invalid("Solo una zona Activa puede pasar a En cierre", "TRANSICION_INVALIDA")
    await _cambiar_estado_zona(
        session, zona, EstadoZona.EN_CIERRE, usuario_id=usuario_id, reason=motivo
    )
    await session.commit()
    await session.refresh(zona)
    return zona


async def activar_zona(
    session: AsyncSession, zona_id: uuid.UUID, *, usuario_id: uuid.UUID | None
) -> Zona:
    zona = await _load_zona(session, zona_id)
    await _cambiar_estado_zona(session, zona, EstadoZona.ACTIVA, usuario_id=usuario_id)
    for mesa in await _mesas_de_zona(session, zona.id):
        if mesa.estado == EstadoMesa.INACTIVA:
            await transicionar_mesa(session, mesa, EstadoMesa.LIBRE, usuario_id=usuario_id)
    await session.commit()
    await session.refresh(zona)
    return zona


async def desactivar_zona(  # REG-20-07 + D-mz-11
    session: AsyncSession, zona_id: uuid.UUID, *, usuario_id: uuid.UUID | None
) -> Zona:
    zona = await _load_zona(session, zona_id)
    mesas = await _mesas_de_zona(session, zona.id)
    if any(m.estado in (EstadoMesa.OCUPADA, EstadoMesa.RESERVADA) for m in mesas):
        raise _conflict("La zona tiene mesas Ocupadas o Reservadas", "ZONA_NO_VACIA")
    await _cambiar_estado_zona(session, zona, EstadoZona.INACTIVA, usuario_id=usuario_id)
    for mesa in mesas:
        if mesa.estado in (EstadoMesa.LIBRE, EstadoMesa.POR_LIMPIAR):
            await transicionar_mesa(session, mesa, EstadoMesa.INACTIVA, usuario_id=usuario_id)
    await session.commit()
    await session.refresh(zona)
    return zona


# ---- Mesas ----


async def crear_mesa(session: AsyncSession, data: schemas.MesaCreate) -> Mesa:
    await _load_zona(session, data.zona_id)  # 404 si la zona no existe
    mesa = Mesa(**data.model_dump())  # id lo genera el backend (D-mz-6)
    session.add(mesa)
    await session.commit()
    await session.refresh(mesa)
    return mesa


async def listar_mesas(
    session: AsyncSession,
    *,
    zona_id: uuid.UUID | None = None,
    estado: EstadoMesa | None = None,
) -> Sequence[Mesa]:
    stmt = select(Mesa)
    if zona_id is not None:
        stmt = stmt.where(Mesa.zona_id == zona_id)
    if estado is not None:
        stmt = stmt.where(Mesa.estado == estado)
    result = await session.execute(stmt)
    return result.scalars().all()


async def obtener_mesa(session: AsyncSession, mesa_id: uuid.UUID) -> Mesa:
    return await _load_mesa(session, mesa_id)


async def actualizar_mesa(
    session: AsyncSession, mesa_id: uuid.UUID, data: schemas.MesaUpdate
) -> Mesa:
    mesa = await _load_mesa(session, mesa_id)
    payload = data.model_dump(exclude_unset=True)
    if "zona_id" in payload:
        await _load_zona(session, payload["zona_id"])
    for field, value in payload.items():
        setattr(mesa, field, value)
    await session.commit()
    await session.refresh(mesa)
    return mesa


async def baja_mesa(  # REG-20-12 (baja lógica, id permanente)
    session: AsyncSession, mesa_id: uuid.UUID, *, usuario_id: uuid.UUID | None
) -> Mesa:
    mesa = await _load_mesa(session, mesa_id)
    mesa.activa = False
    await registrar_audit(
        session,
        event_type="mesa.baja_logica",
        entity_type="mesa",
        entity_id=mesa.id,
        user_id=usuario_id,
        payload={"numero_visible": mesa.numero_visible},
    )
    await session.commit()
    await session.refresh(mesa)
    return mesa


async def marcar_libre(  # REG-20-14
    session: AsyncSession, mesa_id: uuid.UUID, *, usuario_id: uuid.UUID | None
) -> Mesa:
    mesa = await _load_mesa(session, mesa_id)
    if mesa.estado != EstadoMesa.POR_LIMPIAR:
        raise _invalid("La mesa no está en Por limpiar", "MESA_NO_POR_LIMPIAR")
    await transicionar_mesa(session, mesa, EstadoMesa.LIBRE, usuario_id=usuario_id)
    await session.commit()
    await session.refresh(mesa)
    return mesa


async def reservar_mesa(  # seam §28 (operación de servicio testeable)
    session: AsyncSession, mesa_id: uuid.UUID, *, usuario_id: uuid.UUID | None = None
) -> Mesa:
    mesa = await _load_mesa(session, mesa_id)
    await transicionar_mesa(session, mesa, EstadoMesa.RESERVADA, usuario_id=usuario_id)
    await session.commit()
    await session.refresh(mesa)
    return mesa


async def ocupar_mesa(  # seam §21 (operación de servicio testeable)
    session: AsyncSession,
    mesa_id: uuid.UUID,
    *,
    comanda_id: uuid.UUID | None = None,
    usuario_id: uuid.UUID | None = None,
) -> Mesa:
    mesa = await _load_mesa(session, mesa_id)
    await transicionar_mesa(
        session, mesa, EstadoMesa.OCUPADA, usuario_id=usuario_id, comanda_id=comanda_id
    )
    await session.commit()
    await session.refresh(mesa)
    return mesa


async def generar_qr(  # D-mz-6
    session: AsyncSession, mesa_id: uuid.UUID, *, usuario_id: uuid.UUID | None
) -> schemas.QrRead:
    mesa = await _load_mesa(session, mesa_id)
    url = f"/qr/{mesa.id}"
    await registrar_audit(
        session,
        event_type="mesa.qr_generado",
        entity_type="mesa",
        entity_id=mesa.id,
        user_id=usuario_id,
        payload={"url": url},
    )
    await session.commit()
    return schemas.QrRead(mesa_id=mesa.id, url=url)


# ---- Grupos (unir / modificar / separar) ----


async def _validar_mesa_agrupable(mesa: Mesa) -> None:
    if not mesa.activa or mesa.estado == EstadoMesa.INACTIVA:
        raise _invalid("No se puede agrupar una mesa Inactiva", "MESA_INACTIVA")
    if mesa.estado != EstadoMesa.LIBRE:  # D-mz-5: solo desde Libre
        raise _invalid("Solo se pueden agrupar mesas Libres", "MESA_NO_AGRUPABLE")
    if mesa.grupo_id is not None:  # REG-20-03
        raise _conflict("La mesa ya pertenece a un grupo activo", "MESA_YA_AGRUPADA")


async def crear_grupo(
    session: AsyncSession, data: schemas.GrupoMesasCreate, *, usuario_id: uuid.UUID | None
) -> GrupoMesas:
    mesas_ids = list(dict.fromkeys(data.mesas_ids))  # dedup preservando orden
    if len(mesas_ids) < 2:
        raise _invalid("Un grupo requiere 2 o más mesas", "GRUPO_INVALIDO")

    mesas = [await _load_mesa(session, mid) for mid in mesas_ids]
    for mesa in mesas:
        await _validar_mesa_agrupable(mesa)

    grupo = GrupoMesas()
    session.add(grupo)
    await session.flush()  # asigna grupo.id
    for mesa in mesas:
        mesa.grupo_id = grupo.id

    await registrar_audit(
        session,
        event_type=events.GRUPO_CREADO,
        entity_type="grupo",
        entity_id=grupo.id,
        user_id=usuario_id,
        payload={"mesas_ids": [str(m) for m in mesas_ids]},
    )
    await events.emit_grupo_creado(
        grupo_id=grupo.id, mesas_ids=[m.id for m in mesas], usuario_id=usuario_id
    )
    await session.commit()
    await session.refresh(grupo)
    return grupo


async def modificar_grupo(
    session: AsyncSession,
    grupo_id: uuid.UUID,
    data: schemas.GrupoMesasUpdate,
    *,
    usuario_id: uuid.UUID | None,
) -> GrupoMesas:
    grupo = await _load_grupo(session, grupo_id)
    if grupo.dissolved_at is not None:
        raise _conflict("El grupo ya está disuelto", "GRUPO_YA_DISUELTO")

    for mid in data.agregar:
        mesa = await _load_mesa(session, mid)
        await _validar_mesa_agrupable(mesa)
        mesa.grupo_id = grupo.id

    for mid in data.quitar:
        mesa = await _load_mesa(session, mid)
        if mesa.grupo_id == grupo.id:
            mesa.grupo_id = None

    restantes = await _mesas_de_grupo(session, grupo.id)
    if len(restantes) < 2:
        raise _invalid(
            "Un grupo no puede quedar con menos de 2 mesas; disuélvalo en su lugar",
            "GRUPO_INVALIDO",
        )

    await registrar_audit(
        session,
        event_type=events.GRUPO_ACTUALIZADO,
        entity_type="grupo",
        entity_id=grupo.id,
        user_id=usuario_id,
        payload={"mesas_ids": [str(m.id) for m in restantes]},
    )
    await events.emit_grupo_actualizado(
        grupo_id=grupo.id, mesas_ids=[m.id for m in restantes], usuario_id=usuario_id
    )
    await session.commit()
    await session.refresh(grupo)
    return grupo


async def disolver_grupo(
    session: AsyncSession, grupo_id: uuid.UUID, *, usuario_id: uuid.UUID | None
) -> GrupoMesas:
    grupo = await _load_grupo(session, grupo_id)
    if grupo.dissolved_at is not None:
        raise _conflict("El grupo ya está disuelto", "GRUPO_YA_DISUELTO")

    mesas = await _mesas_de_grupo(session, grupo.id)
    mesas_ids = [m.id for m in mesas]
    for mesa in mesas:
        mesa.grupo_id = None
    grupo.dissolved_at = datetime.now(UTC)

    await registrar_audit(
        session,
        event_type=events.GRUPO_DISUELTO,
        entity_type="grupo",
        entity_id=grupo.id,
        user_id=usuario_id,
        payload={"mesas_ids": [str(m) for m in mesas_ids]},
    )
    await events.emit_grupo_disuelto(grupo_id=grupo.id, mesas_ids=mesas_ids, usuario_id=usuario_id)
    await session.commit()
    await session.refresh(grupo)
    return grupo


async def leer_grupo(session: AsyncSession, grupo_id: uuid.UUID) -> schemas.GrupoMesasRead:
    grupo = await _load_grupo(session, grupo_id)
    mesas = await _mesas_de_grupo(session, grupo.id)
    return schemas.GrupoMesasRead(
        id=grupo.id,
        comanda_id=grupo.comanda_id,
        mesas_ids=[m.id for m in mesas],  # derivado (D-mz-5)
        created_at=grupo.created_at,
        dissolved_at=grupo.dissolved_at,
    )

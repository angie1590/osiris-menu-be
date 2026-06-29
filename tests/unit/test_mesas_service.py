"""Service §20 — reglas REG-20-XX, grupos, auditoría y eventos."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from osiris.modules.mesas import schemas, service
from osiris.modules.mesas.models import EstadoMesa, EstadoZona, Mesa, Zona
from osiris.shared.audit import AuditLog
from osiris.shared.exceptions import DomainError


async def _zona(session: AsyncSession, estado: EstadoZona = EstadoZona.ACTIVA) -> Zona:
    zona = Zona(nombre="Zona", aforo_max=10, orden_visualizacion=0, estado=estado)
    session.add(zona)
    await session.commit()
    await session.refresh(zona)
    return zona


async def _mesa(
    session: AsyncSession, zona: Zona, estado: EstadoMesa = EstadoMesa.LIBRE, numero: str = "M1"
) -> Mesa:
    mesa = Mesa(zona_id=zona.id, numero_visible=numero, capacidad=4, estado=estado)
    session.add(mesa)
    await session.commit()
    await session.refresh(mesa)
    return mesa


async def _audit_count(session: AsyncSession, event_type: str) -> int:
    result = await session.execute(
        select(func.count()).select_from(AuditLog).where(AuditLog.event_type == event_type)
    )
    return int(result.scalar_one())


async def test_crear_mesa_inicia_libre(session: AsyncSession) -> None:
    zona = await service.crear_zona(session, schemas.ZonaCreate(nombre="Barra"))
    mesa = await service.crear_mesa(
        session, schemas.MesaCreate(zona_id=zona.id, numero_visible="B1", capacidad=2)
    )
    assert mesa.estado == EstadoMesa.LIBRE


async def test_reg_20_01_ocupar_solo_desde_libre_o_reservada(session: AsyncSession) -> None:
    zona = await _zona(session)
    libre = await _mesa(session, zona, EstadoMesa.LIBRE, "M1")
    await service.ocupar_mesa(session, libre.id)
    assert (await service.obtener_mesa(session, libre.id)).estado == EstadoMesa.OCUPADA

    por_limpiar = await _mesa(session, zona, EstadoMesa.POR_LIMPIAR, "M2")
    with pytest.raises(DomainError) as exc:
        await service.ocupar_mesa(session, por_limpiar.id)
    assert exc.value.code == "TRANSICION_INVALIDA"


async def test_reg_20_02_una_comanda_activa(session: AsyncSession) -> None:
    zona = await _zona(session)
    mesa = await _mesa(session, zona)
    mesa.comanda_activa_id = uuid.uuid4()
    await session.commit()
    with pytest.raises(DomainError) as exc:
        await service.ocupar_mesa(session, mesa.id)
    assert exc.value.code == "MESA_CON_COMANDA"


async def test_reg_20_07_zona_inactiva_no_ocupa_ni_reserva(session: AsyncSession) -> None:
    zona = await _zona(session, EstadoZona.INACTIVA)
    mesa = await _mesa(session, zona)
    with pytest.raises(DomainError) as exc:
        await service.ocupar_mesa(session, mesa.id)
    assert exc.value.code == "ZONA_INACTIVA"
    with pytest.raises(DomainError):
        await service.reservar_mesa(session, mesa.id)


async def test_reservada_en_zona_en_cierre_se_rechaza(session: AsyncSession) -> None:
    zona = await _zona(session, EstadoZona.EN_CIERRE)
    mesa = await _mesa(session, zona)
    with pytest.raises(DomainError) as exc:
        await service.reservar_mesa(session, mesa.id)
    assert exc.value.code == "ZONA_EN_CIERRE"


async def test_desactivar_zona(session: AsyncSession) -> None:
    zona = await _zona(session)
    libre = await _mesa(session, zona, EstadoMesa.LIBRE, "M1")
    por_limpiar = await _mesa(session, zona, EstadoMesa.POR_LIMPIAR, "M2")

    await service.desactivar_zona(session, zona.id, usuario_id=None)
    assert (await service.obtener_mesa(session, libre.id)).estado == EstadoMesa.INACTIVA
    assert (await service.obtener_mesa(session, por_limpiar.id)).estado == EstadoMesa.INACTIVA


async def test_desactivar_zona_con_reservada_se_rechaza(session: AsyncSession) -> None:
    zona = await _zona(session)
    await _mesa(session, zona, EstadoMesa.RESERVADA)
    with pytest.raises(DomainError) as exc:
        await service.desactivar_zona(session, zona.id, usuario_id=None)
    assert exc.value.code == "ZONA_NO_VACIA"


async def test_marcar_libre(session: AsyncSession) -> None:
    zona = await _zona(session)
    mesa = await _mesa(session, zona, EstadoMesa.POR_LIMPIAR)
    await service.marcar_libre(session, mesa.id, usuario_id=None)
    assert (await service.obtener_mesa(session, mesa.id)).estado == EstadoMesa.LIBRE

    otra = await _mesa(session, zona, EstadoMesa.LIBRE, "M9")
    with pytest.raises(DomainError) as exc:
        await service.marcar_libre(session, otra.id, usuario_id=None)
    assert exc.value.code == "MESA_NO_POR_LIMPIAR"


async def test_baja_logica_conserva_id(session: AsyncSession) -> None:
    zona = await _zona(session)
    mesa = await _mesa(session, zona)
    original = mesa.id
    bajada = await service.baja_mesa(session, mesa.id, usuario_id=None)
    assert bajada.activa is False
    assert bajada.id == original  # id permanente, no se borra


async def test_crear_grupo_y_reglas(session: AsyncSession) -> None:
    zona = await _zona(session)
    m1 = await _mesa(session, zona, numero="M1")
    m2 = await _mesa(session, zona, numero="M2")
    grupo = await service.crear_grupo(
        session, schemas.GrupoMesasCreate(mesas_ids=[m1.id, m2.id]), usuario_id=None
    )
    assert (await service.obtener_mesa(session, m1.id)).grupo_id == grupo.id
    assert (await service.obtener_mesa(session, m2.id)).grupo_id == grupo.id

    # mesa ya agrupada → rechazo (REG-20-03)
    m3 = await _mesa(session, zona, numero="M3")
    with pytest.raises(DomainError) as exc:
        await service.crear_grupo(
            session, schemas.GrupoMesasCreate(mesas_ids=[m1.id, m3.id]), usuario_id=None
        )
    assert exc.value.code == "MESA_YA_AGRUPADA"


async def test_crear_grupo_con_mesa_inactiva_se_rechaza(session: AsyncSession) -> None:
    zona = await _zona(session)
    m1 = await _mesa(session, zona, numero="M1")
    m2 = await _mesa(session, zona, EstadoMesa.INACTIVA, "M2")
    with pytest.raises(DomainError) as exc:
        await service.crear_grupo(
            session, schemas.GrupoMesasCreate(mesas_ids=[m1.id, m2.id]), usuario_id=None
        )
    assert exc.value.code == "MESA_INACTIVA"


async def test_crear_grupo_una_mesa_se_rechaza(session: AsyncSession) -> None:
    zona = await _zona(session)
    m1 = await _mesa(session, zona)
    # Construido sin validación de schema para ejercitar la guarda del service.
    data = schemas.GrupoMesasCreate.model_construct(mesas_ids=[m1.id])
    with pytest.raises(DomainError) as exc:
        await service.crear_grupo(session, data, usuario_id=None)
    assert exc.value.code == "GRUPO_INVALIDO"


async def test_disolver_grupo(session: AsyncSession) -> None:
    zona = await _zona(session)
    m1 = await _mesa(session, zona, numero="M1")
    m2 = await _mesa(session, zona, numero="M2")
    grupo = await service.crear_grupo(
        session, schemas.GrupoMesasCreate(mesas_ids=[m1.id, m2.id]), usuario_id=None
    )

    await service.disolver_grupo(session, grupo.id, usuario_id=None)
    assert (await service.obtener_mesa(session, m1.id)).grupo_id is None
    assert (await service.obtener_mesa(session, m2.id)).grupo_id is None
    grupo_read = await service.leer_grupo(session, grupo.id)
    assert grupo_read.dissolved_at is not None
    assert await _audit_count(session, "grupo.disuelto") == 1

    with pytest.raises(DomainError) as exc:
        await service.disolver_grupo(session, grupo.id, usuario_id=None)
    assert exc.value.code == "GRUPO_YA_DISUELTO"


async def test_mesas_ids_derivado(session: AsyncSession) -> None:
    zona = await _zona(session)
    m1 = await _mesa(session, zona, numero="M1")
    m2 = await _mesa(session, zona, numero="M2")
    grupo = await service.crear_grupo(
        session, schemas.GrupoMesasCreate(mesas_ids=[m1.id, m2.id]), usuario_id=None
    )
    grupo_read = await service.leer_grupo(session, grupo.id)
    assert set(grupo_read.mesas_ids) == {m1.id, m2.id}


async def test_qr_usa_id_permanente(session: AsyncSession) -> None:
    zona = await _zona(session)
    mesa = await _mesa(session, zona)
    qr = await service.generar_qr(session, mesa.id, usuario_id=None)
    assert qr.mesa_id == mesa.id
    assert str(mesa.id) in qr.url
    assert await _audit_count(session, "mesa.qr_generado") == 1


async def test_auditoria_cambio_estado(session: AsyncSession) -> None:
    zona = await _zona(session)
    mesa = await _mesa(session, zona)
    await service.ocupar_mesa(session, mesa.id)
    assert await _audit_count(session, "mesa.estado_cambiado") >= 1
    await service.cerrar_zona(session, zona.id, "mantenimiento", usuario_id=None)
    assert await _audit_count(session, "zona.estado_cambiado") >= 1


async def test_evento_ws_emitido_al_cambiar_estado(
    session: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> None:
    from osiris.websocket.manager import manager

    capturados: list[tuple[str, dict]] = []

    async def _spy(channel: str, message: dict) -> None:
        capturados.append((channel, message))

    monkeypatch.setattr(manager, "broadcast", _spy)

    zona = await _zona(session)
    mesa = await _mesa(session, zona)
    await service.ocupar_mesa(session, mesa.id)

    assert any(ch == "mesas" and msg["type"] == "mesa.estado_cambiado" for ch, msg in capturados)

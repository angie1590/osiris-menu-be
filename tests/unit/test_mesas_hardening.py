"""Service §20 hardening — unicidad, crear-en-activa, desactivar/reactivar, eventos."""

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
    session: AsyncSession, zona: Zona, *, estado: EstadoMesa = EstadoMesa.LIBRE, numero: str = "M1"
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


# ---- REG-20-15 unicidad de numero_visible ----


async def test_numero_visible_duplicado_en_misma_zona(session: AsyncSession) -> None:
    zona = await service.crear_zona(session, schemas.ZonaCreate(nombre="Barra"))
    await service.crear_mesa(session, schemas.MesaCreate(zona_id=zona.id, numero_visible="J8"))
    with pytest.raises(DomainError) as exc:
        await service.crear_mesa(session, schemas.MesaCreate(zona_id=zona.id, numero_visible="J8"))
    assert exc.value.code == "NUMERO_VISIBLE_DUPLICADO"


async def test_numero_visible_duplicado_trim_y_case(session: AsyncSession) -> None:
    zona = await service.crear_zona(session, schemas.ZonaCreate(nombre="Barra"))
    await service.crear_mesa(session, schemas.MesaCreate(zona_id=zona.id, numero_visible="J8"))
    for variante in (" J8 ", "j8", "J8  "):
        with pytest.raises(DomainError) as exc:
            await service.crear_mesa(
                session, schemas.MesaCreate(zona_id=zona.id, numero_visible=variante)
            )
        assert exc.value.code == "NUMERO_VISIBLE_DUPLICADO"


async def test_numero_visible_se_guarda_trim(session: AsyncSession) -> None:
    zona = await service.crear_zona(session, schemas.ZonaCreate(nombre="Barra"))
    mesa = await service.crear_mesa(
        session, schemas.MesaCreate(zona_id=zona.id, numero_visible="  M5  ")
    )
    assert mesa.numero_visible == "M5"


async def test_numero_visible_repetible_en_otra_zona(session: AsyncSession) -> None:
    z1 = await service.crear_zona(session, schemas.ZonaCreate(nombre="Barra"))
    z2 = await service.crear_zona(session, schemas.ZonaCreate(nombre="Jardín"))
    await service.crear_mesa(session, schemas.MesaCreate(zona_id=z1.id, numero_visible="J8"))
    mesa = await service.crear_mesa(session, schemas.MesaCreate(zona_id=z2.id, numero_visible="J8"))
    assert mesa.numero_visible == "J8"


# ---- REG-20-16 crear mesa solo en zona activa ----


async def test_crear_mesa_en_zona_inactiva_se_rechaza(session: AsyncSession) -> None:
    zona = await _zona(session, EstadoZona.INACTIVA)
    with pytest.raises(DomainError) as exc:
        await service.crear_mesa(session, schemas.MesaCreate(zona_id=zona.id, numero_visible="M1"))
    assert exc.value.code == "ZONA_NO_ACTIVA"


async def test_crear_mesa_en_zona_en_cierre_se_rechaza(session: AsyncSession) -> None:
    zona = await _zona(session, EstadoZona.EN_CIERRE)
    with pytest.raises(DomainError) as exc:
        await service.crear_mesa(session, schemas.MesaCreate(zona_id=zona.id, numero_visible="M1"))
    assert exc.value.code == "ZONA_NO_ACTIVA"


# ---- REG-20-18 desactivar mesa con validaciones ----


async def test_desactivar_mesa_ocupada_se_rechaza(session: AsyncSession) -> None:
    zona = await _zona(session)
    mesa = await _mesa(session, zona, estado=EstadoMesa.OCUPADA)
    with pytest.raises(DomainError) as exc:
        await service.baja_mesa(session, mesa.id, usuario_id=None)
    assert exc.value.code == "MESA_NO_DESACTIVABLE"


async def test_desactivar_mesa_reservada_se_rechaza(session: AsyncSession) -> None:
    zona = await _zona(session)
    mesa = await _mesa(session, zona, estado=EstadoMesa.RESERVADA)
    with pytest.raises(DomainError) as exc:
        await service.baja_mesa(session, mesa.id, usuario_id=None)
    assert exc.value.code == "MESA_NO_DESACTIVABLE"


async def test_desactivar_mesa_con_comanda_se_rechaza(session: AsyncSession) -> None:
    zona = await _zona(session)
    mesa = await _mesa(session, zona)
    mesa.comanda_activa_id = uuid.uuid4()
    await session.commit()
    with pytest.raises(DomainError) as exc:
        await service.baja_mesa(session, mesa.id, usuario_id=None)
    assert exc.value.code == "MESA_NO_DESACTIVABLE"


async def test_desactivar_mesa_agrupada_se_rechaza(session: AsyncSession) -> None:
    zona = await _zona(session)
    m1 = await _mesa(session, zona, numero="M1")
    m2 = await _mesa(session, zona, numero="M2")
    await service.crear_grupo(
        session, schemas.GrupoMesasCreate(mesas_ids=[m1.id, m2.id]), usuario_id=None
    )
    with pytest.raises(DomainError) as exc:
        await service.baja_mesa(session, m1.id, usuario_id=None)
    assert exc.value.code == "MESA_NO_DESACTIVABLE"


async def test_desactivar_mesa_valida_baja_y_audita(session: AsyncSession) -> None:
    zona = await _zona(session)
    mesa = await _mesa(session, zona)
    await service.baja_mesa(session, mesa.id, usuario_id=None)
    refrescada = await service.obtener_mesa(session, mesa.id)
    assert refrescada.activa is False
    assert refrescada.estado == EstadoMesa.INACTIVA
    assert await _audit_count(session, "mesa.baja_logica") == 1


# ---- REG-20-19 reactivar mesa ----


async def test_reactivar_mesa_en_zona_activa(session: AsyncSession) -> None:
    zona = await _zona(session)
    mesa = await _mesa(session, zona)
    await service.baja_mesa(session, mesa.id, usuario_id=None)
    reactivada = await service.reactivar_mesa(session, mesa.id, usuario_id=None)
    assert reactivada.activa is True
    assert reactivada.estado == EstadoMesa.LIBRE
    assert await _audit_count(session, "mesa.reactivada") == 1


async def test_reactivar_mesa_en_zona_inactiva_se_rechaza(session: AsyncSession) -> None:
    zona = await _zona(session)
    mesa = await _mesa(session, zona)
    await service.baja_mesa(session, mesa.id, usuario_id=None)
    # zona pasa a inactiva (no hay mesas ocupadas/reservadas)
    await service.desactivar_zona(session, zona.id, usuario_id=None)
    with pytest.raises(DomainError) as exc:
        await service.reactivar_mesa(session, mesa.id, usuario_id=None)
    assert exc.value.code == "ZONA_NO_ACTIVA"


async def test_reactivar_mesa_en_zona_en_cierre_se_rechaza(session: AsyncSession) -> None:
    zona = await _zona(session)
    mesa = await _mesa(session, zona)
    await service.baja_mesa(session, mesa.id, usuario_id=None)
    await service.cerrar_zona(session, zona.id, "evento", usuario_id=None)
    with pytest.raises(DomainError) as exc:
        await service.reactivar_mesa(session, mesa.id, usuario_id=None)
    assert exc.value.code == "ZONA_NO_ACTIVA"


# ---- eventos específicos ----


async def test_desactivar_reactivar_emiten_eventos(
    session: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> None:
    from osiris.websocket.manager import manager

    capturados: list[tuple[str, dict]] = []

    async def _spy(channel: str, message: dict) -> None:
        capturados.append((channel, message))

    monkeypatch.setattr(manager, "broadcast", _spy)

    zona = await _zona(session)
    mesa = await _mesa(session, zona)
    await service.baja_mesa(session, mesa.id, usuario_id=None)
    await service.reactivar_mesa(session, mesa.id, usuario_id=None)

    tipos = [m["type"] for _, m in capturados]
    assert "mesa.desactivada" in tipos
    assert "mesa.reactivada" in tipos

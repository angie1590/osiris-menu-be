"""Unit: ConnectionManager aísla canales y limpia conexiones (D-d)."""

from __future__ import annotations

from typing import Any

from osiris.websocket.manager import ConnectionManager, comanda_channel


class FakeConnection:
    def __init__(self) -> None:
        self.received: list[Any] = []

    async def send_json(self, data: Any) -> None:
        self.received.append(data)


async def test_broadcast_reaches_only_target_channel() -> None:
    manager = ConnectionManager()
    mesa_conn = FakeConnection()
    cocina_conn = FakeConnection()
    manager.add("mesas", mesa_conn)
    manager.add("cocina", cocina_conn)

    await manager.broadcast("mesas", {"type": "mesa.estado_cambiado"})

    assert mesa_conn.received == [{"type": "mesa.estado_cambiado"}]
    assert cocina_conn.received == []


async def test_disconnect_clears_connection() -> None:
    manager = ConnectionManager()
    conn = FakeConnection()
    channel = comanda_channel("abc-123")
    manager.add(channel, conn)
    assert manager.count(channel) == 1

    manager.remove(channel, conn)
    assert manager.count(channel) == 0

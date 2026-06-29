"""ConnectionManager en memoria por canal (D-d).

Suficiente para un único servidor local (T-28). Los nombres de canal son lógicos
(`mesas`, `comandas:<comanda_id>`, `cocina`, `barra`, `connectivity`); las rutas
físicas viven en `websocket/api.py` bajo `/ws/...`.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Protocol


class SupportsSendJson(Protocol):
    async def send_json(self, data: Any) -> None: ...


def comanda_channel(comanda_id: str) -> str:
    """Nombre lógico del canal de una comanda específica."""
    return f"comandas:{comanda_id}"


class ConnectionManager:
    """Indexa conexiones por canal y permite broadcast a los suscriptores de un canal."""

    def __init__(self) -> None:
        self._channels: dict[str, set[SupportsSendJson]] = defaultdict(set)

    def add(self, channel: str, connection: SupportsSendJson) -> None:
        self._channels[channel].add(connection)

    def remove(self, channel: str, connection: SupportsSendJson) -> None:
        self._channels.get(channel, set()).discard(connection)
        if not self._channels.get(channel):
            self._channels.pop(channel, None)

    def count(self, channel: str) -> int:
        return len(self._channels.get(channel, set()))

    async def broadcast(self, channel: str, message: dict[str, Any]) -> None:
        """Envía `message` (payload tipado base) a todas las conexiones del canal."""
        for connection in list(self._channels.get(channel, set())):
            await connection.send_json(message)


# Instancia única del proceso (un worker en MVP).
manager = ConnectionManager()

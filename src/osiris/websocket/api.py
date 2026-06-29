"""Endpoints WebSocket scaffolding. Rutas físicas `/ws/...` para los canales canónicos.

| Nombre lógico            | Ruta física                     |
|--------------------------|---------------------------------|
| mesas                    | /ws/mesas                       |
| comandas:<comanda_id>    | /ws/comandas/{comanda_id}       |
| cocina                   | /ws/cocina                      |
| barra                    | /ws/barra                       |
| connectivity             | /ws/connectivity                |

Sólo transporte: al conectar se emite un evento tipado `connected` y se mantiene la
conexión viva haciendo echo. La lógica de negocio por canal llega con cada módulo.
"""

from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from .manager import comanda_channel, manager

ws_router = APIRouter(prefix="/ws", tags=["websocket"])


async def _serve(channel: str, websocket: WebSocket, **extra: str) -> None:
    await websocket.accept()
    manager.add(channel, websocket)
    await websocket.send_json({"type": "connected", "channel": channel, **extra})
    try:
        while True:
            # Scaffolding: mantenemos la conexión viva; echo simple sin reglas de negocio.
            data = await websocket.receive_text()
            await websocket.send_json({"type": "echo", "channel": channel, "data": data})
    except WebSocketDisconnect:
        manager.remove(channel, websocket)


@ws_router.websocket("/mesas")
async def ws_mesas(websocket: WebSocket) -> None:
    await _serve("mesas", websocket)


@ws_router.websocket("/comandas/{comanda_id}")
async def ws_comandas(websocket: WebSocket, comanda_id: str) -> None:
    await _serve(comanda_channel(comanda_id), websocket, comanda_id=comanda_id)


@ws_router.websocket("/cocina")
async def ws_cocina(websocket: WebSocket) -> None:
    await _serve("cocina", websocket)


@ws_router.websocket("/barra")
async def ws_barra(websocket: WebSocket) -> None:
    await _serve("barra", websocket)


@ws_router.websocket("/connectivity")
async def ws_connectivity(websocket: WebSocket) -> None:
    await _serve("connectivity", websocket)

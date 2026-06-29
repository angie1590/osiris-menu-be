"""Integration: handshake WebSocket de un canal canónico (realtime-foundation)."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_ws_mesas_connect_emits_connected(client: TestClient) -> None:
    with client.websocket_connect("/ws/mesas") as ws:
        message = ws.receive_json()
        assert message["type"] == "connected"
        assert message["channel"] == "mesas"


def test_ws_comanda_channel_includes_id(client: TestClient) -> None:
    with client.websocket_connect("/ws/comandas/abc-123") as ws:
        message = ws.receive_json()
        assert message["type"] == "connected"
        assert message["channel"] == "comandas:abc-123"
        assert message["comanda_id"] == "abc-123"

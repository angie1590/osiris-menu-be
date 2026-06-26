"""Verifica que los errores se sirven con el contrato base estructurado."""

from __future__ import annotations

from fastapi.testclient import TestClient

from osiris.main import app

client = TestClient(app)


def test_unknown_route_returns_structured_error() -> None:
    response = client.get("/ruta-que-no-existe")

    assert response.status_code == 404
    body = response.json()
    assert set(body) == {"error"}
    assert body["error"]["code"] == "not_found"
    assert isinstance(body["error"]["message"], str)

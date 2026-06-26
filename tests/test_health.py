"""Test de humo: la app arranca y `/health` responde correctamente."""

from __future__ import annotations

from fastapi.testclient import TestClient

from osiris.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

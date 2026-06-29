"""Integration: /health y OpenAPI sirven correctamente (backend-foundation)."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_health_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "osiris-menu-api"


def test_openapi_served(client: TestClient) -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "paths" in schema
    assert "/api/v1/mesas" in schema["paths"]


def test_module_routers_mounted(client: TestClient) -> None:
    for module in ("mesas", "comandas", "cocina-barra"):
        response = client.get(f"/api/v1/{module}")
        assert response.status_code == 200
        assert response.json()["status"] == "scaffolding"

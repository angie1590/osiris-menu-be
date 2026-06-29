"""API §20 hardening — capacidad positiva, duplicados, reactivar endpoint."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient


def _rid() -> dict[str, str]:
    return {"X-Request-Id": str(uuid.uuid4())}


def _zona(client: TestClient, nombre: str = "Zona") -> str:
    return client.post("/api/v1/zonas", json={"nombre": nombre}, headers=_rid()).json()["id"]


def _mesa(client: TestClient, zona_id: str, numero: str = "M1") -> dict:
    resp = client.post(
        "/api/v1/mesas",
        json={"zona_id": zona_id, "numero_visible": numero, "capacidad": 4},
        headers=_rid(),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_capacidad_cero_se_rechaza(client: TestClient) -> None:
    zona_id = _zona(client)
    resp = client.post(
        "/api/v1/mesas",
        json={"zona_id": zona_id, "numero_visible": "M1", "capacidad": 0},
        headers=_rid(),
    )
    assert resp.status_code == 422


def test_numero_visible_duplicado_api(client: TestClient) -> None:
    zona_id = _zona(client)
    _mesa(client, zona_id, "J8")
    dup = client.post(
        "/api/v1/mesas",
        json={"zona_id": zona_id, "numero_visible": " j8 ", "capacidad": 2},
        headers=_rid(),
    )
    assert dup.status_code == 409
    assert dup.json()["error"]["code"] == "NUMERO_VISIBLE_DUPLICADO"


def test_crear_mesa_en_zona_inactiva_api(client: TestClient) -> None:
    zona_id = _zona(client)
    client.post(f"/api/v1/zonas/{zona_id}/desactivar", headers=_rid())
    resp = client.post(
        "/api/v1/mesas",
        json={"zona_id": zona_id, "numero_visible": "M1", "capacidad": 2},
        headers=_rid(),
    )
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "ZONA_NO_ACTIVA"


def test_desactivar_y_reactivar_mesa_api(client: TestClient) -> None:
    zona_id = _zona(client)
    mesa = _mesa(client, zona_id, "M1")

    # desactivar (DELETE)
    desac = client.delete(f"/api/v1/mesas/{mesa['id']}", headers=_rid())
    assert desac.status_code == 200
    assert desac.json()["activa"] is False
    assert desac.json()["estado"] == "inactiva"

    # reactivar
    react = client.post(f"/api/v1/mesas/{mesa['id']}/reactivar", headers=_rid())
    assert react.status_code == 200
    assert react.json()["activa"] is True
    assert react.json()["estado"] == "libre"


def test_reactivar_mesa_endpoint_existe_en_openapi(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    assert "/api/v1/mesas/{mesa_id}/reactivar" in schema["paths"]

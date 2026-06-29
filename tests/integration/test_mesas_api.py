"""API §20 — endpoints de zonas, mesas y grupos."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient


def _rid() -> dict[str, str]:
    return {"X-Request-Id": str(uuid.uuid4())}


def _crear_zona(client: TestClient, nombre: str = "Zona") -> dict:
    resp = client.post("/api/v1/zonas", json={"nombre": nombre}, headers=_rid())
    assert resp.status_code == 201, resp.text
    return resp.json()


def _crear_mesa(client: TestClient, zona_id: str, numero: str = "M1") -> dict:
    resp = client.post(
        "/api/v1/mesas",
        json={"zona_id": zona_id, "numero_visible": numero, "capacidad": 4},
        headers=_rid(),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_crear_zona_y_mesa(client: TestClient) -> None:
    zona = _crear_zona(client)
    assert zona["estado"] == "activa"
    mesa = _crear_mesa(client, zona["id"])
    assert mesa["estado"] == "libre"


def test_post_mesas_ignora_id_cliente(client: TestClient) -> None:
    zona = _crear_zona(client)
    fake = str(uuid.uuid4())
    resp = client.post(
        "/api/v1/mesas",
        json={"id": fake, "zona_id": zona["id"], "numero_visible": "M1", "capacidad": 2},
        headers=_rid(),
    )
    assert resp.status_code == 201
    assert resp.json()["id"] != fake


def test_idempotencia_mutador(client: TestClient) -> None:
    headers = _rid()
    first = client.post("/api/v1/zonas", json={"nombre": "Z"}, headers=headers)
    assert first.status_code == 201
    second = client.post("/api/v1/zonas", json={"nombre": "Z"}, headers=headers)
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "IDEMPOTENCY_KEY_REUSED"


def test_mutador_sin_request_id(client: TestClient) -> None:
    resp = client.post("/api/v1/zonas", json={"nombre": "Z"})
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "MISSING_REQUEST_ID"


def test_cerrar_zona_requiere_motivo(client: TestClient) -> None:
    zona = _crear_zona(client)
    sin_motivo = client.post(f"/api/v1/zonas/{zona['id']}/cerrar", json={}, headers=_rid())
    assert sin_motivo.status_code == 422
    con_motivo = client.post(
        f"/api/v1/zonas/{zona['id']}/cerrar", json={"motivo": "mantenimiento"}, headers=_rid()
    )
    assert con_motivo.status_code == 200
    assert con_motivo.json()["estado"] == "en_cierre"


def test_listar_mesas_filtra_por_zona(client: TestClient) -> None:
    zona = _crear_zona(client)
    _crear_mesa(client, zona["id"], "M1")
    resp = client.get(f"/api/v1/mesas?zona_id={zona['id']}")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_desactivar_zona_vacia(client: TestClient) -> None:
    zona = _crear_zona(client)
    _crear_mesa(client, zona["id"], "M1")
    resp = client.post(f"/api/v1/zonas/{zona['id']}/desactivar", headers=_rid())
    assert resp.status_code == 200
    assert resp.json()["estado"] == "inactiva"


def test_grupos_crear_y_disolver(client: TestClient) -> None:
    zona = _crear_zona(client)
    m1 = _crear_mesa(client, zona["id"], "M1")["id"]
    m2 = _crear_mesa(client, zona["id"], "M2")["id"]

    creado = client.post("/api/v1/grupos", json={"mesas_ids": [m1, m2]}, headers=_rid())
    assert creado.status_code == 201
    assert set(creado.json()["mesas_ids"]) == {m1, m2}
    grupo_id = creado.json()["id"]

    disuelto = client.post(f"/api/v1/grupos/{grupo_id}/disolver", headers=_rid())
    assert disuelto.status_code == 200
    assert disuelto.json()["dissolved_at"] is not None


def test_grupo_una_mesa_se_rechaza(client: TestClient) -> None:
    zona = _crear_zona(client)
    m1 = _crear_mesa(client, zona["id"], "M1")["id"]
    resp = client.post("/api/v1/grupos", json={"mesas_ids": [m1]}, headers=_rid())
    assert resp.status_code == 422  # min_length=2 a nivel de schema

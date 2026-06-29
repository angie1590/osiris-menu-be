"""Integration: política de idempotencia X-Request-Id → 409 en reuso (D-b).

Se ejercita contra el endpoint interno de prueba `/api/v1/_internal/echo` porque aún no
hay mutadores reales de negocio.
"""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

ECHO = "/api/v1/_internal/echo"


def test_duplicate_request_id_is_rejected(client: TestClient) -> None:
    request_id = str(uuid.uuid4())
    headers = {"X-Request-Id": request_id}

    first = client.post(ECHO, headers=headers)
    assert first.status_code == 200
    assert first.json()["request_id"] == request_id

    second = client.post(ECHO, headers=headers)
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "IDEMPOTENCY_KEY_REUSED"


def test_missing_request_id_is_rejected(client: TestClient) -> None:
    response = client.post(ECHO)
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "MISSING_REQUEST_ID"


def test_invalid_request_id_is_rejected(client: TestClient) -> None:
    response = client.post(ECHO, headers={"X-Request-Id": "not-a-uuid"})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_REQUEST_ID"

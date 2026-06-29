"""Excepciones de dominio tipadas (D-c).

Todas derivan de `DomainError` y portan `code`, `message`, `status_code` y `details`.
El handler global las serializa al envelope `{ "error": { code, message, details } }`.
"""

from __future__ import annotations

from typing import Any


class DomainError(Exception):
    """Error de dominio base. No usar `Exception` genérica en el código."""

    code: str = "DOMAIN_ERROR"
    status_code: int = 400

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code
        if status_code is not None:
            self.status_code = status_code
        self.details: dict[str, Any] = details or {}


class MissingRequestId(DomainError):
    code = "MISSING_REQUEST_ID"
    status_code = 400


class InvalidRequestId(DomainError):
    code = "INVALID_REQUEST_ID"
    status_code = 400


class IdempotencyKeyReused(DomainError):
    """Política inicial del scaffolding: rechazar un X-Request-Id ya visto (D-b)."""

    code = "IDEMPOTENCY_KEY_REUSED"
    status_code = 409

    def __init__(self, message: str = "X-Request-Id ya procesado", **kwargs: Any) -> None:
        super().__init__(message, **kwargs)

"""Excepciones de dominio del backend.

Todas las excepciones de negocio heredan de :class:`OsirisError` para que el
manejador central de errores las serialice al contrato base
``{ "error": { "code", "message", "details"? } }``.
"""

from __future__ import annotations

from typing import Any


class OsirisError(Exception):
    """Excepción base de dominio.

    Subclases pueden fijar ``code`` y ``status_code`` por defecto, o pasarlos
    por instancia. ``details`` es un mapa opcional con contexto serializable.
    """

    code: str = "internal_error"
    status_code: int = 500

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
        self.details = details

"""Operador actual (placeholder, D-mz-10).

Mientras no exista auth real, `usuario_id` es opcional: se toma de un header temporal
`X-Operator-Id` si viene, o queda `None`. Cuando exista auth real, será obligatorio para
los mutadores operativos.
"""

from __future__ import annotations

import uuid

from fastapi import Header


async def current_operator(
    x_operator_id: str | None = Header(default=None, alias="X-Operator-Id"),
) -> uuid.UUID | None:
    if not x_operator_id:
        return None
    try:
        return uuid.UUID(x_operator_id)
    except ValueError:
        return None

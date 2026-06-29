"""Niveles de autorización 1–4 (placeholder de scaffolding, D-j).

El glosario define qué roles cumplen cada nivel. Aquí sólo se establece el contrato;
la validación real de identidad/nivel se implementará en la propuesta de auth.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from enum import IntEnum


class NivelAutorizacion(IntEnum):
    NIVEL_1 = 1  # Cualquier operador autenticado
    NIVEL_2 = 2  # Cajero, Admin Socio, Admin Contable, Super Admin
    NIVEL_3 = 3  # Admin Socio, Admin Contable, Super Admin
    NIVEL_4 = 4  # Admin Socio o Super Admin


def require_nivel(nivel: NivelAutorizacion) -> Callable[[], Awaitable[NivelAutorizacion]]:
    """Devuelve una dependencia placeholder que (por ahora) no valida identidad.

    TODO(auth): reemplazar por validación real de sesión/PIN según la propuesta de auth.
    """

    async def _dependency() -> NivelAutorizacion:
        return nivel

    return _dependency

"""§22 — Eventos WebSocket (canales lógicos `cocina` y `barra`).

El módulo propaga eventos de §21 filtrados por ruteo y emite agotamiento de producto.
Placeholder: sólo nombres de evento; emisión real con la propuesta funcional de §22.
"""

from __future__ import annotations

CHANNEL_COCINA = "cocina"
CHANNEL_BARRA = "barra"

PRODUCTO_AGOTADO = "producto.agotado"
PRODUCTO_RESTAURADO = "producto.restaurado"

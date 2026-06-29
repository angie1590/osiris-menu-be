"""§20 — Nombres de eventos WebSocket del módulo (canal lógico `mesas`).

Placeholder: sólo se declaran los nombres de evento de la reference-spec. Los payloads
tipados y la emisión real llegan con la propuesta funcional de §20.
"""

from __future__ import annotations

CHANNEL = "mesas"

MESA_ESTADO_CAMBIADO = "mesa.estado_cambiado"
ZONA_ESTADO_CAMBIADO = "zona.estado_cambiado"
GRUPO_CREADO = "grupo.creado"
GRUPO_DISUELTO = "grupo.disuelto"

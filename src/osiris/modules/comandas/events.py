"""§21 — Nombres de eventos WebSocket del módulo (canal lógico `comandas:<comanda_id>`).

Placeholder: sólo nombres de evento de la reference-spec. Payloads tipados y emisión
real llegan con la propuesta funcional de §21.
"""

from __future__ import annotations

COMANDA_CREADA = "comanda.creada"
COMANDA_ESTADO_CAMBIADO = "comanda.estado_cambiado"
COMANDA_ANULADA = "comanda.anulada"
COMANDA_ITEM_AGREGADO = "comanda.item_agregado"
COMANDA_ITEM_ESTADO_CAMBIADO = "comanda.item_estado_cambiado"
COMANDA_ITEM_ANULADO = "comanda.item_anulado"
COMANDA_ITEM_RECHAZADO = "comanda.item_rechazado"
COMANDA_TRASLADADA = "comanda.trasladada"
COMANDA_DIVIDIDA = "comanda.dividida"

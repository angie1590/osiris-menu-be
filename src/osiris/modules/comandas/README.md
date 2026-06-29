# Módulo §21 · Comandas

Scaffolding del módulo. Estructura y router placeholder; **sin reglas de negocio**.

- Spec de referencia: `openspec/reference-specs/21-comandas.md`
- Reglas (REG-21-xx), entidades (Comanda, ItemComanda, DivisionCuenta), matriz D-02,
  inventario híbrido D-01, combos D-03, división D-09, traslados D-08: pendientes de la
  propuesta funcional de §21.
- Canal WebSocket lógico: `comandas:<comanda_id>` → ruta física `/ws/comandas/{comanda_id}`.
- Todo mutador real usará la dependencia de idempotencia `X-Request-Id` (`shared/idempotency.py`).

Capas: `api.py` (orquesta), `service.py` (lógica), `models.py` (enums/estado),
`schemas.py` (contrato público), `events.py` (eventos del canal).

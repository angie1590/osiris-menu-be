# Módulo §20 · Mesas y zonas

Scaffolding del módulo. Estructura y router placeholder; **sin reglas de negocio**.

- Spec de referencia: `openspec/reference-specs/20-mesas.md`
- Reglas (REG-20-xx), entidades (Zona, Mesa, GrupoMesas) y transiciones: pendientes de la
  propuesta funcional de §20.
- Canal WebSocket lógico: `mesas` → ruta física `/ws/mesas`.
- Terminología canónica: ver `openspec/glossary.md`.

Capas: `api.py` (orquesta), `service.py` (lógica), `models.py` (enums/estado),
`schemas.py` (contrato público), `events.py` (eventos del canal).

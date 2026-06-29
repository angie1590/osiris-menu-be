# Módulo §22 · Cocina y barra

Scaffolding del módulo. **No posee entidades propias**: consume `ItemComanda` de §21
(filtrado por ruteo) y catálogo/inventario de §25/§26.

- Spec de referencia: `openspec/reference-specs/22-cocina-barra.md`
- Reglas (R-22-xx), vistas operativas, consumo confirmado D-01, agotamiento N-11: pendientes
  de la propuesta funcional de §22.
- Canales WebSocket lógicos: `cocina` → `/ws/cocina`, `barra` → `/ws/barra`.
- Ruteo canónico: `modules.comandas.models.Ruteo`.

Capas: `api.py` (orquesta), `service.py` (lógica), `models.py` (re-exporta ruteo),
`schemas.py` (contrato público), `events.py` (eventos de los canales).

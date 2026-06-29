# Módulo §20 · Mesas y zonas

Primer vertical funcional. Implementa las reglas REG-20-XX que no dependen de §21/§28.

- Spec de referencia: `openspec/reference-specs/20-mesas.md`; capability: `mesas-zonas`.
- Entidades: `Zona`, `Mesa`, `GrupoMesas`. La pertenencia a grupo vive en `Mesa.grupo_id`
  (única fuente de verdad); `GrupoMesas` no persiste `mesas_ids` (se deriva en read models).
- Estados: valores técnicos snake_case en API/DB (`libre`, `por_limpiar`, `en_cierre`, ...);
  la UI mapea a las etiquetas canónicas del glosario.
- Unir mesas = crear grupo; separar = disolver grupo (`POST /grupos/{id}/disolver`). Sin
  comanda real en §20 (eso es §21).
- Reglas: REG-20-01 (Ocupada solo desde Libre/Reservada), REG-20-02 (una comanda activa),
  REG-20-03 (grupos exclusivos), REG-20-07/09 (zona Inactiva/En cierre), REG-20-08 (cierre
  Nivel 2 + motivo), REG-20-12 (id permanente, baja lógica), REG-20-14 (Por limpiar→Libre).
- Auditoría persistente en `audit_logs` (`shared/audit.py`). `usuario_id` opcional hasta auth real.
- Canal WebSocket: `mesas` → `/ws/mesas`. Eventos: `mesa.estado_cambiado`, `zona.estado_cambiado`,
  `grupo.creado`, `grupo.actualizado`, `grupo.disuelto`.
- Contrato preparado (no implementado): §21 Comandas y §28 Reservas (columnas + seams).

Capas: `api.py` (orquesta), `service.py` (reglas), `models.py` (entidades/enums),
`schemas.py` (contrato), `events.py` (eventos del canal).

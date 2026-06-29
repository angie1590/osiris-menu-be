## Context

El scaffolding está aplicado y archivado. `modules/mesas` existe como placeholder (router `{status: "scaffolding"}`, enums `EstadoZona`/`EstadoMesa`). El backend tiene: app FastAPI con `/api/v1`, `db.py` (SQLAlchemy 2 async + asyncpg), `shared/` (envelope de error, excepciones de dominio, dependencia de idempotencia `X-Request-Id`), `auth/levels.py` (`NivelAutorizacion` + `require_nivel` placeholder, D-j), `websocket/` (ConnectionManager + canales `/ws/...`, broadcaster en memoria). El frontend tiene `src/api/apiClient.ts`, `src/ws/wsClient.ts`, `src/modules/mesas/` placeholder, componentes `ui/`, TanStack Query.

§20 es el primer vertical funcional: implementa las reglas REG-20-XX que **no** dependen de §21 Comandas ni §28 Reservas, y deja el resto como contrato/placeholder explícito.

## Goals / Non-Goals

**Goals:**
- Modelos `Zona`, `Mesa`, `GrupoMesas` (+ `audit_logs`) y migración `0002`.
- Service con REG-20-01/02/07/08/09/12/14, desactivación de zona, transición a Reservada (seam §28) y unir/separar grupos.
- Endpoints REST con `X-Request-Id` y envelope de error, incluido `POST /grupos/{id}/disolver`.
- Eventos WS del canal `mesas` (incluye `grupo.actualizado`) con broadcaster testeable.
- Auditoría persistente en `audit_logs`.
- Módulo frontend `mesas` (api/ws/types/hooks/components) + vistas Mesero/Admin con UI mínima de unir/separar.

**Non-Goals:**
- Apertura/cierre real de comanda (§21), reservas (§28), QR público/imagen (§32), caja/SRI (§23/§24), cocina/barra (§22), inventario/catálogo/reportes.
- Auth real: se usa el placeholder `require_nivel`; el contrato del endpoint queda correcto.
- §31 Configuración: no se implementa; `saltar_estado_por_limpiar` se difiere a §21 (ver D-mz-3).

## Decisions

### D-mz-1 · Reglas como máquina de estados en `service.py`, transición central única
Toda transición de estado de mesa pasa por `transicionar_mesa(mesa, nuevo_estado, *, contexto)` que valida REG-20-01 (orígenes válidos para Ocupada), REG-20-07 (zona Inactiva sin Ocupada/Reservada), REG-20-09 (zona En cierre sin nuevas ocupaciones/reservas), emite el evento `mesa.estado_cambiado` y escribe el audit log. La transición a `reservada` es una operación de servicio testeable (seam §28). Centralizar evita reglas dispersas.

### D-mz-2 · `comanda_activa_id`/`reserva_activa_id`/`comanda_id` como columnas sin FK dura todavía
Las tablas `comandas`/`reservas` no existen. Se modelan `Mesa.comanda_activa_id`, `Mesa.reserva_activa_id` y `GrupoMesas.comanda_id` como `UUID?` **sin** ForeignKey por ahora (se añadirá la FK con §21/§28), para soportar REG-20-02 como invariante de servicio sin romper la migración.

### D-mz-3 · `saltar_estado_por_limpiar` pertenece a §21, no gobierna `marcar-libre`
En §20, `POST /mesas/{id}/marcar-libre` solo exige que la mesa esté en `por_limpiar` (REG-20-14, cualquier operador autenticado). El flag `saltar_estado_por_limpiar` **no** se usa en §20: pertenece al futuro cierre de comanda de §21, donde se decidirá si al cerrar la comanda la mesa pasa a `por_limpiar` o directo a `libre`. No se añade el setting en esta propuesta para no dejar configuración muerta.
- Alternativa descartada: usar el flag para bloquear `marcar-libre` — confunde dos momentos distintos (cierre de comanda vs avance manual de limpieza).

### D-mz-4 · Autorización Nivel 2 vía placeholder `require_nivel`, motivo obligatorio en el schema
REG-20-08 (Activa→En cierre) usa `Depends(require_nivel(NivelAutorizacion.NIVEL_2))` (placeholder D-j, hoy no bloquea) y exige `motivo: str` en el body (validado por Pydantic). El **contrato** queda correcto y los tests verifican que falta-de-motivo se rechaza; la validación de identidad real llega con la propuesta de auth.

### D-mz-5 · GrupoMesas: `Mesa.grupo_id` es la única fuente de verdad; unir/separar; sin comanda (cierra PEND-mz-1)
`GrupoMesas` **no** persiste `mesas_ids`; la pertenencia vive en `Mesa.grupo_id`. `GrupoMesasRead.mesas_ids` es un campo **derivado** (consulta de mesas con ese `grupo_id`), evitando desincronización. No se usa tabla intermedia: la relación es 1‑grupo→N‑mesas y `Mesa.grupo_id` la expresa directamente; una tabla intermedia solo se justificaría con relación N‑a‑N, que no aplica.

- **Unir mesas = crear `GrupoMesas`** (`POST /grupos`): requiere ≥2 mesas, todas en estado `libre`, ninguna `inactiva`, ninguna ya agrupada (REG-20-03). Asigna el mismo `grupo_id`, emite `grupo.creado`, audita. **No** crea comanda real ni fuerza Ocupada: en §20 el grupo es agrupación lógica/física. La comanda compartida es de §21.
- **Modificar grupo** (`PATCH /grupos/{id}`): agrega/quita mesas bajo las mismas reglas; no permite dejar <2 mesas (para vaciar se disuelve); emite `grupo.actualizado`, audita.
- **Separar mesas = disolver `GrupoMesas`** (`POST /grupos/{id}/disolver`): solo grupo activo (sin `dissolved_at`); setea `dissolved_at`, limpia `grupo_id` de todas sus mesas, emite `grupo.disuelto`, audita. **No** elimina físicamente. Si §21 asocia una comanda activa al grupo, la disolución con comanda activa se resolverá en §21.
- **Estado válido para agrupar**: solo `libre`. Una mesa en `por_limpiar` debe avanzarse a `libre` (`marcar-libre`) antes de agruparse. Decisión estricta para claridad; relajarla a `por_limpiar` requeriría una decisión D-XX futura.

### D-mz-6 · Identificador permanente, baja lógica y QR (cierra PEND-mz-3)
`Mesa.id` es `UUID` generado por el backend; `POST /mesas` **no** acepta `id` del cliente (si llega, se ignora). `DELETE /mesas/{id}` es baja lógica (`activa=false`), nunca borra; el `id` no se reutiliza (REG-20-12). `POST /mesas/{id}/qr` devuelve una URL/payload que codifica el `id` permanente (D-04); **no** genera imagen ni impresión física (eso es §32). La generación de QR queda auditada.

### D-mz-7 · Eventos WS reutilizan el `ConnectionManager`; emisión desde el service; `usuario_id?`
El service llama a helpers de `events.py` que construyen el payload tipado (Pydantic) y hacen `manager.broadcast("mesas", payload)`: `mesa.estado_cambiado`, `zona.estado_cambiado`, `grupo.creado`, `grupo.actualizado`, `grupo.disuelto`. Para testear sin sockets, el broadcaster es inyectable/observable: los tests verifican que el service invoca el broadcast con el payload correcto.

### D-mz-8 · Enums técnicos en API/DB, etiquetas canónicas en UI
API/DB usan valores técnicos estables snake_case: `EstadoZona` (`activa`, `en_cierre`, `inactiva`), `EstadoMesa` (`libre`, `reservada`, `ocupada`, `por_limpiar`, `inactiva`). La UI mapea a las etiquetas canónicas del glosario (`Activa`, `En cierre`, `Inactiva`, `Libre`, `Reservada`, `Ocupada`, `Por limpiar`). Esto reemplaza los valores en español de los enums del scaffolding (que pasan a snake_case). El mapeo a etiquetas vive en el frontend (`modules/mesas/types.ts` o un helper de labels).
- Razón: valores técnicos son estables ante cambios de redacción y seguros para URLs/JSON; las etiquetas humanas son responsabilidad de presentación.

### D-mz-9 · Auditoría persistente mínima en `audit_logs` (cierra parte de la auditoría del Principio 1)
Se crea `shared/audit.py` con un helper `registrar_audit(session, *, event_type, entity_type, entity_id, user_id=None, reason=None, payload)` y el modelo/tabla `audit_logs` (`id`, `event_type`, `entity_type`, `entity_id`, `user_id?`, `reason?`, `payload` jsonb, `created_at`). No se usa solo `logging.info`. Operaciones auditadas en §20: cambio de estado de mesa, cambio de estado de zona, creación de grupo, disolución de grupo, generación de QR, baja lógica de mesa.
- Alternativa descartada: solo logging estructurado a stdout — no es consultable ni cumple "log append-only" de forma persistente. La tabla es la base reutilizable para los demás módulos.

### D-mz-10 · `usuario_id` opcional hasta auth real (cierra PEND-mz-2)
Mientras no exista auth real, `usuario_id`/`user_id` en eventos y `audit_logs` es **opcional**: si no hay operador autenticado se registra `null` y la operación procede. Se obtiene de una dependencia placeholder (p. ej. un `current_operator` que hoy devuelve `None`). Cuando exista auth real, `usuario_id` se volverá **obligatorio** para los mutadores operativos. Spec, payloads WS y audit logs quedan alineados con esta política.

### D-mz-11 · Desactivar zona: valida ocupación y propaga estado a las mesas
`POST /zonas/{id}/desactivar` rechaza si hay mesas `ocupada` o `reservada`; si no, la zona pasa a `inactiva` y sus mesas `libre`/`por_limpiar` pasan a `inactiva` (consistente con el diagrama de estados de la reference-spec). `POST /zonas/{id}/activar` devuelve a `libre` las mesas que la zona había inactivado.

## Risks / Trade-offs

- **[Columnas sin FK a comandas/reservas]** → Se añadirán FKs con §21/§28 vía migración; mientras tanto la integridad se cuida en el service (D-mz-2).
- **[Auth placeholder no bloquea de verdad]** → REG-20-08 Nivel 2 y `usuario_id` son contrato hasta auth real; el contrato (dependencia + motivo + audit) ya está. Documentado (D-mz-4, D-mz-10).
- **[Agrupar solo desde `libre`]** → Más estricto que algunos flujos de traslado (que admiten `por_limpiar`); si operación lo requiere, se relaja vía decisión D-XX (D-mz-5).
- **[`audit_logs` crece sin retención]** → En MVP sin política de retención; aceptable. Retención/rotación se define en operación/§30 más adelante.
- **[Transiciones automáticas REG-20-10/11/13 ausentes]** → Dependen de §21/§28; quedan como contrato. No se simulan para no inventar alcance.

## Migration Plan

1. Backend: modelos `Zona/Mesa/GrupoMesas` + `AuditLog`; enums a snake_case; `alembic revision` → `0002_mesas_zonas_audit` (tablas `zonas`, `mesas`, `grupos_mesas`, `audit_logs`); `upgrade head` (PG en compose; sqlite en tests).
2. Backend: `schemas.py` (create/update/read + `GrupoMesasRead.mesas_ids` derivado + acciones), `service.py` (transición central + reglas + grupos + auditoría), `shared/audit.py`, `events.py` (payloads + broadcast incl. `grupo.actualizado`), `api.py` (endpoints con `X-Request-Id`).
3. Frontend: `modules/mesas/{api,ws,types}.ts` (+ mapeo de etiquetas), hooks, componentes (incl. indicador de grupo y UI mínima unir/separar), vistas Mesero/Admin.
4. Tests backend + frontend; `ruff`/`eslint` verdes; `docker compose up --build` levanta los 4 servicios y los endpoints/canal responden.

Rollback: la migración `0002` tiene `downgrade` que elimina las tablas; el módulo vuelve a placeholder revirtiendo los archivos. Sin datos productivos.

## Open Questions

Ninguna pendiente. Cierres:
- **PEND-mz-1** (grupo y comanda) → cerrada por **D-mz-5**: en §20 el grupo es agrupación lógica/física sin comanda; el acoplamiento es de §21.
- **PEND-mz-2** (`usuario_id`) → cerrada por **D-mz-10**: opcional (`null`) hasta auth real; obligatorio después.
- **PEND-mz-3** (QR) → cerrada por **D-mz-6**: URL/payload con el `id` permanente; sin imagen/impresión (eso es §32).

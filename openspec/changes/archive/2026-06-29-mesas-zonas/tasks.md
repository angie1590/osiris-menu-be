## 1. Backend · modelos, enums y migración

- [x] 1.1 Cambiar los enums a valores técnicos snake_case (D-mz-8): `EstadoZona` (`activa`, `en_cierre`, `inactiva`), `EstadoMesa` (`libre`, `reservada`, `ocupada`, `por_limpiar`, `inactiva`)
- [x] 1.2 `modules/mesas/models.py`: `Zona`, `Mesa`, `GrupoMesas`. `Mesa.grupo_id` es la fuente de verdad; `GrupoMesas` NO tiene `mesas_ids`. `comanda_activa_id`/`reserva_activa_id`/`GrupoMesas.comanda_id` como `UUID?` sin FK dura (D-mz-2). `Mesa.activa` para baja lógica; `Mesa.id` UUID generado por backend (D-mz-6)
- [x] 1.3 `shared/audit.py` + modelo/tabla `audit_logs` (`id`, `event_type`, `entity_type`, `entity_id`, `user_id?`, `reason?`, `payload` jsonb, `created_at`) y helper `registrar_audit(...)` (D-mz-9)
- [x] 1.4 Generar migración `0002_mesas_zonas_audit` (tablas `zonas`, `mesas`, `grupos_mesas`, `audit_logs`); verificar `alembic upgrade head` / `downgrade`

## 2. Backend · schemas

- [x] 2.1 `modules/mesas/schemas.py`: Zona (create/update/read), Mesa (create/update/read, filtros `zona_id`/`estado`). `MesaCreate` NO acepta `id` (lo genera el backend, D-mz-6)
- [x] 2.2 `GrupoMesasCreate` (lista de ≥2 `mesas_ids` de entrada), `GrupoMesasRead` con `mesas_ids` **derivado** de `Mesa.grupo_id` (D-mz-5); `CerrarZonaRequest` (motivo obligatorio); schema de respuesta de QR
- [x] 2.3 Enums expuestos con valores técnicos; documentar el mapeo a etiquetas canónicas (la UI lo aplica)

## 3. Backend · service (reglas REG-20-XX)

- [x] 3.1 `transicionar_mesa(...)` central: REG-20-01 (Ocupada solo desde Libre/Reservada), REG-20-07 (zona Inactiva sin Ocupada/Reservada), REG-20-09 (zona En cierre sin nuevas ocupaciones/reservas); emite evento + audit (D-mz-1)
- [x] 3.2 REG-20-02: guard de `comanda_activa_id` (no ocupar mesa con comanda activa)
- [x] 3.3 Operación de servicio `reservar_mesa` (seam §28) testeable; rechaza en zona `inactiva`/`en_cierre`
- [x] 3.4 REG-20-08 `cerrar_zona` (Nivel 2 placeholder + motivo, log); `activar_zona` (Inactiva→Activa, devuelve mesas a `libre`); `desactivar_zona` (rechaza si hay Ocupada/Reservada; si no, zona→`inactiva` y mesas `libre`/`por_limpiar`→`inactiva`, D-mz-11)
- [x] 3.5 REG-20-12 baja lógica de mesa (`activa=false`, id permanente); QR (`generar_qr`) codifica el `id` permanente, sin imagen (D-mz-6)
- [x] 3.6 REG-20-14 `marcar_libre` (Por limpiar→Libre, cualquier operador; rechaza si no está en `por_limpiar`); `saltar_estado_por_limpiar` NO se usa en §20 (D-mz-3)
- [x] 3.7 Grupos — crear (`crear_grupo`): ≥2 mesas, todas `libre`, no `inactiva`, no agrupadas; fija `grupo_id`, emite `grupo.creado`, audita; sin comanda (D-mz-5)
- [x] 3.8 Grupos — modificar (`modificar_grupo`): agrega/quita mesas con mismas reglas, no dejar <2 mesas, emite `grupo.actualizado`, audita
- [x] 3.9 Grupos — disolver (`disolver_grupo`): solo grupo activo, setea `dissolved_at`, limpia `grupo_id` de las mesas, emite `grupo.disuelto`, audita; no elimina físicamente (D-mz-5)
- [x] 3.10 `current_operator` placeholder → `usuario_id` opcional (`null`) en eventos y audit (D-mz-10)

## 4. Backend · API REST

- [x] 4.1 Zonas: `GET/POST /zonas`, `PATCH /zonas/{id}`, `POST /zonas/{id}/{cerrar,activar,desactivar}`
- [x] 4.2 Mesas: `GET/POST /mesas`, `GET/PATCH/DELETE /mesas/{id}`, `POST /mesas/{id}/marcar-libre`, `POST /mesas/{id}/qr` (filtros `zona_id`/`estado`)
- [x] 4.3 Grupos: `POST /grupos`, `PATCH /grupos/{id}`, `POST /grupos/{id}/disolver`
- [x] 4.4 Todos los mutadores con `Depends(idempotency_guard)` (`X-Request-Id`) y envelope de error; reemplazar el router placeholder previo manteniendo `/api/v1`

## 5. Backend · WebSocket y eventos

- [x] 5.1 `modules/mesas/events.py`: payloads tipados (Pydantic) y helpers `emit_mesa_estado_cambiado`, `emit_zona_estado_cambiado`, `emit_grupo_creado`, `emit_grupo_actualizado`, `emit_grupo_disuelto` con `manager.broadcast("mesas", ...)`; incluyen `usuario_id?`, `timestamp` y entidades afectadas (D-mz-7)
- [x] 5.2 Cablear las emisiones desde el service en cada transición/operación de grupo

## 6. Frontend · módulo mesas (datos)

- [x] 6.1 `src/modules/mesas/types.ts`: tipos de Zona/Mesa/GrupoMesas, enums técnicos y **mapeo estado técnico → etiqueta canónica** (D-mz-8)
- [x] 6.2 `src/modules/mesas/api.ts`: funciones sobre el `apiClient` central para zonas/mesas/grupos (incl. cerrar/activar/desactivar/marcar-libre/qr/disolver)
- [x] 6.3 `src/modules/mesas/ws.ts`: suscripción al canal `mesas` y tipos de eventos (incl. `grupo.actualizado`)
- [x] 6.4 `src/modules/mesas/hooks/`: hooks TanStack Query (`useZonas`, `useMesas`, `useCrearZona`, `useCerrarZona`, `useMarcarLibre`, `useCrearGrupo`, `useDisolverGrupo`, ...) con invalidación tras mutaciones

## 7. Frontend · componentes y vistas

- [x] 7.1 Componentes: `MesaEstadoBadge`, `ZonaEstadoBadge` (etiqueta canónica), `MesaCard` (con **indicador de grupo** si `grupo_id`), `ZonaLayout`
- [x] 7.2 Formularios `ZonaForm` y `MesaForm` con React Hook Form + Zod (validación de UX)
- [x] 7.3 Vista **Mesero** (`views/mesero/`): mesas agrupadas por zona; loading/empty/error
- [x] 7.4 Vista **Admin** (`views/admin/`): administrar zonas/mesas + UI mínima de unir/separar (llama API, muestra errores del backend, sin decidir reglas); loading/empty/error

## 8. Tests backend

- [x] 8.1 Crear zona; crear mesa; mesa inicia en `libre`
- [x] 8.2 REG-20-01: Ocupada solo desde Libre/Reservada (acepta desde Libre, rechaza desde Por limpiar)
- [x] 8.3 `POST /mesas` no acepta `id` del cliente (lo ignora/rechaza); baja lógica conserva id; id no reutilizable (REG-20-12)
- [x] 8.4 REG-20-07: zona Inactiva no admite mesa Ocupada ni Reservada
- [x] 8.5 Reservada: rechazo en zona Inactiva; rechazo en zona En cierre
- [x] 8.6 REG-20-08: Activa→En cierre requiere Nivel 2 + motivo (rechazo sin motivo)
- [x] 8.7 Desactivar zona: rechazo con mesa Ocupada; rechazo con mesa Reservada; sin ellas → zona Inactiva y mesas `libre`/`por_limpiar` → `inactiva`
- [x] 8.8 REG-20-14: Por limpiar→Libre permitido para operador autenticado; rechazo si la mesa no está en `por_limpiar`
- [x] 8.9 Grupos: crear con 2 mesas válidas; rechazo con 1 mesa; rechazo con mesa Inactiva; rechazo con mesa ya agrupada (REG-20-03)
- [x] 8.10 Grupos: disolver limpia `grupo_id` de las mesas, setea `dissolved_at`, emite `grupo.disuelto`, registra audit log; rechazo si ya disuelto
- [x] 8.11 `GrupoMesasRead.mesas_ids` se deriva correctamente desde `Mesa.grupo_id`
- [x] 8.12 QR/payload usa el `mesa.id` permanente y no crea identificador nuevo
- [x] 8.13 Auditoría: cambio de estado de mesa, cambio de estado de zona, creación de grupo, disolución de grupo, generación de QR y baja lógica de mesa registran fila en `audit_logs` (con `user_id` `null` si no hay operador)
- [x] 8.14 Endpoints mutadores procesan `X-Request-Id` (duplicado → `409 IDEMPOTENCY_KEY_REUSED`)
- [x] 8.15 Evento WS se genera al cambiar estado de mesa/zona (broadcaster testeable verifica payload)

## 9. Tests frontend

- [x] 9.1 Renderizar `ZonaLayout` con zonas/mesas
- [x] 9.2 `MesaCard` muestra el estado correcto (etiqueta canónica) y el indicador de grupo cuando hay `grupo_id`
- [x] 9.3 Estados loading/empty/error en la vista
- [x] 9.4 `ZonaForm` valida con Zod (rechaza inválido)
- [x] 9.5 `MesaForm` valida con Zod (rechaza inválido)
- [x] 9.6 Hooks llaman al cliente API del módulo (mock de `apiClient`)
- [x] 9.7 UI de unir/separar: la vista llama a la API y muestra el error del backend, sin decidir la regla localmente
- [x] 9.8 La vista no contiene reglas de negocio complejas duplicadas (consume contrato del backend)

## 10. Verificación y calidad

- [x] 10.1 Backend: `pytest` verde; `ruff check` + `ruff format --check` verdes
- [x] 10.2 Frontend: `npm run lint`, `npm run test`, `npm run build` verdes
- [x] 10.3 `docker compose up --build` levanta los 4 servicios; `/api/v1/zonas`, `/api/v1/mesas`, grupos y `/ws/mesas` responden
- [x] 10.4 Confirmar criterios: §20 E2E, sin reglas duplicadas en frontend, terminología canónica en UI / valores técnicos en API, sin ampliar alcance a §21/§22/§23/§24/§25/§26/§28/§31/§32 más allá de contratos; sin preguntas abiertas (PEND-mz-1..3 cerradas por D-mz-5/10/6)

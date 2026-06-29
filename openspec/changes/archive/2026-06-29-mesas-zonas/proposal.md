## Why

El scaffolding inicial ya está aplicado, verificado y archivado (`backend-foundation`, `frontend-foundation`, `realtime-foundation`, `mvp-modules-scaffolding`, `workspace-orchestration`). §20 Mesas y zonas es el **módulo fundacional** del MVP: las comandas se abren sobre mesas, los meseros operan sobre mesas y las reservas se asignan a mesas. Construirlo de punta a punta primero desbloquea §21 Comandas y §22 Cocina/barra sobre un contrato real.

Esta propuesta convierte el placeholder de `modules/mesas` en el **primer vertical funcional** (backend + frontend + WebSocket + auditoría), implementando las reglas críticas de `openspec/reference-specs/20-mesas.md` y dejando como contrato/placeholder explícito todo lo que depende de §21 Comandas y §28 Reservas (aún no implementados).

## What Changes

- **Modelos backend**: `Zona`, `Mesa`, `GrupoMesas` (SQLAlchemy 2 async) + migración Alembic. **`Mesa.grupo_id` es la única fuente de verdad** de la pertenencia a grupo; `GrupoMesas` NO persiste `mesas_ids` (se deriva en los read models). El `id` de mesa lo genera el backend y es permanente (baja lógica, nunca se reutiliza).
- **Enums con valores técnicos en API/DB** (`activa`, `en_cierre`, `inactiva`, `libre`, `reservada`, `ocupada`, `por_limpiar`) y **etiquetas canónicas del glosario en la UI** vía mapeo.
- **Service layer §20** con las reglas REG-20-XX implementables sin §21/§28: transición de mesa (REG-20-01), una sola comanda activa (REG-20-02), zona Inactiva sin Ocupada/Reservada (REG-20-07), Activa→En cierre Nivel 2 + motivo (REG-20-08), zona En cierre rechaza nuevas ocupaciones/reservas (REG-20-09), desactivar zona con validación y propagación a mesas, identificador permanente + baja lógica (REG-20-12), Por limpiar→Libre por cualquier operador (REG-20-14), y transición a Reservada como operación de servicio (seam §28).
- **Unir/separar mesas**: unir = crear `GrupoMesas`; separar = disolver `GrupoMesas`. Reglas explícitas de creación (≥2 mesas, todas `libre`, no `inactiva`, no agrupadas), de modificación (`PATCH`, no dejar <2 mesas), y de disolución. Agrupación lógica/física, **sin comanda real** (la comanda compartida es de §21).
- **Endpoints REST** bajo `/api/v1` para zonas, mesas y grupos —incluido `POST /grupos/{id}/disolver`—, todos los mutadores con `X-Request-Id` y errores estructurados.
- **Eventos WebSocket** del canal `mesas` (`/ws/mesas`): `mesa.estado_cambiado`, `zona.estado_cambiado`, `grupo.creado`, `grupo.actualizado`, `grupo.disuelto`, con payload tipado y `usuario_id?`.
- **Auditoría persistente**: tabla `audit_logs` + `shared/audit.py`, registrando cambio de estado de mesa/zona, creación y disolución de grupo, generación de QR y baja lógica de mesa. `usuario_id` opcional (`null`) hasta auth real.
- **QR**: `POST /mesas/{id}/qr` devuelve URL/payload con el `id` permanente; sin imagen ni impresión física (eso es §32).
- **Frontend `modules/mesas`**: `api.ts`, `ws.ts`, `types.ts`, hooks TanStack Query, componentes (`MesaCard` con indicador de grupo, `ZonaLayout`, badges, forms) y vistas Mesero/Admin (con UI mínima de unir/separar). Sin reglas de negocio duplicadas.
- **Tests**: backend (reglas REG-20-XX, grupos, disolución, auditoría, idempotencia, eventos WS, derivación de `mesas_ids`, id no aceptado del cliente, escenarios Reservada/desactivar) y frontend (render, indicador de grupo, estados, validación Zod, hooks, no-duplicación de reglas).
- **Graduación de scaffolding**: `modules/mesas` deja de ser placeholder; la requirement de "routers placeholder sin reglas" de `mvp-modules-scaffolding` se acota a `comandas`/`cocina_barra`, y la de terminología admite valores técnicos en API/DB para módulos implementados.
- **Identificadores**: se usan `REG-20-XX` canónicos (la reference-spec ya los usa). Sin cambios de significado.

## Capabilities

### New Capabilities
- `mesas-zonas`: gestión completa de zonas, mesas y grupos (§20): entidades (con `Mesa.grupo_id` como fuente de verdad), enums técnicos/UI, reglas REG-20-XX implementables sin §21/§28, unir/separar grupos, endpoints REST (incl. disolver), eventos WebSocket del canal `mesas`, auditoría persistente, y el módulo frontend con vistas Mesero/Admin.

### Modified Capabilities
- `mvp-modules-scaffolding`: la requirement de routers placeholder se acota a `comandas`/`cocina_barra` (§20 queda implementado por `mesas-zonas`); la requirement de terminología canónica admite valores técnicos snake_case en API/DB mapeados a etiquetas del glosario en UI para módulos implementados.

## Impact

- **Backend nuevo/cambiado**: `src/osiris/modules/mesas/{models,schemas,service,api,events}.py` (de placeholder a funcional), `src/osiris/shared/audit.py` (nuevo), migración Alembic `0002_mesas_zonas_audit` (tablas `zonas`, `mesas`, `grupos_mesas`, `audit_logs`), router de mesas ya montado bajo `/api/v1`.
- **Frontend nuevo/cambiado**: `osiris-menu-fe/src/modules/mesas/**` (api/ws/types/hooks/components), vistas `views/mesero/` y `views/admin/`, componentes reutilizables nuevos en `src/components/`, mapeo estado técnico → etiqueta canónica.
- **Contratos preparados (no implementados)**: §21 Comandas (apertura/cierre, `comanda_activa_id`, comanda compartida del grupo) y §28 Reservas (`reserva_activa_id`, verificación, no-show) quedan como columnas + operaciones de servicio + placeholders documentados.
- **Dependencias externas**: ninguna nueva. Stack y Docker Compose sin cambios estructurales; el compose debe seguir levantando los cuatro servicios.
- **Fuera de alcance**: apertura/cierre real de comanda, reservas completas, QR público completo, facturación, caja, cocina/barra, inventario, catálogo, reportes; y reglas funcionales de §21/§22/§23/§24/§25/§26/§28/§31/§32 más allá de contratos/placeholders explícitos. Auth real ausente: se usa el placeholder `require_nivel`.

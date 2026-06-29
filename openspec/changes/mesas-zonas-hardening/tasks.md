## 1. Backend · validaciones y reactivación

- [x] 1.1 `schemas.py`: `MesaCreate.capacidad`/`MesaUpdate.capacidad` con `Field(ge=1)` (capacidad positiva, REG-20-17); quitar default 0 donde aplique
- [x] 1.2 `service.crear_mesa`: validar `zona.estado == activa` (rechazar `inactiva`/`en_cierre`, `ZONA_NO_ACTIVA`, REG-20-16) y unicidad de `numero_visible` en la zona incluyendo inactivas, **con `trim` y case-insensitive** (`NUMERO_VISIBLE_DUPLICADO`, REG-20-15); guardar el valor `trim`-eado tal cual (sin forzar mayúsculas)
- [x] 1.3 `service.actualizar_mesa`: si cambia `numero_visible` o `zona_id`, aplicar `trim` y revalidar unicidad case-insensitive por zona (REG-20-15)
- [x] 1.4 `service.baja_mesa`: rechazar si `ocupada`/`reservada`/agrupada/`comanda_activa_id` (`MESA_NO_DESACTIVABLE`, REG-20-18); mantener baja lógica; audit `mesa.baja_logica`; emitir `mesa.desactivada`
- [x] 1.5 `service.reactivar_mesa` (nuevo): requiere `activa == false` y zona `activa` (rechazar zona `inactiva`/`en_cierre`); pasa a `libre`; audit `mesa.reactivada`; emitir `mesa.reactivada` (REG-20-19)
- [x] 1.6 `events.py`: helpers `emit_mesa_desactivada` / `emit_mesa_reactivada` con payload `{ mesa_id, activa, usuario_id?, timestamp }` (eventos **específicos**, NO reutilizar `mesa.estado_cambiado`; D-h5b)

## 2. Backend · API y migración

- [x] 2.1 `api.py`: `POST /mesas/{id}/reactivar` (con `X-Request-Id`, `current_operator`, envelope de error)
- [x] 2.2 Verificar que `DELETE /mesas/{id}` (desactivar) propaga las nuevas validaciones de REG-20-18
- [x] 2.3 `models.py` + migración `0003_mesa_numero_visible_unico`: índice único **funcional** `lower(numero_visible)` por `zona_id` (respalda unicidad case-insensitive, REG-20-15); `alembic upgrade head`/`downgrade`
- [x] 2.4 Nota de datos: si hay duplicados locales previos, la migración del índice único fallará — limpiar/renombrar duplicados locales antes de aplicar; NO relajar la regla por datos de prueba (documentado en design)

## 3. Frontend · componentes shadcn y toasts

- [x] 3.1 Agregar componentes shadcn en `src/components/ui/`: `card`, `badge`, `alert`, `dialog` (Tailwind + cva; dialog sobre `@radix-ui/react-dialog`)
- [x] 3.2 Agregar `sonner` **únicamente como mecanismo de toast** (no autoriza otras librerías UI fuera de Tailwind/shadcn/Radix); montarlo una vez en `main.tsx`; helper para mostrar errores de mutación como toast
- [x] 3.3 Actualizar `package.json`/lock con `@radix-ui/react-dialog` y `sonner` (justificadas en design); `npm ci` sigue funcionando

## 4. Frontend · módulo mesas (datos/UX)

- [x] 4.1 `modules/mesas/api.ts` + `hooks`: `reactivarMesa` / `useReactivarMesa`; `bajaMesa` ya existe → `useDesactivarMesa` con invalidación
- [x] 4.2 Helper `esAgrupable(mesa)` = `estado === "libre" && activa && grupo_id == null` (prevención UX, no regla de negocio; REG-20-20)
- [x] 4.3 `MesaForm`: zod `capacidad` positiva (`>= 1`) y `numero_visible` requerido; `ZonaForm` mantiene validaciones

## 5. Frontend · rediseño vista Admin

- [x] 5.1 Reescribir `views/admin/Admin.tsx` con Card/Badge/Alert/Dialog + Tailwind (sin HTML plano); estados loading/empty/error
- [x] 5.2 Acciones contextuales de zona (REG-20-21): `inactiva` → "Activar"; `activa` → acciones válidas; `en_cierre` → estado + acciones válidas
- [x] 5.3 Formulario "Nueva mesa" sólo en zonas `activa`; mensaje informativo en `inactiva`/`en_cierre`
- [x] 5.4 Acciones de mesa: "Activar" (mesa inactiva + zona activa), **"Desactivar mesa"** (mesa elegible; nunca "Eliminar" aunque el verbo HTTP sea `DELETE`), QR (Dialog "Ver QR"/"Copiar URL", REG-20-22), "Separar grupo" para mesas agrupadas; deshabilitar con explicación cuando no apliquen
- [x] 5.5 Selección para unir sólo sobre mesas agrupables; checkbox deshabilitado/no disponible para el resto; botón "Unir mesas" deshabilitado hasta 2+ válidas con ayuda (REG-20-20)
- [x] 5.6 Errores backend como toast/alert contextual (no banda cruda global)

## 6. Tests backend

- [x] 6.1 Crear dos mesas con mismo `numero_visible` en la misma zona → falla; variantes por espacios/mayúsculas (` J8 `, `j8`) también fallan (trim + case-insensitive); en zonas distintas → ok
- [x] 6.2 Crear mesa en zona `inactiva` → falla; en `en_cierre` → falla
- [x] 6.3 Crear mesa con `capacidad = 0` → falla (422)
- [x] 6.4 Agrupar mesa `inactiva`/`por_limpiar`/`ocupada`/`reservada`/ya agrupada → falla; unir requiere 2+ válidas
- [x] 6.5 Desactivar mesa `ocupada`/`reservada`/agrupada/con `comanda_activa_id` → falla
- [x] 6.6 Desactivar mesa válida → baja lógica + audit log
- [x] 6.7 Reactivar mesa en zona `activa` → `libre`; en zona `inactiva` → falla; en zona `en_cierre` → falla
- [x] 6.8 Reactivar/desactivar registran audit log y emiten `mesa.reactivada`/`mesa.desactivada`; QR usa `mesa.id`; mutadores mantienen `X-Request-Id`; errores con envelope estructurado

## 7. Tests frontend

- [x] 7.1 No permite seleccionar mesas `inactiva`/`por_limpiar`/`ocupada`/`reservada`/agrupadas para unir
- [x] 7.2 Botón "Unir mesas" disabled con <2 válidas; enabled con 2+ libres válidas
- [x] 7.3 Zona `inactiva` muestra "Activar" y no "Desactivar"; `activa`/`en_cierre` muestran acciones válidas
- [x] 7.4 No aparece formulario "Nueva mesa" en zona `inactiva` ni `en_cierre`
- [x] 7.5 Mesa muestra acción QR; mesa `inactiva` (zona activa) muestra "Activar"; mesa agrupada muestra indicador + "Separar grupo"
- [x] 7.6 Errores backend se muestran como toast/alert consistente
- [x] 7.7 `MesaForm` valida `numero_visible` requerido y capacidad positiva; UI sin reglas complejas duplicadas; usa componentes reutilizables (no HTML plano)

## 8. Documentación · riesgos residuales

- [x] 8.1 Crear `openspec/known-risks.md` con pendientes controlados: vistas placeholder (Cocina/Barra §22, Caja §23, Público QR §32); e2e multi-módulo (tras §20+§21+§22); auth real (`usuario_id` placeholder); retención de `audit_logs` (antes de producción); agrupar `por_limpiar` requiere D-XX nueva
- [x] 8.2 Encabezar `known-risks.md` aclarando que **no es fuente normativa** (es backlog/riesgos controlados); las reglas cerradas viven en `decisions.md`/specs y no se implementan desde este archivo. No mezclar riesgos con reglas implementadas

## 9. Verificación y calidad

- [x] 9.1 Backend: `pytest` verde; `ruff check` + `ruff format --check` verdes
- [x] 9.2 Frontend: `npm run lint`, `npm run test`, `npm run build` verdes
- [x] 9.3 `docker compose up --build` levanta los 4 servicios; migración `0003` aplicada; endpoints (incl. `POST /mesas/{id}/reactivar`) y `/ws/mesas` responden
- [x] 9.4 Confirmar criterios: validaciones backend como autoridad, UI previene errores obvios sin duplicar reglas, Admin alineada al stack visual, riesgos residuales registrados, sin ampliar alcance a módulos futuros

## 10. Cierre QA post-apply

QA post-apply de `mesas-zonas-hardening` **cerrado**. Los residuales propios de §20 fueron
corregidos o registrados como pendientes controlados. Los pendientes restantes pertenecen a
futuros verticales o a preparación productiva y **no bloquean avanzar a §21 Comandas**.

Residuales **cerrados con código** en esta ronda:
- [x] 10.1 Frontend tipa explícitamente los eventos WS `mesa.desactivada` y `mesa.reactivada` (union discriminada `MesaWebSocketEvent` en `modules/mesas/ws.ts`, alineada al payload real del backend `{ type, mesa_id, activa, usuario_id?, timestamp? }`; sin campos inventados, sin `any`).
- [x] 10.2 Handler preparado `handleMesaEvent` (+ `useMesasRealtime`, `isMesaWebSocketEvent`) que invalida las queries de §20 (zonas/mesas, prefijo `["mesas"]`) para todos los eventos conocidos sin descartarlos; tests en `modules/mesas/realtime.test.ts`.
- [x] 10.3 Warning de bundle Vite (>500 kB) mitigado con code splitting por ruta (`React.lazy` + `Suspense`); build verde sin warning. Registrado/monitoreado como PEND-FE-PERF-01.

Residuales **registrados como pendientes controlados** (no implementados ahora) en
`openspec/known-risks.md`: PEND-AUTH-01 (auth real), PEND-AUDIT-01 (retención audit_logs),
PEND-E2E-01 (e2e multi-módulo), PEND-VIEW-01 (vistas de otros verticales), PEND-GROUP-01
(agrupar `por_limpiar` requiere D-XX), PEND-FE-PERF-01 (bundle).

NO se implementó en esta ronda: auth real, retención de `audit_logs`, e2e multi-módulo, ni
vistas reales de otros verticales. No se cambiaron reglas de negocio aprobadas.

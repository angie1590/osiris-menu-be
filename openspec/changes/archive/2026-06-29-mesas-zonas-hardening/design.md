## Context

§20 `mesas-zonas` está aplicado y archivado. El backend (`modules/mesas/{models,schemas,service,api,events}.py`, `shared/audit.py`, migración `0002`) implementa las reglas REG-20-01..14, grupos, QR y auditoría. El frontend tiene `modules/mesas` (api/ws/types/hooks/components: `MesaCard`, `ZonaLayout`, badges, `ZonaForm`, `MesaForm`) y la vista Admin, pero la UI es plana (HTML básico) y sólo existe `components/ui/button.tsx` como shadcn.

La validación manual encontró: duplicados de `numero_visible` por zona, selección/agrupación de mesas inválidas prevenida tarde (sólo por backend), acciones de zona/mesa no contextuales (se ofrece "Desactivar" en zonas ya inactivas), formulario "Nueva mesa" visible en zonas no activas, falta de acción QR por mesa, y errores mostrados como banda cruda. El backend ya rechaza correctamente la agrupación de mesas no-`libre`/inactivas/agrupadas (`_validar_mesa_agrupable`), así que el grueso del trabajo de grupos es **UX**, no backend.

## Goals / Non-Goals

**Goals:**
- Cerrar validaciones backend faltantes: unicidad de `numero_visible` por zona, crear mesa sólo en zona `activa`, capacidad positiva, desactivar mesa con validaciones, reactivar mesa.
- Rediseñar la vista Admin con shadcn/ui sobre Radix + Tailwind 4: cards, badges, alerts, dialog; acciones contextuales; selección válida para unir; acción QR por mesa; errores consistentes.
- Tests backend y frontend para las correcciones; Docker/lint/tests/build verdes.
- Registrar riesgos residuales del QA como pendientes controlados en `openspec/known-risks.md`.

**Non-Goals:**
- §21/§22/§23/§24/§25/§26/§28/§31/§32; vistas `barra`/`cocina`/`caja`/`publico` (siguen placeholders).
- Auth real, retención de `audit_logs`, e2e multi-módulo, rediseño global de la app.
- Permitir agrupar mesas `por_limpiar` (se mantiene la decisión conservadora: sólo `libre`).

## Decisions

### D-h1 · `numero_visible` único por zona (case-insensitive, trim), incluyendo inactivas
Chequeo previo en `crear_mesa`/`actualizar_mesa` que lanza `DomainError` estructurado (`code` `NUMERO_VISIBLE_DUPLICADO`, 409) para un mensaje claro, respaldado por un constraint en DB (migración `0003`). Se incluyen las mesas inactivas porque conservan el registro (baja lógica) y el QR sigue apuntando a su `id`: reutilizar el número generaría ambigüedad histórica y de auditoría. Se permite el mismo número en zonas distintas (la zona desambigua).

**Normalización (item de QA):** el backend hace `trim` de `numero_visible` antes de validar y guardar, y la unicidad por zona es **case-insensitive** (`J8`, `j8`, ` J8 ` colisionan). Implementación: el servicio compara contra `func.lower(trim(numero_visible))`; el constraint de DB se crea sobre una expresión `lower(numero_visible)` por `zona_id` (índice único funcional) para respaldar la regla case-insensitive. Se guarda el valor ya `trim`-eado tal cual lo escribió el operador (sin forzar mayúsculas/minúsculas), preservando la presentación.
- Decisión: **case-insensitive** para evitar duplicados visuales; si en el futuro se quisiera case-sensitive, requeriría una decisión explícita y justificada.
- Alternativa descartada: unicidad sólo entre mesas activas — permitiría re-crear un número "liberado" por baja y chocar con QR/auditoría previos.
- Alternativa descartada: unicidad global (todas las zonas) — innecesariamente restrictiva; el negocio numera por zona.

### D-h2 · Crear mesa sólo en zona `activa`
`crear_mesa` valida `zona.estado == activa`; `inactiva`/`en_cierre` → `DomainError` (`ZONA_NO_ACTIVA`, 409). La UI no muestra el formulario "Nueva mesa" fuera de zonas activas (prevención UX), pero el backend es la autoridad.

### D-h3 · Capacidad positiva (`>= 1`)
`MesaCreate.capacidad` y `MesaUpdate.capacidad` con `Field(ge=1)`; el zod de `MesaForm` exige `>= 1`. Default deja de ser `0`.
- Razón: una mesa con capacidad 0 no es operativa; evita datos sin sentido.

### D-h4 · Desactivar mesa = baja lógica validada; `DELETE /mesas/{id}` la implementa; UI dice "Desactivar"
Se endurece `baja_mesa`: rechaza si `ocupada`, `reservada`, `grupo_id` no nulo o `comanda_activa_id` no nulo (`MESA_NO_DESACTIVABLE`, 409). Mantiene `activa=false` (no delete físico), audita (`mesa.baja_logica`) y emite el evento específico `mesa.desactivada`. `DELETE /mesas/{id}` sigue siendo el verbo HTTP (alineado con la reference-spec), pero **la UI y todos los textos la llaman siempre "Desactivar mesa", nunca "Eliminar"**: el registro y `mesa.id` se conservan.

### D-h5 · Reactivar mesa: nueva operación + `POST /mesas/{id}/reactivar`
`reactivar_mesa`: requiere `mesa.activa == false`; si la zona no está `activa` (es decir `inactiva` o `en_cierre`) → `DomainError` (`ZONA_NO_ACTIVA`). Pone `activa=true` y transiciona a `libre`. Audita `mesa.reactivada` y emite el evento específico `mesa.reactivada`.

### D-h5b · Eventos WS específicos para activa/desactiva (cierra ambigüedad de eventos)
Decisión cerrada: desactivar/reactivar emiten eventos **específicos** `mesa.desactivada` y `mesa.reactivada`, **no** se reutiliza `mesa.estado_cambiado`. Razón: `activa=false/true` es un cambio de baja lógica, distinto del ciclo de estado operativo (`libre`/`ocupada`/...). Payload mínimo de ambos: `{ mesa_id, activa, usuario_id?, timestamp }`. Se agregan los helpers `emit_mesa_desactivada` / `emit_mesa_reactivada` en `events.py`.

### D-h6 · QR ya correcto; se expone en UI
El backend ya devuelve `{mesa_id, url=/qr/{mesa.id}}` sin crear identificador nuevo. No cambia el backend del QR. La UI añade una acción por mesa (Dialog "Ver QR" + "Copiar URL") que consume `POST /mesas/{id}/qr`. La imagen/impresión sigue fuera de alcance (§32).

### D-h7 · Stack visual: shadcn/ui sobre Radix + Tailwind; nuevas dependencias acotadas
Se agregan componentes shadcn mínimos en `src/components/ui/`: `card`, `badge`, `alert`, `dialog`. `card`/`badge`/`alert` son Tailwind + `cva` (sin Radix nuevo). `dialog` usa `@radix-ui/react-dialog` (nueva dep, justificada para el modal de QR y confirmaciones). Para toasts se agrega **`sonner`** (ligero, del ecosistema shadcn) montado una vez en `main.tsx`; los errores de mutación se muestran como toast, y los de carga como `Alert` contextual.
- Alternativa descartada: construir un toaster propio — reinventar; `sonner` es el estándar shadcn.
- Justificación de deps nuevas (CLAUDE.md exige justificar): `@radix-ui/react-dialog` (accesibilidad del modal QR/confirmaciones) y `sonner` (toasts consistentes). Ambas dentro del stack visual aprobado (shadcn/Radix).
- **Alcance de `sonner`**: se acepta **únicamente** como mecanismo de toast del frontend. NO autoriza introducir otras librerías de UI fuera de Tailwind/shadcn/Radix; cualquier componente visual adicional debe seguir siendo shadcn/Radix + Tailwind.

### D-h8 · Prevención UX sin duplicar reglas; backend como autoridad
La UI deriva "agrupable" de los flags del backend (`estado === "libre" && activa && grupo_id == null`) sólo para habilitar/deshabilitar el checkbox y el botón "Unir"; no reimplementa la lógica de transición ni de auditoría. Si por carrera el backend rechaza, se muestra el toast con el mensaje del envelope. Las acciones de zona/mesa se renderizan según `estado` (contextual). Esto satisface REG-20-20/21/22 sin violar "no duplicar reglas de negocio".

### D-h9 · Riesgos residuales en `openspec/known-risks.md`
No existe archivo de riesgos. Se crea `openspec/known-risks.md` con los pendientes controlados (vistas placeholder de otros verticales, e2e multi-módulo, auth real, retención de `audit_logs`, agrupar `por_limpiar` como futura D-XX). Es documentación de seguimiento, **no** tareas de esta corrección, y no se mezcla con reglas implementadas.

**`known-risks.md` NO es fuente normativa.** Es backlog/riesgos controlados. Las reglas cerradas siguen viviendo en `openspec/decisions.md` y en los specs (`openspec/specs/`); `known-risks.md` no debe usarse para implementar reglas de negocio ni para justificar comportamiento. Un riesgo que se decida resolver pasa por una propuesta/decisión formal, no por editar este archivo.

## Risks / Trade-offs

- **[Constraint de unicidad sobre datos previos]** → En desarrollo sin datos productivos; si hubiera duplicados previos, la migración fallaría. Mitigación: entorno limpio; documentar que producción requeriría des-duplicar antes.
- **[Nuevas dependencias FE]** → `@radix-ui/react-dialog` y `sonner` aumentan el bundle; aceptable y dentro del stack shadcn/Radix aprobado. Se actualiza `package-lock.json` para que `npm ci` del Dockerfile siga funcionando.
- **[UI deriva "agrupable" de flags]** → Riesgo de divergir de la regla del backend si ésta cambia. Mitigación: la UI sólo previene; el backend valida siempre y su error se muestra. Un cambio de regla de negocio se reflejará primero en backend.
- **[Reactivar usa `transicionar_mesa(LIBRE)`]** → `transicionar_mesa` no valida zona para destino `libre`; la validación de zona activa se hace en `reactivar_mesa` antes de transicionar. Cubierto por tests.

## Migration Plan

1. Backend: schemas (`capacidad ge=1`), `service` (unicidad case-insensitive + trim, crear-en-activa, baja validada, `reactivar_mesa`), `api` (`POST /mesas/{id}/reactivar`), `events` (`mesa.desactivada`/`mesa.reactivada`), migración `0003_mesa_numero_visible_unico` (índice único funcional `lower(numero_visible)` por `zona_id`). `alembic upgrade head` / `downgrade`.

**Datos duplicados previos:** si existen mesas con `numero_visible` duplicado por zona en una base local, la migración del índice único **fallará al aplicarse**. La solución es **limpiar/renombrar los duplicados locales antes** de aplicar la migración; NO se relaja la regla por datos de prueba. En este entorno de desarrollo no hay datos productivos; en producción se des-duplicaría primero.
2. Frontend: componentes shadcn (`card`, `badge`, `alert`, `dialog`) + `sonner` en `main.tsx`; rediseño de `views/admin/Admin.tsx`; hooks `useReactivarMesa`, `useBajaMesa`/`useDesactivarMesa`; helper `esAgrupable(mesa)`; acción QR (Dialog).
3. Docs: crear `openspec/known-risks.md`.
4. Verificación: `pytest`+`ruff` (backend), `eslint`+`vitest`+`build` (frontend), `docker compose up --build` (migración aplicada, endpoints + `/ws/mesas`).

Rollback: la migración `0003` tiene `downgrade` (drop del UniqueConstraint); el resto se revierte por archivos. Sin datos productivos.

## Open Questions

Ninguna bloqueante. Decisiones tomadas: unicidad incluye inactivas y es **case-insensitive + trim** (D-h1), capacidad `>= 1` (D-h3), `DELETE` = desactivar (UI nunca "Eliminar") + `POST /reactivar` (D-h4/D-h5), eventos **específicos** `mesa.desactivada`/`mesa.reactivada` (D-h5b), `sonner` sólo como toaster + `@radix-ui/react-dialog` como deps del stack visual (D-h7), `known-risks.md` no normativo (D-h9). Permitir agrupar `por_limpiar` queda registrado en `known-risks.md` como futura decisión D-XX (no se implementa).

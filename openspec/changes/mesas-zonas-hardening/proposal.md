## Why

El vertical §20 `mesas-zonas` ya está aplicado y pasó QA técnico, pero la validación manual de la vista Admin reveló reglas incompletas, fallos de usabilidad e inconsistencia visual. Antes de avanzar a §21 Comandas hay que endurecer §20: cerrar validaciones backend faltantes, prevenir errores obvios en la UI, rediseñar la vista Admin alineada al stack visual (Tailwind 4 + shadcn/ui + Radix) y registrar los riesgos residuales del QA como pendientes controlados.

Esta propuesta **corrige §20** sin ampliar alcance a otros módulos.

## What Changes

**Backend (validaciones faltantes, fuente de verdad):**
- `numero_visible` **único por zona** (incluye mesas inactivas; se permite repetir el número en zonas distintas). Constraint en DB + chequeo de servicio con error estructurado.
- Crear mesa **solo en zona `activa`**; rechazar en `inactiva` y `en_cierre`.
- **Capacidad positiva** (`capacidad ≥ 1`).
- **Desactivar mesa** (baja lógica) sólo si no está `ocupada`, `reservada`, agrupada ni con `comanda_activa_id`; mantiene el registro y el `id`.
- **Reactivar mesa**: nueva operación/endpoint — una mesa `inactiva` se reactiva sólo si su zona está `activa`, pasando a `libre`.
- Mantener: agrupación solo de mesas `libre`/activas/no agrupadas (ya implementado), QR por `mesa.id`, `X-Request-Id`, envelope de error, audit logs (se suman desactivar/reactivar mesa).

**Frontend (UX/UI de Admin Mesas y zonas):**
- Rediseño de la vista Admin con componentes shadcn/ui sobre Radix (Card, Badge, Alert, Dialog) y Tailwind 4; sin layout plano HTML básico.
- **Acciones contextuales de zona**: `inactiva` → "Activar" (no "Desactivar"); `activa` → acciones válidas; `en_cierre` → estado claro + acciones válidas.
- **Acciones de mesa** claras: Activar / Desactivar / QR / Separar grupo, según estado y reglas (deshabilitadas con explicación cuando no aplican).
- Formulario "Nueva mesa" sólo en zonas `activa`; en `inactiva`/`en_cierre` mensaje informativo.
- **Selección para unir** sólo sobre mesas válidas (`libre`, activas, no agrupadas); las demás no seleccionables/deshabilitadas; botón "Unir mesas" deshabilitado hasta 2+ válidas con ayuda clara.
- **QR por mesa**: acción visible (Ver QR / Copiar URL) usando `mesa.id`; sin imagen ni impresión (eso es §32).
- Errores backend mostrados de forma consistente (toast/alert contextual), no banda cruda global.
- Validación de formularios con React Hook Form + Zod (numero_visible requerido, capacidad positiva).

**OpenSpec / documentación:**
- Specs de §20 (`mesas-zonas`) actualizadas con las reglas nuevas (REG-20-15…REG-20-22) y la requirement de frontend ampliada.
- Nuevo `openspec/known-risks.md` con los riesgos residuales del QA como **pendientes controlados** (no tareas de esta corrección).

## Capabilities

### New Capabilities
<!-- Ninguna: es hardening de la capability existente. -->

### Modified Capabilities
- `mesas-zonas`: se añaden reglas de unicidad de `numero_visible`, creación de mesa restringida a zona `activa`, capacidad positiva, desactivación/reactivación de mesa con validaciones, y se amplía la requirement de frontend (acciones contextuales, selección válida, QR por mesa, alineación con el stack visual, errores consistentes).

## Impact

- **Backend cambiado**: `modules/mesas/{service,schemas,api}.py` (validaciones + reactivar), migración `0003_mesa_numero_visible_unico` (constraint `(zona_id, numero_visible)`), tests nuevos.
- **Frontend cambiado**: `views/admin/Admin.tsx` (rediseño), nuevos componentes shadcn en `src/components/ui/` (Card, Badge, Alert, Dialog) y de módulo (acciones de mesa, diálogo QR, lógica de selección válida), hooks (`useReactivarMesa`, `useDesactivarMesa`/`useBajaMesa`), tests nuevos. Posibles dependencias nuevas: `@radix-ui/react-dialog` y un mecanismo de toast (`sonner`), justificadas en design.
- **Sin ampliar alcance**: no se tocan §21/§22/§23/§24/§25/§26/§28/§31/§32; las vistas `barra`/`cocina`/`caja`/`publico` siguen placeholders (registradas como pendientes). Auth real, retención de audit logs y e2e multi-módulo quedan como pendientes controlados en `known-risks.md`.
- **Compatibilidad**: el constraint de unicidad puede fallar si ya existen duplicados en datos previos; al ser entorno de desarrollo sin datos productivos, no hay migración de datos. Documentado en design.

## ADDED Requirements

### Requirement: REG-20-15 numero_visible único por zona

Dentro de una misma `Zona`, `numero_visible` MUST ser único entre **todas** las mesas, incluidas las `inactiva` (baja lógica), para evitar ambigüedad operativa, de auditoría y de QR. El mismo `numero_visible` MAY repetirse en zonas distintas (la zona desambigua). El backend MUST normalizar `numero_visible` con `trim` (sin espacios al inicio/fin) antes de validar y guardar, y la unicidad por zona MUST ser **case-insensitive**, de modo que variantes como `J8`, `j8` y ` J8 ` se consideren la misma. La unicidad MUST garantizarse en el service con error de dominio estructurado y respaldarse con un constraint en base de datos.

#### Scenario: Duplicado en la misma zona se rechaza

- **WHEN** se crea una mesa con un `numero_visible` ya usado por otra mesa (activa o inactiva) de la misma zona
- **THEN** el backend rechaza con error de dominio (no se crea la mesa)

#### Scenario: Duplicado por espacios o mayúsculas se rechaza

- **WHEN** existe la mesa `J8` y se crea otra con ` J8 ` o `j8` en la misma zona
- **THEN** el backend normaliza (`trim`, case-insensitive) y rechaza por duplicado

#### Scenario: Mismo número en zonas distintas se permite

- **WHEN** se crea una mesa con un `numero_visible` que existe en otra zona
- **THEN** la operación se acepta

### Requirement: REG-20-16 creación de mesa solo en zona activa

Una `Mesa` MUST poder crearse únicamente en una `Zona` en estado `activa`. Crear una mesa en una zona `inactiva` o `en_cierre` MUST rechazarse con error de dominio.

#### Scenario: Crear mesa en zona inactiva se rechaza

- **WHEN** se intenta crear una mesa en una zona `inactiva`
- **THEN** el backend rechaza con error de dominio

#### Scenario: Crear mesa en zona en_cierre se rechaza

- **WHEN** se intenta crear una mesa en una zona `en_cierre`
- **THEN** el backend rechaza con error de dominio

### Requirement: REG-20-17 capacidad de mesa positiva

La `capacidad` de una `Mesa` MUST ser un entero positivo (`>= 1`). Crear o actualizar una mesa con capacidad `0` o negativa MUST rechazarse en validación.

#### Scenario: Capacidad cero se rechaza

- **WHEN** se intenta crear una mesa con `capacidad = 0`
- **THEN** la validación rechaza la operación

### Requirement: REG-20-18 desactivación de mesa con validaciones

Desactivar una `Mesa` (baja lógica, `activa = false`) MUST rechazarse si la mesa está `ocupada`, `reservada`, agrupada (`grupo_id` no nulo) o tiene `comanda_activa_id`. La desactivación MUST conservar el registro y el `id` (no delete físico), registrar audit log y emitir el evento `mesa.desactivada`. Es **baja lógica**, no eliminación: la UI y los textos MUST llamarla siempre "Desactivar mesa", nunca "Eliminar".

#### Scenario: Desactivar mesa ocupada se rechaza

- **WHEN** se intenta desactivar una mesa `ocupada`
- **THEN** el backend rechaza con error de dominio

#### Scenario: Desactivar mesa reservada se rechaza

- **WHEN** se intenta desactivar una mesa `reservada`
- **THEN** el backend rechaza con error de dominio

#### Scenario: Desactivar mesa con comanda activa se rechaza

- **WHEN** se intenta desactivar una mesa con `comanda_activa_id` no nulo
- **THEN** el backend rechaza con error de dominio

#### Scenario: Desactivar mesa agrupada se rechaza

- **WHEN** se intenta desactivar una mesa con `grupo_id` no nulo
- **THEN** el backend rechaza con error de dominio

#### Scenario: Desactivar mesa válida hace baja lógica y audita

- **WHEN** se desactiva una mesa `libre`, no agrupada y sin comanda activa
- **THEN** la mesa queda `activa = false`, conserva su `id`, se registra audit log y se emite `mesa.desactivada`

### Requirement: REG-20-19 reactivación de mesa

Una `Mesa` `inactiva` MUST poder reactivarse únicamente si su `Zona` está `activa`; al reactivarse MUST pasar a estado `libre`, registrar audit log y emitir el evento `mesa.reactivada`. Reactivar una mesa cuya zona está `inactiva` o `en_cierre` MUST rechazarse.

#### Scenario: Reactivar mesa en zona activa

- **WHEN** se reactiva una mesa `inactiva` cuya zona está `activa`
- **THEN** la mesa queda `activa = true` y en estado `libre`, se registra audit log y se emite `mesa.reactivada`

#### Scenario: Reactivar mesa en zona inactiva se rechaza

- **WHEN** se intenta reactivar una mesa cuya zona está `inactiva`
- **THEN** el backend rechaza con error de dominio

#### Scenario: Reactivar mesa en zona en_cierre se rechaza

- **WHEN** se intenta reactivar una mesa cuya zona está `en_cierre`
- **THEN** el backend rechaza con error de dominio

### Requirement: REG-20-20 prevención UX de selección de mesas no agrupables

La UI de Admin MUST impedir, como validación de UX, seleccionar para unir cualquier mesa que no sea agrupable: `inactiva`, `por_limpiar`, `ocupada`, `reservada` o ya agrupada. El botón de unir MUST permanecer deshabilitado hasta que haya 2 o más mesas válidas (`libre`, activas, no agrupadas) seleccionadas. El backend MUST seguir siendo la autoridad: la UI no duplica reglas complejas, sólo previene errores obvios.

#### Scenario: Mesa no agrupable no es seleccionable

- **WHEN** se renderiza una mesa `inactiva`, `por_limpiar`, `ocupada`, `reservada` o agrupada en la selección de unir
- **THEN** su control de selección está deshabilitado/no disponible

#### Scenario: Mesa por_limpiar no es seleccionable para unir

- **WHEN** se renderiza una mesa en estado `por_limpiar` en la selección de unir
- **THEN** su control de selección está deshabilitado/no disponible

#### Scenario: Unir deshabilitado hasta 2 válidas

- **WHEN** hay menos de 2 mesas válidas seleccionadas
- **THEN** el botón "Unir mesas" está deshabilitado y muestra ayuda para seleccionar al menos 2 mesas libres

### Requirement: REG-20-21 acciones contextuales de zona y mesa en la UI

La UI de Admin MUST mostrar acciones contextuales según estado y MUST NOT mostrar acciones inválidas: una zona `inactiva` muestra "Activar" (no "Desactivar"); una zona `activa` muestra sus acciones válidas; una zona `en_cierre` muestra su estado y acciones permitidas. Para mesas: una mesa `inactiva` en zona `activa` muestra "Activar"; una mesa elegible muestra "Desactivar"; una mesa `ocupada`/`reservada`/agrupada no ofrece desactivar (o lo muestra deshabilitado con explicación). El formulario "Nueva mesa" MUST mostrarse sólo en zonas `activa`; en `inactiva`/`en_cierre` MUST mostrarse un mensaje informativo en lugar del formulario. La acción de baja lógica de mesa MUST llamarse siempre **"Desactivar mesa"** en UI y textos; la UI MUST NOT mostrar "Eliminar mesa" aunque el endpoint sea `DELETE` (el registro y `mesa.id` se conservan).

#### Scenario: Zona inactiva ofrece Activar, no Desactivar

- **WHEN** se renderiza una zona `inactiva`
- **THEN** la UI muestra la acción "Activar" y no muestra "Desactivar"

#### Scenario: La UI nunca muestra "Eliminar mesa"

- **WHEN** se renderizan las acciones de una mesa elegible
- **THEN** la acción de baja se etiqueta "Desactivar mesa" y no aparece "Eliminar"

#### Scenario: Nueva mesa sólo en zona activa

- **WHEN** se renderiza una zona `inactiva` o `en_cierre`
- **THEN** no se muestra el formulario "Nueva mesa" sino un mensaje informativo

### Requirement: REG-20-22 acción de QR por mesa en la UI

Cada `Mesa` en la UI MUST exponer una acción clara de QR (p. ej. "Ver QR" / "Copiar URL QR" / ver payload) que use el identificador permanente `mesa.id`. La acción MUST dejar claro que el QR pertenece a esa mesa. MUST NOT generar imagen ni impresión física (queda para §32).

#### Scenario: Mesa muestra acción de QR basada en su id

- **WHEN** se renderiza una mesa en Admin
- **THEN** ofrece una acción de QR cuyo payload/URL usa el `mesa.id` permanente

### Requirement: Errores backend mostrados de forma consistente en la UI

La UI MUST mostrar los errores del backend de forma consistente (toast o alert contextual junto a la acción), no como una banda cruda que parezca un error global permanente. Los mensajes MUST provenir del envelope de error del backend.

#### Scenario: Error de operación se muestra como toast/alert

- **WHEN** una operación (unir, desactivar, reactivar, crear) falla en el backend
- **THEN** la UI muestra el mensaje del backend como toast/alert contextual, sin banda global permanente

## MODIFIED Requirements

### Requirement: Endpoints REST de §20 bajo /api/v1

El backend MUST exponer bajo `/api/v1`: `GET/POST /zonas`, `PATCH /zonas/{id}`, `POST /zonas/{id}/cerrar`, `POST /zonas/{id}/activar`, `POST /zonas/{id}/desactivar`, `GET/POST /mesas`, `GET/PATCH/DELETE /mesas/{id}`, `POST /mesas/{id}/marcar-libre`, `POST /mesas/{id}/reactivar`, `POST /mesas/{id}/qr`, `POST /grupos`, `PATCH /grupos/{id}`, `POST /grupos/{id}/disolver`. `DELETE /mesas/{id}` es la desactivación (baja lógica) con sus validaciones (REG-20-18); `POST /mesas/{id}/reactivar` reactiva la mesa (REG-20-19). Todo endpoint mutador MUST aceptar `X-Request-Id` (idempotencia) y MUST devolver errores con el envelope estructurado del proyecto.

#### Scenario: Mutador rechaza X-Request-Id duplicado

- **WHEN** se repite una mutación con el mismo `X-Request-Id`
- **THEN** el backend responde `409` `IDEMPOTENCY_KEY_REUSED` sin doble efecto

#### Scenario: Listar mesas filtradas

- **WHEN** se hace `GET /api/v1/mesas?zona_id=&estado=`
- **THEN** se devuelven las mesas que cumplen el filtro

#### Scenario: Reactivar mesa expone endpoint dedicado

- **WHEN** se invoca `POST /api/v1/mesas/{id}/reactivar`
- **THEN** el backend aplica REG-20-19 (reactiva si la zona está activa, deja la mesa `libre`)

### Requirement: Eventos WebSocket del canal mesas

Los cambios de estado de mesa y zona, la activación/desactivación de mesa, y las operaciones de grupo MUST emitir eventos por el canal lógico `mesas` (ruta física `/ws/mesas`) con payload tipado: `mesa.estado_cambiado`, `mesa.desactivada`, `mesa.reactivada`, `zona.estado_cambiado`, `grupo.creado`, `grupo.actualizado`, `grupo.disuelto`. Se usan eventos específicos `mesa.desactivada` y `mesa.reactivada` (no se reutiliza `mesa.estado_cambiado`) porque `activa=false/true` no es el mismo ciclo de estado operativo (`libre`/`ocupada`/...). Sus payloads mínimos MUST ser `{ mesa_id, activa, usuario_id?, timestamp }`. Cada payload MUST incluir las entidades afectadas, `timestamp` y `usuario_id?` (opcional, ver requisito de `usuario_id`). MUST NOT usarse Socket.IO. La emisión MUST hacerse por un broadcaster testeable.

#### Scenario: Cambio de estado de mesa emite evento

- **WHEN** una mesa cambia de estado operativo (p. ej. `libre` → `ocupada`) a través del service
- **THEN** se emite `mesa.estado_cambiado` por el canal `mesas` con el payload tipado

#### Scenario: Desactivar y reactivar emiten eventos específicos

- **WHEN** se desactiva o se reactiva una mesa
- **THEN** se emite `mesa.desactivada` o `mesa.reactivada` respectivamente, con `{ mesa_id, activa, usuario_id?, timestamp }`

### Requirement: Auditoría persistente de operaciones críticas

El backend MUST registrar auditoría persistente en una tabla `audit_logs` con columnas `id`, `event_type`, `entity_type`, `entity_id`, `user_id?`, `reason?`, `payload` (json/jsonb), `created_at`, mediante un helper en `shared/audit.py`. MUST NOT usarse solo `logging.info`. Las operaciones que MUST quedar auditadas en §20 son: cambio de estado de mesa, cambio de estado de zona, creación de mesa, **desactivación (baja lógica) de mesa**, **reactivación de mesa**, creación de grupo, disolución de grupo, y generación de QR/payload de QR.

#### Scenario: Cambio de estado de zona registra audit log

- **WHEN** una zona transita de estado (p. ej. `activa` → `en_cierre`)
- **THEN** se inserta una fila en `audit_logs` con `event_type`, `entity_type=zona`, `entity_id`, `reason` y `payload`

#### Scenario: Desactivar y reactivar mesa registran audit log

- **WHEN** se desactiva (baja lógica) o se reactiva una mesa
- **THEN** se inserta la fila de `audit_logs` correspondiente a cada operación

### Requirement: Módulo frontend de mesas sin reglas de negocio duplicadas

El frontend MUST implementar `src/modules/mesas/` con `api.ts` (vía cliente Axios central de `src/api/`), `ws.ts` (canal `mesas`), `types.ts`, hooks de TanStack Query y los componentes `MesaCard`, `ZonaLayout`, `MesaEstadoBadge`, `ZonaEstadoBadge`, `MesaForm`, `ZonaForm`. La vista **Admin** MUST estar construida con componentes del stack visual del proyecto (Tailwind 4 + shadcn/ui sobre Radix UI: Card, Badge, Alert, Dialog), sin layout plano HTML básico, con estados loading/empty/error. Debe proveer una **vista Mesero** (layout de mesas agrupadas por zona) y la vista **Admin** (administración de zonas y mesas con unir/separar). `MesaCard` MUST mostrar un indicador de grupo cuando la mesa tiene `grupo_id`. Los formularios MUST usar React Hook Form + Zod (numero_visible requerido, capacidad positiva). El frontend MUST NOT decidir reglas de negocio ni duplicar reglas complejas: previene errores obvios (acciones contextuales REG-20-21, selección válida REG-20-20, QR por mesa REG-20-22) usando los estados/flags del backend, y el backend mantiene la autoridad; los errores se muestran de forma consistente (toast/alert).

#### Scenario: Vista Mesero muestra mesas por zona

- **WHEN** se renderiza la vista Mesero con datos de zonas y mesas
- **THEN** se muestran las mesas agrupadas por zona con su estado y etiqueta canónica

#### Scenario: MesaCard muestra indicador de grupo

- **WHEN** se renderiza una `MesaCard` de una mesa con `grupo_id`
- **THEN** muestra un indicador de pertenencia a grupo

#### Scenario: Admin usa componentes del stack visual

- **WHEN** se inspecciona la vista Admin
- **THEN** usa Card/Badge/Alert/Dialog de shadcn/Radix + Tailwind, no HTML plano básico, y delega las reglas al backend

#### Scenario: Formularios validan con Zod y estados de carga

- **WHEN** se envía un formulario inválido o la carga está pendiente/vacía/falla
- **THEN** la validación Zod impide el envío (numero_visible requerido, capacidad positiva) y la vista muestra loading/empty/error según corresponda

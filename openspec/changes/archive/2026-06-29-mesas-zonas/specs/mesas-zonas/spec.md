## ADDED Requirements

### Requirement: Entidades Zona, Mesa y GrupoMesas persistidas

El backend MUST persistir `Zona`, `Mesa` y `GrupoMesas` (SQLAlchemy 2 async) con migración Alembic. `Zona` MUST tener `id`, `nombre`, `descripcion?`, `estado`, `aforo_max`, `orden_visualizacion`, `created_at`, `updated_at`. `Mesa` MUST tener `id` (permanente), `zona_id` (mutable), `numero_visible`, `capacidad`, `estado`, `comanda_activa_id?`, `reserva_activa_id?`, `grupo_id?`, `activa`, `created_at`, `updated_at`. `GrupoMesas` MUST tener `id`, `comanda_id?` (nullable hasta §21), `created_at`, `dissolved_at?`. `GrupoMesas` MUST NOT persistir un arreglo `mesas_ids`: la pertenencia a un grupo se modela exclusivamente con `Mesa.grupo_id` como única fuente de verdad.

#### Scenario: Migración crea las tablas

- **WHEN** se aplica `alembic upgrade head`
- **THEN** existen las tablas `zonas`, `mesas` y `grupos_mesas`, y `grupos_mesas` no tiene columna `mesas_ids`

#### Scenario: Pertenencia a grupo vive en Mesa.grupo_id

- **WHEN** se inspecciona el modelo `GrupoMesas`
- **THEN** no tiene arreglo de mesas; la relación se resuelve por `Mesa.grupo_id`

### Requirement: Valores técnicos en API/DB y etiquetas canónicas en UI

Los enums de estado MUST persistirse y exponerse en API/DB con valores técnicos estables en snake_case: `EstadoZona` = `activa`, `en_cierre`, `inactiva`; `EstadoMesa` = `libre`, `reservada`, `ocupada`, `por_limpiar`, `inactiva`. La UI MUST mostrar las etiquetas canónicas del glosario (`Activa`, `En cierre`, `Inactiva`, `Libre`, `Reservada`, `Ocupada`, `Por limpiar`) mediante un mapeo, sin cambiar los valores técnicos del contrato.

#### Scenario: API expone valores técnicos

- **WHEN** un cliente lee una mesa o zona vía API
- **THEN** el campo `estado` usa el valor técnico (p. ej. `por_limpiar`), no la etiqueta en español

#### Scenario: UI muestra etiquetas canónicas

- **WHEN** la UI renderiza el estado de una mesa o zona
- **THEN** muestra la etiqueta canónica del glosario derivada del valor técnico

### Requirement: Identificador de mesa permanente generado por el backend

El backend MUST generar el `id` (UUID) de cada `Mesa`; `POST /mesas` MUST NOT aceptar un `id` enviado por el cliente. El `id` MUST ser permanente y MUST NOT reutilizarse. La eliminación de una mesa MUST ser baja lógica (`activa = false`), conservando el registro y su `id` (REG-20-12).

#### Scenario: POST no acepta id del cliente

- **WHEN** se crea una mesa enviando un `id` en el body
- **THEN** el backend ignora/rechaza ese `id` y genera uno propio

#### Scenario: Baja lógica conserva el id

- **WHEN** se da de baja una mesa
- **THEN** queda `activa = false`, el registro se conserva y su `id` no se reutiliza para una mesa nueva

### Requirement: Mesa nueva inicia Libre

Una `Mesa` creada en una zona Activa MUST iniciar en estado `libre`.

#### Scenario: Estado inicial Libre

- **WHEN** se crea una mesa en una zona Activa
- **THEN** su estado inicial es `libre`

### Requirement: REG-20-01 transición a Ocupada solo desde Libre o Reservada

El service MUST permitir transicionar una mesa a `ocupada` únicamente desde `libre` o `reservada`; cualquier otro origen MUST rechazarse con error de dominio. La transición real la dispara §21; aquí se expone como operación de servicio con contrato preparado.

#### Scenario: Ocupar desde Libre

- **WHEN** una mesa `libre` transita a `ocupada`
- **THEN** la transición se acepta

#### Scenario: Ocupar desde Por limpiar se rechaza

- **WHEN** una mesa `por_limpiar` intenta transitar a `ocupada`
- **THEN** el service rechaza con error de dominio

### Requirement: REG-20-02 una sola comanda activa por mesa

Una `Mesa` MUST NOT tener más de una comanda activa. El service MUST rechazar ocupar una mesa que ya tenga `comanda_activa_id`. La asignación real de comandas es de §21; aquí es invariante de servicio.

#### Scenario: Mesa ya ocupada no acepta segunda comanda

- **WHEN** se intenta ocupar una mesa que ya tiene `comanda_activa_id`
- **THEN** el service rechaza con error de dominio

### Requirement: Transición a Reservada como operación de servicio (seam §28)

El service MUST exponer una operación testeable para transicionar una mesa a `reservada` (mecanismo claro para que los escenarios de §20 sean ejecutables). El disparador real (ventana de reserva, verificación) es de §28 Reservas; en §20 no hay flujo de reservas. Transicionar a `reservada` MUST respetar las reglas de zona (Inactiva y En cierre la rechazan).

#### Scenario: Reservar una mesa Libre en zona Activa

- **WHEN** se transiciona a `reservada` una mesa `libre` de una zona `activa`
- **THEN** la mesa queda `reservada`

#### Scenario: Reservar en zona Inactiva se rechaza

- **WHEN** se intenta transicionar a `reservada` una mesa de una zona `inactiva`
- **THEN** el service rechaza con error de dominio

#### Scenario: Reservar en zona En cierre se rechaza

- **WHEN** se intenta transicionar a `reservada` una mesa de una zona `en_cierre`
- **THEN** el service rechaza con error de dominio

### Requirement: REG-20-07 zona Inactiva sin mesas Ocupadas ni Reservadas

Una `Zona` `inactiva` MUST NOT admitir mesas `ocupada` ni `reservada`. El service MUST rechazar transiciones que dejarían una mesa Ocupada o Reservada en una zona Inactiva.

#### Scenario: Ocupar mesa en zona Inactiva se rechaza

- **WHEN** se intenta ocupar una mesa cuya zona está `inactiva`
- **THEN** el service rechaza con error de dominio

### Requirement: REG-20-08 cierre de zona requiere Nivel 2 y motivo

La transición `activa` → `en_cierre` MUST requerir autorización Nivel 2 (dependencia placeholder de auth) y un `motivo` obligatorio. La operación MUST quedar en log auditable.

#### Scenario: Cerrar zona sin motivo se rechaza

- **WHEN** se invoca cerrar una zona sin `motivo`
- **THEN** la operación se rechaza por validación

#### Scenario: Cerrar zona con motivo y Nivel 2

- **WHEN** un operador Nivel 2 cierra una zona `activa` con motivo
- **THEN** la zona transita a `en_cierre` y queda en audit log

### Requirement: REG-20-09 zona En cierre rechaza nuevas ocupaciones y reservas

Una `Zona` `en_cierre` MUST NOT aceptar nuevas ocupaciones ni reservas de mesa. El service MUST rechazar ocupar o reservar mesas de una zona En cierre. La transición automática a Inactiva al cerrarse la última comanda (REG-20-10) depende de §21 y queda como contrato.

#### Scenario: Ocupar mesa en zona En cierre se rechaza

- **WHEN** se intenta ocupar una mesa cuya zona está `en_cierre`
- **THEN** el service rechaza con error de dominio

### Requirement: Desactivar zona valida ocupación y propaga a las mesas

`POST /zonas/{id}/desactivar` MUST rechazar la desactivación si la zona tiene alguna mesa `ocupada` o `reservada`. Si no las hay, la zona MUST pasar a `inactiva` y sus mesas `libre` o `por_limpiar` MUST pasar a `inactiva`. `POST /zonas/{id}/activar` (Inactiva→Activa) MUST devolver a `libre` las mesas inactivadas por la zona.

#### Scenario: Desactivar con mesa Ocupada se rechaza

- **WHEN** se intenta desactivar una zona con una mesa `ocupada`
- **THEN** la operación se rechaza con error de dominio

#### Scenario: Desactivar con mesa Reservada se rechaza

- **WHEN** se intenta desactivar una zona con una mesa `reservada`
- **THEN** la operación se rechaza con error de dominio

#### Scenario: Desactivar zona vacía propaga Inactiva

- **WHEN** se desactiva una zona sin mesas Ocupadas ni Reservadas
- **THEN** la zona pasa a `inactiva` y sus mesas `libre`/`por_limpiar` pasan a `inactiva`

### Requirement: REG-20-14 Por limpiar → Libre por cualquier operador

`POST /mesas/{id}/marcar-libre` MUST permitir a cualquier operador autenticado transicionar una mesa de `por_limpiar` a `libre`, sin autorización adicional. En §20, `marcar-libre` solo exige que la mesa esté en `por_limpiar`. El flag `saltar_estado_por_limpiar` NO aplica a §20: pertenece al futuro cierre de comanda de §21 (decidir si la mesa pasa a `por_limpiar` o directo a `libre`).

#### Scenario: Operador marca Por limpiar como Libre

- **WHEN** un operador autenticado marca como `libre` una mesa en `por_limpiar`
- **THEN** la mesa transita a `libre`

#### Scenario: Marcar-libre sobre mesa no Por limpiar se rechaza

- **WHEN** se invoca `marcar-libre` sobre una mesa que no está en `por_limpiar`
- **THEN** el service rechaza con error de dominio

### Requirement: Unir mesas crea un GrupoMesas

Unir mesas se modela como crear un `GrupoMesas`. `POST /grupos` MUST exigir 2 o más mesas, todas en estado `libre`, ninguna `inactiva`, y ninguna perteneciente a otro grupo activo. Al crearse, MUST asignar el mismo `grupo_id` a todas las mesas, emitir `grupo.creado`, y registrar audit log. En §20 el grupo es agrupación lógica/física; MUST NOT crear comanda real (la comanda compartida es de §21).

#### Scenario: Crear grupo con 2 mesas válidas

- **WHEN** se crea un grupo con 2 mesas `libre` no agrupadas
- **THEN** el grupo se crea, ambas mesas registran el mismo `grupo_id`, se emite `grupo.creado` y se registra audit log

#### Scenario: Crear grupo con menos de 2 mesas se rechaza

- **WHEN** se intenta crear un grupo con 1 mesa
- **THEN** la operación se rechaza con error de dominio

#### Scenario: Crear grupo con mesa Inactiva se rechaza

- **WHEN** se intenta crear un grupo incluyendo una mesa `inactiva`
- **THEN** la operación se rechaza con error de dominio

#### Scenario: Crear grupo con mesa ya agrupada se rechaza (REG-20-03)

- **WHEN** se intenta incluir en un nuevo grupo una mesa que ya pertenece a un grupo activo
- **THEN** la operación se rechaza con error de dominio

### Requirement: Modificar grupo agrega o quita mesas

`PATCH /grupos/{id}` MUST permitir agregar o quitar mesas de un grupo activo bajo las mismas reglas: no agregar mesas `inactiva`, no agregar mesas ya agrupadas, y no dejar el grupo con menos de 2 mesas (para reducir a 0 o 1 mesa se MUST disolver el grupo). MUST mantener `Mesa.grupo_id` consistente, emitir `grupo.actualizado` y registrar audit log.

#### Scenario: Agregar una mesa válida al grupo

- **WHEN** se agrega al grupo una mesa `libre` no agrupada
- **THEN** la mesa registra el `grupo_id`, se emite `grupo.actualizado` y se registra audit log

#### Scenario: Dejar el grupo con menos de 2 mesas se rechaza

- **WHEN** se intenta quitar mesas hasta dejar el grupo con 1 mesa
- **THEN** la operación se rechaza; para vaciar el grupo se debe disolver

### Requirement: Separar mesas disuelve el GrupoMesas

Separar mesas se modela como disolver un `GrupoMesas`. `POST /grupos/{id}/disolver` MUST operar solo sobre un grupo activo (sin `dissolved_at`), setear `dissolved_at`, limpiar `grupo_id` en todas las mesas del grupo, emitir `grupo.disuelto` y registrar audit log. MUST NOT eliminar físicamente el grupo. Si en el futuro §21 asocia una comanda activa al grupo, la disolución con comanda activa se resolverá en §21; en §20 no se implementa.

#### Scenario: Disolver grupo limpia mesas y marca dissolved_at

- **WHEN** se disuelve un grupo activo
- **THEN** todas sus mesas quedan con `grupo_id` nulo, el grupo queda con `dissolved_at` seteado, se emite `grupo.disuelto` y se registra audit log

#### Scenario: Disolver grupo ya disuelto se rechaza

- **WHEN** se intenta disolver un grupo que ya tiene `dissolved_at`
- **THEN** la operación se rechaza con error de dominio

### Requirement: mesas_ids derivado en read models

Los schemas de lectura de grupo (`GrupoMesasRead`) MUST exponer `mesas_ids` como campo **derivado**, calculado consultando las mesas con ese `grupo_id`, sin persistirlo. Esto evita desincronización entre `GrupoMesas` y `Mesa.grupo_id`.

#### Scenario: mesas_ids se deriva de Mesa.grupo_id

- **WHEN** se lee un grupo con dos mesas asignadas
- **THEN** `GrupoMesasRead.mesas_ids` contiene exactamente las mesas cuyo `grupo_id` es el del grupo

### Requirement: Endpoints REST de §20 bajo /api/v1

El backend MUST exponer bajo `/api/v1`: `GET/POST /zonas`, `PATCH /zonas/{id}`, `POST /zonas/{id}/cerrar`, `POST /zonas/{id}/activar`, `POST /zonas/{id}/desactivar`, `GET/POST /mesas`, `GET/PATCH/DELETE /mesas/{id}`, `POST /mesas/{id}/marcar-libre`, `POST /mesas/{id}/qr`, `POST /grupos`, `PATCH /grupos/{id}`, `POST /grupos/{id}/disolver`. Todo endpoint mutador MUST aceptar `X-Request-Id` (idempotencia) y MUST devolver errores con el envelope estructurado del proyecto.

#### Scenario: Mutador rechaza X-Request-Id duplicado

- **WHEN** se repite una mutación con el mismo `X-Request-Id`
- **THEN** el backend responde `409` `IDEMPOTENCY_KEY_REUSED` sin doble efecto

#### Scenario: Listar mesas filtradas

- **WHEN** se hace `GET /api/v1/mesas?zona_id=&estado=`
- **THEN** se devuelven las mesas que cumplen el filtro

### Requirement: QR usa el identificador permanente de la mesa

`POST /mesas/{id}/qr` MUST devolver una URL o payload que codifica el `id` permanente de la mesa (D-04), sin crear un identificador nuevo ni cambiar el `id`. En esta etapa MUST NOT generar imagen ni impresión física (eso es de §32 Carta pública/QR).

#### Scenario: QR codifica el mismo id de mesa

- **WHEN** se genera/regenera el QR de una mesa
- **THEN** el payload/URL contiene el mismo `mesa.id` permanente y no se crea un identificador nuevo

### Requirement: Eventos WebSocket del canal mesas

Los cambios de estado de mesa y zona y las operaciones de grupo MUST emitir eventos por el canal lógico `mesas` (ruta física `/ws/mesas`) con payload tipado: `mesa.estado_cambiado`, `zona.estado_cambiado`, `grupo.creado`, `grupo.actualizado`, `grupo.disuelto`. Cada payload MUST incluir las entidades afectadas, `timestamp` y `usuario_id?` (opcional, ver requisito de `usuario_id`). MUST NOT usarse Socket.IO. La emisión MUST hacerse por un broadcaster testeable.

#### Scenario: Cambio de estado de mesa emite evento

- **WHEN** una mesa cambia de estado a través del service
- **THEN** se emite `mesa.estado_cambiado` por el canal `mesas` con el payload tipado

#### Scenario: Disolver grupo emite evento

- **WHEN** se disuelve un grupo
- **THEN** se emite `grupo.disuelto` con los datos del grupo y las mesas afectadas

### Requirement: Auditoría persistente de operaciones críticas

El backend MUST registrar auditoría persistente en una tabla `audit_logs` con columnas `id`, `event_type`, `entity_type`, `entity_id`, `user_id?`, `reason?`, `payload` (json/jsonb), `created_at`, mediante un helper en `shared/audit.py`. MUST NOT usarse solo `logging.info`. Las operaciones que MUST quedar auditadas en §20 son: cambio de estado de mesa, cambio de estado de zona, creación de grupo, disolución de grupo, generación de QR/payload de QR, y baja lógica de mesa.

#### Scenario: Cambio de estado de zona registra audit log

- **WHEN** una zona transita de estado (p. ej. `activa` → `en_cierre`)
- **THEN** se inserta una fila en `audit_logs` con `event_type`, `entity_type=zona`, `entity_id`, `reason` y `payload`

#### Scenario: Baja lógica de mesa registra audit log

- **WHEN** se da de baja lógica una mesa
- **THEN** se inserta una fila en `audit_logs` correspondiente

### Requirement: usuario_id opcional hasta auth real

Mientras no exista auth real, `usuario_id`/`user_id` en eventos WebSocket y audit logs MUST ser opcional: si no hay usuario autenticado, se registra `null`. Cuando se implemente auth real, `usuario_id` MUST volverse obligatorio para los mutadores operativos.

#### Scenario: Mutación sin usuario autenticado registra null

- **WHEN** se ejecuta un mutador sin operador autenticado
- **THEN** el audit log y el evento registran `usuario_id = null` y la operación procede

### Requirement: Módulo frontend de mesas sin reglas de negocio duplicadas

El frontend MUST implementar `src/modules/mesas/` con `api.ts` (vía cliente Axios central de `src/api/`), `ws.ts` (canal `mesas`), `types.ts`, hooks de TanStack Query y los componentes `MesaCard`, `ZonaLayout`, `MesaEstadoBadge`, `ZonaEstadoBadge`, `MesaForm`, `ZonaForm`. Debe proveer una **vista Mesero** (layout de mesas agrupadas por zona) y una **vista Admin** (administración de zonas y mesas, incluida UI mínima de unir/separar mesas). `MesaCard` MUST mostrar un indicador de grupo cuando la mesa tiene `grupo_id`. Los formularios MUST usar React Hook Form + Zod (validación de UX). El frontend MUST NOT decidir reglas de unión/separación ni duplicar reglas de negocio: solo llama a la API y muestra los errores del backend.

#### Scenario: Vista Mesero muestra mesas por zona

- **WHEN** se renderiza la vista Mesero con datos de zonas y mesas
- **THEN** se muestran las mesas agrupadas por zona con su estado y etiqueta canónica

#### Scenario: MesaCard muestra indicador de grupo

- **WHEN** se renderiza una `MesaCard` de una mesa con `grupo_id`
- **THEN** muestra un indicador de pertenencia a grupo

#### Scenario: UI delega reglas de unión/separación al backend

- **WHEN** el usuario intenta unir o separar mesas
- **THEN** la UI llama a la API y muestra el error del backend si la operación es inválida, sin decidir la regla localmente

#### Scenario: Formularios validan con Zod y estados de carga

- **WHEN** se envía un formulario inválido o la carga está pendiente/vacía/falla
- **THEN** la validación Zod impide el envío y la vista muestra loading/empty/error según corresponda

### Requirement: Integración con Comandas y Reservas como contrato preparado

La integración real con §21 Comandas (apertura/cierre, comanda compartida del grupo, REG-20-06/10) y §28 Reservas (verificación REG-20-05, no-show REG-20-13, reactivación REG-20-11) MUST quedar como contrato/placeholder documentado y MUST NOT implementarse aquí. Las columnas `comanda_activa_id`, `reserva_activa_id` y `GrupoMesas.comanda_id` MUST existir para soportar la integración futura sin migración disruptiva.

#### Scenario: Columnas de integración presentes sin lógica de comandas/reservas

- **WHEN** se inspeccionan los modelos de §20
- **THEN** existen `comanda_activa_id`, `reserva_activa_id` y `GrupoMesas.comanda_id` sin lógica de apertura/cierre de comanda ni de reservas

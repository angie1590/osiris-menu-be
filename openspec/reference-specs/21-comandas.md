# Módulo: Comandas (§21)

## Propósito

Gestiona el ciclo de vida del pedido del cliente: apertura sobre mesa, agregado/anulación de ítems, envío a cocina/barra, división de cuenta, traslado entre mesas, y cierre con facturación. Es el módulo con mayor actividad operativa.

## Entidades

### Comanda

| Campo | Tipo | Notas |
|---|---|---|
| id | UUID | PK |
| numero | string | correlativo legible |
| mesa_ids | array UUID | una o más mesas (Grupo) |
| mesero_id | UUID | usuario responsable |
| reserva_id | UUID? | si nació de una reserva |
| estado | enum | Abierta / Pendiente de cobro / Cerrada / Anulada |
| origen | enum | mesero / cliente_qr (Fase 2A) |
| notas | text | observaciones del mesero |
| descuento | json? | tipo, monto, usuario autorizador |
| opened_at | timestamp | |
| closed_at | timestamp? | |
| anulacion_motivo | text? | si Anulada |

### ItemComanda

| Campo | Tipo | Notas |
|---|---|---|
| id | UUID | PK |
| comanda_id | UUID | FK |
| producto_id | UUID | FK Producto del catálogo |
| cantidad | int | |
| precio_unitario | decimal | **congelado al agregar** (N-04) |
| modificaciones | json | extras, remociones, punto de cocción |
| notas | text | para cocina/barra |
| estado | enum | Pendiente / Enviado / En preparación / Listo / Entregado / Rechazado / Anulado |
| ruteo | enum | cocina / barra |
| division_cuenta_id | UUID? | si aplica división |
| combo_padre_id | UUID? | si es componente de un combo |
| estado_timestamps | json | { pendiente_at, enviado_at, en_preparacion_at, listo_at, entregado_at, ... } |

### DivisionCuenta

| Campo | Tipo | Notas |
|---|---|---|
| id | UUID | PK |
| comanda_id | UUID | FK |
| numero_cuenta | int | 1, 2, 3, ... dentro de la comanda |
| receptor_fiscal | json | tipo (Consumidor Final / Cliente identificado), datos |
| modalidad | enum | por_item / partes_iguales / mixta |
| propina | decimal | calculada sobre subtotal de la cuenta |
| factura_id | UUID? | si ya facturada |

## Estados globales de la comanda

```
                  ┌─ Pendiente de cobro ── cobro completado ──→ Cerrada
                  │                                                │
   Abierta ──────┤                                                 │
                  │                                                │
                  └─ todos los ítems anulados / sin consumo ──→ Anulada

   Cerrada ── reapertura Nivel 4 ──→ Abierta (con nota de crédito asociada)
```

## Estados individuales del ítem

```
Pendiente ──→ Enviado ──→ En preparación ──→ Listo ──→ Entregado ──┬─→ (terminal)
    │           │              │                                   │
    │           │              │                                   └─→ Rechazado (Nivel 2)
    │           │              │
    └─ Anulado ←┴──────────────┘
```

Transiciones permitidas según D-02 (matriz de anulación):

| Estado | Mesero | Cocina/Barra | Cajero | Admin Socio |
|---|---|---|---|---|
| Pendiente → Anulado | ✅ sin auth | N/A | ✅ sin auth | ✅ sin auth |
| Enviado → Anulado | ❌ | ✅ con motivo | ✅ con motivo | ✅ con motivo |
| En preparación → Anulado | ❌ | ✅ motivo+Nivel 2 | ✅ motivo+Nivel 2 | ✅ con motivo |
| Listo → Anulado | ❌ | ❌ | ✅ motivo+Nivel 2 | ✅ con motivo |
| Entregado → Anulado | ❌ | ❌ | ❌ (usar Rechazado) | ✅ motivo+Nivel 4 |
| Entregado → Rechazado | ❌ | ❌ | ✅ motivo+Nivel 2 | ✅ motivo+Nivel 2 |

## Reglas de negocio (críticas)

1. **REG-21-01**: toda comanda tiene al menos una mesa asociada al abrirse.
2. **REG-21-02**: el Mesero responsable se asigna al abrir. Cambio queda en log.
3. **REG-21-03**: precio unitario se congela al agregar el ítem (N-04). Cambios de catálogo no afectan ítems ya agregados.
4. **REG-21-04**: ítem Anulado o Rechazado **se conserva** en la comanda como registro histórico. No se elimina.
5. **REG-21-05**: la comanda no puede transitar a Pendiente de cobro si tiene ítems en estado no terminal (Pendiente, Enviado, En preparación, Listo).
6. **REG-21-06**: la comanda no puede transitar a Cerrada sin facturación completa por §23 Caja. Excepción: anulación explícita Nivel 2 (R-21-07).
7. **REG-21-07**: anulación de comanda completa requiere motivo + Nivel 2 (D-10b). Sin consecuencia fiscal. Mesa pasa a Por limpiar o Libre.
8. **REG-21-08**: descuento de inventario híbrido (D-01):
   - Al pasar ítem a **Enviado**: crea **reserva teórica**.
   - Al pasar a **En preparación**: registra **consumo confirmado**.
   - Anulaciones antes de En preparación: liberan reserva sin impacto en inventario.
9. **REG-21-09**: ítem Rechazado mantiene consumo confirmado (D-10a). El reemplazo es ítem nuevo en la comanda.
10. **REG-21-10**: traslado de comanda preserva ítems, estados, mesero, historial e identificador. Solo cambia mesa.
11. **REG-21-11**: traslado sujeto a 7 reglas (D-08):
    - destino Libre o Por limpiar
    - destino no parte de Grupo
    - si comanda vinculada a reserva: capacidad compatible o Nivel 2 para forzar
    - preservación íntegra
    - origen → Por limpiar o Libre según config
    - destino → Ocupada
    - log con motivo, usuarios, timestamp
12. **REG-21-12**: no se permite agregar ítems a comanda en estado Pendiente de cobro, Cerrada o Anulada.
13. **REG-21-13**: división de cuenta se confirma al momento de facturar en §23. Modificable hasta entonces sin consecuencia fiscal.
14. **REG-21-14**: cada cuenta de una división genera **factura SRI independiente** con receptor propio, IVA propio sobre sus ítems, propina propia. Descuentos pre-división se prorratean proporcionalmente (D-09).
15. **REG-21-15**: combo (D-03):
    - al agregar un combo, sistema genera automáticamente los componentes
    - cada componente tiene su propio ruteo y estado
    - ítem padre pasa a Listo solo cuando **todos** sus componentes están Listos
    - padre → Entregado se propaga a todos los componentes
    - anulación del padre anula todos los componentes
16. **REG-21-16**: producto Agotado en catálogo no se puede agregar a comandas nuevas. Los ya agregados antes del agotamiento siguen su curso normal.
17. **REG-21-17**: concurrencia: serialización a nivel de DB. Si dos meseros intentan agregar el último ítem en stock, gana el primero que confirma. El segundo recibe rechazo de "producto agotado".
18. **REG-21-18**: reapertura de comanda Cerrada requiere Nivel 4 + motivo + generación de nota de crédito asociada en §24.

## Resiliencia offline del Mesero (R-21-19)

La tablet del Mesero soporta pérdida temporal de conexión con el servidor local:

- Hasta **50 cambios no enviados** se conservan en IndexedDB.
- Al reconectar, los cambios se reintentan automáticamente.
- **Idempotencia garantizada**: cada operación tiene un `request_id` UUID generado en el cliente. El backend rechaza request_ids duplicados.
- Ventana offline esperada: minutos, no horas. Si supera 15 minutos, alerta al Mesero.
- La cola offline del Mesero aplica solo a pérdida temporal de conexión entre la tablet y el backend local. No implica operación autónoma indefinida ni reemplaza la autoridad del backend. Al reconectar, el backend valida permisos, stock, estados e idempotencia antes de aceptar cada cambio. X-Request-Id es obligatorio en todos los mutadores, porque ya está mencionado en la API esperada.

## División de cuenta (D-09)

Modalidades:

- **por_item**: cada ítem asignado explícitamente a una cuenta.
- **partes_iguales**: total dividido en N partes iguales.
- **mixta**: algunos ítems individuales, el resto en partes iguales entre cuentas restantes.

Políticas fiscales/operativas:

- Una **factura por cuenta**.
- Propina **por cuenta** sobre su subtotal.
- Descuentos aplicados a la comanda **antes** de dividir, **prorrateados proporcionalmente**.
- IVA **por cuenta** sobre sus ítems (obligación normativa).
- Medios de pago mixtos permitidos dentro de cada cuenta.

## API esperada (esbozo)

```
POST   /api/v1/comandas                    # abrir comanda
GET    /api/v1/comandas/{id}
PATCH  /api/v1/comandas/{id}               # editar notas, mesero
POST   /api/v1/comandas/{id}/cerrar        # → Pendiente de cobro (si todos ítems terminales)
POST   /api/v1/comandas/{id}/anular        # Nivel 2 + motivo
POST   /api/v1/comandas/{id}/reabrir       # Nivel 4 + motivo + nota crédito
POST   /api/v1/comandas/{id}/trasladar     # 7 reglas + motivo
POST   /api/v1/comandas/{id}/agregar-mesa  # extender Grupo

POST   /api/v1/comandas/{id}/items
PATCH  /api/v1/comandas/{id}/items/{item_id}
POST   /api/v1/comandas/{id}/items/{item_id}/enviar     # → Enviado, crea reserva inventario
POST   /api/v1/comandas/{id}/items/{item_id}/anular     # según matriz D-02
POST   /api/v1/comandas/{id}/items/{item_id}/rechazar   # Entregado → Rechazado, Nivel 2

POST   /api/v1/comandas/{id}/divisiones    # crear división de cuenta
PATCH  /api/v1/comandas/{id}/divisiones/{div_id}
```

Cada request mutador acepta header `X-Request-Id` (UUID v4) para idempotencia.

## Eventos WebSocket emitidos

- `comanda.creada` / `comanda.estado_cambiado` / `comanda.anulada`
- `comanda.item_agregado` / `comanda.item_estado_cambiado` / `comanda.item_anulado` / `comanda.item_rechazado`
- `comanda.trasladada` — payload incluye mesa_origen, mesa_destino, motivo
- `comanda.dividida` — payload incluye cuentas creadas

Latencia objetivo: <500ms.

## Logs requeridos (Principio 1)

Todo lo que mute estado material:

- Apertura, cierre, anulación, reapertura de comanda.
- Cambio de mesero responsable.
- Agregado, cambio de estado, anulación, rechazo de ítem (incluye motivo si aplica).
- Traslado de comanda.
- División de cuenta (creación, modificación).
- Aplicación de descuentos.

## Contratos con otros módulos

- **§20 Mesas y zonas**: consulta estado, solicita transiciones (Ocupada al abrir, Por limpiar/Libre al cerrar).
- **§22 Cocina y barra**: envía ítems al ruteo configurado. Recibe actualizaciones de estado de ítems.
- **§23 Caja y cobro**: la comanda en Pendiente de cobro pasa a Caja para facturación y cobro.
- **§25 Catálogo**: consulta productos activos, precios, ruteo, tiempos, composición de combos.
- **§26 Inventario**: modelo híbrido D-01. Reserva teórica al Enviado, consumo confirmado al pasar a En preparación.
- **§28 Reservas**: una comanda puede originarse en una reserva (vínculo bidireccional).

## Casos de uso clave para tests

1. Abrir comanda sobre mesa Libre → Ocupada.
2. Agregar ítem → Pendiente. Enviar → Enviado (crea reserva inventario). Cocina marca En preparación → consumo confirmado.
3. Mesero anula ítem Pendiente → permitido sin auth.
4. Mesero intenta anular ítem Enviado → rechazado por matriz.
5. Cocina anula ítem En preparación → motivo + Nivel 2.
6. Cajero rechaza ítem Entregado → motivo + Nivel 2, mantiene consumo, no factura.
7. Cerrar comanda con ítem en Pendiente → rechazo (R-CMD-05).
8. Anular comanda completa sin consumo → motivo + Nivel 2, sin consecuencia fiscal.
9. Dividir comanda por_item, dos cuentas con receptores fiscales distintos → 2 facturas.
10. Trasladar comanda a mesa Libre → ok, mesa origen a Por limpiar, destino a Ocupada.
11. Trasladar a mesa parte de Grupo → rechazo.
12. Agregar combo → genera componentes automáticamente. Cocina marca componente A Listo, barra marca componente B Listo → padre pasa a Listo.
13. Producto Agotado, dos meseros intentan agregar simultáneamente → primero gana, segundo recibe error.
14. Tablet Mesero offline, agrega 3 ítems, reconecta → 3 ítems sincronizados sin duplicados (idempotencia).

## Frontend

Vistas:

- **mesero**: comanda activa con lista de ítems editables, selector de mesa, catálogo lateral.
- **caja**: cierre de comanda, división de cuenta, paso a facturación.

Componentes clave:

- `<ComandaActiva comanda={...} />` con lista de ítems y acciones rápidas.
- `<CatalogoSelector />` para agregar ítems con búsqueda y categorías.
- `<DivisionCuenta />` con modalidades por_item / partes_iguales / mixta.
- `<EstadoSemaforico />` (compartido).

Hooks:

- `useComanda(id)` con sync WebSocket.
- `useEnviarItem()` con manejo de offline y reintentos.
- `useTrasladar()` con validación de las 7 reglas.

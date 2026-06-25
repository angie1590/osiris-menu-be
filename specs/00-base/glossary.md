# Glosario canónico

Términos del dominio. Esta es la **terminología obligatoria** en código, comentarios, commit messages, UI, mensajes de error, documentación. Evita sinónimos.

---

## Estructura del local

**Zona** — Espacio físico diferenciado del restaurante. Cuatro zonas iniciales: Barra, Primer piso, Segundo piso, Jardín. Tiene estado: Activa, En cierre, Inactiva.

**Mesa** — Unidad física de servicio con capacidad para N personas. Pertenece a una Zona. Tiene identificador único permanente.

**Grupo de Mesas** — Agrupación lógica de 2+ mesas con una sola comanda compartida. Temporal: se separa al cerrar la comanda.

**Aforo** — Número de personas que pueden estar en una zona (informativo, no bloqueante).

---

## Operación

**Comanda** — Pedido de un grupo de clientes a una o más mesas. Vive desde la apertura del mesero hasta el cierre con facturación. Estados globales: Abierta, Pendiente de cobro, Cerrada, Anulada.

**Ítem de comanda** — Una línea individual dentro de una comanda. Estados: Pendiente, Enviado, En preparación, Listo, Entregado, Rechazado, Anulado.

**Producto** — Entidad del catálogo (§25) que se vende. Tiene precio, ruteo (cocina o barra), receta de insumos. Puede ser combo (compuesto por componentes).

**Combo** — Producto vendible compuesto por dos o más componentes con ruteo independiente. Definido en catálogo.

**Componente** — Ítem hijo de un combo. Tiene ruteo propio único (cocina o barra) y receta propia.

**Receta** — Lista de insumos consumidos al preparar un producto (o un componente). Definida en §26 Inventario.

**Ruteo** — Destino de preparación de un ítem: cocina o barra. Único por ítem vendible.

**Reserva** — Compromiso de mesa para una hora específica con cliente identificado.

**No presentada** — Reserva cuyo horario venció (con tolerancia configurable) sin que el cliente haya llegado.

---

## Hardware y dispositivos

**Servidor local** — Único servidor físico en el restaurante. Doble rol: aloja el backend + base de datos + frontend servido, y actúa como **computadora de caja** del Cajero/Barman.

**Computadora de caja** — Es el mismo servidor local. Usada por Cajero/Barman para cobro y facturación.

**Tablet del Mesero** — Dispositivo móvil de 10" usado por meseros para tomar comandas. Autenticación individual.

**Tablet fija de cocina** — Dispositivo de 12-13" montado fijo en cocina. Modo kiosko. PIN compartido entre Chef y Ayudante.

**Tablet fija de barra** — Análogo a la de cocina, montada en barra. Usada por Barman.

**Computadora de Admin** — Equipo adicional para Admin Socio o Admin Contable cuando operan desde posiciones distintas a la caja.

**Vista operativa de cocina / Vista operativa de barra** — Pantalla de la aplicación frontend filtrada por ruteo, que se muestra en la tablet fija correspondiente. **No usar "pantalla" como sinónimo genérico de dispositivo.**

---

## Roles y autorizaciones

**Super Admin** — Familiar técnico (cónyuge de la PO). Mantenimiento, custodia de credenciales fiscales. NO es socio.

**Admin Socio** — Cualquiera de los tres hermanos socios. Gestión de negocio, autorización Nivel 4.

**Admin Contable** — Hermana titular del RUC. Gestión fiscal.

**Cajero / Barman** — Empleado contratado con doble función. Cobro, facturación, cierre de caja, atención de barra.

**Mesero** — Empleados contratados (2 posiciones con rotación). Toma de comandas y atención de sala.

**Chef** — Empleado contratado. Gestión de cocina.

**Ayudante** — Empleado contratado. Apoyo en cocina.

**Personal de cocina** — Chef + Ayudante (genérico cuando aplica a ambos).

**Personal de barra** — Barman (genérico).

**Personal de cocina o barra** — Cuando un requisito aplica a ambos.

---

## Niveles de autorización

**Nivel 1** — Cualquier operador autenticado.

**Nivel 2** — Cajero, Admin Socio, Admin Contable, Super Admin.

**Nivel 3** — Admin Socio, Admin Contable, Super Admin.

**Nivel 4** — Admin Socio o Super Admin.

---

## Fiscal y normativo

**SRI** — Servicio de Rentas Internas, Ecuador. Autoridad fiscal.

**RUC** — Registro Único de Contribuyentes. Identificador fiscal de la persona o empresa que emite facturas.

**Comprobante electrónico** — Documento fiscal generado y firmado electrónicamente, transmitido al SRI.

**Clave de acceso** — Identificador único del comprobante electrónico, generado al emitir.

**Nota de crédito** — Documento fiscal de corrección que revierte parcial o totalmente una factura previa.

**LOPDP** — Ley Orgánica de Protección de Datos Personales, Ecuador.

**IESS** — Instituto Ecuatoriano de Seguridad Social. Régimen de afiliación de empleados.

---

## Inventario (D-01)

**Reserva teórica** — Stock comprometido cuando un ítem pasa a Enviado. Impide vender el mismo producto sin stock suficiente. No es descuento real. Se libera si el ítem se anula antes de En preparación.

**Consumo confirmado** — Descuento permanente de insumos cuando un ítem pasa a En preparación. Refleja consumo real. No se libera con anulaciones posteriores (incluido Rechazado).

**Merma** — Diferencia entre inventario teórico y físico. Incluye rechazos, derrames, pérdidas operativas.

---

## Operación offline / conectividad

**Offline** — En este sistema significa "sin internet, pero con red local funcional". Si la red local falla, el sistema deja de operar.

**Cola de comprobantes** — Lista persistente de facturas firmadas y pendientes de transmisión al SRI cuando vuelva la conectividad.

**Ticket provisional** — Comprobante temporal entregado al cliente cuando se factura offline, con la clave de acceso. La factura electrónica se enviará al SRI cuando vuelva la conexión.

**Semáforo de conectividad** — Indicador visual de tres colores (verde, amarillo, rojo) mostrado siempre en la UI para informar el estado de conectividad con el SRI.

---

## Identificadores

**N-XX** — Decisión de negocio tomada durante discovery (Fase 0).

**T-XX** — Decisión técnica tomada durante discovery (Fase 0).

**D-XX** — Decisión funcional post-discovery, tomada durante construcción.

**REQ-<sección>-<nn>** — Requisito funcional.

**REG-<sección>-<nn>** — Regla de negocio.

**NFR-<sección>-<nn>** — Requisito no funcional.

**NOR-<sección>-<nn>** — Requisito normativo.

**PEND-<sección>-<nn>** — Decisión explícitamente pendiente con responsable y plazo.

**SUP-XX** — Supuesto del entorno operativo.

# Decisiones consolidadas

Repositorio único de decisiones del proyecto. Cada decisión tiene identificador permanente. Si se modifica materialmente, se crea una nueva con número distinto y la original queda como `superseded`.

---

## Decisiones D-XX (post-discovery, funcionales)

### D-01 · Punto de descuento de inventario

**Modelo híbrido de dos capas.**

- Al transitar un ítem a **Enviado**: se crea reserva teórica de inventario. Impide vender el mismo producto sin stock suficiente a otras comandas. No es descuento real.
- Al transitar el ítem a **En preparación**: se registra consumo confirmado. Descuenta permanentemente el insumo del inventario.
- Anulaciones previas a En preparación liberan la reserva teórica sin impacto en inventario confirmado.

Módulos impactados: §21 Comandas, §22 Cocina y barra, §26 Inventario, §30 Reportes.

---

### D-02 · Matriz de anulación por rol y estado del ítem

| Estado ítem | Mesero | Personal cocina/barra | Cajero | Admin Socio |
|---|---|---|---|---|
| Pendiente | ✅ sin auth | N/A | ✅ sin auth | ✅ sin auth |
| Enviado | ❌ | ✅ con motivo | ✅ con motivo | ✅ con motivo |
| En preparación | ❌ | ✅ motivo + Nivel 2 | ✅ motivo + Nivel 2 | ✅ con motivo |
| Listo | ❌ | ❌ | ✅ motivo + Nivel 2 | ✅ con motivo |
| Entregado | ❌ | ❌ | ❌ (usar Rechazado, D-10a) | ✅ motivo + Nivel 4 |

Módulos impactados: §21, §22, §23, §24.

---

### D-03 · Ruteo del ítem y combos

- Productos vendibles tienen **ruteo único**: cocina o barra, no ambos.
- Productos que requieren preparación simultánea en ambos se modelan como **combos con componentes separados**, cada componente con su propio ruteo único.
- Ítem padre del combo pasa a Listo solo cuando todos sus componentes están Listos.
- La transición del padre a Entregado se propaga a todos los componentes.
- La anulación del padre anula todos sus componentes con el mismo motivo.

Módulos impactados: §21, §22, §25 (debe soportar combos), §26 (recetas a nivel de componente).

---

### D-04 · Identificador de mesa y QR

- El QR codifica un **identificador único permanente** de la mesa lógica, no de la ubicación física.
- La mesa puede cambiar de zona, ser reubicada o reemplazada físicamente sin regenerar el QR.
- Los identificadores **nunca se reutilizan**, incluso si la mesa original se da de baja.
- Si se reemplaza físicamente la mesa, el QR se reimprime con el mismo identificador.

Módulos impactados: §20, §32.

---

### D-05 · Apertura de comanda sobre mesa Reservada

- Cualquier operador puede abrir comanda sobre mesa Reservada.
- Requiere **verificación explícita** de la reserva (código de reserva o nombre del cliente).
- La comanda creada queda **vinculada con la reserva** correspondiente.

Módulos impactados: §20, §21, §28.

---

### D-06 · Desactivación de zona con mesas activas

- Estado intermedio **En cierre** para las zonas.
- Una zona En cierre no acepta nuevas comandas ni nuevas reservas.
- Las comandas abiertas siguen su curso hasta cerrarse naturalmente.
- Al cerrarse la última comanda, la zona pasa automáticamente a Inactiva.
- Reservas futuras de la zona se reasignan o cancelan con notificación al cliente.

Módulos impactados: §20, §28.

---

### D-07 · Transición Por limpiar → Libre

- El paso **Por limpiar es configurable**: puede saltarse globalmente.
- Si está activo, **cualquier operador con acceso a tablet** (Mesero, Cajero, personal de cocina, personal de barra) puede avanzar la transición a Libre **sin autorización adicional**.

Módulos impactados: §20, §31.

---

### D-08 · Reglas de traslado de comanda

Siete reglas formales:

1. Mesa destino en estado **Libre o Por limpiar**.
2. Mesa destino **no parte de un Grupo activo**.
3. Si la comanda origen está vinculada a una reserva: **compatibilidad de capacidad** con la reserva, o autorización Nivel 2 para forzar.
4. El traslado **preserva íntegramente**: ítems, estados, mesero, historial, identificador.
5. Mesa origen transita a Por limpiar o Libre según configuración.
6. Mesa destino transita a Ocupada.
7. La operación queda en log con mesa origen, mesa destino, motivo obligatorio, usuario ejecutor, timestamp.

Módulos impactados: §20, §21, §28.

---

### D-09 · División de cuenta

Cinco políticas:

1. **Factura por división**: cada cuenta genera factura electrónica independiente al SRI con su propio receptor fiscal.
2. **Propina por cuenta**: cada cuenta calcula propina sobre su subtotal.
3. **Descuentos antes de dividir**: aplicados a la comanda completa, prorrateados proporcionalmente entre cuentas según subtotal.
4. **IVA por cuenta**: obligación normativa SRI. No existe opción de IVA global con prorrateo.
5. **Medios de pago mixtos** permitidos dentro de cada cuenta (efectivo + tarjeta, etc.).

Módulos impactados: §21, §23, §24.

---

### D-10a · Ítem rechazado después de entregado

- Nuevo estado **Rechazado**, derivado de Entregado.
- Requiere **autorización Nivel 2** y motivo obligatorio.
- **Mantiene** el consumo confirmado de inventario (insumos ya consumidos).
- **No factura** al cliente.
- El reemplazo se modela como ítem nuevo en la comanda.

Módulos impactados: §21, §22, §23, §24, §26, §30.

---

### D-10b · Comanda abierta sin consumo

- **Anulación con motivo obligatorio y autorización Nivel 2**.
- La comanda transita a estado Anulada sin consecuencia fiscal.
- La mesa transita a Por limpiar o Libre según configuración.

Módulos impactados: §21.

---

## Decisiones T-XX (técnicas de discovery — las más relevantes para código)

| ID | Decisión |
|---|---|
| T-01 | T-01 no prohíbe servicios locales autocontenidos como PostgreSQL, Redis o contenedores Docker. Prohíbe dependencias cloud obligatorias para la operación crítica. |
| T-02 | WebSockets como mecanismo único de comunicación en tiempo real. |
| T-08 | Configuración inicial del sistema vía interfaz del Admin Socio. |
| T-15 | Backend en Python (Opción B). Razón: librería propietaria de facturación SRI escrita en Python. |
| T-28 | Servidor con doble rol: servidor del sistema + computadora de caja. |
| T-30 | Estrategia de backups 3-2-1 adaptada. |
| T-31 | Tablets de 10" para meseros. Tablets fijas de 12-13" para cocina/barra. |
| T-32 | Tres redes lógicas separadas: Sistema, Empleados, Clientes. |
| T-33 | Autenticación por PIN compartido en tablet fija de cocina (Chef + Ayudante). |
| T-34 | Re-autenticación con PIN personal cuando la acción requiere identificación individual. |
| T-35 | Docker Compose único como entorno oficial de desarrollo. El workspace raíz debe levantar backend, frontend, PostgreSQL y Redis con un solo `docker-compose.yml`. Esta decisión reemplaza la restricción inicial de “Sin Docker en MVP” para el desarrollo de osiris-menu. |

---

## Decisiones N-XX (negocio de discovery — las más relevantes para código)

| ID | Decisión |
|---|---|
| N-02 | Cuatro zonas operativas: Barra, Primer piso, Segundo piso, Jardín. |
| N-03 | Soporte de agrupación de mesas para grupos grandes. |
| N-04 | Precio congelado al momento de agregar ítem a comanda; cambios de catálogo posteriores no afectan ítems ya agregados. |
| N-06 | Traslado de comanda entre mesas con motivo obligatorio. |
| N-09 | Mesero confirma entrega de ítem al cliente. |
| N-10 | Ruteo cocina/barra configurado a nivel de producto en catálogo. |
| N-11 | Producto puede marcarse como Agotado temporalmente desde cocina/barra. |
| N-14 | División de cuenta: por ítem, por partes iguales, mixta. Medios de pago mixtos permitidos. |
| N-20 | Reapertura de comanda Cerrada con autorización Nivel 4 y nota de crédito asociada. |
| N-47 | Reservas: ventana de 30 minutos antes para transición de mesa a Reservada. Configurable. |
| N-48 | Agrupación de mesas: una sola comanda compartida, se separan al cerrar. |
| N-52 | QR físico en cada mesa con identificador codificado en URL. |

---

## Cómo proponer una decisión nueva D-XX

Cuando durante la programación encuentres una ambigüedad que no esté resuelta en estas decisiones ni en las specs:

1. **No la resuelvas tú solo en código**. Detente.
2. Levanta una propuesta de decisión nueva: identificador tentativo, contexto, opciones evaluadas, recomendación, módulos impactados.
3. La decisión se cierra explícitamente.
4. Una vez cerrada, se agrega aquí con el siguiente número D-XX disponible (después de D-10b).

# Módulo: Cocina y barra (§22)

## Propósito

Provee las vistas operativas en tiempo real para el personal de cocina y de barra. Muestra los ítems que deben prepararse, permite actualizar el estado de cada ítem durante su preparación, gestiona el descuento confirmado de inventario, notifica al Mesero cuando un ítem está Listo, y permite reportar agotamiento de productos.

## Naturaleza del módulo

- **Dos vistas distintas, mismo módulo**:
  - **Vista operativa de cocina**: muestra ítems con ruteo `cocina`. Usuarios: personal de cocina (Chef + Ayudante).
  - **Vista operativa de barra**: muestra ítems con ruteo `barra`. Usuarios: personal de barra (Barman).
- Las vistas se renderizan en **tablets fijas** de 12-13" en modo kiosko.
- Autenticación por **PIN compartido** (T-33) entre operadores de la misma estación. Re-autenticación con PIN personal cuando la acción requiere identificación individual (T-34).

## Entidades

Este módulo **no posee entidades propias**. Consume:

- `ItemComanda` de §21 Comandas (filtrado por ruteo).
- `Producto` de §25 Catálogo (estado Agotado, tiempos estándar, recetas para combos).
- `Receta` de §26 Inventario (para registrar consumo confirmado).

## Vista operativa

Cada vista (cocina o barra) muestra:

- **Lista de tarjetas de comanda** ordenadas por antigüedad (más antigua primero, orden estable).
- Por tarjeta: número de mesa o Grupo, mesero responsable, hora de apertura, notas generales.
- Por ítem: nombre del producto, cantidad, modificaciones (extras/remociones/cocción), notas libres, tiempo desde envío, estado actual, referencia a combo padre si aplica.
- Botones por ítem: Marcar En preparación, Marcar Listo, Anular (con motivo), Reportar Agotado.
- Indicador semafórico de tiempo:
  - **Amarillo** al 100% del tiempo estándar del producto.
  - **Rojo** al 150% del tiempo estándar.
- Indicador de estado de conexión con el backend (compartido).

## Reglas de negocio (críticas)

1. **R-COC-01**: el ruteo del ítem se determina **exclusivamente** por la configuración del producto en el catálogo (§25). El módulo solo filtra y muestra.
2. **R-COC-02**: ruteo único por ítem vendible (D-03). Productos que requieren cocina + barra se modelan como combos con componentes separados.
3. **R-COC-03**: al transitar ítem a **En preparación** desde una tablet fija, se aplica **consumo confirmado** del inventario (D-01) según receta del producto. Si es componente de combo, descuento al nivel del componente.
4. **R-COC-04**: anulación desde tablet fija sujeta a matriz D-02:
   - Enviado → Anulado: motivo obligatorio.
   - En preparación → Anulado: motivo + Nivel 2.
   - No se permite anular Listo ni posteriores desde tablet fija.
5. **R-COC-05**: marcar un ítem como **Listo no implica entrega**. La entrega la marca el Mesero en su propia tablet cuando lleva el producto a la mesa.
6. **R-COC-06**: para combos, el padre pasa a Listo solo cuando todos los componentes están Listos. Hasta entonces, el padre permanece En preparación.
7. **R-COC-07**: reporte de agotamiento (N-11):
   - Transita el producto a Agotado en catálogo.
   - **No afecta ítems ya agregados** a comandas abiertas (siguen su curso de preparación).
   - Bloquea nuevas adiciones del producto a cualquier comanda.
   - Se revierte al restaurar el producto (operador) o automáticamente al reinicio de servicio según configuración.
8. **R-COC-08**: ítem Rechazado (D-10a) **no libera** el consumo confirmado. La merma se preserva. Esto queda en log.
9. **R-COC-09**: tablet fija opera en modo kiosko. Pérdida de conexión: muestra indicador, los últimos datos quedan visibles. **No acepta transiciones de estado** durante ventana offline; se permiten solo al restablecer conexión.
10. **R-COC-10**: sesión compartida con PIN. Acciones que requieren autorización individual (Nivel 2 para anular En preparación, por ejemplo) exigen re-autenticación con PIN personal en el momento. Log refleja el usuario individual identificado.
11. **R-COC-11**: tiempos de preparación estándar provienen del catálogo (configurados por Chef o Admin Socio). Umbrales de color (100% amarillo, 150% rojo) son configurables globalmente.
12. **R-COC-12**: orden estable de tarjetas. Si dos comandas se abren en el mismo segundo, criterio de desempate: identificador correlativo.

## Sonidos de notificación

Configurables a nivel de **dispositivo o instalación**, no a nivel de usuario individual:

- Aparición de nuevo ítem en la vista.
- Cambio de estado de ítem.
- Alertas de tiempo superado (amarillo, rojo).

Configuración por defecto:

- Tablet fija de cocina: sonidos activados.
- Tablet fija de barra: sonidos a criterio del personal.

## API esperada (esbozo)

Este módulo consume el API de §21 Comandas para transiciones de estado:

```
POST /api/v1/comandas/{id}/items/{item_id}/preparar    # → En preparación, registra consumo D-01
POST /api/v1/comandas/{id}/items/{item_id}/listo       # → Listo
POST /api/v1/comandas/{id}/items/{item_id}/anular      # según matriz D-02 desde cocina/barra
```

Y agrega endpoints específicos del módulo:

```
GET  /api/v1/cocina/items                # ítems filtrados ruteo=cocina, no terminales
GET  /api/v1/barra/items                 # ítems filtrados ruteo=barra, no terminales
POST /api/v1/productos/{id}/agotar       # marcar Agotado
POST /api/v1/productos/{id}/restaurar    # revertir Agotado
```

## Eventos WebSocket suscritos

La tablet fija se suscribe a:

- `comanda.item_agregado` filtrado por ruteo de la vista (cocina o barra).
- `comanda.item_estado_cambiado` filtrado por ruteo.
- `comanda.cerrada` o `comanda.anulada` (para retirar ítems de la vista).
- `producto.agotado` y `producto.restaurado` (cambia disponibilidad para nuevas comandas).
- `connectivity.estado` (semáforo).

## Eventos WebSocket emitidos

Las transiciones desde tablet fija propagan los eventos del módulo Comandas:

- `comanda.item_estado_cambiado` con `nuevo_estado: en_preparacion | listo | anulado`, `origen: cocina | barra`.
- `producto.agotado` cuando se reporta agotamiento.

## Logs requeridos

- Cambio de estado de ítem desde tablet fija (con usuario identificado vía PIN, incluyendo re-autenticación cuando aplica).
- Reporte de agotamiento de producto.
- Restauración de producto.
- Intentos de anulación rechazados por matriz (para auditoría de comportamiento).
- Sesiones de tablet fija (apertura por PIN compartido y eventos individuales).

## Configuración asociada (§31)

- `umbral_tiempo_amarillo_pct`: default 100.
- `umbral_tiempo_rojo_pct`: default 150.
- `sonidos_cocina_activos`: default true.
- `sonidos_barra_activos`: default false.
- `auto_restaurar_agotados_reinicio`: default true.

## Contratos con otros módulos

- **§21 Comandas**: recibe ítems vía WebSocket; emite transiciones de estado de ítem. Bidireccional.
- **§25 Catálogo**: lee ruteo, tiempos de preparación, composición de combos, estado de agotamiento.
- **§26 Inventario**: escribe consumo confirmado al pasar ítem a En preparación. Permite ajustes de merma desde tablet fija.
- **§31 Configuración**: lee umbrales de tiempo, configuración de sonidos, política de agotamiento.

## Casos de uso clave para tests

1. Mesero envía ítem (cocina) → aparece en vista operativa de cocina en <500ms.
2. Chef marca En preparación → consumo confirmado en inventario.
3. Chef marca Listo → Mesero recibe notificación en su tablet.
4. Cocina anula ítem Enviado → motivo obligatorio, queda en log.
5. Cocina intenta anular ítem En preparación sin Nivel 2 → exige re-autenticación con PIN personal de usuario con Nivel 2.
6. Combo: cocina marca componente A Listo, barra marca componente B Listo → padre pasa a Listo, Mesero recibe notificación.
7. Reporte de agotamiento: ítem ya en comanda abierta sigue su curso, pero nuevo intento de agregar el producto a otra comanda es rechazado.
8. Ítem Rechazado por Cajero post-entrega: consumo confirmado se mantiene, log refleja la merma.
9. Tablet fija pierde conexión: muestra indicador, no acepta cambios. Reconecta: estado se reanuda, se permite operar.
10. Tiempo de preparación supera 100% del estándar → ítem se marca amarillo. Supera 150% → rojo.

## Frontend

Vistas dedicadas:

- **cocina**: layout fullscreen optimizado para tablet fija 12-13", legible a 2 metros, botones grandes.
- **barra**: análogo a cocina, con el filtro de ruteo correspondiente.

Componentes:

- `<TarjetaComanda comanda={...} items={...} />` con lista de ítems y acciones.
- `<ItemPreparacion item={...} onPreparar onListo onAnular />` con indicador semafórico de tiempo.
- `<BotonAgotar producto={...} />` para reportar agotamiento.

Hooks:

- `useVistaOperativa(ruteo)` con suscripción WebSocket filtrada.
- `useTransicionItem()` con PIN re-auth si Nivel 2 requerido.
- `useTiempoTranscurrido(item)` con tick por segundo y cálculo de color semafórico.

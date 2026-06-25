# Principios de diseño no negociables

Estos diez principios prevalecen sobre cualquier decisión técnica oportunista. Cualquier propuesta de cambio al sistema debe validarse contra estos principios. Si una decisión técnica viola un principio, **el principio gana**, no la decisión técnica.

---

## 1. Trazabilidad total

Toda acción material sobre los datos queda registrada en log: quién, cuándo, desde qué dispositivo, con qué contexto y, cuando aplica, con qué motivo.

**Implicaciones prácticas:**
- Logs append-only. No se editan, no se reescriben, no se eliminan dentro del periodo de retención.
- La eliminación lógica de entidades preserva el historial completo de acciones previas.
- Toda acción que modifica estado material debe tener su entrada de log correspondiente.

---

## 2. Inmutabilidad fiscal

Los datos fiscales son inalterables en el tiempo.

**Implicaciones prácticas:**
- Una factura emitida y transmitida al SRI no se modifica nunca. Corrección solo vía nota de crédito.
- Un comprobante anulado preserva la información original con su clave de acceso y el detalle de la anulación.
- Datos fiscales se conservan accesibles durante el periodo de retención exigido (7 años).

---

## 3. Operación offline resiliente

El restaurante no se detiene por un problema de internet.

**Implicaciones prácticas:**
- El sistema opera plenamente sin internet excepto: transmisión SRI, mensajes al cliente, backup a nube.
- Operaciones offline-compatibles continúan normalmente.
- Las que requieren internet se encolan para reintento automático al recuperar conexión.
- El operador es notificado del estado de conectividad de forma transparente (semáforo).

---

## 4. Cumplimiento como propiedad emergente

El operador cumple por usar el sistema correctamente.

**Implicaciones prácticas:**
- El operador no necesita conocer los detalles de la normativa para cumplirla.
- El sistema le ofrece flujos que ya incorporan las obligaciones normativas (SRI, LOPDP, IESS, laboral).
- El cumplimiento es una propiedad del diseño, no una carga para el equipo operativo.

---

## 5. Cumplimiento por defecto

Las opciones por defecto del sistema cumplen la normativa.

**Implicaciones prácticas:**
- Ante ambigüedad, el default es la alternativa que cumple normativa más estrictamente.
- Si una operación admitiría una interpretación legal y otra que no, el sistema rechaza la segunda y obliga al operador a tomar la decisión consciente con motivo registrado.

---

## 6. Mínimo privilegio

Cada rol accede solo a lo estrictamente necesario.

**Implicaciones prácticas:**
- El acceso a datos y operaciones se concede al rol más restringido posible.
- Acciones sensibles (anulación, descuentos, reapertura de comanda, cambios de catálogo, modificación de empleados, exportación de datos) requieren autorización adicional de un rol con nivel suficiente, con motivo registrado.
- La UI debe esconder acciones no permitidas al rol activo. La validación de autorización ocurre en backend como segunda capa.

---

## 7. Configuración trazable

Todo cambio de parámetro queda registrado.

**Implicaciones prácticas:**
- Cualquier cambio de un parámetro configurable (precios, ruteo, umbrales, políticas, mensajes) queda en log con usuario, timestamp, valor anterior y valor nuevo.
- La configuración del sistema en un instante histórico es siempre reconstruible a partir del log.

---

## 8. Evolución sin migración

El MVP soporta las extensiones de Fase 2 sin rediseño.

**Implicaciones prácticas:**
- El diseño del MVP contempla explícitamente: auto-pedido desde QR, WhatsApp Business API, mejoras iterativas.
- Modelo de datos, arquitectura de módulos y sistema de permisos deben soportar estas extensiones como activaciones de capacidades ya contempladas, sin requerir migración de datos ni reescritura de código fundacional.

---

## 9. Transparencia con el operador

El operador siempre sabe qué está pasando.

**Implicaciones prácticas:**
- Indicador semafórico de conectividad con el SRI visible siempre.
- Pendientes en cola visibles.
- Tiempo desde el envío de un ítem visible en cocina/barra.
- Resultado de cada acción del operador comunicado claramente.
- El operador nunca recibe sorpresas ante el cliente porque el sistema ocultó información relevante.

---

## 10. Validación rigurosa antes de producción

Nada llega a producción sin validación técnica formal.

**Implicaciones prácticas:**
- Pruebas unitarias para lógica de dominio.
- Pruebas de integración con SRI en ambiente sandbox.
- Validación manual de los flujos principales por parte del equipo de desarrollo.
- El equipo técnico es responsable de mantener este principio incluso bajo presión de plazos.

---

## Cómo usar estos principios en el código

Cuando implementes algo y dudes entre dos caminos, pregúntate:

1. ¿Esta decisión es consistente con los 10 principios?
2. Si alguno se ve afectado, ¿estoy violándolo, o sólo es tensión productiva?
3. Si lo violo, ¿hay un buen argumento para suspenderlo, documentado en una decisión D-XX nueva?

Si no puedes contestar las 3 preguntas con tranquilidad, **detén la implementación y pide una decisión explícita**.

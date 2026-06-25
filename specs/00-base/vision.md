# Visión del sistema

## Qué es

Sistema operativo integral del restaurante-cervecería Asiringui, en Cuenca, Ecuador. Apertura prevista Q3 2026. Local familiar de aproximadamente 60 plazas en cuatro zonas (Barra, Primer piso, Segundo piso, Jardín), operación martes a domingo.

## Para qué existe

Asiringui necesita operar diariamente con orden, trazabilidad, cumplimiento normativo y eficiencia, sin depender de herramientas heterogéneas y desconectadas (papel, hojas de cálculo, software fiscal independiente, mensajería informal).

El sistema provee la plataforma integral única que soporta el ciclo operativo completo: desde la atención al cliente hasta el cierre fiscal del día, con visibilidad consolidada para los socios y cumplimiento estricto de la normativa ecuatoriana aplicable.

## Atributos rectores

1. **Integralidad**: el sistema cubre el ciclo operativo completo del restaurante sin agujeros que obliguen a herramientas externas.
2. **Cumplimiento normativo por defecto**: el operador cumple SRI, LOPDP, IESS y laboral por usar el sistema correctamente, sin saber detalles legales.
3. **Trazabilidad total**: toda acción material queda registrada con usuario, momento y contexto.
4. **Resiliencia operativa**: opera sin internet, soporta fallos parciales, mantiene operación sin degradación visible para el cliente.
5. **Visibilidad consolidada**: los socios acceden a información consolidada y oportuna, no fragmentada entre herramientas.

## Dimensionamiento

- Capacidad: ~60 plazas, ~20 mesas, 4 zonas.
- Operación: 6 días/semana, 12 horas promedio diarias.
- Volumen estimado: 40-80 comandas/día en operación consolidada.
- Operadores concurrentes: 4-5 simultáneos durante el servicio.
- Personal total: 6-8 empleados contratados + socios.
- Catálogo: 50-100 ítems vendibles.

## Antivisión — lo que el sistema NO es ni debe llegar a ser

- **NO** es un ERP empresarial para multi-restaurante ni franquicia. Es para Asiringui específicamente.
- **NO** es un producto comercial revendible.
- **NO** es una app móvil nativa para clientes. La interacción del cliente es indirecta (mediante meseros) o vía web responsive (carta QR, reservas, en Fase 2 auto-pedido).
- **NO** es multi-tenant ni cloud-dependiente para operación crítica. La operación local autocontenida es estructural.

## Estructura societaria del negocio

Cuatro voces societarias:

- Tres hermanos socios fundadores: dos administradores activos del restaurante + un tercero que opera adicionalmente la fábrica de cerveza Asiringui como negocio independiente.
- Padres como unidad conjunta: una sola voz societaria, plenos derechos sobre toda la información del sistema incluida nómina.

Roles operativos del proyecto:

- **Product Owner**: hermana administradora (ingeniera de sistemas).
- **Super Admin / implementación técnica**: cónyuge de la PO (ingeniero de sistemas). NO es socio.
- **Admin Socio responsable de operación**: otro hermano.
- **Admin Contable**: hermana titular del RUC.

## Decisiones estructurantes vigentes

- **Estrategia B**: calidad premium con precio justo.
- **Operación 6 días/semana** desde apertura (martes-domingo).
- **Régimen fiscal general** con facturación electrónica SRI desde día 1.
- **Cumplimiento laboral IESS** desde la primera contratación.
- **Servidor local**, sin cloud obligatorio para operación crítica.
- **Equipo técnico familiar reducido**: 2 personas. El sistema debe ser construible y mantenible en este marco.

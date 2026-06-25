# Stack técnico y arquitectura

## Stack del backend

| Capa | Tecnología | Versión / nota |
|---|---|---|
| Lenguaje | Python | 3.12+ |
| Framework web | FastAPI | última estable. Decisión firme: no Django ni Flask |
| Base de datos | PostgreSQL | versión mayor estable con soporte activo oficial |
| ORM | SQLAlchemy | con Alembic para migraciones |
| Validación | Pydantic | integrado en FastAPI |
| WebSockets | nativo FastAPI | no Socket.IO ni librerías externas |
| Hashing | passlib + bcrypt | obligatorio para passwords |
| Cripto / firmas | cryptography | para certificados SRI |
| PDF | WeasyPrint o ReportLab | según necesidad |
| Email | smtplib stdlib | proveedor externo SMTP |
| Testing | pytest | estándar Python |
| Tareas programadas | APScheduler | integrado, sin Celery/Redis en MVP |

## Stack del frontend

| Capa | Tecnología | Nota |
|---|---|---|
| Lenguaje | TypeScript | strict: true obligatorio |
| Framework | React | 18+ funcional con hooks |
| Build | Vite | |
| Routing | React Router | |
| Estado servidor | TanStack Query | obligatorio para datos del backend |
| Estado UI | useState/useReducer | Zustand si se necesita global |
| Estilos | Tailwind CSS | utility-first |
| Componentes base | shadcn/ui | sobre Tailwind |
| Forms | React Hook Form + Zod | obligatorio para todo form |
| HTTP | fetch o ky | |
| Iconos | lucide-react | |
| Testing | Vitest + Playwright | unit + e2e |

## Arquitectura física

### Hardware

- **Servidor local** (1 unidad): doble rol — aloja backend + DB + frontend servido + actúa como computadora de caja del Cajero/Barman.
- **Tablets de meseros** (3-4 unidades de 10"): aplicación frontend vía WiFi.
- **Tablets fijas de cocina y barra** (2 unidades de 12-13"): montadas fijas, alimentación constante, modo kiosko.
- **Computadoras adicionales** (1-2 unidades): Admin Socio / Admin Contable cuando operan desde posiciones distintas a la caja.
- **UPS** del servidor.
- **Red WiFi segmentada** en tres VLANs (sistema, empleados, clientes).
- **Discos de backup externos** (7 unidades USB, rotación diaria).

Costo estimado total: $3,920 - $7,900 USD.

### Red

Tres redes lógicas separadas con VLAN o redes físicas independientes:

- **Red Sistema**: backend + tablets meseros + tablets fijas cocina/barra + computadoras admin. Único punto de salida a internet por destinos autorizados (SRI, NTP, DNS, OCSP, backups cloud, VPN admin, email/WhatsApp en Fase 2).
- **Red Empleados**: uso personal de empleados, sin acceso a red Sistema ni a red Clientes.
- **Red Clientes**: WiFi público con captive portal. Client isolation activado. Sin acceso a red Sistema ni red Empleados.

### Despliegue

Decisión cerrada en Parte III v1.2:

- Procesos del sistema gestionados por **systemd** (no Docker en MVP).
- **Scripts Bash versionados** en repo para despliegue, actualización y rollback.
- **Ansible opcional** solo para bootstrap inicial de hardware nuevo (reconstrucción ante desastre).
- Sin contenedores, sin orquestación, sin Kubernetes.

### Conexión backend ↔ PostgreSQL

Ambos en el mismo host. Conexión por socket Unix local o TCP a localhost. **No requiere TLS** porque el tráfico no sale del host. TLS sí es obligatorio para acceso administrativo remoto vía VPN.

## Comunicación frontend ↔ backend

- **HTTPS / TLS** obligatorio para todas las conexiones del frontend al backend, incluso dentro de la red local. Certificado puede ser autogenerado e instalado en los dispositivos cliente.
- **WSS** (WebSocket Secure) con el mismo certificado.
- **Sesión** en cookie httpOnly seteada por backend al login. NO usar localStorage para el token.

## Política de conectividad (3 niveles, semafórica)

- **Nivel 1**: conectividad general a internet (DNS + healthcheck HTTP).
- **Nivel 2**: conectividad específica al SRI (healthcheck al endpoint del SRI).
- **Nivel 3**: indicador visual semafórico en la UI.

| Color | Significado | Comportamiento |
|---|---|---|
| Verde | Internet OK + SRI responde | Transmisión inmediata de comprobantes y mensajes |
| Amarillo | Internet OK + SRI no responde | Comprobantes encolados. Alerta al Admin Contable si persiste >15 min |
| Rojo | Sin internet | Comprobantes y mensajes encolados. Operación offline normal |

## Backups (estrategia 3-2-1 adaptada)

- **Snapshot local**: cada hora durante horario operativo. Retención: últimos 24.
- **Backup diario**: al cierre del día. Destino: disco USB externo con rotación de 7 discos. Retención: 30 días.
- **Backup semanal**: domingos 23:00. Destino: almacenamiento cifrado en nube. Retención: 12 meses.
- **Backup fiscal de larga duración**: cierre mensual. Destino: nube cifrada + disco físico. Retención: 7 años (obligación SRI).

Objetivo de recuperación: <2 horas con hardware disponible.

## Operación offline

El sistema opera plenamente sin internet, excepto para tres operaciones:

1. Transmisión al SRI (factura encolada hasta recuperar conexión, ticket provisional al cliente con clave de acceso).
2. Envío de mensajes al cliente (email/WhatsApp en Fase 2).
3. Backup semanal a nube.

La "operación offline" en este sistema significa "sin internet, pero con red local funcional". Si la red local falla, el sistema deja de operar.

## Seguridad (capas)

1. Cifrado en reposo (LUKS o equivalente en el volumen de datos).
2. Cifrado en tránsito (TLS 1.2+ obligatorio).
3. Hashing de contraseñas con bcrypt vía passlib.
4. Certificados SRI cifrados con clave adicional, accesible solo a backend y Super Admin.
5. Backups cifrados antes de salir del servidor.
6. Logs de acceso a datos sensibles activos.
7. Mínimo privilegio en roles de base de datos.

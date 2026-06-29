# osiris-menu-be · Asiringui

Backend del sistema operativo integral del restaurante-cervecería Asiringui, en Cuenca, Ecuador. Apertura prevista Q3 2026. Local familiar de ~60 plazas en 4 zonas (Barra, Primer piso, Segundo piso, Jardín), operación martes a domingo.

El frontend vive en el repo `osiris-menu-fe`. Las decisiones de negocio del sistema completo son únicas y se documentan aquí.

## Stack obligatorio

| Capa | Tecnología | Nota |
|---|---|---|
| Lenguaje | Python 3.11+ | Alineado con `osiris-inventario-be`. |
| Dependencias | Poetry | Gestión de dependencias y entorno del backend. |
| Framework web | FastAPI | Decisión cerrada T-15. No usar Django ni Flask. |
| Servidor ASGI | Uvicorn | Ejecución del backend FastAPI. |
| Base de datos | PostgreSQL 16 | Base transaccional principal. |
| ORM | SQLAlchemy 2.x async + Alembic | SQLAlchemy async para runtime; Alembic para migraciones. |
| Driver DB | asyncpg | Driver PostgreSQL async. |
| Validación | Pydantic v2 | Schemas de API y validación de datos. |
| Settings | pydantic-settings | Configuración por variables de entorno. |
| WebSockets | Nativos en FastAPI | No Socket.IO ni librerías externas. |
| Hashing | passlib + bcrypt | Obligatorio para passwords. |
| Auth/JWT | python-jose | Firmado y validación de tokens si aplica. |
| Cripto | cryptography | Certificados SRI y operaciones criptográficas. |
| PDF | ReportLab o WeasyPrint | Según necesidad de comprobantes/reportes. |
| Excel | openpyxl | Exportaciones operativas/reportes cuando aplique. |
| HTTP client | httpx | Integraciones externas, SRI u otros servicios. |
| Testing | pytest + pytest-asyncio + pytest-cov | Unit e integración. |
| Lint/format | ruff | `ruff check` y `ruff format`. |
| Tareas programadas | APScheduler | Jobs locales programados. No Celery. |
| Cache/estado operativo liviano | Redis async | Cache, estado efímero o coordinación local. No dependencia cloud. |
| Contenedores | Docker + Docker Compose | Un único compose raíz levanta backend, frontend, PostgreSQL y Redis. |

No introducir librerías nuevas sin justificación explícita.

## Arquitectura física y entorno de ejecución

* Un único servidor local en el restaurante con doble rol: aloja backend, base de datos, frontend servido y actúa como computadora de caja.
* El sistema se implementa con Docker desde el inicio.
* En desarrollo debe existir un único `docker-compose.yml` en la raíz del workspace que levante:

  - `postgres`

  - `redis`

  - `api`

  - `web`

* Backend, frontend y servicios de infraestructura se levantan juntos con:

```bash

docker compose up --build

* No crear docker-compose separados por repo como flujo principal.
* En producción se podrá decidir si mantener Docker Compose o migrar a despliegue gestionado por systemd, pero el MVP de desarrollo se construye y valida con Docker.
* Backend y PostgreSQL se comunican por red interna Docker.
* El frontend consume el backend por VITE_API_URL en navegador y por VITE_API_PROXY_TARGET=http://api:8000 dentro de Docker.
* HTTPS/TLS y WSS son obligatorios para operación real/remota; en desarrollo local pueden usarse HTTP/WS.

## Principios no negociables

Estos 10 principios prevalecen sobre cualquier decisión técnica oportunista:

1. **Trazabilidad total**: toda acción material queda en log append-only con usuario, timestamp, contexto y motivo cuando aplica.
2. **Inmutabilidad fiscal**: una factura emitida nunca se modifica; corrección solo vía nota de crédito.
3. **Operación offline resiliente**: el sistema opera sin internet; solo SRI, email/WhatsApp y backup-nube requieren conectividad.
4. **Cumplimiento como propiedad emergente**: el operador cumple SRI/LOPDP/IESS por usar el sistema correctamente, sin saber los detalles legales.
5. **Cumplimiento por defecto**: ante ambigüedad, el default es la opción más estricta normativamente.
6. **Mínimo privilegio**: acciones sensibles requieren autorización adicional con motivo registrado.
7. **Configuración trazable**: cada cambio de parámetro queda en log con valor anterior y nuevo.
8. **Evolución sin migración**: el MVP soporta extensiones de Fase 2 (auto-pedido QR, WhatsApp Business API) sin rediseño.
9. **Transparencia con el operador**: el operador siempre ve el estado real del sistema (semáforo de conectividad, cola pendiente, tiempos).
10. **Validación rigurosa antes de producción**: nada llega a producción sin tests unitarios e integración con SRI sandbox.

Si una propuesta de cambio viola un principio, el principio gana. Si crees que hay que suspender un principio, documéntalo como decisión D-XX nueva.

## Roles del sistema

| Rol | Función principal |
|---|---|
| **Super Admin** | Familiar técnico (cónyuge de la PO). Mantenimiento, custodia de credenciales fiscales. NO es socio. |
| **Admin Socio** | Cualquiera de los 3 hermanos. Gestión de negocio, autorización Nivel 4. |
| **Admin Contable** | Hermana titular del RUC. Gestión fiscal. |
| **Cajero / Barman** | Cobro, facturación, cierre de caja, atención de barra. |
| **Mesero** | Toma de comandas, atención de sala. |
| **Chef** | Gestión de cocina. |
| **Ayudante** | Apoyo en cocina. |

**Padres como unidad conjunta**: una sola voz societaria, plenos derechos sobre toda la información del sistema incluida nómina. Operativamente acceden con credenciales Admin Socio.

## Niveles de autorización

| Nivel | Roles que lo cumplen |
|---|---|
| 1 | Cualquier operador autenticado |
| 2 | Cajero, Admin Socio, Admin Contable, Super Admin |
| 3 | Admin Socio, Admin Contable, Super Admin |
| 4 | Admin Socio, Super Admin |

## Decisiones cerradas

Identificadores N-XX (negocio de discovery), T-XX (técnico de discovery), D-XX (funcionales post-discovery). Detalle completo en `openspec/decisions.md`. Tabla resumen de las D-XX más estructurantes:

| ID | Asunto | Módulos impactados |
|---|---|---|
| D-01 | Modelo híbrido dos capas para descuento de inventario (reserva teórica al Enviado, consumo confirmado al pasar a En preparación) | §21, §22, §26, §30 |
| D-02 | Matriz formal de anulación de ítems por rol y estado | §21, §22, §23, §24 |
| D-03 | Ruteo único por ítem vendible; productos mixtos se modelan como combos con componentes separados | §21, §22, §25, §26 |
| D-04 | QR como identificador lógico permanente de mesa; no se reutilizan identificadores | §20, §32 |
| D-05 | Verificación explícita de reserva al abrir comanda sobre mesa Reservada | §20, §21, §28 |
| D-06 | Estado intermedio "En cierre" para desactivación gradual de zonas | §20, §28 |
| D-07 | Por limpiar → Libre configurable; cualquier operador sin autorización adicional | §20, §31 |
| D-08 | Siete reglas formales para traslado de comanda | §20, §21, §28 |
| D-09 | Cinco políticas fiscales y operativas para división de cuenta | §21, §23, §24 |
| D-10a | Estado "Rechazado" derivado de Entregado, mantiene consumo no factura | §21, §22, §23, §24, §26, §30 |
| D-10b | Anulación de comanda sin consumo con motivo y Nivel 2 | §21 |

Cuando aparezca durante la programación una decisión nueva no contemplada: **no inventarla en código**. Levantar como decisión nueva, documentarla en `openspec/decisions.md`, y luego continuar.

## Convenciones de código

- **PEP 8**. Formato con `ruff format`. Lint con `ruff check`.
- **Type hints obligatorios** en funciones públicas. Usar `from __future__ import annotations`.
- **snake_case** para variables/funciones, **PascalCase** para clases, **UPPER_CASE** para constantes de módulo.
- **Logging** con `logging` del stdlib (JSON estructurado en producción). Nunca `print()`.
- **Excepciones tipadas** (no `raise Exception` genérica). Excepciones de dominio en `shared/exceptions.py`.
- **Commits** convencionales: `feat:`, `fix:`, `chore:`, `docs:`, `test:`, `refactor:`.

## Convenciones de API

- Todo endpoint mutador acepta header **`X-Request-Id`** (UUID v4) para **idempotencia**. Tabla `request_ids_procesados` con TTL.
- Errores estructurados: `{ "error": { "code": string, "message": string, "details"?: object } }`.
- OpenAPI generado automáticamente por FastAPI; es el contrato público del backend.
- Versionado en path: `/api/v1/...`.

## Convenciones de testing

- **Sin tests, no se mergea**.
- Cada PR menciona en su descripción qué regla de negocio o D-XX cubre.
- `pytest` para unit + integration. Tests de integración con SRI usan el ambiente sandbox real del SRI.
- Cobertura mínima razonable. No perseguir 100% por sí mismo.

## Reglas de seguridad — no negociables

- **NUNCA** poner credenciales, claves, tokens, contraseñas, certificados en código ni en archivos versionados. Solo variables de entorno y `.env` ignorado por git.
- **NUNCA** loguear datos sensibles (contraseñas, tokens, datos fiscales completos, números de tarjeta).
- **NUNCA** `eval`, `exec` o equivalentes con input del usuario.
- **NUNCA** construir SQL con string formatting. Solo SQLAlchemy ORM o parámetros bindeados.
- **Hashing de contraseñas**: solo bcrypt vía passlib.
- **Sesión**: cookie httpOnly seteada por backend. No tokens en respuestas JSON ni accesibles desde JavaScript del cliente.

## Comunicación con el frontend

- **REST** vía HTTP/JSON (esquemas Pydantic, OpenAPI generado).
- **WebSockets** para eventos en tiempo real:
  - `mesas` — cambios de estado de mesa y zona.
  - `comandas:<comanda_id>` — cambios de comanda específica abierta.
  - `cocina` — ítems con ruteo cocina, no terminales.
  - `barra` — ítems con ruteo barra, no terminales.
  - `connectivity` — estado del semáforo de conectividad con SRI.
- **Latencia objetivo**: <500 ms desde evento en cliente origen hasta render en cliente destino, en red local.

## Estructura de carpetas del código

```
src/osiris/
├── main.py              ← entrypoint FastAPI
├── config.py            ← settings con pydantic-settings
├── db.py                ← engine, sesión, Base de SQLAlchemy
├── auth/                ← autenticación, niveles, logs
├── modules/
│   ├── mesas/           ← §20
│   ├── comandas/        ← §21
│   └── cocina_barra/    ← §22
├── websocket/           ← canales WS, broadcasting
└── shared/              ← excepciones, tipos comunes, helpers
```

Cada módulo en `modules/<nombre>/` tiene: `models.py`, `schemas.py`, `service.py`, `api.py`, `events.py`.

## Glosario

Términos canónicos del dominio. Detalle completo en `openspec/glossary.md`. Los más críticos:

- **Comanda** — pedido de un grupo de clientes a una o más mesas. Vive desde apertura hasta cierre con facturación.
- **Ítem de comanda** — línea individual dentro de una comanda con su propio ciclo de estados.
- **Grupo de Mesas** — agrupación lógica de 2+ mesas con una sola comanda compartida.
- **Combo** — producto vendible compuesto por componentes con ruteo independiente (D-03).
- **Tablet fija** — dispositivo de 12-13" montado fijo en cocina o barra (no "pantalla" como genérico).
- **Vista operativa de cocina / barra** — pantalla de la app filtrada por ruteo, en la tablet fija correspondiente.
- **Personal de cocina o barra** — Chef + Ayudante (cocina) o Barman (barra).
- **Reserva teórica / Consumo confirmado** — modelo híbrido de inventario (D-01). Reserva al Enviado, consumo al pasar a En preparación.
- **Offline** — sin internet pero con red local funcional. Si la red local cae, el sistema deja de operar.

## Referencias rápidas

- Decisiones detalladas: `openspec/decisions.md`
- Glosario extendido: `openspec/glossary.md`
- Specs de referencia previas al desarrollo (input para proposals de los módulos del MVP): `openspec/reference-specs/`
  - `20-mesas.md`
  - `21-comandas.md`
  - `22-cocina-barra.md`
- Convenciones específicas del repo (estructura de carpetas, comandos `npm`/`uv`, qué NO hacer): `CLAUDE.md` (raíz)

## Qué NO hacer

- No introducir frameworks adicionales (Celery, Redis, Django) sin justificación explícita.
- No quitar Docker ni romper el `docker-compose.yml` raíz.
- No crear un compose independiente para backend o frontend que contradiga el compose raíz.
- No introducir microservicios. El sistema es monolito modular.
- No depender de servicios cloud para operación crítica diaria.
- No mockear el SRI con datos falsos en producción; usar sandbox real para integración.
- No commitear `.env`, certificados, ni datos reales de empleados o clientes.
- No agregar ítems al frontend sin actualizar primero la spec si la spec ya existe.
- No reutilizar identificadores de mesa eliminados (D-04).
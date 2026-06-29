## ADDED Requirements

### Requirement: Aplicación FastAPI con versionado de API

El backend MUST exponer una aplicación FastAPI cuyos endpoints de dominio vivan bajo el prefijo de path `/api/v1`. El versionado MUST estar en el path, no en headers ni en query.

#### Scenario: Routers montados bajo /api/v1

- **WHEN** se inspeccionan las rutas registradas de la aplicación
- **THEN** todos los routers de dominio están montados bajo el prefijo `/api/v1`

### Requirement: Endpoint de salud

El backend MUST exponer un endpoint `GET /health` que responda `200` con un cuerpo JSON que indique el estado del servicio. Este endpoint NO requiere autenticación.

#### Scenario: Health responde OK

- **WHEN** un cliente hace `GET /health`
- **THEN** recibe `200` con un JSON que reporta el servicio operativo

### Requirement: Documentación OpenAPI generada

El backend MUST generar y servir la especificación OpenAPI automáticamente vía FastAPI. La OpenAPI es el contrato público del backend.

#### Scenario: OpenAPI disponible

- **WHEN** un cliente hace `GET /openapi.json`
- **THEN** recibe un documento OpenAPI válido que describe los endpoints registrados

### Requirement: Configuración por variables de entorno

El backend MUST cargar su configuración con `pydantic-settings` desde variables de entorno (al menos `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, expiraciones de token, `APP_ENV`, `CORS_ORIGINS`). Los secretos MUST NOT estar embebidos en el código.

#### Scenario: Configuración leída del entorno

- **WHEN** la aplicación arranca con las variables de entorno definidas
- **THEN** los settings se cargan desde el entorno y no hay credenciales hardcodeadas en el código fuente

### Requirement: Capa de datos asíncrona

El backend MUST configurar SQLAlchemy 2.x async con driver `asyncpg`, una `Base` declarativa común y una dependencia de sesión async para los endpoints. Las migraciones MUST gestionarse con Alembic, incluyendo una baseline inicial.

#### Scenario: Sesión async disponible

- **WHEN** un endpoint solicita la dependencia de sesión de base de datos
- **THEN** recibe una sesión async de SQLAlchemy conectada vía asyncpg

#### Scenario: Alembic baseline presente

- **WHEN** se inspecciona el directorio de migraciones
- **THEN** existe una migración baseline aplicable con Alembic

### Requirement: Envelope de error estructurado

Todas las respuestas de error del backend MUST seguir el envelope `{ "error": { "code": string, "message": string, "details"?: object } }`. Las excepciones de dominio MUST ser tipadas y vivir en `shared/exceptions.py`, mapeadas a este envelope por un handler global.

#### Scenario: Error de dominio devuelve envelope

- **WHEN** un endpoint lanza una excepción de dominio tipada
- **THEN** la respuesta HTTP contiene el envelope con `code` y `message`, y opcionalmente `details`

### Requirement: Idempotencia por X-Request-Id en mutadores

Todo endpoint mutador MUST aceptar el header `X-Request-Id` (UUID v4) para idempotencia. La política inicial del scaffolding es de **rechazo**: un `X-Request-Id` ya procesado MUST NOT ejecutar el efecto de nuevo y el backend MUST responder `409` con el código de dominio `IDEMPOTENCY_KEY_REUSED` en el envelope de error. En esta etapa el backend MUST NOT intentar reconstruir ni devolver la respuesta original. El registro de claves vistas se respalda en una tabla `request_ids_procesados` con TTL.

#### Scenario: Request duplicado se rechaza con 409

- **WHEN** un cliente envía dos mutaciones con el mismo `X-Request-Id`
- **THEN** la primera se procesa y la segunda recibe `409` con `code` `IDEMPOTENCY_KEY_REUSED`, sin producir un segundo cambio de estado

### Requirement: Seguridad base de sesión y secretos

El backend MUST NOT devolver tokens accesibles por JavaScript del cliente; la sesión MUST basarse en cookie `httpOnly` seteada por el backend. Los passwords (cuando apliquen) MUST hashearse solo con bcrypt vía passlib. MUST NOT loguearse datos sensibles.

#### Scenario: Sesión por cookie httpOnly

- **WHEN** el backend establece una sesión autenticada
- **THEN** lo hace mediante cookie `httpOnly` y no expone el token en el cuerpo JSON de la respuesta

### Requirement: Stack de dependencias del backend

El `pyproject.toml` MUST declarar el stack obligatorio de `project.md`, incluyendo además de FastAPI/Uvicorn/SQLAlchemy/asyncpg/Alembic/Pydantic/pydantic-settings/python-jose/passlib[bcrypt]/bcrypt/redis/httpx/pytest/ruff: `cryptography`, `ReportLab` o `WeasyPrint`, `openpyxl` y `APScheduler`. `APScheduler` MUST declararse como dependencia disponible, pero en esta etapa MUST NOT configurarse ningún job ni scheduler en el arranque.

#### Scenario: Stack obligatorio declarado

- **WHEN** se inspecciona `pyproject.toml`
- **THEN** están declaradas `cryptography`, `ReportLab` o `WeasyPrint`, `openpyxl` y `APScheduler` junto al resto del stack obligatorio

#### Scenario: APScheduler sin jobs en scaffolding

- **WHEN** la aplicación arranca en esta etapa
- **THEN** no se inicializa ningún scheduler ni job programado, aunque la dependencia esté disponible

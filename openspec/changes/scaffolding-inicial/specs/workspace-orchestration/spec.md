## ADDED Requirements

### Requirement: Docker Compose raíz único

El workspace `osiris-menu/` MUST tener un único `docker-compose.yml` en su raíz que levante los servicios `postgres`, `redis`, `api` y `web`. MUST NOT existir archivos compose por repo que compitan con éste como flujo de desarrollo (T-35, project.md).

#### Scenario: Levantar el sistema completo con un solo comando

- **WHEN** un desarrollador ejecuta `docker compose up --build` desde la raíz del workspace
- **THEN** se construyen y arrancan los cuatro servicios `postgres`, `redis`, `api` y `web` sin pasos manuales adicionales

#### Scenario: No hay compose competidor

- **WHEN** se inspeccionan `osiris-menu-be/` y `osiris-menu-fe/`
- **THEN** ninguno define un `docker-compose.yml` propio que se use como flujo de desarrollo principal

### Requirement: Healthchecks y orden de arranque

Los servicios `postgres` y `redis` MUST declarar healthcheck, y el servicio `api` MUST depender de ambos con condición `service_healthy`. El servicio `web` MUST depender de `api`.

#### Scenario: API espera dependencias sanas

- **WHEN** se levanta el compose y `postgres`/`redis` aún no están listos
- **THEN** el servicio `api` no arranca hasta que ambos healthchecks reporten estado saludable

### Requirement: Red interna y exposición de puertos

Los servicios MUST comunicarse por la red interna Docker usando nombres de servicio (`postgres`, `redis`, `api`). `api` MUST exponerse en el host en `8000` y `web` en `5173`. Postgres MUST mapearse a `5433:5432` en el host.

#### Scenario: Frontend consume backend dentro de Docker

- **WHEN** el servicio `web` resuelve `VITE_API_PROXY_TARGET=http://api:8000`
- **THEN** alcanza al backend por la red interna Docker sin pasar por el host

### Requirement: Dockerfile de backend

`osiris-menu-be` MUST incluir un `Dockerfile` basado en `python:3.11-slim` que instale dependencias con Poetry y ejecute el backend con Uvicorn sobre el entrypoint de FastAPI. El layout de import MUST ser único y consistente con `src/osiris/main.py`.

#### Scenario: Imagen de backend construye y sirve

- **WHEN** se construye la imagen del servicio `api` y arranca el contenedor
- **THEN** Uvicorn sirve la aplicación FastAPI en el puerto `8000`

### Requirement: Dockerfile de frontend

`osiris-menu-fe` MUST incluir un `Dockerfile` que instale dependencias del proyecto y ejecute el servidor de desarrollo Vite en el puerto `5173`.

#### Scenario: Imagen de frontend construye y sirve

- **WHEN** se construye la imagen del servicio `web` y arranca el contenedor
- **THEN** Vite sirve la aplicación en el puerto `5173`

### Requirement: Configuración base de entorno

El workspace MUST incluir un `.env.example` con todas las variables requeridas por los servicios (incluyendo `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, expiraciones de token, `APP_ENV`, `CORS_ORIGINS`, `VITE_API_URL`, `VITE_API_PROXY_TARGET`). El archivo `.env` real MUST NOT versionarse.

#### Scenario: Plantilla de entorno disponible y secreto ignorado

- **WHEN** un desarrollador copia `.env.example` a `.env`
- **THEN** dispone de todas las variables necesarias para levantar el compose, y `.env` está excluido por `.gitignore`

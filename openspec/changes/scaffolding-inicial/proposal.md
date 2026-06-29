## Why

El repositorio `osiris-menu-be` tiene el OpenSpec canónico (project.md, decisions.md, glossary.md, reference-specs) pero `src/` y `tests/` están vacíos, no existe `pyproject.toml`, ni Dockerfiles, ni el `docker-compose.yml` raíz del workspace, y `osiris-menu-fe` solo contiene su `CLAUDE.md`. Sin una base arquitectónica común, backend y frontend no pueden avanzar simultáneamente desde un mismo contrato.

Esta propuesta deja lista la arquitectura base, Docker, estructura de módulos, contratos técnicos y scaffolding inicial del frontend, sin implementar todavía el POS completo. Es el prerequisito de todas las propuestas funcionales posteriores (§20, §21, §22 y siguientes).

## What Changes

- **Workspace y orquestación**: un único `docker-compose.yml` en la raíz del workspace (`osiris-menu/`) que levanta `postgres`, `redis`, `api` y `web` con healthchecks, red interna Docker y `.env.example`. `Dockerfile` de backend (Poetry + Uvicorn) y `Dockerfile` de frontend (Vite). Flujo oficial `docker compose up --build` (T-35, project.md).
- **Backend foundation**: scaffolding de `src/osiris/` con `main.py`, `config.py` (pydantic-settings), `db.py` (SQLAlchemy 2.x async + asyncpg), `shared/` (excepciones de dominio tipadas, envelope de error), `auth/` (placeholder de niveles 1–4), versionado `/api/v1`, OpenAPI automático, endpoint `/health`, middleware/tabla de idempotencia para `X-Request-Id`, baseline de Alembic. `pyproject.toml` con el stack obligatorio.
- **Realtime foundation**: WebSockets nativos de FastAPI con connection manager y los cinco canales canónicos como scaffolding tipado (`mesas`, `comandas:<comanda_id>`, `cocina`, `barra`, `connectivity`). Sin lógica de negocio, solo el transporte y los contratos de payload base.
- **Scaffolding de módulos MVP**: estructura `modules/{mesas,comandas,cocina_barra}/` con `models.py`, `schemas.py`, `service.py`, `api.py`, `events.py`, `README.md` por módulo y routers vacíos/placeholder registrados bajo `/api/v1`. Los enums de estado y nombres canónicos provienen del glosario; las reglas de negocio NO se implementan aquí (quedan para propuestas por módulo).
- **Frontend foundation**: scaffolding de `osiris-menu-fe` (React 19 + TS estricto + Vite + Router + TanStack Query + Tailwind), cliente API base (Axios con interceptor `X-Request-Id` y manejo del envelope de error), cliente WebSocket base, y vistas placeholder enrutadas: Mesero, Cocina, Barra, Caja, Admin, Público QR.
- **Tests mínimos de arranque**: backend (`/health`, OpenAPI sirve, idempotencia rechaza `X-Request-Id` duplicado, ping de WebSocket); frontend (render de cada vista placeholder, cliente API instancia).
- No se cambia ninguna decisión funcional existente. No se introduce ninguna decisión D-XX nueva. No se duplican reglas de negocio en el frontend.

## Capabilities

### New Capabilities
- `workspace-orchestration`: `docker-compose.yml` raíz único, Dockerfiles de backend y frontend, `.env.example`, servicios `postgres`/`redis`/`api`/`web` con healthchecks y red interna Docker.
- `backend-foundation`: aplicación FastAPI base, configuración por entorno, capa de datos async, versionado `/api/v1`, OpenAPI, envelope de error estructurado, idempotencia por `X-Request-Id`, endpoint `/health` y baseline de migraciones.
- `realtime-foundation`: transporte WebSocket nativo con connection manager y los cinco canales canónicos como contrato base tipado.
- `mvp-modules-scaffolding`: estructura modular de §20 Mesas y zonas, §21 Comandas y §22 Cocina y barra con archivos y routers placeholder, sin reglas de negocio.
- `frontend-foundation`: scaffolding del frontend, cliente API base, cliente WebSocket base y vistas placeholder (Mesero, Cocina, Barra, Caja, Admin, Público QR).

### Modified Capabilities
<!-- Ninguna: openspec/specs/ está vacío; no hay capabilities previas cuyos requisitos cambien. -->

## Impact

- **Nuevo en `osiris-menu-be`**: `pyproject.toml`, `Dockerfile`, `alembic.ini`, `migrations/`, `scripts/`, `src/osiris/**`, `tests/**`.
- **Nuevo en la raíz del workspace `osiris-menu/`**: `docker-compose.yml`, `.env.example`.
- **Nuevo en `osiris-menu-fe`**: `package.json`, `vite.config.ts`, `Dockerfile`, `src/**` (cliente API, cliente WS, vistas placeholder, router), `tests/**`.
- **Dependencias**: stack backend y frontend definidos en `CLAUDE.md`/`project.md`; Postgres 16 y Redis 7 vía Docker.
- **Contratos públicos establecidos**: `/api/v1`, OpenAPI, envelope de error, header `X-Request-Id`, canales WebSocket. Las propuestas funcionales posteriores construyen sobre estos contratos sin redefinirlos.
- **Sin impacto fiscal ni de inventario**: módulos fuera de alcance (SRI, Caja, Inventario, Catálogo, Reservas, Reportes, WhatsApp, QR auto-pedido, Nómina/IESS, backups productivos, certificados SRI) no se implementan.

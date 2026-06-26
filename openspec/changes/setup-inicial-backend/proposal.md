## Why

El repo `osiris-menu-be` solo contiene documentación (`CLAUDE.md`, `openspec/`): no existe todavía código ni tooling Python. Antes de poder implementar cualquier módulo de negocio (§20 mesas, §21 comandas, §22 cocina-barra) se necesita una base ejecutable, con estructura, configuración y testing reproducibles, que todos los cambios posteriores hereden. Este cambio establece esa base.

## What Changes

- Inicializar el proyecto Python con **uv** y `pyproject.toml` (Python 3.12+), declarando solo las dependencias base del scaffolding: FastAPI, Uvicorn, Pydantic + pydantic-settings, pytest. (ORM, Alembic, auth y WebSockets quedan fuera de alcance — serán cambios separados.)
- Crear el paquete `src/osiris/` con `__init__.py`, `main.py` (app FastAPI mínima) y `config.py` (settings tipados con pydantic-settings).
- Exponer un endpoint de salud `GET /health` que devuelve estado del servicio, para verificación operativa y readiness.
- Definir el contrato base de **errores estructurados** (`{ "error": { "code", "message", "details?" } }`) y el versionado de API en path (`/api/v1/...`) como convención del scaffolding, sin endpoints de negocio aún.
- Configurar **ruff** (format + check) y **pytest** con un test de humo que arranca la app y verifica `/health`.
- Añadir `.env.example` con las variables no sensibles base (entorno, host/puerto, nivel de log) y asegurar que `.env` está ignorado por git.
- Documentar en `README.md` cómo instalar (`uv sync`), correr (`uv run`), testear (`pytest`) y lintar (`ruff`).

Sin alcance en este cambio: PostgreSQL/SQLAlchemy/Alembic, autenticación y sesión, canales WebSocket, integración SRI, módulos de negocio. Cada uno será su propia propuesta sobre esta base.

## Capabilities

### New Capabilities
- `backend-scaffolding`: estructura ejecutable mínima del backend — proyecto uv/pyproject, paquete `src/osiris/`, app FastAPI con `/health`, settings tipados, contrato base de errores y versionado, tooling de lint (ruff) y testing (pytest), `.env.example` y README de operación.

### Modified Capabilities
<!-- Ninguna: no existen specs de capacidades previas en openspec/specs/. -->

## Impact

- **Código nuevo**: `pyproject.toml`, `uv.lock`, `src/osiris/__init__.py`, `src/osiris/main.py`, `src/osiris/config.py`, `src/osiris/shared/` (errores base), `tests/`, `ruff.toml` (o sección en `pyproject.toml`), `.env.example`, `README.md`.
- **Dependencias nuevas**: FastAPI, Uvicorn, Pydantic, pydantic-settings, pytest, ruff, httpx (cliente de test). Todas dentro del stack ya aprobado en `project.md`/`CLAUDE.md`.
- **Sistemas**: ninguna integración externa todavía; corre 100% local. No toca SRI, ni base de datos, ni red.
- **Convenciones establecidas**: estructura de carpetas de `project.md`, contrato de errores y versionado `/api/v1` que todos los módulos posteriores reutilizarán.
- **Sin breaking changes**: es la primera unidad de código del repo.

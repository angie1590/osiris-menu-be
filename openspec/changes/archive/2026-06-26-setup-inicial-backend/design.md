## Context

`osiris-menu-be` no tiene código todavía: solo `CLAUDE.md`, `.gitignore` y `openspec/`. `project.md` ya cierra el stack (Python 3.12+, FastAPI, PostgreSQL, SQLAlchemy+Alembic, Pydantic, WS nativos, pytest, sin Docker, systemd) y las convenciones (errores estructurados, `/api/v1`, `X-Request-Id`, cookie httpOnly, logging stdlib JSON). Este cambio crea la **base ejecutable mínima** que el resto de cambios hereda. El alcance fue acotado explícitamente a *scaffolding base*: no incluye base de datos, autenticación, WebSockets ni módulos de negocio (cada uno será su propia propuesta sobre esta base).

La arquitectura física es un único host Linux que corre el backend nativo bajo systemd; la conexión a Postgres será intra-host. Eso refuerza decisiones simples y sin contenedores.

## Goals / Non-Goals

**Goals:**
- Proyecto Python reproducible con `uv` + `pyproject.toml` (Python 3.12+).
- App FastAPI importable (`osiris.main:app`) que arranca con Uvicorn y expone `/health`.
- Configuración tipada con `pydantic-settings` y `.env.example` versionado (`.env` ignorado).
- Contrato base de errores `{ "error": { code, message, details? } }` y prefijo `/api/v1` listos para reutilizar.
- Tooling de calidad: `ruff` (format + check) y `pytest` con test de humo.
- `README.md` con los comandos de operación.

**Non-Goals:**
- PostgreSQL, SQLAlchemy, Alembic y migraciones (cambio aparte).
- Autenticación, sesión por cookie httpOnly, niveles de autorización (cambio aparte).
- Canales WebSocket y broadcasting (cambio aparte).
- Integración SRI, logging JSON de producción completo, despliegue systemd/CI.
- Cualquier endpoint o modelo de negocio (§20/§21/§22).

## Decisions

**D1 — Gestor de paquetes: `uv` con `pyproject.toml` (PEP 621).**
`CLAUDE.md`/`project.md` ya mencionan `uv`. `uv` da resolución rápida y `uv.lock` reproducible sin capas extra. *Alternativas*: Poetry (más pesado, segundo lockfile propietario), pip + requirements.txt (sin lock determinista nativo). Se elige `uv` por velocidad y lockfile estándar.

**D2 — Layout `src/` con paquete `osiris`.**
Se sigue la estructura ya definida en `project.md`: `src/osiris/{__init__,main,config}.py` y `src/osiris/shared/` para excepciones/helpers comunes. El layout `src/` evita imports accidentales del árbol de trabajo y obliga a instalar el paquete. *Alternativa*: paquete plano en raíz — descartado por las trampas de import y porque la estructura ya está fijada.

**D3 — Configuración con `pydantic-settings` (`Settings` cacheado).**
`config.py` define una clase `Settings(BaseSettings)` con `environment`, `host`, `port`, `log_level` y `api_prefix="/api/v1"`, leyendo de entorno y `.env`. Se expone vía un accessor cacheado (`@lru_cache`) para inyección y testeo. *Alternativa*: leer `os.environ` directo — descartado por falta de validación/tipado.

**D4 — Manejo de errores centralizado desde el día uno.**
Se define `shared/exceptions.py` con una excepción de dominio base y un `exception_handler` registrado en `main.py` que serializa al contrato `{ "error": { code, message, details? } }`. También se normalizan las respuestas de `HTTPException`/404 a ese shape. Hacerlo ahora evita que cada módulo reinvente el formato. *Alternativa*: posponer hasta el primer módulo — descartado porque el contrato es transversal y barato de fijar ya.

**D5 — `/health` sin versionar; negocio bajo `/api/v1`.**
`/health` queda en la raíz (probe de readiness simple, estable entre versiones). Los routers de negocio se montarán bajo `settings.api_prefix`. En este cambio se crea el `APIRouter` v1 vacío (o solo se fija la convención) sin endpoints de negocio.

**D6 — Testing con `pytest` + `httpx`/`TestClient`.**
Test de humo que instancia la app y verifica `GET /health` → `200 {status: ok}`. `httpx` (vía Starlette `TestClient`) ya es la vía estándar con FastAPI. *Alternativa*: requests — innecesario, httpx cubre sync/async.

**D7 — Configuración de `ruff` en `pyproject.toml`.**
Una sola fuente de config (sección `[tool.ruff]`) en vez de `ruff.toml` separado, para mantener todo el tooling en un archivo. Reglas alineadas con PEP 8 y las convenciones de `project.md` (type hints, `from __future__ import annotations`).

## Risks / Trade-offs

- **Sobre-ingeniería temprana del contrato de errores** → Mitigación: mantenerlo mínimo (una excepción base + un handler), documentado, sin jerarquías especulativas; crece cuando los módulos lo necesiten.
- **Fijar dependencias que luego cambian de versión** → Mitigación: `uv.lock` versionado; rangos abiertos razonables en `pyproject.toml`; actualizaciones explícitas vía `uv lock --upgrade`.
- **`/health` demasiado trivial para readiness real** → Mitigación: aceptable ahora (no hay dependencias externas); cuando entren DB/SRI se ampliará a un readiness con checks, como cambio futuro.
- **Divergencia entre estructura documentada y creada** → Mitigación: las tareas siguen literalmente el layout de `project.md`; cualquier desvío se registra como decisión.

## Migration Plan

No aplica migración de datos ni rollback complejo: es la primera unidad de código del repo. Despliegue = merge del PR. Rollback = revertir el commit. La ejecución en producción (systemd) se define en un cambio posterior de infraestructura.

## Open Questions

- ¿El `APIRouter` `/api/v1` se crea vacío ahora o se difiere al primer módulo? Default propuesto: dejar la convención y el montaje listos, sin endpoints, para que el primer módulo solo añada su router.
- Nivel de log por defecto (`INFO` vs `DEBUG`) en dev — default propuesto: `INFO`, sobrescribible por `.env`.

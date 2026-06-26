## 1. Inicialización del proyecto (uv + pyproject)

- [x] 1.1 Crear `pyproject.toml` (PEP 621) con `requires-python = ">=3.12"`, metadatos del paquete `osiris` y layout `src/`.
- [x] 1.2 Declarar dependencias base: `fastapi`, `uvicorn[standard]`, `pydantic`, `pydantic-settings`.
- [x] 1.3 Declarar dependencias de desarrollo (grupo dev): `pytest`, `httpx`, `ruff`.
- [x] 1.4 Ejecutar `uv sync` y verificar que genera/actualiza `uv.lock` y crea el entorno sin errores.
- [x] 1.5 Verificar que `.env`, `.venv` y artefactos de build están cubiertos por `.gitignore` (ajustar si falta `.env`).

## 2. Estructura del paquete `osiris`

- [x] 2.1 Crear `src/osiris/__init__.py`.
- [x] 2.2 Crear `src/osiris/config.py` con `Settings(BaseSettings)` (`environment`, `host`, `port`, `log_level`, `api_prefix="/api/v1"`) y accessor cacheado (`@lru_cache`).
- [x] 2.3 Crear `src/osiris/shared/__init__.py` y `src/osiris/shared/exceptions.py` con una excepción de dominio base.
- [x] 2.4 Crear `.env.example` con variables no sensibles base (entorno, host, puerto, nivel de log) y comentarios.

## 3. Aplicación FastAPI

- [x] 3.1 Crear `src/osiris/main.py` con la instancia `app = FastAPI(...)` y carga de `Settings`.
- [x] 3.2 Implementar `GET /health` que responda `200` con `{ "status": "ok" }` (sin auth, sin deps externas).
- [x] 3.3 Montar un `APIRouter` base bajo `settings.api_prefix` (`/api/v1`), sin endpoints de negocio.
- [x] 3.4 Registrar el manejador de excepciones que serializa al contrato `{ "error": { "code", "message", "details"? } }`, incluyendo normalización de `HTTPException`/404.
- [x] 3.5 Verificar arranque manual con `uv run uvicorn osiris.main:app` y que `/openapi.json` responde `200`.

## 4. Tooling de calidad (ruff)

- [x] 4.1 Añadir sección `[tool.ruff]` en `pyproject.toml` alineada con PEP 8 y convenciones de `project.md` (incl. `from __future__ import annotations`).
- [x] 4.2 Ejecutar `uv run ruff format .` y `uv run ruff check .`; corregir hasta salida limpia (código 0).

## 5. Testing

- [x] 5.1 Crear `tests/__init__.py` y configuración mínima de pytest (sección `[tool.pytest.ini_options]` en `pyproject.toml`).
- [x] 5.2 Crear `tests/test_health.py`: test de humo que arranca la app (TestClient/httpx), solicita `GET /health` y verifica `200` + `{ "status": "ok" }`.
- [x] 5.3 Añadir un test que verifique que una ruta inexistente devuelve el contrato de error estructurado.
- [x] 5.4 Ejecutar `uv run pytest` y verificar suite en verde (código 0).

## 6. Documentación

- [x] 6.1 Crear/actualizar `README.md` con instalación (`uv sync`), arranque (`uv run uvicorn osiris.main:app`), tests (`uv run pytest`) y lint (`uv run ruff check .`).
- [x] 6.2 Verificación final: `uv sync`, `ruff check`, `pytest` y arranque manual pasan en un checkout limpio.
- [x] 6.3 Verificar que uv.lock queda commiteado en git (no en .gitignore).

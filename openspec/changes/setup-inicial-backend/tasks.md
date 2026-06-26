## 1. Inicialización del proyecto (uv + pyproject)

- [ ] 1.1 Crear `pyproject.toml` (PEP 621) con `requires-python = ">=3.12"`, metadatos del paquete `osiris` y layout `src/`.
- [ ] 1.2 Declarar dependencias base: `fastapi`, `uvicorn[standard]`, `pydantic`, `pydantic-settings`.
- [ ] 1.3 Declarar dependencias de desarrollo (grupo dev): `pytest`, `httpx`, `ruff`.
- [ ] 1.4 Ejecutar `uv sync` y verificar que genera/actualiza `uv.lock` y crea el entorno sin errores.
- [ ] 1.5 Verificar que `.env`, `.venv` y artefactos de build están cubiertos por `.gitignore` (ajustar si falta `.env`).

## 2. Estructura del paquete `osiris`

- [ ] 2.1 Crear `src/osiris/__init__.py`.
- [ ] 2.2 Crear `src/osiris/config.py` con `Settings(BaseSettings)` (`environment`, `host`, `port`, `log_level`, `api_prefix="/api/v1"`) y accessor cacheado (`@lru_cache`).
- [ ] 2.3 Crear `src/osiris/shared/__init__.py` y `src/osiris/shared/exceptions.py` con una excepción de dominio base.
- [ ] 2.4 Crear `.env.example` con variables no sensibles base (entorno, host, puerto, nivel de log) y comentarios.

## 3. Aplicación FastAPI

- [ ] 3.1 Crear `src/osiris/main.py` con la instancia `app = FastAPI(...)` y carga de `Settings`.
- [ ] 3.2 Implementar `GET /health` que responda `200` con `{ "status": "ok" }` (sin auth, sin deps externas).
- [ ] 3.3 Montar un `APIRouter` base bajo `settings.api_prefix` (`/api/v1`), sin endpoints de negocio.
- [ ] 3.4 Registrar el manejador de excepciones que serializa al contrato `{ "error": { "code", "message", "details"? } }`, incluyendo normalización de `HTTPException`/404.
- [ ] 3.5 Verificar arranque manual con `uv run uvicorn osiris.main:app` y que `/openapi.json` responde `200`.

## 4. Tooling de calidad (ruff)

- [ ] 4.1 Añadir sección `[tool.ruff]` en `pyproject.toml` alineada con PEP 8 y convenciones de `project.md` (incl. `from __future__ import annotations`).
- [ ] 4.2 Ejecutar `uv run ruff format .` y `uv run ruff check .`; corregir hasta salida limpia (código 0).

## 5. Testing

- [ ] 5.1 Crear `tests/__init__.py` y configuración mínima de pytest (sección `[tool.pytest.ini_options]` en `pyproject.toml`).
- [ ] 5.2 Crear `tests/test_health.py`: test de humo que arranca la app (TestClient/httpx), solicita `GET /health` y verifica `200` + `{ "status": "ok" }`.
- [ ] 5.3 Añadir un test que verifique que una ruta inexistente devuelve el contrato de error estructurado.
- [ ] 5.4 Ejecutar `uv run pytest` y verificar suite en verde (código 0).

## 6. Documentación

- [ ] 6.1 Crear/actualizar `README.md` con instalación (`uv sync`), arranque (`uv run uvicorn osiris.main:app`), tests (`uv run pytest`) y lint (`uv run ruff check .`).
- [ ] 6.2 Verificación final: `uv sync`, `ruff check`, `pytest` y arranque manual pasan en un checkout limpio.
- [ ] 6.3 Verificar que uv.lock queda commiteado en git (no en .gitignore).

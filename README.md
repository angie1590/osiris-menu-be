# Asiringui · osiris-menu-be

Backend del sistema operativo integral del restaurante-cervecería **Asiringui**
(Cuenca, Ecuador). API y servicios construidos con FastAPI sobre Python 3.12+.

El contexto de negocio, el stack obligatorio y los principios no negociables
están en [`CLAUDE.md`](./CLAUDE.md). Las specs de negocio viven en `openspec/`.

## Requisitos

- **Python 3.12+**
- **[uv](https://docs.astral.sh/uv/)** como gestor de paquetes y entornos.

## Instalación

```bash
uv sync
```

Esto crea el entorno virtual (`.venv/`) e instala las dependencias exactas
fijadas en `uv.lock` (incluido el grupo de desarrollo).

## Arranque

```bash
uv run uvicorn osiris.main:app --app-dir src --reload --port 8000
```

> `--app-dir src` añade `src/` al path de importación. Es necesario aquí porque
> la ruta del proyecto contiene un espacio (`Osiris Menu`), lo que impide que
> Python procese el editable install vía `.pth`. En un host sin espacios en la
> ruta (p. ej. `/opt/osiris` en producción) basta `uv run uvicorn osiris.main:app`.

Endpoints disponibles en el scaffolding:

- `GET /health` → `{ "status": "ok" }` (sin auth, para readiness).
- `GET /openapi.json` → esquema OpenAPI generado por FastAPI.
- `GET /docs` → documentación interactiva (Swagger UI).

La API de negocio se servirá bajo el prefijo de versión `/api/v1` (vacío aún).

## Configuración

La configuración se carga con `pydantic-settings` desde variables de entorno
(prefijo `OSIRIS_`) y desde un archivo `.env` opcional. Copia la plantilla:

```bash
cp .env.example .env
```

| Variable             | Por defecto   | Descripción                     |
| -------------------- | ------------- | ------------------------------- |
| `OSIRIS_ENVIRONMENT` | `development` | Entorno de ejecución            |
| `OSIRIS_HOST`        | `127.0.0.1`   | Host de escucha                 |
| `OSIRIS_PORT`        | `8000`        | Puerto de escucha               |
| `OSIRIS_LOG_LEVEL`   | `INFO`        | Nivel de log                    |

> `.env` está ignorado por git; nunca se versionan secretos.

## Contrato de errores

Todos los errores se devuelven con el formato:

```json
{ "error": { "code": "not_found", "message": "Not Found", "details": {} } }
```

`details` es opcional. Los módulos de negocio reutilizan este contrato lanzando
subclases de `osiris.shared.exceptions.OsirisError`.

## Tests

```bash
uv run pytest
```

## Lint y formato

```bash
uv run ruff check .     # linting
uv run ruff format .    # formateo
```

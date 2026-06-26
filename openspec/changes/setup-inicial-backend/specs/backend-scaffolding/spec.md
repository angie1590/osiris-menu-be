## ADDED Requirements

### Requirement: Proyecto Python inicializado con uv

El sistema SHALL proveer un proyecto Python gestionado con `uv` y un `pyproject.toml` que declare Python 3.12+ y únicamente las dependencias base del scaffolding (FastAPI, Uvicorn, Pydantic, pydantic-settings) más las de desarrollo (pytest, ruff, httpx). El proyecto SHALL ser instalable de forma reproducible mediante un archivo de bloqueo versionado.

#### Scenario: Instalación reproducible desde cero

- **WHEN** un desarrollador clona el repo y ejecuta `uv sync` sobre un entorno limpio
- **THEN** se crea el entorno virtual con exactamente las versiones del archivo de bloqueo y el comando termina con código de salida 0

#### Scenario: Versión mínima de Python respetada

- **WHEN** se intenta instalar el proyecto con una versión de Python anterior a 3.12
- **THEN** `uv` rechaza la instalación indicando el requisito `>=3.12`

### Requirement: Aplicación FastAPI ejecutable

El sistema SHALL exponer una aplicación FastAPI importable desde `osiris.main` que pueda arrancarse con Uvicorn. La aplicación SHALL servir todos los endpoints de negocio futuros bajo el prefijo de versión `/api/v1`.

#### Scenario: La app arranca

- **WHEN** se ejecuta `uv run uvicorn osiris.main:app`
- **THEN** el servidor inicia sin errores y queda escuchando en el host y puerto configurados

#### Scenario: Documentación OpenAPI disponible

- **WHEN** un cliente solicita `GET /openapi.json` con la app corriendo
- **THEN** el servidor responde `200` con el esquema OpenAPI generado por FastAPI

### Requirement: Endpoint de salud

El sistema SHALL exponer `GET /health` que reporte que el servicio está operativo, sin requerir autenticación ni dependencias externas.

#### Scenario: Servicio operativo

- **WHEN** un cliente solicita `GET /health`
- **THEN** el servidor responde `200` con un cuerpo JSON que incluye un campo de estado (p. ej. `{ "status": "ok" }`)

### Requirement: Configuración tipada por entorno

El sistema SHALL cargar su configuración mediante `pydantic-settings`, tomando valores de variables de entorno y de un archivo `.env` opcional. SHALL existir un `.env.example` versionado con las variables base no sensibles (entorno, host, puerto, nivel de log) y `.env` SHALL estar ignorado por git. Variables ausentes obligatorias SHALL producir un error de arranque claro.

#### Scenario: Valores por defecto en desarrollo

- **WHEN** la app arranca sin un archivo `.env` presente
- **THEN** usa los valores por defecto definidos en `config.py` y arranca correctamente

#### Scenario: Sobrescritura por variable de entorno

- **WHEN** se define una variable de entorno reconocida (p. ej. el puerto) antes de arrancar
- **THEN** la configuración efectiva refleja ese valor en lugar del valor por defecto

#### Scenario: Secretos nunca versionados

- **WHEN** se inspecciona el control de versiones
- **THEN** `.env` no está rastreado por git y solo `.env.example` (sin valores sensibles) está versionado

### Requirement: Contrato base de errores estructurados

El sistema SHALL devolver los errores en el formato `{ "error": { "code": string, "message": string, "details"?: object } }` de forma consistente, mediante un manejador de excepciones registrado en la app. Este contrato SHALL estar disponible para que todos los módulos posteriores lo reutilicen.

#### Scenario: Ruta inexistente devuelve error estructurado

- **WHEN** un cliente solicita una ruta que no existe
- **THEN** el servidor responde con el formato `{ "error": { "code", "message" } }` y un código de estado HTTP apropiado

### Requirement: Tooling de calidad y testing

El sistema SHALL incluir `ruff` configurado para formato y linting, y `pytest` con al menos un test de humo que arranque la aplicación y verifique `/health`. El linter y los tests SHALL poder ejecutarse mediante comandos documentados.

#### Scenario: Lint en código conforme

- **WHEN** se ejecuta `uv run ruff check .` sobre el código del scaffolding
- **THEN** el comando termina con código de salida 0 (sin violaciones)

#### Scenario: Test de humo pasa

- **WHEN** se ejecuta `uv run pytest`
- **THEN** el test de humo arranca la app, solicita `GET /health`, recibe `200` con estado `ok`, y la suite termina con código de salida 0

### Requirement: Documentación de operación

El sistema SHALL incluir un `README.md` que documente cómo instalar (`uv sync`), arrancar el servidor, ejecutar los tests (`pytest`) y ejecutar el linter (`ruff`).

#### Scenario: README cubre los comandos esenciales

- **WHEN** una persona nueva lee el `README.md`
- **THEN** encuentra instrucciones explícitas y ejecutables para instalar, correr, testear y lintar el proyecto

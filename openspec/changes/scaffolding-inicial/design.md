## Context

`osiris-menu-be` ya contiene el OpenSpec canónico (`project.md`, `decisions.md`, `glossary.md`, `reference-specs/`) pero `src/` y `tests/` están vacíos y no existe `pyproject.toml`, `Dockerfile`, `alembic.ini`, ni el `docker-compose.yml` raíz del workspace. `osiris-menu-fe` solo tiene su `CLAUDE.md`. El objetivo es montar la base arquitectónica para que backend y frontend avancen simultáneamente desde un único OpenSpec, replicando el enfoque de `osiris-inventario-be` / `osiris-inventario-fe`.

Restricciones que gobiernan este diseño (no se re-discuten aquí, se aplican):
- Stack obligatorio backend y frontend de `CLAUDE.md` y `project.md`.
- Docker obligatorio con un único `docker-compose.yml` raíz (T-35).
- Monolito modular, sin microservicios; WebSockets nativos (T-02); sin dependencias cloud para operación crítica (T-01).
- Contratos: `/api/v1`, OpenAPI, envelope de error, `X-Request-Id`.
- Terminología canónica del glosario; reglas de negocio sólo en backend.

**Entorno de aplicación**: este cambio crea archivos en tres ubicaciones (backend, frontend y la raíz del workspace). Debe aplicarse **desde la raíz del workspace `osiris-menu/`**, o desde un entorno con permisos de escritura en `osiris-menu-be/`, `osiris-menu-fe/` y el `docker-compose.yml` raíz. Si el entorno de apply solo tiene escritura en `osiris-menu-be/`, el frontend y el compose raíz deben crearse en un paso con el alcance correcto.

## Goals / Non-Goals

**Goals:**
- Dejar el árbol de carpetas backend (`src/osiris/...`) y frontend (`src/...`) con la estructura canónica.
- `docker compose up --build` levanta `postgres`, `redis`, `api`, `web` sin pasos manuales.
- Establecer los contratos técnicos transversales (versionado, OpenAPI, envelope de error, idempotencia `X-Request-Id`, canales WebSocket) como cimientos reutilizables.
- Scaffolding de los tres módulos MVP (§20, §21, §22) con estructura y routers placeholder.
- Cliente API y cliente WebSocket base en el frontend, más seis vistas placeholder enrutadas.
- Tests mínimos de arranque en ambos lados.

**Non-Goals:**
- Implementar reglas de negocio de §20/§21/§22 (transiciones de estado, matriz D-02, inventario híbrido D-01, división de cuenta D-09, traslados D-08). Eso es trabajo de propuestas por módulo.
- Implementar SRI, Caja, Inventario, Catálogo, Reservas, Reportes, WhatsApp, auto-pedido QR, Nómina/IESS, backups productivos, certificados SRI reales.
- Definir el esquema de datos definitivo de cada entidad: en esta etapa los `models.py` son placeholders mínimos; el modelado entidad-por-entidad lo cierra cada propuesta de módulo con su migración Alembic.
- Autenticación/roles completos: `auth/` queda como placeholder de niveles 1–4, sin flujo de login productivo.
- Configurar jobs programados: `APScheduler` se incluye como dependencia disponible del stack, pero **sin jobs configurados** hasta una propuesta funcional posterior (no-show, auto-restaurar agotados, etc.).

## Decisions

### D-a · Layout de import `src/osiris/` (src-layout), ejecutado con `--app-dir src`
Se adopta el layout `src/osiris/main.py` (no `app/main.py`) consistente con `project.md`. El runtime no depende de un install editable: se ejecuta con `uvicorn osiris.main:app --app-dir src` y `pytest` con `pythonpath=["src"]`. En Docker el `WORKDIR /app` con `COPY . .` y `--app-dir src` mantiene el mismo layout.
- Alternativa descartada: `app/` flat-layout — contradice `project.md`/`CLAUDE.md`.
- Alternativa descartada: install editable con package — innecesario; `--app-dir src` / `pythonpath` evita acoplarse a la instalación del paquete.

### D-b · Idempotencia `X-Request-Id`: política inicial de rechazo `409`
El contrato exige idempotencia en todo mutador. **Política inicial del scaffolding**: un `X-Request-Id` ya visto se **rechaza** con `409` y código de dominio `IDEMPOTENCY_KEY_REUSED`. En esta etapa **no** se intenta reconstruir ni devolver la respuesta original; eso se evaluará en una propuesta posterior cuando existan mutadores reales con cuerpo de respuesta persistible. Se implementa como una dependencia FastAPI reutilizable que lee el header `X-Request-Id`, consulta/inserta en la tabla `request_ids_procesados` (con TTL) y corta el doble efecto.
- Alternativa descartada (por ahora): devolver la respuesta original cacheada — requiere persistir el cuerpo de respuesta por clave; se difiere hasta tener mutadores reales.
- Redis se reserva para estado efímero; la fuente de verdad de idempotencia es Postgres (durabilidad ante reinicio).

### D-c · Envelope de error y excepciones de dominio centralizadas
Excepciones tipadas en `shared/exceptions.py` (p. ej. `DomainError` con `code`, `message`, `details`) y un exception handler global que las serializa al envelope `{ "error": { code, message, details? } }`. El rechazo de idempotencia (`IDEMPOTENCY_KEY_REUSED`) usa este mismo envelope. Todos los módulos lanzan estas excepciones; el handler es único.
- Alternativa descartada: construir el envelope manualmente en cada router — duplicación y deriva del contrato.

### D-d · WebSockets: connection manager en memoria por canal; nombres lógicos vs rutas físicas
Se implementa un `ConnectionManager` en memoria que indexa conexiones por canal (`mesas`, `cocina`, `barra`, `connectivity`) y por `comanda_id` para `comandas:<comanda_id>`. Broadcast itera suscriptores del canal. Suficiente para un único servidor local (T-28); no se introduce pub/sub distribuido.

Los nombres de canal del glosario/`project.md` (`mesas`, `comandas:<comanda_id>`, `cocina`, `barra`, `connectivity`) son **nombres lógicos**. La **ruta física recomendada** de cada endpoint WebSocket es:
- `mesas` → `/ws/mesas`
- `comandas:<comanda_id>` → `/ws/comandas/{comanda_id}`
- `cocina` → `/ws/cocina`
- `barra` → `/ws/barra`
- `connectivity` → `/ws/connectivity`

- Alternativa descartada: Redis pub/sub para fan-out — innecesario con un solo proceso/servidor; se documenta como evolución si se escala a múltiples workers.
- Nota: con múltiples workers Uvicorn el manager en memoria no comparte estado; en MVP se corre un worker. Riesgo registrado abajo.

### D-e · Migraciones: baseline Alembic
Alembic se configura contra `DATABASE_URL` async (asyncpg) con una migración baseline. La baseline incluye la tabla `request_ids_procesados` (para que la idempotencia sea testeable desde el arranque); no incluye tablas de dominio de módulos. Cada módulo agrega su propia migración al implementar sus modelos.
- Alternativa descartada: `create_all` en arranque — prohibido por la regla "todo cambio de modelos requiere migración Alembic".

### D-f · Frontend: cliente API Axios con interceptor de `X-Request-Id` y sesión por cookie
Un único `apiClient` (Axios) con `baseURL = VITE_API_URL`, `withCredentials: true` (cookie httpOnly), interceptor que inyecta `X-Request-Id` (UUID v4) en métodos mutadores y un interceptor de respuesta que normaliza el envelope de error (incluido `409 IDEMPOTENCY_KEY_REUSED`). Cliente WebSocket base con reconexión simple. TanStack Query para estado servidor. Sin tokens en `localStorage`/`sessionStorage`.
- Alternativa descartada: `fetch` crudo — Axios da interceptores centralizados para `X-Request-Id` y errores, alineado con inventario.

### D-g · Vistas placeholder por perfil, enrutadas con React Router
Seis rutas: `/mesero`, `/cocina`, `/barra`, `/caja`, `/admin`, `/qr/:mesaId` (Público QR). Cada una es un componente placeholder que prueba el routing y el consumo del contrato, sin reglas de negocio.
- Alternativa descartada: una sola vista con tabs — no refleja que cocina/barra van en tablets fijas fullscreen distintas (§22) y mesero en tablet 10".

### D-h · Compose raíz vive en el workspace, fuera de ambos repos
El `docker-compose.yml` y `.env.example` se crean en `osiris-menu/` (raíz del workspace), no dentro de `osiris-menu-be` ni `osiris-menu-fe`, para no crear composes competidores (project.md). El build context de `api` apunta a `./osiris-menu-be` y el de `web` a `./osiris-menu-fe`.

### D-i · APScheduler como dependencia disponible, sin jobs
`APScheduler` se incluye en el stack obligatorio del backend (alineado con `project.md`) pero en esta etapa **no se configura ningún job ni scheduler en arranque**. Queda disponible para la primera propuesta funcional que requiera tareas programadas locales (no-show de reservas, auto-restaurar agotados, etc.).
- Alternativa descartada: omitir la dependencia hasta el primer job — fijar el stack completo ahora evita re-tocar `pyproject.toml`/lockfile en cada módulo.

### D-j · `auth/` como placeholder de niveles 1–4; PIN diferido (cierra PEND-scaffold-01)
En el scaffolding, `src/osiris/auth/` queda como placeholder de los niveles de autorización 1–4, **sin** flujo de login productivo. El modelo de PIN compartido (T-33) y PIN personal (T-34) se difiere a una propuesta de autenticación dedicada.
- Razón: el scaffolding fija el contrato de niveles sin comprometer el modelo de credenciales antes de tener la propuesta de auth.
- Alternativa descartada: implementar PIN ya — excede el alcance de scaffolding y tocaría reglas de identificación individual (§22, T-34).

### D-k · Ruta Público QR `/qr/:mesaId` desde el inicio (cierra PEND-scaffold-02)
La vista Público QR se enruta como `/qr/:mesaId`, aceptando el identificador permanente de mesa (D-04) desde ya, aunque la vista sea placeholder. Fija el contrato del QR sin reutilizar identificadores.
- Razón: evita un re-enrutado posterior y deja el contrato del QR alineado con D-04/§32.
- Alternativa descartada: placeholder sin parámetro — obligaría a cambiar la ruta cuando se implemente la carta pública.

## Risks / Trade-offs

- **[ConnectionManager en memoria no escala a múltiples workers]** → MVP corre un solo worker Uvicorn; documentar evolución a Redis pub/sub si se añade escalado horizontal. No es requerido por T-28 (servidor único).
- **[Scaffolding tienta a colar reglas de negocio]** → Los routers/servicios placeholder no implementan transiciones ni autorizaciones; cualquier ambigüedad se levanta como decisión D-XX, no se codifica (regla de `project.md`).
- **[Modelos placeholder podrían fijar prematuramente el esquema]** → `models.py` mínimos y explícitamente marcados como placeholder; el modelado real y su migración los cierra cada propuesta de módulo.
- **[Dos repos + un OpenSpec puede desincronizar el contrato]** → El frontend consume OpenAPI/contratos del backend; no duplica reglas. El OpenSpec único en backend es la fuente de verdad.
- **[Compose duplicado por repo]** → Prohibido; sólo el compose raíz. Los Dockerfiles viven en cada repo pero no hay compose por repo.
- **[Apply sin permisos en frontend/raíz]** → Aplicar desde la raíz del workspace o un entorno con escritura en be/fe/compose; ver la nota de "Entorno de aplicación".

## Migration Plan

No hay datos productivos ni esquema previo: es un arranque desde cero (`src/` y `tests/` vacíos). El "despliegue" es local vía Docker Compose. El apply requiere escritura en `osiris-menu-be/`, `osiris-menu-fe/` y la raíz del workspace.

1. Backend: `pyproject.toml`, `Dockerfile`, `alembic.ini`, `migrations/` baseline, árbol `src/osiris/...`, tests mínimos.
2. Frontend: scaffolding Vite/React/TS, `Dockerfile`, cliente API/WS, vistas placeholder, tests mínimos.
3. Raíz: `docker-compose.yml` + `.env.example`.
4. Validación: `docker compose up --build` levanta los cuatro servicios; `/health`, `/openapi.json` responden; suites mínimas verdes.

Rollback: al ser scaffolding inicial sin datos, revertir es eliminar/branchear los archivos creados. Sin migración de datos involucrada.

## Open Questions

Ninguna pendiente. Las dos preguntas previas quedaron cerradas:

- **PEND-scaffold-01** (auth/PIN) → cerrada por **D-j**: `auth/` placeholder de niveles 1–4 ahora; PIN compartido (T-33) / personal (T-34) en propuesta dedicada.
- **PEND-scaffold-02** (ruta QR) → cerrada por **D-k**: Público QR enrutado como `/qr/:mesaId` con identificador permanente de mesa (D-04) desde el inicio.

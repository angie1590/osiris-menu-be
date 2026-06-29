## 1. Backend · base del proyecto

- [x] 1.1 Crear `pyproject.toml` (Poetry) con el stack obligatorio completo de `project.md`: FastAPI, Uvicorn, SQLAlchemy 2.x async, asyncpg, Alembic, Pydantic v2, pydantic-settings, python-jose, passlib[bcrypt], bcrypt, redis async, httpx, `cryptography`, `ReportLab` o `WeasyPrint`, `openpyxl`, `APScheduler`, pytest + pytest-asyncio + pytest-cov, ruff; configurar `pytest` con `pythonpath=["src"]` y ruff (D-a). `APScheduler` se declara como dependencia disponible pero NO se configura ningún job ni scheduler en arranque (D-i)
- [x] 1.2 Crear `src/osiris/__init__.py`, `src/osiris/main.py` (app FastAPI, CORS desde `CORS_ORIGINS`) y montar el router raíz bajo `/api/v1`
- [x] 1.3 Crear `src/osiris/config.py` con `pydantic-settings` leyendo `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, expiraciones de token, `APP_ENV`, `CORS_ORIGINS` (sin secretos hardcodeados)
- [x] 1.4 Crear `src/osiris/db.py` (engine async asyncpg, `Base` declarativa, dependencia de sesión async)
- [x] 1.5 Implementar `GET /health` (200 JSON, sin auth) y verificar que `/openapi.json` se sirve

## 2. Backend · contratos transversales

- [x] 2.1 Crear `src/osiris/shared/exceptions.py` con excepciones de dominio tipadas (`code`, `message`, `details`) y un exception handler global que serializa al envelope `{ "error": { code, message, details? } }` (D-c)
- [x] 2.2 Implementar la dependencia de idempotencia `X-Request-Id` en `shared/` y la tabla `request_ids_procesados` con TTL (D-b). Política inicial: un `X-Request-Id` duplicado se rechaza con `409` y código `IDEMPOTENCY_KEY_REUSED` en el envelope de error; NO se reconstruye ni devuelve la respuesta original todavía
- [x] 2.3 Crear `src/osiris/auth/` como placeholder de niveles de autorización 1–4, sin flujo de login productivo; PIN compartido (T-33)/personal (T-34) diferido a propuesta de auth (D-j)

## 3. Backend · WebSockets nativos

- [x] 3.1 Crear `src/osiris/websocket/` con un `ConnectionManager` en memoria indexado por canal y por `comanda_id` (D-d)
- [x] 3.2 Registrar los cinco canales canónicos como endpoints WebSocket scaffolding usando la ruta física recomendada `/ws/...`: `/ws/mesas`, `/ws/comandas/{comanda_id}`, `/ws/cocina`, `/ws/barra`, `/ws/connectivity` (nombres lógicos del glosario mapeados a estas rutas)
- [x] 3.3 Implementar `connect`/`disconnect`/`broadcast` con payload tipado base (sin lógica de negocio por canal)

## 4. Backend · scaffolding de módulos MVP

- [x] 4.1 Crear `src/osiris/modules/mesas/` (§20) con `__init__.py`, `models.py`, `schemas.py`, `service.py`, `api.py`, `events.py`, `README.md`; enums de estado de Zona/Mesa con términos del glosario; router placeholder bajo `/api/v1`
- [x] 4.2 Crear `src/osiris/modules/comandas/` (§21) con la misma estructura; enums de estado de Comanda/Ítem de comanda del glosario; router placeholder bajo `/api/v1`
- [x] 4.3 Crear `src/osiris/modules/cocina_barra/` (§22) con la misma estructura; router placeholder bajo `/api/v1` (consume ruteo de §21, sin entidades propias)
- [x] 4.4 Verificar que los routers placeholder no implementan reglas de negocio (transiciones, autorizaciones, inventario) y que separan capas api/service/models/schemas (mvp-modules-scaffolding)

## 5. Backend · migraciones

- [x] 5.1 Crear `alembic.ini` y `migrations/` configurados contra `DATABASE_URL` async (asyncpg)
- [x] 5.2 Generar la migración baseline (incluyendo `request_ids_procesados`; sin tablas de dominio de módulos) y verificar `alembic upgrade head` (D-e)

## 6. Frontend · base del proyecto

- [x] 6.1 Inicializar `osiris-menu-fe` con Vite + React 19 + TypeScript estricto; agregar el stack obligatorio: React Router DOM 7, TanStack Query 5, Axios, Tailwind CSS 4, shadcn/ui sobre Radix UI, React Hook Form, Zod, lucide-react, date-fns, Recharts, y testing con Vitest + Testing Library + Playwright (sin Redux/MobX/MUI/AntD/Bootstrap/styled-components/emotion)
- [x] 6.2 Configurar `vite.config.ts` con proxy a `VITE_API_PROXY_TARGET` y lectura de `VITE_API_URL`
- [x] 6.3 Configurar router con las seis rutas de perfil (`src/routes/`)
- [x] 6.4 Estructura de carpetas dedicada según `osiris-menu-fe/CLAUDE.md`: `src/{routes,api,ws,auth,hooks,types,lib}/`, `src/views/<perfil>/`, `src/modules/{mesas,comandas,cocina-barra}/` (index/api/ws/types/hooks/components), `src/components/ui/` (HTTP por `src/api/`, WS por `src/ws/`)

## 7. Frontend · clientes y vistas placeholder

- [x] 7.1 Crear `apiClient` (Axios, en `src/api/`) con `baseURL=VITE_API_URL`, `withCredentials: true`, interceptor que inyecta `X-Request-Id` (UUID v4) en mutaciones e interceptor que normaliza el envelope de error; sin tokens en `localStorage`/`sessionStorage` (D-f)
- [x] 7.2 Crear cliente WebSocket base (en `src/ws/`) con reconexión automática, backoff exponencial y heartbeat para los canales canónicos (mesas, comandas, cocina, barra, connectivity)
- [x] 7.3 Crear vistas placeholder enrutadas en `src/views/<perfil>/`: Mesero (`/mesero`), Cocina (`/cocina`), Barra (`/barra`), Caja (`/caja`), Admin (`/admin`), Público QR (`/qr/:mesaId`) — sin reglas de negocio (D-g, D-k)

## 8. Docker y orquestación del workspace

- [x] 8.1 Crear `Dockerfile` de backend (`python:3.11-slim`, Poetry, Uvicorn con `--app-dir src`)
- [x] 8.2 Crear `Dockerfile` de frontend (`node:20-alpine`, `npm ci`, sirve Vite en 5173)
- [x] 8.3 Crear el `docker-compose.yml` raíz único en `osiris-menu/` con `postgres`, `redis`, `api`, `web`, healthchecks, red interna, puertos (`8000`, `5173`, `5433:5432`) y `depends_on` con `service_healthy` (D-h)
- [x] 8.4 Crear `.env.example` en la raíz del workspace con todas las variables; confirmar que `.env` está en `.gitignore`
- [x] 8.5 Verificar `docker compose up --build` levanta los cuatro servicios sin pasos manuales y que `web` alcanza `api` por la red interna

## 9. Tests mínimos de arranque

- [x] 9.1 Backend: test de `GET /health` (200), test de que `/openapi.json` se sirve
- [x] 9.2 Backend: test de idempotencia contra un endpoint dummy/ruta interna de test (aún no hay mutadores reales de negocio) — `X-Request-Id` duplicado responde `409` `IDEMPOTENCY_KEY_REUSED` y no produce segundo efecto
- [x] 9.3 Backend: test de WebSocket — conexión/ping a un canal y broadcast llega al suscriptor; otro canal no lo recibe
- [x] 9.4 Frontend: test de render de cada vista placeholder y de que `apiClient` se instancia con `X-Request-Id` en mutaciones
- [x] 9.5 Backend lint/format: `ruff check src tests` y `ruff format --check src tests` verdes
- [x] 9.6 Frontend lint: `npm run lint` (ESLint flat config) verde

## 10. OpenSpec · consistencia documental

- [x] 10.1 Verificar/actualizar `openspec/decisions.md` para que documente T-35 (Docker Compose único como entorno oficial de desarrollo del workspace); si faltara o estuviera desactualizado, dejarlo consistente con este cambio
- [x] 10.2 Verificar que `openspec/project.md` ya no contiene la restricción "Sin Docker en MVP" (debe reflejar Docker obligatorio desde el inicio, alineado con T-35)

## 11. Cierre

- [x] 11.1 Confirmar criterios de `CLAUDE.md`: compose levanta sin pasos extra, sin reglas duplicadas en frontend, sin contradicción con `decisions.md`, terminología del glosario respetada
- [x] 11.2 No quedan preguntas abiertas (PEND-scaffold-01/02 cerradas por D-j/D-k); si durante el apply escala una ambigüedad nueva, levantarla como decisión D-XX antes de implementarla

CLAUDE.md · osiris-menu-be

Guía principal para construir osiris-menu con OpenSpec.

Este repositorio contiene el backend y el OpenSpec canónico del proyecto completo. El frontend vive en el repo hermano osiris-menu-fe, pero se construye simultáneamente desde este mismo OpenSpec.

Regla principal

Antes de implementar cualquier cambio funcional, leer primero:

openspec/project.md
openspec/decisions.md
openspec/glossary.md
openspec/reference-specs/

Archivos de referencia iniciales:

openspec/reference-specs/20-mesas.md
openspec/reference-specs/21-comandas.md
openspec/reference-specs/22-cocina-barra.md

No duplicar estas reglas dentro de CLAUDE.md. Este archivo debe ser corto y operativo para no consumir tokens innecesarios.

Forma de trabajo con OpenSpec

El desarrollo se hará como en osiris-inventario: backend y frontend avanzan juntos desde un único OpenSpec ubicado en el backend.

Flujo obligatorio:

1. Leer openspec/project.md.
2. Leer openspec/decisions.md.
3. Leer openspec/glossary.md.
4. Leer la spec de referencia del módulo si existe.
5. Crear o actualizar proposal/spec en OpenSpec antes de implementar cambios grandes.
6. Implementar backend, frontend y tests alineados al mismo contrato.
7. No inventar reglas de negocio fuera de OpenSpec.

Si una regla no existe o es ambigua:

* No resolverla silenciosamente en código.
* Proponer una decisión nueva D-XX.
* Documentar módulos impactados.
* Esperar cierre explícito antes de implementar la regla como definitiva.

Alcance actual del MVP

Módulos iniciales:

* §20 Mesas y zonas
* §21 Comandas
* §22 Cocina y barra

Estos módulos deben quedar preparados para integrarse luego con:

* §23 Caja y cobro
* §24 Facturación SRI
* §25 Catálogo
* §26 Inventario
* §28 Reservas
* §31 Configuración
* §32 Carta pública QR

Stack obligatorio backend

Usar el mismo enfoque técnico de osiris-inventario-be, adaptado a osiris-menu.

* Python 3.11+
* FastAPI
* Uvicorn
* PostgreSQL 16
* SQLAlchemy 2.x async
* asyncpg
* Alembic
* Pydantic v2
* pydantic-settings
* Poetry
* python-jose
* passlib[bcrypt]
* bcrypt
* Redis async
* httpx
* ReportLab y openpyxl cuando aplique
* pytest
* pytest-asyncio
* pytest-cov
* ruff
* Docker
* Docker Compose

No usar Django, Flask, Celery, microservicios ni frameworks adicionales sin decisión explícita.

Stack obligatorio frontend

El frontend vive en ../osiris-menu-fe, pero se coordina desde este OpenSpec.

Usar el mismo enfoque técnico y visual de osiris-inventario-fe:

* React 19
* TypeScript estricto
* Vite
* React Router DOM 7
* TanStack Query 5
* Axios
* Tailwind CSS 4
* shadcn/ui sobre Radix UI
* React Hook Form
* Zod
* lucide-react
* date-fns
* Recharts
* Vitest
* Testing Library
* Playwright
* Docker
* Docker Compose

No usar Redux, MobX, Material UI, Ant Design, Bootstrap, styled-components ni emotion.

Docker obligatorio

A diferencia de la decisión inicial de discovery, este proyecto sí debe implementarse con Docker desde el inicio.

Debe existir un único docker-compose.yml en la carpeta raíz del workspace que levante:

* postgres
* redis
* api
* web

Estructura recomendada:

osiris-menu/
├── docker-compose.yml
├── .env.example
├── osiris-menu-be/
│   ├── CLAUDE.md
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── openspec/
│   ├── src/
│   ├── tests/
│   └── scripts/
└── osiris-menu-fe/
    ├── CLAUDE.md
    ├── Dockerfile
    ├── package.json
    ├── vite.config.ts
    ├── src/
    └── tests/

Comando principal:

docker compose up --build

No crear docker-compose separados que compitan entre sí.

docker-compose.yml esperado en la raíz

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: osiris
      POSTGRES_PASSWORD: osiris_dev_pass
      POSTGRES_DB: osiris_menu
    ports:
      - "5433:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U osiris -d osiris_menu"]
      interval: 5s
      timeout: 5s
      retries: 10
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 10
  api:
    build:
      context: ./osiris-menu-be
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://osiris:osiris_dev_pass@postgres:5432/osiris_menu
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: dev-secret-key-change-in-production
      ACCESS_TOKEN_EXPIRE_MINUTES: 30
      REFRESH_TOKEN_EXPIRE_DAYS: 7
      APP_ENV: development
      CORS_ORIGINS: '["http://localhost:5173"]'
    volumes:
      - ./osiris-menu-be/src:/app/src
      - ./osiris-menu-be/openspec:/app/openspec
      - ./osiris-menu-be/migrations:/app/migrations
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
  web:
    build:
      context: ./osiris-menu-fe
      dockerfile: Dockerfile
    ports:
      - "5173:5173"
    environment:
      VITE_API_URL: http://localhost:8000
      VITE_API_PROXY_TARGET: http://api:8000
    volumes:
      - ./osiris-menu-fe/src:/app/src
      - ./osiris-menu-fe/public:/app/public
    depends_on:
      - api
volumes:
  postgres_data:
  redis_data:

Dockerfile backend esperado

FROM python:3.11-slim
WORKDIR /app
RUN pip install poetry==1.8.4 && \
    poetry config virtualenvs.create false
COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-interaction --no-ansi --no-root
COPY . .
RUN if [ -f scripts/entrypoint.sh ]; then \
      sed -i 's/\r$//' scripts/entrypoint.sh && chmod +x scripts/entrypoint.sh; \
    fi
EXPOSE 8000
CMD ["uvicorn", "osiris.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

Si el layout real usa app/main.py, cambiar el comando a:

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

No mezclar layouts.

Estructura backend recomendada

src/osiris/
├── main.py
├── config.py
├── db.py
├── auth/
├── modules/
│   ├── mesas/
│   ├── comandas/
│   └── cocina_barra/
├── websocket/
└── shared/

Cada módulo:

modules/<nombre>/
├── __init__.py
├── models.py
├── schemas.py
├── service.py
├── api.py
├── events.py
└── README.md

Reglas de implementación

* La lógica de negocio vive en service.py.
* Las rutas FastAPI solo orquestan request/response.
* Los modelos SQLAlchemy no deben contener lógica compleja.
* Los schemas Pydantic son el contrato público.
* Todo endpoint mutador acepta X-Request-Id para idempotencia.
* Toda mutación material genera log auditable.
* Toda acción sensible valida nivel de autorización.
* Toda transición de estado debe estar respaldada por spec o decisión.
* Todo cambio de modelos requiere migración Alembic.
* Todo endpoint nuevo requiere tests.

API

* Versionado en path: /api/v1/...
* OpenAPI generado por FastAPI.
* Errores estructurados:

{
  "error": {
    "code": "DOMAIN_ERROR_CODE",
    "message": "Mensaje legible para el operador",
    "details": {}
  }
}

WebSockets

Usar WebSockets nativos de FastAPI.

Canales iniciales:

* mesas
* comandas:<comanda_id>
* cocina
* barra
* connectivity

No usar Socket.IO.

Todo evento debe tener payload tipado y test asociado cuando afecte reglas críticas.

Seguridad

* Nunca commitear .env.
* Nunca commitear certificados, claves privadas ni credenciales SRI.
* Nunca loguear tokens, passwords, tarjetas ni datos fiscales completos.
* No usar eval ni exec.
* No construir SQL con strings.
* Passwords solo con bcrypt vía passlib.
* Sesión por cookie httpOnly.
* No devolver tokens accesibles por JavaScript.

Testing

Sin tests, no se considera terminado.

Backend:

docker compose exec api pytest
docker compose exec api pytest tests/unit/
docker compose exec api pytest tests/integration/
docker compose exec api ruff check src tests
docker compose exec api ruff format src tests

Frontend desde este mismo flujo:

docker compose exec web npm run lint
docker compose exec web npm run test
docker compose exec web npm run build

Criterios de terminado

Un cambio está terminado solo si:

* La spec o decisión correspondiente existe.
* Backend implementado.
* Frontend implementado si hay impacto UI.
* Tests backend agregados o actualizados.
* Tests frontend agregados o actualizados cuando aplique.
* Docker Compose levanta sin pasos manuales extra.
* No hay reglas duplicadas fuera de OpenSpec.
* No hay contradicción con openspec/decisions.md.
* Se usa terminología de openspec/glossary.md.

Qué NO hacer

* No duplicar en este archivo el contenido completo de decisiones, glosario o specs.
* No implementar reglas no documentadas.
* No usar Docker Compose separados por repo como flujo principal.
* No meter lógica de negocio en el frontend.
* No guardar tokens en localStorage/sessionStorage.
* No introducir librerías por comodidad sin justificar.
* No cambiar nombres canónicos del glosario.
* No ignorar idempotencia en mutaciones.
* No crear endpoints sin tests.
* No modificar reglas fiscales sin decisión explícita.
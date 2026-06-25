# Asiringui · osiris-menu-be

Sistema operativo integral del restaurante-cervecería Asiringui, en Cuenca, Ecuador. Este repo contiene el **backend** del sistema. El frontend vive en el repo `osiris-menu-fe`.

## Qué construye este repo

API y backend de un sistema POS / gestión integral para un restaurante de aproximadamente 60 plazas, con cumplimiento fiscal SRI Ecuador, cumplimiento LOPDP, operación offline-resiliente, y soporte de hasta 5 operadores concurrentes.

Apertura prevista del restaurante: tercer trimestre de 2026.

## Stack obligatorio

- **Lenguaje**: Python 3.12+
- **Framework web**: FastAPI (decisión cerrada, no usar Django ni Flask)
- **Base de datos**: PostgreSQL (versión mayor estable con soporte activo)
- **ORM**: SQLAlchemy + Alembic para migraciones
- **WebSockets**: integrados en FastAPI (no usar Socket.IO ni librerías externas)
- **Validación**: Pydantic
- **Hashing**: passlib + bcrypt
- **Cripto / firmas**: librería `cryptography`
- **PDF**: WeasyPrint o ReportLab según necesidad
- **Testing**: pytest
- **Servidor**: el sistema corre nativo sobre Linux con systemd. **No usar Docker en MVP.**

No introducir librerías nuevas sin justificación explícita. Si necesitas algo que no está en esta lista, pregúntalo antes de instalarlo.

## Arquitectura física

- Un único servidor local en el restaurante, que cumple **doble rol**: aloja el backend + base de datos + frontend servido, y actúa como la computadora de caja del Cajero/Barman.
- Backend y PostgreSQL corren en el mismo host. Conexión interna por socket Unix local o TCP a localhost. No usar TLS para conexiones intra-host.
- TLS sí es obligatorio para acceso administrativo remoto vía VPN.
- Sin Docker, sin contenedores. Procesos gestionados con systemd.

## Estructura del repo (a crear)

```
osiris-menu-be/
├── CLAUDE.md                      ← este archivo
├── README.md
├── pyproject.toml                 ← gestión de deps con pip/uv
├── alembic.ini
├── specs/                         ← single source of truth de negocio
│   ├── 00-base/
│   │   ├── vision.md
│   │   ├── stack.md
│   │   ├── principles.md
│   │   ├── decisions.md           ← N-XX, T-XX, D-XX
│   │   └── glossary.md
│   ├── 20-mesas/spec.md
│   ├── 21-comandas/spec.md
│   └── 22-cocina-barra/spec.md
├── src/
│   └── osiris/
│       ├── __init__.py
│       ├── main.py                ← entrypoint FastAPI
│       ├── config.py              ← settings (pydantic-settings)
│       ├── db.py                  ← engine, sesión, base SQLAlchemy
│       ├── auth/                  ← autenticación, autorización, niveles
│       ├── modules/
│       │   ├── mesas/             ← §20
│       │   ├── comandas/          ← §21
│       │   └── cocina_barra/      ← §22
│       ├── websocket/             ← canales WS, broadcasting
│       └── shared/                ← utilidades, tipos comunes
├── migrations/                    ← alembic versions
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
└── scripts/                       ← bash de deploy, backup, restore
```

Cada módulo dentro de `src/osiris/modules/` sigue la misma estructura interna:

```
modules/<nombre>/
├── __init__.py
├── models.py          ← SQLAlchemy models
├── schemas.py         ← Pydantic schemas para API
├── service.py         ← lógica de negocio pura
├── api.py             ← rutas FastAPI
├── events.py          ← eventos WebSocket emitidos por el módulo
└── README.md          ← resumen y ejemplos de uso
```

## Principios no negociables

Vienen del documento Product Vision (Parte I, §7). Son **prevalentes sobre cualquier decisión técnica oportunista**:

1. **Trazabilidad total**: toda acción material queda registrada en log inmutable con usuario, timestamp, contexto y, cuando aplica, motivo.
2. **Inmutabilidad fiscal**: una factura emitida no se modifica. Corrección solo vía nota de crédito.
3. **Operación offline resiliente**: el sistema opera sin internet. Sólo SRI, email/WhatsApp y backup-nube requieren conectividad.
4. **Cumplimiento como propiedad emergente**: el operador cumple normativa SRI/LOPDP/IESS por usar el sistema correctamente, sin saber los detalles legales.
5. **Cumplimiento por defecto**: ante ambigüedad, la opción por defecto es la que cumple más estrictamente la normativa.
6. **Mínimo privilegio**: acciones sensibles requieren autorización adicional con motivo registrado.
7. **Configuración trazable**: cambio de parámetro = log con usuario, timestamp, valor anterior y nuevo.
8. **Evolución sin migración**: el MVP soporta las extensiones de Fase 2 (auto-pedido QR, WhatsApp Business API) sin rediseño.
9. **Transparencia con el operador**: el operador siempre sabe el estado del sistema (conectividad SRI, cola pendiente, tiempos).
10. **Validación rigurosa antes de producción**: nada llega a producción sin pruebas unitarias e integración con SRI sandbox.

## Roles del sistema

Siete roles. Permisos detallados están en `specs/00-base/decisions.md`:

- **Super Admin** (familiar técnico — cónyuge de la PO): mantenimiento, custodia de credenciales fiscales.
- **Admin Socio** (cualquiera de los 3 hermanos): gestión de negocio, autorización nivel 4.
- **Admin Contable** (hermana titular del RUC): gestión fiscal.
- **Cajero / Barman**: cobro, facturación, cierre de caja, atención de barra.
- **Mesero**: comandas y atención de sala.
- **Chef**: cocina, control de inventario de cocina.
- **Ayudante**: apoyo en cocina.

Niveles de autorización:
- **Nivel 1**: cualquier operador autenticado.
- **Nivel 2**: Cajero, Admin Socio, Admin Contable, Super Admin.
- **Nivel 3**: Admin Socio, Admin Contable, Super Admin.
- **Nivel 4**: Admin Socio o Super Admin.

## Cómo trabajar con las specs

Las specs en `specs/` son **la fuente de verdad de negocio**. Antes de implementar cualquier comportamiento de un módulo, leer su spec.

- Si una decisión está en spec, **implementarla tal como está**.
- Si una decisión está en spec y crees que debe cambiar, **levanta una propuesta de cambio de spec**, no la cambies en código primero.
- Si una decisión NO está en spec, **pregúntala antes de inventarla**.
- Los identificadores **N-XX** (negocio), **T-XX** (técnico) y **D-XX** (funcional post-discovery) son referencias. Su definición vive en `specs/00-base/decisions.md`.

## Convenciones de código

- **Python**: PEP 8. Formato con `ruff format`. Lint con `ruff check`.
- **Imports**: stdlib → terceros → propios, separados con línea en blanco.
- **Type hints obligatorios** en toda función pública. Usar `from __future__ import annotations`.
- **Naming**: snake_case para variables/funciones, PascalCase para clases, UPPER_CASE para constantes módulo.
- **Logging**: usar `logging` del stdlib con configuración estructurada (JSON en producción). Nunca `print()`.
- **Errores**: excepciones tipadas (no `raise Exception`). Excepciones de dominio van en `shared/exceptions.py`.
- **Commits**: convencionales (`feat:`, `fix:`, `chore:`, `docs:`, `test:`, `refactor:`). Referencia spec si aplica: `feat(comandas): add REG-21-08 ...` no es necesario pero ayuda.

## Reglas de seguridad — no negociables

- **NUNCA** poner credenciales, claves, tokens, contraseñas, certificados en código ni en archivos versionados. Usar variables de entorno y `.env` ignorado por git.
- **NUNCA** loguear datos sensibles (contraseñas, tokens, datos fiscales completos del cliente, números de tarjeta).
- **NUNCA** usar `eval`, `exec` o construcciones similares con input del usuario.
- **NUNCA** construir SQL con string formatting; usar SQLAlchemy ORM o parámetros bindeados.
- **Hashing de contraseñas**: solo bcrypt vía passlib. Nunca MD5 ni SHA1 para passwords.
- **Datos personales**: aplicar LOPDP. Ver `specs/00-base/principles.md` para detalle.

## Cómo correr

```bash
# Setup inicial (una vez)
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head

# Desarrollo
uvicorn osiris.main:app --reload --port 8000

# Tests
pytest                          # toda la suite
pytest tests/unit/              # solo unit
pytest -k mesas                 # solo lo que matchea "mesas"

# Lint / format
ruff check src/ tests/
ruff format src/ tests/

# Migraciones
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

## Cuándo invocar a Claude Code

- Para implementar un módulo nuevo: **leer su spec primero**, luego pedir implementación.
- Para refactorizar código: pedir lectura previa del módulo, luego propuesta antes de cambiar.
- Para escribir tests: especificar qué REG/regla se está testeando.
- Para resolver bugs: incluir el reproductor antes de pedir el fix.

## Qué NO hacer

- No introducir frameworks adicionales (no Celery, no Redis, no Django) sin justificación explícita acordada.
- No usar Docker en MVP.
- No introducir microservicios; el sistema es un monolito modular.
- No agregar dependencias de servicios cloud para operación crítica diaria.
- No mockear el SRI con datos falsos en producción; usar siempre el ambiente sandbox real del SRI para tests de integración.
- No commitear `.env`, certificados, ni archivos con datos reales de empleados o clientes.

## Comunicación con el frontend

El frontend (`osiris-menu-fe`) consume:

- **API REST** vía HTTP (formato OpenAPI generado por FastAPI).
- **WebSockets** para eventos en tiempo real (cambios de estado de mesa, ítem, comanda).

Contratos formales (schemas Pydantic, eventos WS) son la **interfaz pública del backend**. Cambios incompatibles requieren bump de versión de API.

## Glosario rápido

- **Comanda**: pedido de un grupo de clientes a una o más mesas. Vive desde apertura hasta cierre con facturación.
- **Grupo de Mesas**: agrupación lógica de 2+ mesas con una sola comanda compartida.
- **Combo**: producto vendible compuesto por componentes con ruteo independiente (cocina o barra).
- **Vista operativa de cocina / barra**: pantalla de aplicación filtrada por ruteo, mostrada en tablet fija.
- **Tablet fija**: dispositivo de 12-13" montado fijo en cocina o barra.
- **Reserva teórica / Consumo confirmado**: modelo híbrido de inventario (D-01). Reserva al Enviado, consumo al pasar a En preparación.

Glosario extendido: `specs/00-base/glossary.md`.

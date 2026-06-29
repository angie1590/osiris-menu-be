# mvp-modules-scaffolding

## Purpose

Estructura modular de los tres módulos MVP del backend (§20 Mesas y zonas, §21 Comandas, §22 Cocina y barra) con archivos y routers placeholder, terminología canónica y separación de capas, sin reglas de negocio.

## Requirements

### Requirement: Estructura modular de los módulos MVP

El backend MUST incluir la estructura de los tres módulos MVP bajo `src/osiris/modules/`: `mesas` (§20), `comandas` (§21) y `cocina_barra` (§22). Cada módulo MUST contener los archivos `__init__.py`, `models.py`, `schemas.py`, `service.py`, `api.py`, `events.py` y `README.md`, según la estructura definida en `CLAUDE.md` y `project.md`.

#### Scenario: Cada módulo MVP tiene su estructura completa

- **WHEN** se inspecciona `src/osiris/modules/mesas`, `.../comandas` y `.../cocina_barra`
- **THEN** cada uno contiene `models.py`, `schemas.py`, `service.py`, `api.py`, `events.py` y `README.md`

### Requirement: Routers placeholder registrados bajo /api/v1

Cada módulo MVP MUST exponer un router FastAPI registrado bajo `/api/v1`, aunque sea placeholder. Los routers MUST NOT implementar reglas de negocio en esta etapa; las reglas viven en las propuestas funcionales por módulo respaldadas por spec o decisión.

#### Scenario: Routers de módulos montados

- **WHEN** se listan las rutas registradas de la aplicación
- **THEN** existen rutas placeholder de `mesas`, `comandas` y `cocina_barra` bajo el prefijo `/api/v1`

### Requirement: Terminología canónica en el scaffolding

Los nombres de entidades, estados y enums declarados en el scaffolding MUST usar la terminología canónica del glosario (por ejemplo estados de Mesa: Libre, Reservada, Ocupada, Por limpiar, Inactiva; estados de Ítem de comanda: Pendiente, Enviado, En preparación, Listo, Entregado, Rechazado, Anulado). MUST NOT introducirse sinónimos ni renombrarse términos canónicos.

#### Scenario: Enums alineados al glosario

- **WHEN** se revisan los enums de estado declarados en los módulos MVP
- **THEN** coinciden con los términos del glosario y de las reference-specs §20/§21/§22

### Requirement: Separación de responsabilidades por capa

El scaffolding MUST respetar la separación de capas: la lógica de negocio vive en `service.py`, los routers en `api.py` solo orquestan request/response, los modelos en `models.py` no contienen lógica compleja, y los schemas Pydantic en `schemas.py` son el contrato público. Esta separación MUST quedar establecida aunque los cuerpos sean placeholder.

#### Scenario: Capas presentes y delimitadas

- **WHEN** se inspecciona un módulo MVP
- **THEN** las responsabilidades de api/service/models/schemas están en sus archivos correspondientes sin mezclarse

### Requirement: Sin reglas de negocio ni decisiones nuevas en el scaffolding

El scaffolding de los módulos MVP MUST NOT implementar transiciones de estado, matrices de autorización, ni reglas de inventario. Cualquier ambigüedad detectada MUST NOT resolverse silenciosamente en código: MUST levantarse como decisión nueva D-XX según el flujo de `decisions.md`.

#### Scenario: Ambigüedad se levanta como decisión, no se codifica

- **WHEN** durante el scaffolding aparece una regla no documentada en specs/decisiones
- **THEN** se documenta como propuesta de decisión D-XX y no se implementa como regla definitiva en el código

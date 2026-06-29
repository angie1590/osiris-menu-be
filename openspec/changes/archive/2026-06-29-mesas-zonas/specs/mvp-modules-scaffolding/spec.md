## MODIFIED Requirements

### Requirement: Routers placeholder registrados bajo /api/v1

Cada módulo MVP MUST exponer un router FastAPI registrado bajo `/api/v1`. Los módulos **todavía en scaffolding** (`comandas`, `cocina_barra`) MUST mantener su router como placeholder y MUST NOT implementar reglas de negocio; sus reglas viven en sus propuestas funcionales respaldadas por spec o decisión. El módulo `mesas` (§20) ya **no** es placeholder: queda implementado por la capability `mesas-zonas`.

#### Scenario: Routers de módulos montados

- **WHEN** se listan las rutas registradas de la aplicación
- **THEN** existen rutas de `mesas` (implementadas), y placeholders de `comandas` y `cocina_barra` bajo el prefijo `/api/v1`

### Requirement: Sin reglas de negocio ni decisiones nuevas en el scaffolding

El scaffolding de los módulos MVP **aún en placeholder** (`comandas`, `cocina_barra`) MUST NOT implementar transiciones de estado, matrices de autorización, ni reglas de inventario. Cualquier ambigüedad detectada MUST NOT resolverse silenciosamente en código: MUST levantarse como decisión nueva D-XX según el flujo de `decisions.md`. El módulo `mesas` (§20) implementa sus reglas REG-20-XX bajo la capability `mesas-zonas`.

#### Scenario: Ambigüedad se levanta como decisión, no se codifica

- **WHEN** durante el scaffolding de `comandas`/`cocina_barra` aparece una regla no documentada en specs/decisiones
- **THEN** se documenta como propuesta de decisión D-XX y no se implementa como regla definitiva en el código

### Requirement: Terminología canónica en el scaffolding

Los nombres de entidades y las **etiquetas de UI** MUST usar la terminología canónica del glosario; MUST NOT introducirse sinónimos ni renombrarse términos canónicos. Para los módulos ya implementados, los **valores técnicos** de enums en API/DB MAY usar identificadores estables en snake_case (p. ej. `por_limpiar`, `en_cierre`) siempre que mapeen a la etiqueta canónica del glosario en la UI (estrategia establecida por `mesas-zonas` para §20). Los módulos en placeholder (`comandas`, `cocina_barra`) mantienen sus enums alineados al glosario hasta su propuesta funcional.

#### Scenario: Valores técnicos en API/DB mapeados a etiquetas canónicas

- **WHEN** se revisan los enums de un módulo implementado (p. ej. §20)
- **THEN** API/DB usan valores técnicos snake_case y la UI muestra la etiqueta canónica del glosario correspondiente

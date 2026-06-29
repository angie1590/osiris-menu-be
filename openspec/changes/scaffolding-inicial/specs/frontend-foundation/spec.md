## ADDED Requirements

### Requirement: Scaffolding del frontend con stack obligatorio

`osiris-menu-fe` MUST inicializarse con el stack obligatorio: React 19, TypeScript estricto, Vite, React Router DOM 7, TanStack Query 5, Axios, Tailwind CSS 4, shadcn/ui sobre Radix UI, React Hook Form, Zod, lucide-react, date-fns, Recharts, y para testing Vitest + Testing Library + Playwright. MUST NOT introducirse Redux, MobX, Material UI, Ant Design, Bootstrap, styled-components ni emotion.

#### Scenario: Proyecto frontend arranca

- **WHEN** se construye el servicio `web` y arranca Vite
- **THEN** la aplicación React con TypeScript estricto compila y se sirve en `5173`

#### Scenario: Stack obligatorio declarado

- **WHEN** se inspecciona `package.json`
- **THEN** están declaradas las dependencias shadcn/ui sobre Radix UI, React Hook Form, Zod, lucide-react, date-fns, Recharts, Testing Library y Playwright junto al resto del stack obligatorio

### Requirement: Cliente API base

El frontend MUST proveer un cliente API base (Axios) configurado con `VITE_API_URL`, que adjunte automáticamente un header `X-Request-Id` (UUID v4) en las mutaciones e interprete el envelope de error estructurado del backend. Las credenciales se manejan por cookie `httpOnly`; el cliente MUST NOT guardar tokens en `localStorage` ni `sessionStorage`.

#### Scenario: Cliente adjunta X-Request-Id en mutaciones

- **WHEN** el cliente API ejecuta una petición mutadora
- **THEN** incluye un header `X-Request-Id` con UUID v4

#### Scenario: Cliente no persiste tokens en almacenamiento del navegador

- **WHEN** se inspecciona el manejo de sesión del cliente
- **THEN** no se escriben tokens en `localStorage` ni `sessionStorage`

### Requirement: Cliente WebSocket base

El frontend MUST proveer un cliente WebSocket base (en `src/ws/`) capaz de conectarse a los canales canónicos del backend (`mesas`, `comandas:<comanda_id>`, `cocina`, `barra`, `connectivity`) con reconexión automática, backoff exponencial y heartbeat. En esta etapa solo establece el transporte, sin lógica de negocio por canal. No usar Socket.IO.

#### Scenario: Cliente WS se conecta a un canal

- **WHEN** la aplicación abre el cliente WebSocket hacia un canal soportado
- **THEN** establece la conexión y queda lista para recibir eventos tipados

#### Scenario: Reconexión resiliente

- **WHEN** la conexión WebSocket se cae sin cierre explícito del usuario
- **THEN** el cliente reintenta con backoff exponencial y mantiene heartbeat mientras está conectado

### Requirement: Vistas placeholder enrutadas

El frontend MUST incluir vistas placeholder enrutadas para los seis perfiles operativos: Mesero, Cocina, Barra, Caja, Admin y Público QR. Cada vista MUST renderizar como placeholder navegable. La lógica de negocio MUST NOT vivir en el frontend; las vistas consumen el contrato del backend.

#### Scenario: Cada perfil tiene su ruta navegable

- **WHEN** se navega a las rutas de Mesero, Cocina, Barra, Caja, Admin y Público QR
- **THEN** cada una renderiza su vista placeholder correspondiente

#### Scenario: Frontend no duplica reglas de negocio

- **WHEN** se inspeccionan las vistas placeholder
- **THEN** no contienen reglas de negocio del dominio (transiciones de estado, autorizaciones, inventario); solo consumen el contrato del backend

### Requirement: Estructura de carpetas dedicada del frontend

El frontend MUST seguir la estructura de carpetas dedicada definida en `osiris-menu-fe/CLAUDE.md`: `src/routes/`, `src/views/<perfil>/` (mesero, cocina, barra, caja, admin, publico), `src/modules/{mesas,comandas,cocina-barra}/` (cada uno con `index.ts`, `api.ts`, `ws.ts`, `types.ts`, `hooks/`, `components/`), `src/components/ui/`, `src/hooks/`, `src/api/`, `src/ws/`, `src/auth/`, `src/lib/` y `src/types/`. Todo HTTP MUST pasar por `src/api/` y todo WebSocket por `src/ws/`. El scaffolding de módulos MUST NOT contener reglas de negocio.

#### Scenario: Carpetas dedicadas presentes

- **WHEN** se inspecciona `osiris-menu-fe/src`
- **THEN** existen `routes/`, `api/`, `ws/`, `auth/`, `hooks/`, `types/`, `views/<perfil>/` y `modules/{mesas,comandas,cocina-barra}/` con su estructura

### Requirement: Comandos de calidad del frontend

El frontend MUST exponer los scripts `lint`, `test`, `build` y `test:e2e` en `package.json`, ejecutables por `npm run`. `npm run lint` (ESLint) MUST pasar en el scaffolding.

#### Scenario: Lint disponible y verde

- **WHEN** se ejecuta `npm run lint`
- **THEN** ESLint corre sobre el proyecto y termina sin errores

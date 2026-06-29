# realtime-foundation

## Purpose

Transporte WebSocket nativo de FastAPI con connection manager y los cinco canales canónicos como scaffolding tipado (`mesas`, `comandas:<comanda_id>`, `cocina`, `barra`, `connectivity`), sin lógica de negocio.

## Requirements

### Requirement: Transporte WebSocket nativo

El backend MUST proveer comunicación en tiempo real usando WebSockets nativos de FastAPI. MUST NOT usarse Socket.IO ni librerías externas de WebSocket (T-02, project.md).

#### Scenario: Cliente establece conexión WebSocket

- **WHEN** un cliente abre una conexión WebSocket a un canal soportado
- **THEN** el backend acepta la conexión usando el soporte nativo de FastAPI

### Requirement: Canales canónicos base

El transporte MUST exponer como scaffolding los cinco canales canónicos. Los nombres `mesas`, `comandas:<comanda_id>`, `cocina`, `barra` y `connectivity` son **nombres lógicos** del canal (glosario/`project.md`); la **ruta física recomendada** del endpoint WebSocket MUST seguir el patrón `/ws/...`:

| Nombre lógico | Ruta física recomendada |
|---|---|
| `mesas` | `/ws/mesas` |
| `comandas:<comanda_id>` | `/ws/comandas/{comanda_id}` |
| `cocina` | `/ws/cocina` |
| `barra` | `/ws/barra` |
| `connectivity` | `/ws/connectivity` |

En esta etapa solo se establece el transporte y el contrato de payload base; NO se implementa lógica de negocio de cada canal.

#### Scenario: Canales canónicos disponibles en sus rutas físicas

- **WHEN** se inspecciona el registro de endpoints WebSocket
- **THEN** existen los cinco canales canónicos expuestos en `/ws/mesas`, `/ws/comandas/{comanda_id}`, `/ws/cocina`, `/ws/barra` y `/ws/connectivity`

#### Scenario: Canal de comanda parametrizado por id

- **WHEN** un cliente se conecta al canal lógico `comandas:<comanda_id>` vía la ruta física `/ws/comandas/{comanda_id}`
- **THEN** el backend asocia la conexión a ese `comanda_id` específico

### Requirement: Connection manager y broadcasting

El backend MUST incluir un connection manager que registre y descarte conexiones por canal y permita difundir (broadcast) un mensaje a todas las conexiones de un canal. Los eventos MUST tener payload tipado.

#### Scenario: Broadcast llega a los suscriptores del canal

- **WHEN** el backend difunde un evento de prueba en un canal con varios suscriptores conectados
- **THEN** todas las conexiones activas de ese canal reciben el mensaje y las conexiones de otros canales no

#### Scenario: Desconexión limpia el registro

- **WHEN** un cliente cierra su conexión WebSocket
- **THEN** el connection manager descarta esa conexión del canal correspondiente

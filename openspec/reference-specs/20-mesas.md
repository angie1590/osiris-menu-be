# Módulo: Mesas y zonas (§20)

## Propósito

Modela el layout físico del restaurante. Gestiona el estado de ocupación de las mesas en tiempo real. Es el módulo fundacional: las comandas se abren sobre mesas, los meseros operan sobre mesas, las reservas se asignan a mesas.

## Entidades

### Zona

| Campo | Tipo | Notas |
|---|---|---|
| id | UUID | PK |
| nombre | string | "Barra" / "Primer piso" / "Segundo piso" / "Jardín" |
| descripcion | text | opcional |
| estado | enum | Activa / En cierre / Inactiva |
| aforo_max | int | informativo |
| orden_visualizacion | int | para layout |
| created_at, updated_at | timestamp | |

### Mesa

| Campo | Tipo | Notas |
|---|---|---|
| id | UUID | PK. **Permanente. Nunca se reutiliza** (D-04). |
| zona_id | UUID | FK Zona. **Mutable**: la mesa puede cambiar de zona. |
| numero_visible | string | "M12", "Jardín-3", "Barra-A" |
| capacidad | int | personas |
| estado | enum | Libre / Reservada / Ocupada / Por limpiar / Inactiva |
| comanda_activa_id | UUID? | FK Comanda, null si Libre |
| reserva_activa_id | UUID? | FK Reserva, null si no aplica |
| grupo_id | UUID? | FK GrupoMesas si está agrupada |
| activa | bool | baja lógica |
| created_at, updated_at | timestamp | |

### GrupoMesas

| Campo | Tipo | Notas |
|---|---|---|
| id | UUID | PK |
| comanda_id | UUID | FK Comanda compartida |
| mesas_ids | array UUID | mesas que componen el grupo |
| created_at, dissolved_at | timestamp | dissolved_at se setea al cerrar la comanda |

## Estados de mesa

```
       ┌─────────┐
       │  Libre  │ ←──────────────────────────┐
       └────┬────┘                            │
            │                                 │
            ├─ apertura comanda ──→ Ocupada   │
            │                                 │
            └─ horario reserva ──→ Reservada  │
                                      │      │
                                      ├──── verificación reserva ─→ Ocupada
                                      │      
                                      └─ no-show timeout ─→ Libre
       
       Ocupada ── cierre comanda ──┬─→ Por limpiar ── operador marca ──→ Libre
                                   │                
                                   └─→ Libre (si config salta Por limpiar)

       Libre / Reservada ── zona pasa a Inactiva ──→ Inactiva
       Inactiva ── zona vuelve a Activa ──→ Libre
```

## Estados de zona (D-06)

- **Activa**: opera normalmente. Acepta nuevas comandas y reservas.
- **En cierre**: transición. No acepta nuevas comandas ni reservas. Las existentes siguen. Cuando se cierra la última, pasa automáticamente a Inactiva.
- **Inactiva**: fuera de servicio. Todas las mesas en Inactiva. Reservas futuras se reasignan o cancelan con notificación.

## Reglas de negocio (las críticas)

1. **R-MESA-01**: una mesa solo puede pasar a Ocupada desde Libre o Reservada.
2. **R-MESA-02**: una mesa no puede tener más de una comanda activa.
3. **R-MESA-03**: una mesa en Grupo activo no puede ser parte de otro Grupo ni tener comanda independiente.
4. **R-MESA-04**: transición a Reservada es automática 30 minutos antes del horario de reserva (configurable). Durante esta ventana, walk-in requiere autorización Cajero o Admin Socio.
5. **R-MESA-05**: apertura sobre mesa Reservada requiere verificación explícita (código de reserva o nombre del cliente). Vincula comanda con reserva (D-05).
6. **R-MESA-06**: al cerrar comanda, mesa pasa a Por limpiar (default) o Libre (según configuración). Si era Grupo, las mesas se separan.
7. **R-MESA-07**: zona Inactiva no admite mesas Ocupadas ni Reservadas.
8. **R-MESA-08**: transición Activa → En cierre requiere autorización Nivel 2 con motivo (D-06).
9. **R-MESA-09**: zona En cierre rechaza nuevas comandas y nuevas reservas. Comandas abiertas siguen su curso. Reservas futuras se reasignan o cancelan.
10. **R-MESA-10**: al cerrarse la última comanda de una zona En cierre, pasa automáticamente a Inactiva.
11. **R-MESA-11**: zona Inactiva → Activa: el sistema revisa reservas pendientes y las reactiva si el cliente no fue notificado de cancelación.
12. **R-MESA-12**: identificador de mesa no se reutiliza nunca, incluso si la mesa se da de baja (D-04). Si se reemplaza físicamente, el QR se reimprime con el mismo identificador.
13. **R-MESA-13**: reserva no presentada (20 min después del horario, configurable): mesa pasa de Reservada a Libre, reserva se marca como No presentada.
14. **R-MESA-14**: traslado Por limpiar → Libre por cualquier operador autenticado sin autorización adicional, si el paso no está saltado globalmente (D-07).

## API esperada (esbozo)

```
GET    /api/v1/zonas
POST   /api/v1/zonas
PATCH  /api/v1/zonas/{id}
POST   /api/v1/zonas/{id}/cerrar          # Activa → En cierre, Nivel 2
POST   /api/v1/zonas/{id}/activar         # Inactiva → Activa
POST   /api/v1/zonas/{id}/desactivar      # → Inactiva (solo si vacía)

GET    /api/v1/mesas?zona_id=&estado=
POST   /api/v1/mesas
PATCH  /api/v1/mesas/{id}                 # incluye cambio de zona
POST   /api/v1/mesas/{id}/qr              # genera/regenera QR (mismo id)
DELETE /api/v1/mesas/{id}                 # baja lógica, id no se reutiliza

POST   /api/v1/mesas/{id}/marcar-libre    # Por limpiar → Libre
POST   /api/v1/grupos                     # crear Grupo de Mesas
PATCH  /api/v1/grupos/{id}                # agregar mesa al grupo
```

## Eventos WebSocket emitidos

- `mesa.estado_cambiado` — payload: `{ mesa_id, estado_anterior, estado_nuevo, comanda_id?, timestamp, usuario_id }`
- `zona.estado_cambiado` — payload: `{ zona_id, estado_anterior, estado_nuevo, timestamp, usuario_id }`
- `grupo.creado` / `grupo.disuelto` — payload: `{ grupo_id, mesas_ids, comanda_id, timestamp, usuario_id }`

Latencia objetivo: <500ms desde evento UI cliente origen hasta render UI cliente destino.

## Logs requeridos

- Cualquier cambio de estado de mesa o de zona.
- Cualquier traslado de comanda que involucra mesas (logueado en módulo comandas, no aquí).
- Cualquier verificación de reserva al abrir comanda sobre Reservada.
- Cualquier autorización de walk-in sobre mesa Reservada.

## Configuración asociada (§31)

- `ventana_reserva_min`: minutos antes del horario para pasar a Reservada (default 30).
- `tolerancia_no_show_min`: minutos después del horario para marcar No presentada (default 20).
- `saltar_estado_por_limpiar`: bool (default `false`).

## Contratos con otros módulos

- **§21 Comandas**: solicita transiciones de mesa al abrir, trasladar y cerrar comandas. Consulta estado actual.
- **§28 Reservas**: solicita transición a Reservada en la ventana previa. Recibe notificación de no-show.
- **§31 Configuración**: provee parámetros de tiempos y políticas.
- **§32 Carta pública**: usa el identificador de mesa codificado en el QR físico.

## Casos de uso clave para tests

1. Apertura de comanda sobre mesa Libre → Ocupada.
2. Apertura sobre mesa Reservada con código de reserva válido → Ocupada vinculada a reserva.
3. Apertura sobre mesa Reservada sin verificación → rechazo.
4. Cierre de comanda → Por limpiar (con default).
5. Marcar Por limpiar como Libre (cualquier operador).
6. Reserva no presentada después de 20 min → Reservada → Libre, reserva → No presentada.
7. Activar Zona En cierre: rechaza nueva comanda, deja seguir comanda abierta, al cerrarse la última pasa a Inactiva.
8. Crear Grupo de Mesas con 3 mesas Libres → todas en Ocupada, una comanda compartida.
9. Intentar incluir en otro Grupo una mesa que ya pertenece a Grupo activo → rechazo.
10. Cambio de zona de una mesa: id estable, QR estable.

## Frontend (en `osiris-menu-fe`)

Vistas que consumen este módulo:

- **mesero**: layout del salón con grid o lista por zona, estados visibles por color.
- **caja**: dashboard de ocupación por zona, transiciones manuales si aplica.
- **admin**: configuración de zonas y mesas, generación/reimpresión de QR.

Componentes:

- `<MesaCard mesa={...} />` con color por estado.
- `<ZonaLayout zona={...} mesas={...} />` con vista lista o grid.
- `<EstadoSemaforico />` (compartido entre módulos).

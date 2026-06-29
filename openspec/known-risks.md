# Riesgos conocidos / pendientes controlados

> **Este archivo NO es fuente normativa.** Es backlog de riesgos y pendientes controlados.
> Las reglas de negocio cerradas viven en `openspec/decisions.md` y en los specs
> (`openspec/specs/`). No implementar reglas de negocio desde aquí ni usarlo para justificar
> comportamiento: un pendiente que se decida resolver pasa por una propuesta/decisión formal.

Cada ítem es un pendiente identificado durante QA. **Ninguno bloquea §20 Mesas y zonas.**
Todos pertenecen a verticales futuros o a preparación productiva.

## PEND-AUTH-01 · Autenticación/autorización real
Auth real pendiente. Hoy `usuario_id` es opcional/placeholder (`null` si no hay operador) y
`require_nivel` no bloquea. Debe cerrarse cuando se implemente auth/autorización real: impacta
audit logs, mutadores, permisos y eventos WebSocket (`usuario_id` pasará a obligatorio en los
mutadores operativos). **No bloquea §20.**
- Owner sugerido: vertical de autenticación (previo o paralelo a operación productiva).

## PEND-AUDIT-01 · Retención de `audit_logs`
Política de retención/archivado/consulta de `audit_logs` pendiente. La tabla crece sin política.
No bloquea §20 ni el MVP técnico, pero **debe definirse antes de producción**.
- Owner sugerido: preparación productiva / operaciones.

## PEND-E2E-01 · Pruebas e2e multi-módulo
e2e multi-módulo pendientes. Deben implementarse cuando existan al menos §20 Mesas, §21
Comandas y §22 Cocina/Barra, para cubrir flujos extremo a extremo reales. **No bloquea §20.**
- Owner sugerido: cuando §20+§21+§22 estén disponibles.

## PEND-VIEW-01 · Vistas reales de otros verticales
Las vistas `cocina`, `barra`, `caja` y `publico/PublicoQR` siguen siendo placeholders del
scaffolding y pueden permanecer así. Se implementarán en su vertical:
- Cocina y Barra → §22.
- Caja → §23.
- Carta pública / QR → §32.
**No bloquea §20.**

## PEND-GROUP-01 · Agrupar mesas `por_limpiar`
La agrupación de mesas se mantiene limitada a mesas `libre` (decisión conservadora). Permitir
agrupar mesas `por_limpiar` requerirá una **decisión D-XX nueva** (cambia el contrato de
agrupación). Hoy se mantiene la regla; este ítem es recordatorio, no permiso para relajarla.

## PEND-FE-PERF-01 · Tamaño de bundle del frontend
El build frontend está verde. El warning de Vite "chunks > 500 kB" se **mitigó** con code
splitting por ruta (`React.lazy` + `Suspense`): el chunk único pasó a entry ~296 kB + chunks
por vista. **No bloquea §20** ni afecta funcionalidad. Re-evaluar code splitting adicional /
`manualChunks` cuando crezcan los módulos operativos (p. ej. dashboards con Recharts) o antes
de producción.

# Exclusiones de Contenidos Consultados

Registro completo de todo lo que se excluye del ranking de Contenidos Más Consultados,
ya sea por patrón dinámico (Capa 1) o por exclusión manual puntual (Capa 2).

Fuente: `Contenidos_Consultados.py`
Última actualización: 2026-03-26

---

## CAPA 1 — Patrones dinámicos (CONTAINS)

Se excluye cualquier rulename que **contenga** alguno de estos textos (sin distinguir mayúsculas/minúsculas).
Extraídos del PDF "Lógica de armado de contenidos más consultados".

| Patrón | Motivo |
|--------|--------|
| `push` | Mensajes push, no son contenidos consultados por el usuario |
| `recordatorio` | Recordatorios automáticos |
| `confirmación` / `confirmacion` | Pasos de confirmación internos de flujos |
| `cancelacion` / `cancelación` | Pasos de cancelación internos |
| `CXF` | Contenidos internos de tipo CXF |
| `CAT` | Contenidos internos de tipo CAT |
| `api` | Llamadas a API internas |
| `onboarding` | Flujo de bienvenida/onboarding |
| `menú` / `menu` | Navegación de menú |
| `Invocar` | Invocaciones internas entre flujos |
| `Bifurcador` | Nodos de bifurcación lógica |
| `No entendidos` | Motor de no-entendimiento |
| `No, nada de eso` | Respuesta de no-entendimiento |
| `No entend` | Motor de no-entendimiento (variantes) |
| `Orquestador` | Nodos orquestadores internos |
| `CTA` | Call to action internos |
| `Atiende` | Derivación a atención humana |
| `Agente` | Derivación a agente humano |
| `V2` / `v2` | Versiones internas de contenidos |
| `Instancia` | Instancias internas |
| `SIGECI` | Sistema interno SIGECI |
| `USIG` | Sistema interno USIG |
| `Botonera` | Nodos de botonera internos |
| `_autenticacion` | Flujo de autenticación |
| `_` | Todo lo que contenga guión bajo (muy agresivo — cubre la mayoría de códigos técnicos tipo `MO05CUX01_algo`) |
| `Solicitud` | Pasos de solicitud internos |
| `Reconocer` | Nodos de reconocimiento |
| `Terminar` | Nodos de cierre de flujo |
| `Cierre` | Nodos de cierre |
| `Chau` | Mensajes de despedida |
| `miBA` | Flujos de login/autenticación miBA |
| `BOT0` | Contenidos internos de tipo BOT0 |

> **Nota:** el patrón `_` es el más agresivo: excluye cualquier rulename con guión bajo,
> lo que cubre prácticamente todos los códigos técnicos (`MO05CUX01_algo`, `SA06CUX01_x`, etc.).
> Viene definido así en el PDF de lógica original.

---

## CAPA 2 — Exclusiones manuales (nombre exacto)

Para contenidos puntuales que no son capturados por los patrones de Capa 1
pero igualmente deben excluirse del ranking.

### Coyunturas

| Rulename | Motivo |
|----------|--------|
| `Coyuntura (cierre de estación Carlos Gardel línea B)` | Contenido temporal/coyuntural, no representa un trámite recurrente |

### Login y miBA

| Rulename | Motivo |
|----------|--------|
| `3. Login miBA` | Flujo de login, no es un contenido de trámite |
| `3.1 Login miBA` | Variante del flujo de login |
| `miBA - Login exitoso` | Confirmación de login |

### Navegación

| Rulename | Motivo |
|----------|--------|
| `Más temas post Menú 2.0` | Navegación interna del bot *(también cae por patrón `menu`)* |

### Atención y cierre

| Rulename | Motivo |
|----------|--------|
| `Transferir con un agente` | Derivación a agente humano *(también cae por patrón `Agente`)* |
| `147 - ¿Te puedo ayudar en algo más?` | Mensaje de cierre de sesión |
| `Cancelar` | Acción de cancelación |

### No entendidos

| Rulename | Motivo |
|----------|--------|
| `No entendió letra no existente en WA` | Motor de no-entendimiento *(también cae por patrón `No entend`)* |
| `X. Buscaba otra cosa` | Respuesta de no-entendimiento |

### Internos / pasos de flujo

| Rulename | Motivo |
|----------|--------|
| `TUR01CUX13 Preguntar género` | Paso interno del flujo de turnos |
| `MO05CUX01 - Sexo` | Paso interno del flujo de Licencias |
| `Puede estacionar CTA` | Mensaje de respuesta *(también cae por patrón `CTA`)* |

### Grupo Licencias

Todos los rulenames de este grupo representan el mismo trámite de Licencias.
**Solo debe aparecer en el ranking el que tenga más sesiones en el mes.**
Actualmente `Licencias` (MO05CUX02 Apertura) es siempre el de mayor score, por lo que los demás se excluyen.

| Rulename | Nombre amigable | Rol en el grupo |
|----------|-----------------|-----------------|
| `MO05CUX02 Apertura` | **Licencias** ← aparece en el ranking | Entrada principal del flujo |
| `Licencia prorroga  > Consultar` | — | Subcontenido. **Doble espacio antes de `>`** (así viene en los datos). Detectado feb-2026 puesto 9 (62.240 ses.) |
| `MO05CUX01 > Tiene que renovar` | — | Subcontenido. Detectado feb-2026 puesto 10 (47.990 ses.) |
| `LIC00CUX00 Validaciones` | — | Subcontenido. Detectado feb-2026 |

> Si en algún mes uno de los subcontenidos supera a `MO05CUX02 Apertura`, hay que revisar
> si conviene mostrar ese en lugar del principal, o sumar sesiones del grupo (como hace TUR00CUX02).

### Subcontenidos de TelePASE (AUSA)

El contenido principal de TelePASE corresponde al prefijo `MO08CUX03`.
Se excluyen sus subcontenidos para evitar que aparezcan en el ranking.

| Rulename | Detalle | Detectado en |
|----------|---------|--------------|
| `MO08CUX03 Apertura` | Subcontenido del flujo de TelePASE (AUSA) | ene-2026 puesto 10 (28.077 ses.) |

---

## Pendiente de revisión

| Rulename | Sesiones | Mes | Estado |
|----------|----------|-----|--------|
| `SA17CUX01 Apertura` | 26.026 | feb-2026 puesto 10 | Consultar con el equipo si corresponde excluir |

# 📁 Estructura de Queries SQL

Este directorio debe contener las 3 queries SQL que se ejecutan en Athena.

---

## Archivos Requeridos

```
queries/
├── Mensajes.sql    ← Query principal de mensajes
├── Clicks.sql      ← Query de clicks de usuarios
└── Botones.sql     ← Query de interacciones con botones
```

---

## Variables de Fecha

Cada query debe contener las siguientes variables que serán reemplazadas automáticamente:

```sql
{FECHA_INICIO}  -- Será reemplazado por: 2025-12-01
{FECHA_FIN}     -- Será reemplazado por: 2026-01-01
```

---

## Ejemplo: Mensajes.sql

```sql
-- Mensajes del chatbot Boti
SELECT 
    session_id,
    usuario,
    creation_time,
    message,
    rule_name,
    intent_id,
    score,
    msg_from,
    message_type
FROM caba-piba-consume-zone-db.boti_mensajes
WHERE fecha >= '{FECHA_INICIO}'
  AND fecha < '{FECHA_FIN}'
  AND usuario IS NOT NULL
ORDER BY session_id, creation_time
```

---

## Ejemplo: Clicks.sql

```sql
-- Clicks de usuarios en búsquedas
SELECT 
    session_id,
    ts,
    id,
    message,
    mostrado,
    response_message,
    response_intent_id
FROM caba-piba-consume-zone-db.boti_clicks
WHERE fecha >= '{FECHA_INICIO}'
  AND fecha < '{FECHA_FIN}'
ORDER BY session_id, ts
```

---

## Ejemplo: Botones.sql

```sql
-- Interacciones con botones
SELECT 
    session_id,
    ts,
    type,
    one_shot,
    button_id,
    button_text
FROM caba-piba-consume-zone-db.boti_botones
WHERE fecha >= '{FECHA_INICIO}'
  AND fecha < '{FECHA_FIN}'
  AND type IN ('oneShot', 'oneShotSearch')
ORDER BY session_id, ts
```

---

## Notas Importantes

### Database
```
caba-piba-consume-zone-db
```

### Workgroup
```
Production-caba-piba-athena-boti-group
```

### Formato de Fechas
```
FECHA_INICIO: YYYY-MM-DD (ej: 2025-12-01)
FECHA_FIN:    YYYY-MM-DD (ej: 2026-01-01)
```

### Campos Obligatorios

**Mensajes:**
- session_id
- usuario
- creation_time
- msg_from
- message_type
- rule_name

**Clicks:**
- session_id
- ts
- id
- mostrado
- response_intent_id

**Botones:**
- session_id
- ts
- type
- one_shot

---

## Validación

Antes de ejecutar, verifica que:

- ✅ Las 3 queries existen en `queries/`
- ✅ Contienen las variables `{FECHA_INICIO}` y `{FECHA_FIN}`
- ✅ Las tablas existen en la database
- ✅ Tienes permisos de lectura

---

## Testing

Para probar una query manualmente en Athena:

```sql
-- Reemplazar manualmente las fechas
-- Ejemplo para diciembre 2025:
WHERE fecha >= '2025-12-01'
  AND fecha < '2026-01-01'
```

---

**Nota:** Las queries reales deben ser proporcionadas por el equipo de datos según la estructura actual de las tablas en Athena.

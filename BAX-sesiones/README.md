# BAX Sesiones

## Descripción

Cuenta las **sesiones del canal webchat `BAX - App`** en un período, consultando
la tabla `boti_session_metrics_2` en AWS Athena.

Es una **métrica de seguimiento aparte**: genera su propio Excel y **no escribe
en el consolidado** (`Boti_Consolidado_<mes>_<año>.xlsx`). Si el equipo la pide,
hay que ir a buscar el archivo a `output/`.

## Estructura

```
BAX-sesiones/
├── BAX_sesiones.py     # Script principal
├── README.md           # Este archivo
└── output/             # Auto-generado
    ├── bax_sesiones_<mes>_<año>.csv
    └── bax_sesiones_<mes>_<año>.xlsx
```

## Requisitos

```bash
pip install boto3 awswrangler pandas openpyxl
```

### Accesos AWS

| Parámetro | Valor |
|---|---|
| Region | `us-east-1` |
| Workgroup | `Production-caba-piba-athena-boti-group` |
| Database | `caba-piba-consume-zone-db` |
| Tabla | `boti_session_metrics_2` |
| Rol | `PIBADataScientist` |

## Configuración

Lee el período del archivo centralizado de la raíz del repo:

```
C:\GCBA\Metricas_Boti_Mensual\config_fechas.txt
```

Soporta los dos modos:

**Modo 1 — Mes completo**

```ini
MES=8
AÑO=2026
```

**Modo 2 — Rango personalizado**

```ini
FECHA_INICIO=2026-08-01
FECHA_FIN=2026-08-15
```

Si están los dos, gana el rango personalizado.

## Uso

```powershell
# 1. Autenticarse (rol PIBADataScientist)
aws-azure-login --profile default --mode=gui

# 2. Ejecutar
cd C:\GCBA\Metricas_Boti_Mensual\BAX-sesiones
python BAX_sesiones.py
```

**Duración:** ~2 minutos.

## Query ejecutada

```sql
SELECT year, month, day, channel_id, channel_name,
       count(distinct s.session_id) AS Cant_sess
FROM "caba-piba-consume-zone-db"."boti_session_metrics_2" s
WHERE <filtro_particion>
  AND s.channel_id   LIKE '%webchat%'
  AND s.channel_name LIKE '%BAX - App%'
GROUP BY year, month, day, channel_id, channel_name
ORDER BY year, month, day ASC
```

Cuenta `session_id` **distintos**, agrupados por día. El total del período lo
calcula Python sumando la columna (`df['Cant_sess'].sum()`), no la query.

## El filtro por particiones (importante)

Esta es la parte sutil del script y conviene entenderla antes de tocar nada.

### Por qué no se filtra por `session_creation_time`

El filtro de fecha usa las **columnas de partición** `year` / `month` / `day`,
**no** `session_creation_time`. Es deliberado: replica exactamente el criterio
del **Excel original** que se usaba antes, que también filtraba por particiones.

Si se cambiara a `session_creation_time` el número daría distinto y dejaría de
cerrar contra el histórico.

### Por qué se castea `day` a INTEGER

Las particiones son **strings sin ceros a la izquierda**: `month='3'`,
`day='10'`. Eso rompe las comparaciones, porque lexicográficamente `'9' > '10'`.

Por eso, cuando hace falta un rango de días, el filtro usa:

```sql
CAST(day AS INTEGER) BETWEEN 5 AND 12
```

forzando comparación numérica.

### Los tres casos que arma `build_partition_filter()`

**Mes completo** — no necesita filtro de día. Es el caso más eficiente: Athena
descarta particiones enteras sin leerlas.

```sql
year='2026' AND month='8'
```

**Rango parcial dentro de un mes** — agrega el filtro numérico de día.

```sql
year='2026' AND month='8' AND CAST(day AS INTEGER) BETWEEN 1 AND 15
```

**Rango que cruza varios meses** — arma un `OR` de bloques mensuales: el primer
mes desde el día de inicio, los del medio completos, el último hasta el día de
fin.

```sql
(   (year='2026' AND month='7' AND CAST(day AS INTEGER) >= 20)
 OR (year='2026' AND month='8')
 OR (year='2026' AND month='9' AND CAST(day AS INTEGER) <= 10) )
```

## Outputs

### CSV — datos crudos

`output/bax_sesiones_<mes>_<año>.csv`

Una fila por día/canal, con las columnas tal como las devuelve Athena:
`year`, `month`, `day`, `channel_id`, `channel_name`, `Cant_sess`.

### Excel — 3 hojas

`output/bax_sesiones_<mes>_<año>.xlsx`

**Hoja `Resumen`** — el número que interesa.

| | |
|---|---|
| Sesiones BAX (webchat - BAX - App) | `123.456` |
| Período | Agosto 2026 |
| Fecha inicio | 2026-08-01 |
| Fecha fin | 2026-08-31 |

**Hoja `Detalle diario`** — serie temporal, agrupada por fecha (suma los
`channel_id` si hubiera más de uno) y con fila TOTAL al final.

| Fecha | Sesiones diarias |
|---|---|
| 01/08/2026 | 4.120 |
| 02/08/2026 | 3.987 |
| ... | ... |
| **TOTAL** | **123.456** |

**Hoja `Crudo`** — las mismas filas que el CSV, con formato.

En modo rango los archivos se llaman
`bax_sesiones_<YYYYMMDD>_a_<YYYYMMDD>.csv` / `.xlsx`.

## Detalles de implementación

**Reintento sin workgroup.** Si la query falla con un error de workgroup
(`GetWorkGroup`, permisos), el script la reintenta sin especificarlo antes de
darse por vencido.

**Normalización del nombre de columna.** Athena/Presto a veces devuelve
`cant_sess` en minúscula en vez de `Cant_sess`. El script busca las tres
variantes (`Cant_sess`, `cant_sess`, `CANT_SESS`) y renombra a la canónica. Si
no encuentra ninguna, aborta avisando qué columnas llegaron.

## Troubleshooting

**`ExpiredTokenException`** → Token AWS vencido. Re-loguear:

```powershell
aws-azure-login --profile default --mode=gui
```

**`[ADVERTENCIA] No estas usando el rol correcto`** → Estás con otro rol.
Re-loguear y elegir **PIBADataScientist**.

**`La query no retorno resultados para el periodo solicitado`** → Verificar que
el período de `config_fechas.txt` sea correcto y que existan particiones para
ese mes. También puede ser que cambiara el valor de `channel_name` (el filtro
busca `LIKE '%BAX - App%'`).

**`No se encontro la columna de cantidad de sesiones`** → Cambió el esquema que
devuelve Athena. El script imprime las columnas recibidas; actualizar la lista
de candidatos en la normalización.

## Relación con el resto del repo

| Módulo | Celda | Métrica |
|---|---|---|
| **BAX Sesiones** (este) | *Excel propio* | **Sesiones canal webchat BAX - App** |
| Usuarios y Conversaciones | D2, D3 | Conversaciones y Usuarios |
| Sesiones Abiertas | D4 | Sesiones iniciadas por push |
| Sesiones Alcanzadas | D5 | Sesiones que recibieron push |
| Pushes Enviadas | D6 | Mensajes push enviados |
| Contenidos del Bot | D7, D8 | Contenidos activos y relevantes |
| Contenidos más disparados | D11 | Top 10 contenidos |
| No Entendimiento | D13 | Tasa de no comprensión |
| Efectividad | D14 | % usuarios que lograron objetivo |
| CES | D15 | Customer Effort Score |
| CSAT | D16 | Customer Satisfaction |
| Disponibilidad | D17 | Uptime servidor WhatsApp |

---

**Gobierno de la Ciudad de Buenos Aires — Data Analytics**

# Feedback - Efectividad

## Descripción

Calcula la **Tasa de Efectividad** del bot: el porcentaje de usuarios que
respondieron que sí lograron su objetivo, sobre el total de los que
respondieron la encuesta de feedback.

Alimenta la celda **D14** del consolidado.

Además es **insumo de `calcular_efectividad_web_boti.py`** (en la raíz del
repo), que cruza este número con el de Satisfacción Web para sacar la
efectividad combinada. Ver la advertencia sobre celdas más abajo.

## Estructura

```
Feedback_Efectividad/
├── Feedback_Efectividad.py     # Script principal
├── README.md                   # Este archivo
└── output/                     # Auto-generado (5 archivos)
    ├── feedback_efectividad_<mes>_<año>.csv
    ├── feedback_efectividad_<mes>_<año>.xlsx             # Dashboard (D14)
    ├── feedback_efectividad_<mes>_<año>_base_cruda.xlsx
    ├── feedback_efectividad_<mes>_<año>_efectividad.xlsx # ← lo lee el cruce Web+Boti
    └── feedback_efectividad_<mes>_<año>_resumen.xlsx
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
| Tabla | `boti_message_metrics_2` |
| Rol | `PIBADataScientist` |

## Configuración

Lee `../config_fechas.txt`. Soporta mes completo o rango personalizado (si
están los dos, gana el rango).

```ini
MES=8
AÑO=2026
```

## Uso

```powershell
aws-azure-login --profile default --mode=gui
cd C:\GCBA\Metricas_Boti_Mensual\Feedback_Efectividad
python Feedback_Efectividad.py
```

**Duración:** ~2 minutos.

## Query ejecutada

```sql
SELECT rule_name,
       count(distinct(session_id)) AS Cant_Sesiones
FROM "caba-piba-consume-zone-db"."boti_message_metrics_2"
WHERE CAST(session_creation_time AS DATE)
      BETWEEN date '<inicio>' AND date '<fin>'
  AND rule_name LIKE '%CXF%'
GROUP BY rule_name
```

Trae **todas** las reglas que contengan `CXF` con su cantidad de sesiones
únicas. De ese universo, el script usa solo 8 para el cálculo.

> **Nota:** este módulo filtra por `session_creation_time`, a diferencia de
> `BAX-sesiones` que filtra por las particiones `year`/`month`/`day`. Son
> criterios distintos a propósito; no unificar sin verificar contra el
> histórico.

## Las 8 reglas del cálculo

La encuesta de feedback pregunta por cuatro tipos de contenido, y cada una
tiene su versión Sí y No:

| Categoría | Regla "No" | Regla "Sí" |
|---|---|---|
| Integraciones | `CXF01CUX01 No Integraciones` | `CXF01CUX01 Sí Integraciones` |
| Estáticos | `CXF01CUX02 No Estáticos` | `CXF01CUX02 Sí Estáticos` |
| Pushes | `CXF01CUX03 No Pushes` | `CXF01CUX03 Sí Pushes` |
| CATs | `CXF01CUX04 No CATs` | `CXF01CUX04 Sí CATs` |

Están en la constante `REGLAS_EFECTIVIDAD` en la cabecera del script.

> **El match es por nombre exacto.** Si Botmaker renombra una regla (aunque sea
> cambiar una tilde), el script imprime
> `[ADVERTENCIA] No se encontró la regla: <nombre>` y **le asigna 0**. El
> cálculo sigue adelante con un número mal. **Leer siempre el output buscando
> esa advertencia.**

## La fórmula

```
Positivas  = Σ (integraciones_sí + estáticos_sí + pushes_sí + cats_sí)
Negativas  = Σ (integraciones_no + estáticos_no + pushes_no + cats_no)
Total      = Positivas + Negativas

Efectividad = Positivas / Total
```

Ese porcentaje es **D14**.

## Outputs

### Dashboard — el que consolida

`output/feedback_efectividad_<mes>_<año>.xlsx`

Template estándar de 17 filas, con **D14** en formato porcentaje. Es el que lee
`consolidar_excel.py`.

### `_efectividad.xlsx` — el que lee el cruce Web+Boti

Hoja con el desglose por categoría, subtotales, los totales generales
(`SUMA TOTAL DE "NO"` / `SUMA TOTAL DE "SÍ"`) y un bloque de resumen al final:

| | Respuestas | Efectividad |
|---|---|---|
| Positivas | `<B>` | `<C>` ← porcentaje |
| Negativo | `<B>` | `<C>` |
| | `<B>` ← total | |

### ⚠️ Dependencia frágil con `calcular_efectividad_web_boti.py`

El script de la raíz lee **celdas hardcodeadas** de este archivo:

```python
efectividad_positiva_boti = leer_valor_celda(excel_boti, 'C28')
total_boti                = leer_valor_celda(excel_boti, 'B30')
```

Pero el layout de `_efectividad.xlsx` se arma con un **contador de filas
dinámico** que recorre las reglas devueltas por Athena. Es decir: **si cambia
la cantidad de reglas `CXF` que trae la query, las filas se corren y C28/B30
dejan de apuntar a los valores correctos.**

Y no falla ruidosamente — sigue leyendo *algún* número y calcula la efectividad
combinada mal.

**Antes de dar por buena la efectividad Web+Boti**, abrir
`_efectividad.xlsx` y verificar que:

- **C28** sea el porcentaje de la fila "Positivas"
- **B30** sea el total (la fila sin etiqueta, debajo de "Negativo")

Si se corrieron, hay que ajustar las celdas en `calcular_efectividad_web_boti.py`
(líneas 338-339) o —mejor— cambiarlo para que busque por etiqueta en vez de por
posición.

### Los otros tres

`_base_cruda.xlsx` tiene la salida de la query tal cual (`rule_name`,
`Cant_Sesiones`). `_resumen.xlsx` tiene la efectividad general, el desglose
positivas/negativas y el detalle por categoría en formato legible. El `.csv`
es la misma base cruda en texto plano.

## Troubleshooting

**`ExpiredTokenException`** → Token AWS vencido:

```powershell
aws-azure-login --profile default --mode=gui
```

**`[ADVERTENCIA] No se encontró la regla: <nombre>`** → Cambió el nombre de una
regla en Botmaker. Esa categoría cuenta 0 y **la efectividad queda mal**.
Buscar el nombre nuevo en el `_base_cruda.xlsx` (que trae todas las CXF) y
actualizar `REGLAS_EFECTIVIDAD` en la cabecera del script.

**La efectividad da un valor raro (0%, 100%, o muy distinto al mes pasado)** →
Revisar el output por advertencias de reglas no encontradas, y comparar el
total de respuestas contra meses anteriores.

**El cruce Web+Boti da mal** → Ver la sección de dependencia frágil arriba.

## Relación con el resto del repo

| Módulo | Celda | Métrica |
|---|---|---|
| Usuarios y Conversaciones | D2, D3 | Conversaciones y Usuarios |
| Sesiones Abiertas | D4 | Sesiones iniciadas por push |
| Sesiones Alcanzadas | D5 | Sesiones que recibieron push |
| Pushes Enviadas | D6 | Mensajes push enviados |
| Contenidos del Bot | D7, D8 | Contenidos activos y relevantes |
| Contenidos más disparados | D11 | Top 10 contenidos |
| No Entendimiento | D13 | Tasa de no comprensión |
| **Efectividad** (este) | **D14** | **% usuarios que lograron objetivo** |
| CES | D15 | Customer Effort Score |
| CSAT | D16 | Customer Satisfaction |
| Disponibilidad | D17 | Uptime servidor WhatsApp |
| BAX Sesiones | *Excel propio* | Sesiones canal webchat BAX - App |

**Cruce entre repos:** `calcular_efectividad_web_boti.py` (raíz de Boti)
combina este módulo con `Satisfaccion` del repo `Metricas_Web_Mensual`.

---

**Gobierno de la Ciudad de Buenos Aires — Data Analytics**

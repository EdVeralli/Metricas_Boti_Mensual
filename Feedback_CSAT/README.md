# Feedback - CSAT (Customer Satisfaction)

## Descripción

Calcula el **CSAT (Customer Satisfaction)**: el porcentaje de usuarios que
quedaron conformes con la interacción, sobre el total de los que respondieron
la encuesta.

Alimenta la celda **D16** del consolidado.

> **CSAT acá es un PORCENTAJE, no una escala 1-5.**
>
> El texto del template del dashboard dice *"Mide la satisfacción usando una
> escala de 1 a 5"* — eso quedó del diseño original y **no describe lo que
> calcula este script**. El valor que va a D16 es `positivas / total`,
> formateado como porcentaje, y así lo consolida `consolidar_excel.py`.
>
> El módulo que sí devuelve una escala numérica es **CES** (D15, de 1 a 5).

## Estructura

```
Feedback_CSAT/
├── Feedback_CSAT.py        # Script principal
├── README.md               # Este archivo
└── output/                 # Auto-generado
    ├── feedback_csat_<mes>_<año>.csv
    ├── feedback_csat_<mes>_<año>.xlsx          # Dashboard (D16)
    └── feedback_csat_detalle_<mes>_<año>.xlsx  # Desglose por categoría
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

Lee `../config_fechas.txt`. Soporta mes completo o rango personalizado.

```ini
MES=8
AÑO=2026
```

## Uso

```powershell
aws-azure-login --profile default --mode=gui
cd C:\GCBA\Metricas_Boti_Mensual\Feedback_CSAT
python Feedback_CSAT.py
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

La misma query que `Feedback_Efectividad` y `Feedback_CES`. Lo que cambia es
qué reglas toma cada módulo y cómo las combina.

## Las 15 reglas del cálculo

Tres tipos de contenido × cinco respuestas posibles:

| Respuesta | Integraciones (`CXF01CUX01`) | Estáticos (`CXF01CUX02`) | Pushes (`CXF01CUX03`) |
|---|---|---|---|
| Muy conforme | `Muy conforme Integraciones` | `Muy conforme Estáticos` | `Muy conforme Pushes` |
| Conforme | `Conforme Integraciones` | `Conforme Estáticos` | `Conforme Pushes` |
| Inconforme | `Inconforme Integraciones` | `Inconforme Estáticos` | `Inconforme Pushes` |
| Muy inconforme | `Muy inconforme Integraciones` | `Muy inconforme Estáticos` | `Muy inconforme Pushes` |
| No sé | `No sé Integraciones` | `No sé Estáticos` | `No sé Pushes` |

Están en la constante `REGLAS_CSAT` en la cabecera del script.

> **Dato curioso del código:** la regla `'CXF01CUX01 No sé Integraciones '`
> tiene un **espacio al final** en Botmaker. Está así en la constante, con un
> comentario que lo aclara. El script hace `.strip()` en los dos lados de la
> comparación, así que el espacio no molesta — pero si alguien "limpia" la
> constante sin entender por qué estaba, no rompe nada. Solo tenelo presente.

## La fórmula

```
Positivas = Σ (Conforme + Muy conforme)        de las 3 categorías
Negativas = Σ (Inconforme + Muy inconforme
               + No sé)                        de las 3 categorías
Total     = Positivas + Negativas

CSAT = Positivas / Total
```

Ese porcentaje es **D16**.

### "No sé" cuenta como negativa

Es una decisión metodológica del cálculo y conviene tenerla presente al
interpretar el número: los usuarios que eligieron "No sé" **no se descartan**
del denominador ni se cuentan aparte — suman del lado negativo.

Eso hace el CSAT más conservador que si se excluyeran. Si algún mes aparece un
salto raro, vale la pena mirar en el detalle cuánto pesa "No sé" sobre el total.

## Outputs

### Dashboard — el que consolida

`output/feedback_csat_<mes>_<año>.xlsx`

Template estándar de 17 filas con **D16** en formato porcentaje. Es el que lee
`consolidar_excel.py`.

### Detalle

`output/feedback_csat_detalle_<mes>_<año>.xlsx`

Las 15 reglas con sus sesiones, agrupadas por categoría, con subtotales de
positivas y negativas y el cálculo final. Sirve para auditar de dónde sale el
porcentaje y para ver el peso de "No sé".

### CSV

`output/feedback_csat_<mes>_<año>.csv`

La salida cruda de la query: **todas** las reglas `CXF` del período, no solo
las 15 del cálculo. Es donde hay que buscar si una regla cambió de nombre.

## Troubleshooting

**`ExpiredTokenException`** → Token AWS vencido:

```powershell
aws-azure-login --profile default --mode=gui
```

**`[ADVERTENCIA] No se encontró la regla: <nombre>`** → Cambió el nombre en
Botmaker. Esa respuesta cuenta 0 y **el porcentaje queda mal** sin que el
script falle. Buscar el nombre nuevo en el CSV —que trae todas las CXF— y
actualizar `REGLAS_CSAT` en la cabecera. **Leer siempre el output buscando esta
advertencia.**

**CSAT = 0** → No se encontró ninguna de las 15 reglas, o no hubo respuestas en
el período. Revisar el CSV.

**CSAT muy distinto al mes anterior** → Verificar que no haya advertencias de
reglas faltantes, y revisar en el detalle si cambió el peso de "No sé" (que
cuenta como negativa).

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
| Efectividad | D14 | % usuarios que lograron objetivo |
| CES | D15 | Customer Effort Score (1-5, menos es mejor) |
| **CSAT** (este) | **D16** | **% usuarios conformes** |
| Disponibilidad | D17 | Uptime servidor WhatsApp |
| BAX Sesiones | *Excel propio* | Sesiones canal webchat BAX - App |

### Los tres módulos de Feedback

| Módulo | Reglas que usa | Resultado |
|---|---|---|
| Efectividad | 8 (Sí/No × 4 categorías) | Porcentaje |
| CES | 10 (5 niveles × 2 categorías) | Promedio ponderado 1-5 |
| **CSAT** | **15 (5 respuestas × 3 categorías)** | **Porcentaje** |

Los tres corren **la misma query** contra `boti_message_metrics_2` filtrando
`rule_name LIKE '%CXF%'`. Se diferencian solo en la selección y la fórmula.

---

**Gobierno de la Ciudad de Buenos Aires — Data Analytics**

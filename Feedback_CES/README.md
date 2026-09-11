# Feedback - CES (Customer Effort Score)

## Descripción

Calcula el **CES (Customer Effort Score)**: qué tan fácil le resultó al usuario
interactuar con el bot, en una escala de **1 a 5**.

Alimenta la celda **D15** del consolidado.

> **Ojo con la dirección de la escala: en CES, más bajo es mejor.**
> `1 = Muy fácil`, `5 = Muy difícil`. Es al revés que CSAT, donde más alto es
> mejor. Un CES que sube mes a mes es una mala noticia.

## Estructura

```
Feedback_CES/
├── Feedback_CES.py         # Script principal
├── README.md               # Este archivo
└── output/                 # Auto-generado
    ├── feedback_ces_<mes>_<año>.csv
    ├── feedback_ces_<mes>_<año>.xlsx          # Dashboard (D15)
    └── feedback_ces_detalle_<mes>_<año>.xlsx  # Desglose y ponderaciones
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
cd C:\GCBA\Metricas_Boti_Mensual\Feedback_CES
python Feedback_CES.py
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

Es **la misma query** que usan `Feedback_Efectividad` y `Feedback_CSAT`: trae
todas las reglas `CXF` del período. Lo que cambia entre los tres módulos es
**qué reglas selecciona cada uno** de ese universo y cómo las combina.

## Las 10 reglas del cálculo

La pregunta de esfuerzo se hace sobre dos tipos de contenido (Integraciones y
Estáticos), con cinco respuestas posibles cada uno:

| Nivel | Integraciones | Estáticos |
|---|---|---|
| Muy difícil | `CXF01CUX01 Muy difícil Integraciones` | `CXF01CUX02 Muy difícil Estáticos` |
| Difícil | `CXF01CUX01 Difícil Integraciones` | `CXF01CUX02 Difícil Estáticos` |
| Más o menos | `CXF01CUX01 Más o menos Integraciones` | `CXF01CUX02 Más o menos Estáticos` |
| Fácil | `CXF01CUX01 Fácil Integraciones` | `CXF01CUX02 Fácil Estáticos` |
| Muy fácil | `CXF01CUX01 Muy fácil Integraciones` | `CXF01CUX02 Muy fácil Estáticos` |

Están en la constante `REGLAS_CES` en la cabecera del script.

> **El match es por nombre exacto, con tildes.** Los nombres llevan acentos
> (`Muy difícil`, `Fácil`). Si Botmaker renombra una regla o cambia un acento,
> el script imprime
> `[ADVERTENCIA] No se encontró la regla: <nombre>` y **le asigna 0**, y el
> promedio sale mal sin fallar. **Leer siempre el output buscando esa
> advertencia.**

## La fórmula

Primero suma Integraciones + Estáticos por nivel, después hace un **promedio
ponderado** usando estos pesos (constante `VALORES_CES`):

| Nivel | Peso |
|---|---|
| Muy difícil | 5 |
| Difícil | 4 |
| Más o menos | 3 |
| Fácil | 2 |
| Muy fácil | 1 |

```
total_sesiones  = Σ sesiones de los 5 niveles
total_ponderado = Σ (peso_nivel × sesiones_nivel)

CES = total_ponderado / total_sesiones
```

El resultado es un número entre 1 y 5. Ese valor es **D15**.

**Ejemplo.** Si en el mes hubo 100 "Muy fácil", 50 "Fácil" y 10 "Muy difícil":

```
total_sesiones  = 100 + 50 + 10 = 160
total_ponderado = (1×100) + (2×50) + (5×10) = 100 + 100 + 50 = 250
CES             = 250 / 160 = 1.56
```

Un 1.56 indica esfuerzo bajo, que es lo deseable.

## Outputs

### Dashboard — el que consolida

`output/feedback_ces_<mes>_<año>.xlsx`

Template estándar de 17 filas con **D15** como número decimal. Es el que lee
`consolidar_excel.py`.

### Detalle

`output/feedback_ces_detalle_<mes>_<año>.xlsx`

Las 10 reglas con sus sesiones, los totales por nivel, la columna de ponderados
(peso × sesiones) y el cálculo final del promedio. Sirve para auditar de dónde
sale el número.

### CSV

`output/feedback_ces_<mes>_<año>.csv`

La salida cruda de la query: **todas** las reglas `CXF` del período, no solo
las 10 del cálculo. Es donde hay que buscar si una regla cambió de nombre.

## Troubleshooting

**`ExpiredTokenException`** → Token AWS vencido:

```powershell
aws-azure-login --profile default --mode=gui
```

**`[ADVERTENCIA] No se encontró la regla: <nombre>`** → Cambió el nombre en
Botmaker (muy probablemente un tema de acentos). Ese nivel cuenta 0 y **el
promedio queda sesgado**. Buscar el nombre nuevo en el CSV —que trae todas las
CXF— y actualizar `REGLAS_CES` en la cabecera del script.

**CES = 0** → No se encontró ninguna de las 10 reglas, o no hubo respuestas en
el período. Revisar el CSV.

**CES muy distinto al mes anterior** → Antes de reportarlo, verificar que no
haya advertencias de reglas faltantes y comparar `total_sesiones` contra meses
previos. Una caída fuerte del total suele explicar saltos raros.

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
| **CES** (este) | **D15** | **Customer Effort Score (1-5, menos es mejor)** |
| CSAT | D16 | Customer Satisfaction |
| Disponibilidad | D17 | Uptime servidor WhatsApp |
| BAX Sesiones | *Excel propio* | Sesiones canal webchat BAX - App |

Los tres módulos de Feedback (`Efectividad`, `CES`, `CSAT`) corren **la misma
query** y se diferencian solo en qué reglas `CXF` toman y cómo las combinan.

---

**Gobierno de la Ciudad de Buenos Aires — Data Analytics**

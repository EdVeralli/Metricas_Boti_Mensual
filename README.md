# Sistema de Métricas Boti - GCBA

[![GitHub](https://img.shields.io/badge/GitHub-EdVeralli%2FMetricas__Boti__Mensual-blue?logo=github)](https://github.com/EdVeralli/Metricas_Boti_Mensual)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-GCBA-green)]()

Sistema automatizado para el cálculo de métricas mensuales del chatbot **Boti**
de la Ciudad de Buenos Aires.

**Repositorio:** https://github.com/EdVeralli/Metricas_Boti_Mensual

> **¿Buscás el proceso mensual completo?**
> Este README documenta **este repo**. El proceso end-to-end que cruza los dos
> repos (Web + Boti) está en **[`PROCESO_MENSUAL.md`](PROCESO_MENSUAL.md)** —
> ese es el runbook maestro y vive idéntico en ambos repos.

---

## Tabla de Contenidos

- [Descripción General](#descripción-general)
- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso - Guía Rápida](#uso---guía-rápida)
- [Módulos Implementados](#módulos-implementados)
- [Dashboard de Métricas](#dashboard-de-métricas)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Scripts Principales](#scripts-principales)
- [Solución de Problemas](#solución-de-problemas)
- [Changelog](#changelog)

---

## Descripción General

Este sistema procesa datos del chatbot Boti para calcular las métricas mensuales
del tablero institucional. Cada métrica la calcula un módulo independiente que
genera su propio Excel con formato estandarizado; después un consolidador los
unifica en un único dashboard.

### Los números del sistema

| Concepto | Cantidad |
|---|---|
| Módulos totales | **13** |
| Módulos que alimentan el consolidado | **11** |
| Celdas del consolidado que llenamos | **13** (D2-D8, D11, D13-D17) |
| Módulos con Excel propio (no consolidan) | **2** (BAX Sesiones, Temas Consultados) |
| Módulos que requieren ejecución manual | **1** (No Entendidos) |
| Filas del dashboard a cargo de otro equipo | **3** (D9, D10, D12) |

### Características

- **13 módulos independientes**, cada uno con su propio Excel de salida.
- **Configuración centralizada** en `config_fechas.txt` (un solo lugar define el período).
- **Ejecución automatizada** con `run_all.py`.
- **Consolidación automática** con `consolidar_excel.py`.
- **Integración con AWS Athena** para procesamiento de grandes volúmenes.
- **Cruce con el repo Web** para la efectividad combinada.

---

## Arquitectura del Sistema

### Flujo de Trabajo General

```
┌──────────────────────────────────────────────────────────────────┐
│  1. CONFIGURACIÓN                                                │
│     config_fechas.txt  (MES=8, AÑO=2026)                        │
└──────────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────────┐
│  2. NO_ENTENDIDOS  (MANUAL - requiere interacción AWS)           │
│     cd No_Entendidos                                             │
│     ├─ python athena_connector.py   (descarga CSVs, ~25 GB)     │
│     └─ python No_Entendidos.py      (calcula D13)               │
└──────────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────────┐
│  3. EJECUCIÓN DE MÓDULOS  (run_all.py → 12 módulos)             │
│     Verifica que No_Entendidos ya corrió y lo saltea             │
│                                                                  │
│     ── Alimentan el consolidado ──                               │
│     ├─ Usuarios_Conversaciones      → D2, D3                     │
│     ├─ Sesiones_Abiertas_Pushes     → D4                         │
│     ├─ Sesiones_alcanzadas_pushes   → D5                         │
│     ├─ Pushes_Enviadas              → D6                         │
│     ├─ Contenidos_Bot               → D7, D8                     │
│     ├─ Contenidos_mas_disparados    → D11                        │
│     ├─ Feedback_Efectividad         → D14                        │
│     ├─ Feedback_CES                 → D15                        │
│     ├─ Feedback_CSAT                → D16                        │
│     └─ Metricas_Boti_Disponibilidad → D17                        │
│                                                                  │
│     ── Excel propio (no consolidan) ──                           │
│     ├─ BAX-sesiones                                              │
│     └─ Temas_Consultados                                         │
└──────────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────────┐
│  4. CONSOLIDACIÓN  (consolidar_excel.py)                         │
│     Lee los Excel de los 11 módulos y arma el dashboard único    │
│     → Boti_Consolidado_<mes>_<año>.xlsx                          │
└──────────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────────┐
│  5. EFECTIVIDAD WEB+BOTI  (calcular_efectividad_web_boti.py)     │
│     Cruza Feedback_Efectividad (Boti) con Satisfacción (Web)     │
│     → efectividad_web_boti_<mes>_<año>.xlsx                      │
└──────────────────────────────────────────────────────────────────┘
```

### Componentes

**`config_fechas.txt`** — Configuración centralizada en la raíz. Define el
período (mes completo o rango). Lo leen los 13 módulos.

**`run_all.py`** — Orquestador maestro. Verifica pre-requisitos, valida
credenciales AWS, ejecuta 12 módulos en secuencia (saltea No_Entendidos) y
muestra el resumen. Duración: 20-40 minutos.

**Módulos independientes (13 carpetas)** — Cada uno calcula su métrica y deja
el Excel en su propia carpeta `output/`.

**`consolidar_excel.py`** — Lee los Excel de los módulos, extrae los valores de
cada celda y genera el dashboard unificado en la raíz.

---

## Requisitos

### Software

```
Python 3.8+
AWS CLI v2
aws-azure-login
```

### Librerías Python

```bash
pip install boto3 awswrangler pandas numpy openpyxl selenium requests pytz nltk
python -m nltk.downloader stopwords
```

`nltk` + stopwords son necesarios para **Temas Consultados** (clasificación de
mensajes). El script los descarga solo la primera vez si faltan.

### Accesos AWS

| Parámetro | Valor |
|---|---|
| Workgroup | `Production-caba-piba-athena-boti-group` |
| Database | `caba-piba-consume-zone-db` |
| Rol | `PIBADataScientist` |
| Region | `us-east-1` |

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/EdVeralli/Metricas_Boti_Mensual.git
cd Metricas_Boti_Mensual
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar AWS Azure Login (una sola vez)

```bash
aws-azure-login --configure --profile default
```

Completar con Azure Tenant ID, Azure App ID URI y Default Role ARN
(**PIBADataScientist**). Guía detallada en
`CLI_login_AWS-azure_WINDOWS_v2.pdf` (raíz del repo).

---

## Configuración

### Archivo `config_fechas.txt` (raíz del repositorio)

Compartido por los 13 módulos. Define el período a procesar.

**Opción 1 — Mes completo (recomendado):**

```ini
MES=8
AÑO=2026
```

**Opción 2 — Rango personalizado:**

```ini
FECHA_INICIO=2026-08-01
FECHA_FIN=2026-08-15
```

Si especificás `FECHA_INICIO` y `FECHA_FIN`, se ignoran `MES` y `AÑO`.

> **Importante:** `Temas_Consultados` solo soporta la opción 1 (mes completo),
> porque compara el mes contra el anterior.

---

## Uso - Guía Rápida

### PASO 1: Configurar el período

```bash
cd C:\GCBA\Metricas_Boti_Mensual
notepad config_fechas.txt
```

### PASO 2: Login AWS

```bash
aws-azure-login --profile default --mode=gui
```

Elegir el rol **PIBADataScientist**.

### PASO 3: Exportar los TSV de Botmaker

`Contenidos_Bot` necesita **2 archivos TSV** exportados de Botmaker (el del mes
que se reporta y el del mes anterior) copiados en `Contenidos_Bot/`. Sin ellos
ese módulo falla y quedan vacías D7 y D8.

### PASO 4: Ejecutar No_Entendidos (MANUAL)

Requiere interacción para revalidar credenciales AWS antes de cada query.

```bash
cd No_Entendidos
python athena_connector.py
python No_Entendidos.py
cd ..
```

**Duración:** 30-50 minutos.

### PASO 5: Ejecutar los demás módulos

```bash
python run_all.py
```

Verifica que No_Entendidos ya corrió (busca su Excel de output). Si no lo
encuentra, avisa y sigue igual, pero D13 queda sin dato.

**Duración:** 20-40 minutos. El módulo más pesado es
`Contenidos_mas_disparados` (escanea toda la vista de Athena).

### PASO 6: Consolidar

```bash
python consolidar_excel.py
```

Genera `Boti_Consolidado_<mes>_<año>.xlsx` en la raíz.

### PASO 7: Efectividad WEB+BOTI (requiere el repo Web corrido)

```bash
python calcular_efectividad_web_boti.py
```

Genera `efectividad_web_boti/efectividad_web_boti_<mes>_<año>.xlsx`.

---

## Módulos Implementados

### Resumen

| # | Módulo | Carpeta | Celda(s) | Fuente | AWS |
|---|---|---|---|---|---|
| 1 | Usuarios y Conversaciones | `Metricas_Boti_Conversaciones_Usuarios/` | D2, D3 | Athena | Sí |
| 2 | Pushes Enviadas | `Pushes_Enviadas/` | D6 | Athena | Sí |
| 3 | Sesiones Abiertas por Pushes | `Sesiones_Abiertas_Pushes/` | D4 | Athena | Sí |
| 4 | Sesiones Alcanzadas por Pushes | `Sesiones_alcanzadas_pushes/` | D5 | Athena | Sí |
| 5 | **BAX Sesiones** | `BAX-sesiones/` | *Excel propio* | Athena | Sí |
| 6 | Contenidos del Bot | `Contenidos_Bot/` | D7, D8 | 2 TSV Botmaker | No |
| 7 | **Contenidos más disparados** | `Contenidos_mas_disparados/` | D11 | Athena (vista) | Sí |
| 8 | **Temas Consultados** | `Temas_Consultados/` | *Excel propio* | Athena | Sí |
| 9 | No Entendimiento **(MANUAL)** | `No_Entendidos/` | D13 | Athena | Sí |
| 10 | Feedback - Efectividad | `Feedback_Efectividad/` | D14 | Athena | Sí |
| 11 | Feedback - CES | `Feedback_CES/` | D15 | Athena | Sí |
| 12 | Feedback - CSAT | `Feedback_CSAT/` | D16 | Athena | Sí |
| 13 | Disponibilidad WhatsApp | `Metricas_Boti_Disponibilidad/` | D17 | Web scraping | No |

---

### 1. Usuarios y Conversaciones — D2, D3

**Script:** `Usuarios_Conversaciones.py`
Cuenta sesiones únicas y usuarios únicos del período. **~2 min.**

### 2. Pushes Enviadas — D6

**Script:** `Pushes_Enviadas.py`
Cuenta mensajes enviados con formato Template. **~3 min.**

### 3. Sesiones Abiertas por Pushes — D4

**Script:** `Sesiones_Abiertas_porPushes.py`
Sesiones con `starting_cause = 'WhatsAppTemplate'`. **~2 min.**

### 4. Sesiones Alcanzadas por Pushes — D5

**Script:** `Sesiones_Alcanzadas.py`
Sesiones que recibieron al menos un push. **~2 min.**

### 5. BAX Sesiones — Excel propio

**Script:** `BAX_sesiones.py`
Cuenta sesiones del canal **webchat BAX - App**. Genera CSV con datos crudos
(year / month / day / channel_id / channel_name / Cant_sess) y Excel con total
más serie diaria.

**No escribe en el consolidado** — es una métrica de seguimiento aparte. **~2 min.**

### 6. Contenidos del Bot — D7, D8

**Script:** `Contenidos_Bot.py`
**Fuente:** archivos TSV exportados de Botmaker (`rules-*.tsv`). **No requiere AWS.**

- **D7:** contenidos activos en Botmaker (topics prendidos)
- **D8:** contenidos relevantes para el usuario (sin internos / push / login)

> **REQUISITO: 2 archivos TSV en `Contenidos_Bot/`**
>
> | Archivo | Descripción | Ejemplo |
> |---|---|---|
> | TSV mes actual | Exportación del mes que se reporta | `rules-2026.08.31-14.12.tsv` |
> | TSV mes anterior | Exportación del mes previo | `rules-2026.07.31-10.00.tsv` |
>
> Formato Botmaker: `rules-YYYY.MM.DD-HH.MM.tsv`. El script toma los 2 más
> recientes automáticamente y avisa si falta alguno.

**Outputs:** `contenidos_bot_<mes>_<año>.xlsx` + `contenidos_bot_detalle_<mes>_<año>.xlsx`

### 7. Contenidos más disparados — D11

**Script:** `Contenidos_mas_disparados.py`
**Fuente:** vista `boti_vw_buscador_rulename` en Athena.

Replica la lógica del Power BI "Consultas por día". Aplica **filtrado en 2 capas**
(35+ patrones dinámicos + 13 exclusiones manuales), agrupa por prefijo
(`RulenameUnique`), aplica la regla especial `TUR00CUX02` y mapea a nombres
amigables.

**D11** recibe el Top 10 formateado como texto multilínea.

**Outputs:** CSV crudo + Excel detalle (hojas "Buscador de contenidos" e
"Histórico") + dashboard.

Es el módulo **más pesado** del repo — escanea toda la vista. Ver
`Contenidos_mas_disparados/README.md` para el detalle de la lógica.

### 8. Temas Consultados — Excel propio

**Script:** `Temas_Consultados.py`
**Fuente:** Athena (`boti_message_metrics_2`), mes actual + mes anterior.

Reemplaza el flujo manual del notebook `mensajes.ipynb` del repo
[Tablero-de-mensajes-y-disparadores](https://github.com/EdVeralli/Tablero-de-mensajes-y-disparadores),
que queda como referencia histórica.

Clasifica los mensajes de usuario en 14 categorías + "Otros" y genera el
**ranking de temas** que se pega en el tablero:

```
output/ranking_temas_consultados_<mes>_<año>.txt
```

**Outputs:** CSV de temas, top 200 mensajes, comparativo, reporte, top
variaciones y el ranking (en `.txt` y `.xlsx`). Ver `Temas_Consultados/README.md`.

> El CSV grande (`temas_consultados_*.csv`, ~500 MB) está en `.gitignore`.

### 9. No Entendimiento — D13 (MANUAL)

**Scripts (en orden):**
1. `athena_connector.py` — descarga 3 CSVs grandes (~25 GB). **10-20 min.**
2. `No_Entendidos.py` — procesa y calcula D13. **20-30 min.**

Se ejecuta **a mano antes** de `run_all.py` porque pide revalidar credenciales
AWS entre queries.

Desglose típico: OneShots ~65%, Clicks ~13%, Texto ~5%, Abandonos ~5%,
Nada ~6%, NE ~6%, Letra ~0.1%. **D13 = Nada + NE ≈ 11-12%.**

### 10. Feedback - Efectividad — D14

**Script:** `Feedback_Efectividad.py`
Tasa de transacciones completadas. **~2 min.**
También es insumo de `calcular_efectividad_web_boti.py`.

### 11. Feedback - CES — D15

**Script:** `Feedback_CES.py`
Customer Effort Score: promedio ponderado de facilidad de uso (1-5). **~2 min.**

### 12. Feedback - CSAT — D16

**Script:** `Feedback_CSAT.py`
Customer Satisfaction: promedio de satisfacción (1-5). **~2 min.**

### 13. Disponibilidad WhatsApp — D17

**Script:** `WhatsApp_Availability.py`
**Tecnología:** web scraping con Selenium.
**Fuente:** https://metastatus.com/whatsapp-business-api
**No requiere AWS.** **~1 min.**

---

## Dashboard de Métricas

El dashboard final tiene **17 filas** de indicadores. **13 celdas las llenamos
nosotros** (D2-D8, D11, D13-D17); **3 son de otro equipo** (D9, D10, D12).

| Fila | Indicador | Descripción | Módulo | Estado |
|---|---|---|---|---|
| **1** | Headers | Indicador / Descripción / Período | — | Header |
| **2** | Conversaciones | Q Conversaciones | Usuarios y Conversaciones | Implementado |
| **3** | Usuarios | Q Usuarios únicos | Usuarios y Conversaciones | Implementado |
| **4** | Sesiones abiertas por Pushes | Sesiones iniciadas con push | Sesiones Abiertas | Implementado |
| **5** | Sesiones Alcanzadas por Pushes | Sesiones que recibieron push | Sesiones Alcanzadas | Implementado |
| **6** | Mensajes Pushes Enviados | Q de mensajes push | Pushes Enviadas | Implementado |
| **7** | Contenidos en Botmaker | Contenidos activos | Contenidos del Bot | Implementado |
| **8** | Contenidos Prendidos para el USUARIO | Contenidos relevantes | Contenidos del Bot | Implementado |
| **9** | Interacciones | Q Interacciones | — | Otro equipo |
| **10** | Trámites, solicitudes y turnos | Q Trámites disponibles | — | Otro equipo |
| **11** | Contenidos más consultados | Top 10 | **Contenidos más disparados** | **Implementado** |
| **12** | Derivaciones | Q Derivaciones | — | Otro equipo |
| **13** | No entendimiento | Performance motor IA | No Entendidos | Implementado |
| **14** | Tasa de Efectividad | % usuarios que lograron objetivo | Feedback Efectividad | Implementado |
| **15** | CES | Facilidad de interacción (1-5) | Feedback CES | Implementado |
| **16** | Satisfacción (CSAT) | Satisfacción usuario (1-5) | Feedback CSAT | Implementado |
| **17** | Uptime servidor | Disponibilidad WhatsApp | Disponibilidad | Implementado |

### Cómo funciona

1. Cada módulo crea un Excel con la **estructura completa** (17 filas).
2. **Solo llena** las celdas que le corresponden en la columna D.
3. El consolidador lee todos los Excel y extrae los valores.
4. Genera un único Excel con todas las métricas unificadas.

---

## Estructura del Proyecto

```
Metricas_Boti_Mensual/                      ← Repositorio raíz
│
├── README.md                               ← Este documento
├── PROCESO_MENSUAL.md                      ← Runbook maestro (Web + Boti)
├── config_fechas.txt                       ← Configuración centralizada
├── run_all.py                              ← Script maestro
├── consolidar_excel.py                     ← Consolidador de métricas
├── calcular_efectividad_web_boti.py        ← Efectividad cruzada WEB+BOTI
├── diagnosticar_excel.py                   ← Herramienta de diagnóstico
├── CLI_login_AWS-azure_WINDOWS_v2.pdf      ← Guía de setup AWS
│
├── Boti_Consolidado_<mes>_<año>.xlsx       ← Dashboard final (generado)
├── efectividad_web_boti/
│   └── efectividad_web_boti_<mes>_<año>.xlsx
│
├── Metricas_Boti_Conversaciones_Usuarios/  ← [1] D2, D3
│   ├── Usuarios_Conversaciones.py
│   └── output/
│
├── Pushes_Enviadas/                        ← [2] D6
│   ├── Pushes_Enviadas.py
│   └── output/
│
├── Sesiones_Abiertas_Pushes/               ← [3] D4
│   ├── Sesiones_Abiertas_porPushes.py
│   └── output/
│
├── Sesiones_alcanzadas_pushes/             ← [4] D5
│   ├── Sesiones_Alcanzadas.py
│   └── output/
│
├── BAX-sesiones/                           ← [5] Excel propio
│   ├── BAX_sesiones.py
│   └── output/
│
├── Contenidos_Bot/                         ← [6] D7, D8
│   ├── Contenidos_Bot.py
│   ├── rules-*.tsv                         ← Exportados de Botmaker
│   └── output/
│
├── Contenidos_mas_disparados/              ← [7] D11
│   ├── Contenidos_mas_disparados.py
│   ├── README.md                           ← Lógica de filtrado detallada
│   ├── exclusiones_capa2.md
│   ├── NOTAS_UNIFICACION_SCRIPT.md
│   ├── *.pbix                              ← Power BI de referencia
│   └── output/
│
├── Temas_Consultados/                      ← [8] Excel propio
│   ├── Temas_Consultados.py
│   ├── Temas_Consultados_Anual.py          ← Variante anual
│   ├── README.md
│   └── output/
│       └── ranking_temas_<mes>_<año>.txt   ← Texto para el tablero
│
├── No_Entendidos/                          ← [9] D13 (MANUAL)
│   ├── README.md                           ← Documentación detallada
│   ├── athena_connector.py                 ← Paso 1: descarga datos
│   ├── No_Entendidos.py                    ← Paso 2: calcula métricas
│   ├── Mensajes.sql / Clicks.sql / Botones.sql
│   ├── temp/                               ← CSVs temporales (~25 GB, gitignored)
│   └── output/
│
├── Feedback_Efectividad/                   ← [10] D14
│   ├── Feedback_Efectividad.py
│   └── output/
│
├── Feedback_CES/                           ← [11] D15
│   ├── Feedback_CES.py
│   └── output/
│
├── Feedback_CSAT/                          ← [12] D16
│   ├── Feedback_CSAT.py
│   └── output/
│
└── Metricas_Boti_Disponibilidad/           ← [13] D17
    ├── WhatsApp_Availability.py
    └── output/
```

---

## Scripts Principales

### run_all.py

Orquestador maestro. Ejecuta 12 de los 13 módulos (saltea No_Entendidos).

```bash
python run_all.py
```

**Qué hace:**

- Verifica que exista `config_fechas.txt` y lee el período.
- Chequea los pre-requisitos manuales: los 2 TSV de `Contenidos_Bot` y el
  output de `No_Entendidos`. Si falta alguno, avisa pero **no aborta**.
- Valida credenciales AWS antes de arrancar (aborta si no hay).
- Ejecuta los 12 módulos en secuencia, con la salida fluyendo en tiempo real
  (`PYTHONUNBUFFERED=1`, sin `capture_output`).
- Muestra un resumen final con duración y estado por módulo.

**Duración:** 20-40 minutos.

### consolidar_excel.py

Consolida los Excel parciales en el dashboard único.

```bash
python consolidar_excel.py
```

- Busca el Excel más reciente en cada carpeta `output/`.
- Excluye los archivos `*_detalle_*`.
- Extrae las 13 celdas (D2-D8, D11, D13-D17).
- Aplica formato según el tipo de dato (texto multilínea para D11, porcentaje
  para D13/D14/D16/D17, decimal para D15).
- Guarda `Boti_Consolidado_<mes>_<año>.xlsx` en la raíz.

### calcular_efectividad_web_boti.py

Calcula la Tasa de Efectividad combinada WEB+BOTI. **Requiere que el repo
`Metricas_Web_Mensual` ya haya corrido el mismo período.**

```bash
python calcular_efectividad_web_boti.py
```

**Lee:**

- `Feedback_Efectividad/output/feedback_efectividad_<mes>_<año>_efectividad.xlsx`
  → C28 (Efectividad Positiva Boti), B30 (Total Boti)
- `../Metricas_Web_Mensual/Satisfaccion/data/conteo_completo_<mes>_<año>.xlsx`
  → S2 (Total Web), T2 (Tasa Efectividad WEB)

**Fórmula:**

```
Total General          = Total Boti + Total Web
Ponderación Boti       = Total Boti / Total General
Primer Parcial         = Efectividad Positiva Boti × Ponderación Boti
Ponderación WEB        = Total Web / Total General
Segundo Parcial        = Ponderación WEB × Tasa Efectividad WEB
Tasa WEB+BOTI          = Primer Parcial + Segundo Parcial
```

**Genera:** `efectividad_web_boti/efectividad_web_boti_<mes>_<año>.xlsx`

### diagnosticar_excel.py

Herramienta de diagnóstico para inspeccionar Excel corruptos o mal formateados.

```bash
python diagnosticar_excel.py
```

---

## Solución de Problemas

### Token AWS expirado

```
ExpiredTokenException: The security token included in the request is expired
```

Re-loguear en otra terminal y volver a correr. El script toma las credenciales
nuevas automáticamente.

```bash
aws-azure-login --profile default --mode=gui
```

### Rol AWS incorrecto

```
[ADVERTENCIA] No estas usando el rol correcto
```

Estás autenticado con otro rol. Re-loguear y elegir **PIBADataScientist**.

### No_Entendidos no fue ejecutado

```
No_Entendidos NO fue ejecutado para agosto 2026
   Archivo esperado: No_Entendidos/output/no_entendimiento_agosto_2026.xlsx
```

`run_all.py` lo saltea siempre (es manual). Correrlo antes:

```bash
cd No_Entendidos
python athena_connector.py
python No_Entendidos.py
cd ..
python run_all.py
```

### Falta 1 TSV (Contenidos_Bot)

Faltan los TSV de Botmaker en `Contenidos_Bot/`. El script indica cuál falta y
de qué mes. Exportar del portal Botmaker y copiar a esa carpeta.

### Query de Contenidos_mas_disparados parece colgada

Es el módulo más pesado — escanea toda la vista `boti_vw_buscador_rulename`.
El script imprime timestamps en cada paso. Si pasan más de 10 minutos sin
imprimir nada, ahí sí hay un problema real.

### El consolidador no encuentra archivos

```
No se encontraron archivos en [módulo]
```

El módulo no corrió bien. Verificar que existan Excel en su carpeta `output/`
y re-ejecutarlo manualmente.

### Error de memoria RAM

```
Unable to allocate X.XX GiB for an array
```

No_Entendidos y Contenidos_mas_disparados manejan datasets grandes. Cerrar
navegadores y Excel antes de correr.

**Mínimo:** 8 GB. **Recomendado:** 16 GB.

### GitHub rechaza el push (archivo >100 MB)

Algún output se pasó del límite. Los conocidos ya están en `.gitignore`:

- `Temas_Consultados/output/temas_consultados_*.csv` (~500 MB)
- `No_Entendidos/temp/*.csv` (varios GB)

Si aparece otro: agregar el patrón al `.gitignore` y
`git rm --cached <archivo>` para sacarlo del tracking sin borrarlo del disco.

### No se encuentra config_fechas.txt

Crearlo en la raíz del repo:

```bash
cd C:\GCBA\Metricas_Boti_Mensual
echo MES=8 > config_fechas.txt
echo AÑO=2026 >> config_fechas.txt
```

---

## Tips y Buenas Prácticas

**Mejor momento para correr:** primera semana del mes, para procesar el mes
anterior.

**Limpieza de temporales:** los CSVs de `No_Entendidos/temp/` pesan ~25 GB y se
pueden borrar al terminar.

```bash
del No_Entendidos\temp\*.csv
```

**Orden que conviene:** No_Entendidos primero (es el más largo y el que pide
interacción), después `run_all.py`, que corre desatendido.

---

## Changelog

### v2.5 (Septiembre 2026) — **ACTUAL**

- **README reescrito:** estaba desactualizado desde febrero 2026. Documentaba
  10 módulos cuando ya son 13.
- **Documentados 3 módulos faltantes:** `BAX-sesiones`, `Contenidos_mas_disparados`
  y `Temas_Consultados`.
- **Corregido D11:** figuraba como "responsabilidad de otro equipo"; lo genera
  `Contenidos_mas_disparados` desde junio 2026.
- **Agregado link a `PROCESO_MENSUAL.md`**, el runbook maestro end-to-end que
  vive idéntico en ambos repos.
- **Limpieza:** eliminados `run_all_old.py` y el worktree duplicado
  `.claude/worktrees/`.

### v2.4 (Febrero 2026)

- **NUEVO:** `Contenidos_Bot.py` — contenidos activos y relevantes (D7, D8).
- `Contenidos_Bot` convertido de notebook Jupyter a script standalone.
- `run_all.py` verifica que No_Entendidos ya corrió antes de continuar.
- `athena_connector.py` pausa antes de cada query para revalidar credenciales.
- `Feedback_Efectividad.py` con template de Excel unificado (igual que CES/CSAT).

### v2.3 (Enero 2026)

- **NUEVO:** `calcular_efectividad_web_boti.py` — efectividad combinada WEB+BOTI.
- Integración con el repositorio `Metricas_Web_Mensual`.

### v2.2 (Enero 2026)

- `run_all.py` con soporte para múltiples scripts por módulo.
- `consolidar_excel.py`: corregido el path del módulo No_Entendidos.

### v2.1 (Enero 2026)

- Sistema modular con módulos independientes.
- Script maestro `run_all.py` y consolidador automático.
- Dashboard con 17 indicadores.

### v2.0 (Enero 2026)

- Integración con `config_fechas.txt` centralizado.
- Optimización PASO 6 en No_Entendidos (60 min → 2 seg).

### v1.0 (Diciembre 2025)

- Versión inicial con módulos independientes.

---

## Soporte

**Repositorio:** https://github.com/EdVeralli/Metricas_Boti_Mensual

Para reportar problemas: abrir un Issue con logs completos, versión de Python y
pasos para reproducir.

**Equipo:** Data Analytics - GCBA
**Mantenedor:** @EdVeralli

---

## Licencia

Uso interno — Gobierno de la Ciudad de Buenos Aires.

---

**Última actualización:** 11 de septiembre de 2026
**Versión:** 2.5

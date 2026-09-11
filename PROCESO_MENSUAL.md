# Proceso Mensual de Métricas — Runbook

> **Runbook maestro** del proceso mensual de generación de métricas de la
> Ciudad. Vive en los DOS repos con contenido idéntico. Cubre todo el flujo
> end-to-end: pre-requisitos, ejecución, consolidación, distribución y
> troubleshooting.
>
> **Este proceso involucra 3 repos:**
> - `C:\GCBA\Metricas_Web_Mensual` — métricas del sitio (GA4, PRTG, MySQL)
> - `C:\GCBA\Metricas_Boti_Mensual` — métricas del bot (Athena)
> - `C:\GCBA\Tablero-de-mensajes-y-disparadores` — insumo histórico (ya
>   reemplazado por `Temas_Consultados/` en Boti)

---

## Índice

1. [Diagrama del proceso mensual](#1-diagrama-del-proceso-mensual)
2. [Pre-requisitos únicos (setup inicial)](#2-pre-requisitos-únicos-setup-inicial)
3. [Pre-requisitos mensuales (checklist previo)](#3-pre-requisitos-mensuales-checklist-previo)
4. [Ejecución paso a paso](#4-ejecución-paso-a-paso)
5. [Outputs y qué llega a dónde](#5-outputs-y-qué-llega-a-dónde)
6. [Distribución al equipo](#6-distribución-al-equipo)
7. [Cierre: commit y push](#7-cierre-commit-y-push)
8. [Módulos y métricas por repo](#8-módulos-y-métricas-por-repo)
9. [Troubleshooting por módulo](#9-troubleshooting-por-módulo)
10. [Anexo: mapeo de celdas del consolidado](#10-anexo-mapeo-de-celdas-del-consolidado)

---

## 1. Diagrama del proceso mensual

```
┌─────────────────────────────────────────────────────────────────────┐
│                     PRE-REQUISITOS MENSUALES                        │
│  □ VPN GCBA activa           □ Login AWS (PIBADataScientist)        │
│  □ PDFs PRTG descargados     □ config_fechas.txt en ambos repos     │
│  □ Screenshot Power BI mes   □ Tokens Google GA4 vigentes           │
└─────────────────────────┬───────────────────────────────────────────┘
                          ▼
   ┌──────────────────────────────────────────────────────────────┐
   │  PASO A: cd Metricas_Web_Mensual  &&  python run_all.py     │
   │  Corre 7 modulos GA4/PRTG/MySQL + unificador                │
   │  → ba_metricas_consolidado_<mes-año>.xlsx  (raiz)           │
   └──────────────────────────┬───────────────────────────────────┘
                              ▼
   ┌──────────────────────────────────────────────────────────────┐
   │  PASO B: cd Metricas_Boti_Mensual  &&  python run_all.py    │
   │  Corre 12 modulos Athena (No_Entendidos aparte, manual)     │
   │  Luego: python consolidar_excel.py                          │
   │  → Boti_Consolidado_<mes>_<año>.xlsx  (raiz)                │
   └──────────────────────────┬───────────────────────────────────┘
                              ▼
   ┌──────────────────────────────────────────────────────────────┐
   │  PASO C: python calcular_efectividad_web_boti.py            │
   │  Cruza datos de AMBOS repos (Feedback Boti + Satisfaccion   │
   │  Web) y calcula la efectividad combinada.                   │
   │  → efectividad_web_boti_<mes>_<año>.xlsx                    │
   │    (subcarpeta efectividad_web_boti/ en Boti)               │
   └──────────────────────────┬───────────────────────────────────┘
                              ▼
   ┌──────────────────────────────────────────────────────────────┐
   │  PASO D: Distribucion + cierre                              │
   │  - Enviar 3 Excel al equipo (Web / Boti / Efectividad WB)   │
   │  - Commit + push de AMBOS repos                             │
   └──────────────────────────────────────────────────────────────┘
```

---

## 2. Pre-requisitos únicos (setup inicial)

Estos se hacen **una sola vez** cuando se estrena la máquina.

### 2.1. Software base

Python 3.11+ instalado con las dependencias:

```powershell
pip install pandas openpyxl `
            google-analytics-data google-auth google-auth-oauthlib pytz `
            sqlalchemy pymysql `
            pdfplumber `
            boto3 awswrangler `
            nltk `
            playwright pytesseract Pillow
python -m playwright install chromium
python -m nltk.downloader stopwords
```

### 2.2. AWS CLI + aws-azure-login

Necesario para autenticarse contra Athena (rol **PIBADataScientist**).

- Instalar AWS CLI v2.
- Instalar `aws-azure-login`.
- Configurar profile default con el rol PIBADataScientist.
- Verificar guía en `Metricas_Boti_Mensual/CLI_login_AWS-azure_WINDOWS_v2.pdf`.

### 2.3. Tesseract OCR (Windows)

Necesario para `DescubrirBA-Agente` (OCR del Power BI).

- Instalar desde https://github.com/UB-Mannheim/tesseract/wiki
- Ruta por defecto: `C:\Program Files\Tesseract-OCR\`
- **Marcar "Spanish"** en "Additional language data" durante la instalación.
- Verificar: `& "C:\Program Files\Tesseract-OCR\tesseract.exe" --version`

### 2.4. Credenciales

- **Google Analytics 4**: `Metricas_Web_Mensual/client_secrets.json` (OAuth 2.0).
  El `token.json` se genera automáticamente al primer login.
- **MySQL GCBA (Satisfacción)**: `Metricas_Web_Mensual/Satisfaccion/src/config.txt`
  con HOST, USER, PASSWORD, PORT.
- **VPN GCBA (FortiClient)**: cliente instalado y credenciales de acceso.
- **Portal PRTG**: usuario/clave para descargar PDFs mensuales.

---

## 3. Pre-requisitos mensuales (checklist previo)

**Hacer esto ANTES de arrancar la ejecución** cada mes.

### 3.1. Ajustar `config_fechas.txt` en AMBOS repos

Los 2 archivos apuntan al MISMO período (mismo mes y año).

```
# En AMBOS: C:\GCBA\Metricas_Web_Mensual\config_fechas.txt
# Y:        C:\GCBA\Metricas_Boti_Mensual\config_fechas.txt
MES=5
AÑO=2026
```

### 3.2. Conectar VPN GCBA (FortiClient)

Requerido para que Satisfacción Web pueda consultar MySQL.
Sin VPN, ese módulo falla al conectarse.

### 3.3. Login AWS (rol PIBADataScientist)

Requerido para todos los módulos que consultan Athena (casi todos los de Boti).

```powershell
aws-azure-login --profile default --mode=gui
```

Cuando pida el rol, elegir **PIBADataScientist**.

### 3.4. Descargar PDFs PRTG del mes

Requerido por `Caidas_Server`.

- Ingresar al portal PRTG Network Monitor.
- Descargar el reporte de uptime del mes objetivo.
- Copiar los PDFs a `C:\GCBA\Metricas_Web_Mensual\Caidas_Server\data\`.

### 3.5. Ejecutar `No_Entendidos` (manual, requiere interacción)

El módulo `No_Entendidos` de Boti tiene un `athena_connector.py` que puede
pedir re-validar auth. Se ejecuta a mano ANTES del `run_all.py`:

```powershell
cd C:\GCBA\Metricas_Boti_Mensual\No_Entendidos
python athena_connector.py
python No_Entendidos.py
cd ..
```

`run_all.py` va a **saltear** No_Entendidos y va a marcarlo como "ya ejecutado
manualmente" en el resumen final. Si no lo corriste antes, se salta y queda
sin datos ese módulo.

### 3.6. Otros insumos mensuales (dependen del mes)

- **`Contenidos_Bot`**: exportar 2 archivos TSV desde Botmaker (uno anterior,
  uno actual del mes) y copiarlos a `Contenidos_Bot/`. Sin los 2 TSV, el
  módulo falla.
- **`Contenidos_mas_disparados`**: descarga automática desde Athena (no
  requiere TSV manual desde que se hizo el cambio a `trasco_athena_*.csv`).
- **`DescubrirBA-Agente`**: ⚠️ **la automatización Playwright no es confiable**
  (ver 9.6). Contar con hacer el paso manual: el script te pide un screenshot
  del dashboard con el tooltip visible y te dice qué nombre ponerle y dónde
  guardarlo. **Verificar el valor contra el dashboard** antes de cerrar el mes.

---

## 4. Ejecución paso a paso

### Paso A — Métricas Web

```powershell
cd C:\GCBA\Metricas_Web_Mensual
python run_all.py
```

Corre en secuencia 7 módulos + `ba_metrics_unifier.py`:

1. Métricas Principales (GA4) → `Principales/ba_metricas_<mes-año>.xlsx`
2. Satisfacción Web (MySQL) → `Satisfaccion/ba_metricas_<mes-año>.xlsx`
3. Caídas del Servidor (PRTG) → `Caidas_Server/ba_metricas_<mes-año>.xlsx`
4. Ranking de Páginas (GA4) → `Ranking_paginas/ba_metricas_<mes-año>.xlsx`
5. Descubrir BA - LINDA (GA4) → `DescubrirBA-Linda/ba_metricas_<mes-año>.xlsx`
6. BA Productiva (GA4) → `BAProductiva/ba_metricas_<mes-año>.xlsx`
7. Descubrir BA - Agente (OCR Power BI) → `DescubrirBA-Agente/ba_metricas_<mes-año>.xlsx`

Al final unifica en:
**`ba_metricas_consolidado_<mes-año>.xlsx`** (raíz del repo Web).

Duración estimada: **15–25 min**.

### Paso B — Métricas Boti

```powershell
cd C:\GCBA\Metricas_Boti_Mensual
python run_all.py
```

Corre en secuencia 12 módulos (No_Entendidos ya se hizo manual en el paso 3.5):

1. Usuarios y Conversaciones → `Metricas_Boti_Conversaciones_Usuarios/output/`
2. Pushes Enviadas → `Pushes_Enviadas/output/`
3. Sesiones Abiertas por Pushes → `Sesiones_Abiertas_Pushes/output/`
4. Sesiones Alcanzadas por Pushes → `Sesiones_alcanzadas_pushes/output/`
5. BAX Sesiones → `BAX-sesiones/output/`
6. Contenidos del Bot → `Contenidos_Bot/output/`
7. Contenidos mas disparados → `Contenidos_mas_disparados/output/`
8. Temas Consultados → `Temas_Consultados/output/`
9. Feedback - Efectividad → `Feedback_Efectividad/output/`
10. Feedback - CES → `Feedback_CES/output/`
11. Feedback - CSAT → `Feedback_CSAT/output/`
12. Disponibilidad WhatsApp → `Metricas_Boti_Disponibilidad/output/`

Después del `run_all.py`, correr manualmente el consolidador:

```powershell
python consolidar_excel.py
```

Output: **`Boti_Consolidado_<mes>_<año>.xlsx`** (raíz del repo Boti).

Duración estimada: **20–40 min** (la query de `Contenidos_mas_disparados`
es la más pesada, escanea toda la vista).

### Paso C — Efectividad cruzada Web + Boti

Este script vive en la raíz de Boti pero lee datos de **ambos** repos.

```powershell
cd C:\GCBA\Metricas_Boti_Mensual
python calcular_efectividad_web_boti.py
```

Lee:
- `Metricas_Boti_Mensual/Feedback_Efectividad/output/feedback_efectividad_<mes>_<año>_efectividad.xlsx`
- `Metricas_Web_Mensual/Satisfaccion/data/conteo_completo_<mes>_<año>.xlsx`

Genera:
**`efectividad_web_boti_<mes>_<año>.xlsx`** en `efectividad_web_boti/` (subcarpeta
en la raíz de Boti).

---

## 5. Outputs y qué llega a dónde

Al finalizar los 3 pasos, tenés **3 archivos consolidados** para el equipo:

| Archivo | Ubicación | Fuente |
|---|---|---|
| `ba_metricas_consolidado_<mes-año>.xlsx` | Raíz de `Metricas_Web_Mensual/` | Paso A |
| `Boti_Consolidado_<mes>_<año>.xlsx` | Raíz de `Metricas_Boti_Mensual/` | Paso B |
| `efectividad_web_boti_<mes>_<año>.xlsx` | `Metricas_Boti_Mensual/efectividad_web_boti/` | Paso C |

### 5.1. Outputs que NO van al consolidado (pero se entregan igual)

Estos módulos generan su propio Excel y **no escriben en ningún consolidado**.
Hay que buscarlos a mano en su carpeta cuando el equipo los pide:

| Archivo | Ubicación | Para qué sirve |
|---|---|---|
| `ranking_temas_consultados_<mes>_<año>.txt` | `Metricas_Boti_Mensual/Temas_Consultados/output/` | Texto del ranking que se **pega en la celda "Temas más consultados"** del tablero |
| `ranking_temas_consultados_<mes>_<año>.xlsx` | `Metricas_Boti_Mensual/Temas_Consultados/output/` | El mismo ranking en formato template |
| `reporte_mensajes_<mes>_<año>.xlsx` | `Metricas_Boti_Mensual/Temas_Consultados/output/` | Comparativo mes vs mes anterior + Top 100 "Otros" |
| `top_variaciones_<mes>_<año>.xlsx` | `Metricas_Boti_Mensual/Temas_Consultados/output/` | Top 3 subidas/bajadas por categoría |
| `bax_sesiones_<mes>_<año>.xlsx` | `Metricas_Boti_Mensual/BAX-sesiones/output/` | Sesiones del canal webchat BAX - App (total + serie diaria) |
| `ba_metricas_<mes-año>.xlsx` | `Metricas_Web_Mensual/DescubrirBA-Linda/` | Métricas del sitio LINDA |
| `ba_metricas_<mes-año>.xlsx` | `Metricas_Web_Mensual/BAProductiva/` | Métricas de `/inicio/ba-productiva` |
| `ba_metricas_<mes-año>.xlsx` | `Metricas_Web_Mensual/DescubrirBA-Agente/` | Total Conversations del agente `descubrir` |

Además, cada módulo deja sus **archivos parciales** (CSV, Excel detallado,
HTML) en su propia carpeta `output/` o similar. Sirven para auditoría.

---

## 6. Distribución al equipo

Los 3 archivos consolidados se envían típicamente por mail o se suben al
canal de comunicación acordado. Recomendable:

- Adjuntar los 3 xlsx.
- En el cuerpo del mail: nombrar el período, resumen ejecutivo de 3–5
  bullets con los números clave (Total Visitas, Total Conversations, Tasa
  de Efectividad combinada, etc.).

---

## 7. Cierre: commit y push

**Ambos repos** deben quedar versionados con los outputs del mes:

```powershell
# Repo Web
cd C:\GCBA\Metricas_Web_Mensual
git add -A
git commit -m "Metricas <mes> <año>: outputs mensuales"
git push origin main

# Repo Boti
cd C:\GCBA\Metricas_Boti_Mensual
git add -A
git commit -m "Metricas <mes> <año>: outputs mensuales"
git push origin main
```

---

## 8. Módulos y métricas por repo

### Repo WEB — `Metricas_Web_Mensual/`

| # | Módulo | Fuente | Alimenta consolidado | Métricas |
|---|---|---|---|---|
| 1 | Principales | GA4 API | ✅ C3, C5, C6, C7, C8 | Visitas, Usuarios únicos, Usuarios activos, Sesiones, Duración |
| 2 | Satisfacción Web | MySQL (VPN) | ✅ C4, C11, C12 | Tasa Efectividad, Satisfacción HOME, Satisfacción webs |
| 3 | Caídas Server | PDFs PRTG | ✅ C9, C10 | Uptime %, Downtime Home |
| 4 | Ranking Páginas | GA4 API | ✅ C13 | Top 10 sitios más visitados |
| 5 | DescubrirBA-LINDA | GA4 API (hostName) | ❌ Excel propio | Visitas del sitio `linda.buenosaires.gob.ar` |
| 6 | BAProductiva | GA4 API (pagePath) | ❌ Excel propio | Métricas de `/inicio/ba-productiva` |
| 7 | DescubrirBA-Agente | Power BI + OCR | ❌ Excel propio | Total Conversations del agente `descubrir` |

### Repo BOTI — `Metricas_Boti_Mensual/`

| # | Módulo | Fuente | Métrica |
|---|---|---|---|
| 1 | Usuarios y Conversaciones | Athena | Q Conversaciones + Q Usuarios únicos (D2, D3) |
| 2 | Pushes Enviadas | Athena | Q Mensajes push (D6) |
| 3 | Sesiones Abiertas por Pushes | Athena | Q Sesiones abiertas por push (D4) |
| 4 | Sesiones Alcanzadas por Pushes | Athena | Q Sesiones alcanzadas por push (D5) |
| 5 | BAX Sesiones | Athena | Q Sesiones canal webchat BAX - App |
| 6 | Contenidos del Bot | 2 TSV Botmaker | Contenidos prendidos vs usuario (D7, D8) |
| 7 | Contenidos mas disparados | Athena (vista) | Top 10 contenidos consultados (D11) |
| 8 | Temas Consultados | Athena (msgs) | Ranking de temas para tablero |
| 9 | No Entendimiento **(MANUAL)** | Athena | Tasa de no entendimiento (D13) |
| 10 | Feedback Efectividad | Athena | Tasa de Efectividad (D14) |
| 11 | Feedback CES | Athena | Customer Effort Score (D15) |
| 12 | Feedback CSAT | Athena | Customer Satisfaction (D16) |
| 13 | Disponibilidad WhatsApp | ? | Uptime servidor WhatsApp (D17) |

Cruce entre repos:
- **Efectividad Web + Boti** (script en raíz de Boti): combina `Feedback_Efectividad`
  (Boti) con `conteo_completo` (Satisfacción Web).

---

## 9. Troubleshooting por módulo

### 9.1. Google Analytics 4 (Principales, Ranking, DescubrirBA-Linda, BAProductiva)

- **Error `invalid_grant` o `token expired`** → Borrar `token.json` de la raíz
  de `Metricas_Web_Mensual/`. Al re-correr, abre el navegador para re-autenticar.
- **`RefreshError: The credentials do not contain the necessary fields`** → Idem.
- **`client_secrets.json not found`** → Verificar que esté en la raíz del repo
  Web. Sin este archivo no hay auth GA4.

### 9.2. Satisfacción (MySQL)

- **`OperationalError: Can't connect to MySQL server`** → VPN GCBA no está
  conectada. Verificar FortiClient.
- **`Access denied for user`** → Revisar `Satisfaccion/src/config.txt` (HOST,
  USER, PASSWORD).

### 9.3. Caídas Server (PRTG)

- **`No se encontraron PDFs en Caidas_Server/data/`** → No descargaste los PDFs
  del mes desde el portal PRTG. Descargar y copiar antes de correr.
- **`UnboundLocalError: filtered_output_path`** → Bug conocido, ya fue arreglado.
  Si aparece, actualizar `metricas_web_mensual_prtg_extractor.py`.

### 9.4. Athena (todos los módulos Boti)

- **`ExpiredToken`** → Sesión AWS expiró. Re-loguear con
  `aws-azure-login --profile default --mode=gui` y seleccionar `PIBADataScientist`.
- **`[ADVERTENCIA] No estas usando el rol correcto`** → Estás con otro rol
  (ej. PIBAConsumeBoti antiguo). Re-loguear con el rol correcto.
- **Query cuelga por varios minutos** → Es normal para
  `Contenidos_mas_disparados` (escanea toda la vista `boti_vw_buscador_rulename`).
  El script ahora tiene logging verbose con timestamps. Si tarda >10 min sin
  imprimir nada, hay problema real.

### 9.5. Contenidos del Bot

- **`Falta 1 TSV`** → Faltan los 2 TSV exportados de Botmaker. Exportar del
  portal Botmaker y copiar a `Contenidos_Bot/`.

### 9.6. DescubrirBA-Agente (Power BI + OCR)

> **ESTADO AL 2026-09-11: la automatización Playwright NO es confiable.**
> Contar con usar el **fallback manual** hasta nuevo aviso. Ver más abajo.

**El problema de fondo.** El valor sale de hacer hover sobre la barra
`descubrir` del visual "Total Conversations por Agente". Power BI ordena las
barras **por valor descendente**, así que la posición de `descubrir` cambia
mes a mes. En julio 2026 `descubrir` cayó al 4° puesto y el script —que
hardcodeaba "hover en la primera barra"— leyó `out_of_scope` (**16.023**) en
lugar de `descubrir` (**10.210**). El Excel de julio salió mal por eso.

**Qué se intentó (y no funcionó):**

1. **Filtrar el slicer `Agente = descubrir`** para que quede una sola barra en
   posición fija. El click en el slicer funciona, pero el hover posterior cae
   en el lugar equivocado porque el layout se reacomoda.
2. **Reemplazar las coordenadas fijas por búsqueda OCR** de los labels
   (`Mes`, `Agente`, `descubrir`) con `pytesseract.image_to_data()`. Tampoco
   cerró: en la última corrida devolvió **6** en vez de 10.210.

**Por qué cuesta tanto.** El dashboard es un canvas dentro de un iframe
sandboxeado — no hay DOM al que agarrarse, todo es pixel-hunting a ciegas.
Además el navegador headless de Playwright tiene distinto DPR que el Chrome
que se usa para calibrar visualmente, así que las coordenadas que se validan
a ojo no se trasladan tal cual.

**Qué hacer mientras tanto:**

- Dejar que el script caiga al **fallback manual** (paso 2/2). Te dice la URL,
  qué filtro poner, dónde hacer hover, el nombre exacto del PNG y la carpeta
  donde guardarlo. Apretás ENTER y el OCR del screenshot manual sí funciona bien.
- **Verificar siempre el valor** contra el dashboard antes de dar el mes por
  cerrado. Es el único módulo del proceso donde el número puede salir mal sin
  que nada falle a la vista.

**Próximo intento pendiente:** verificar si los slicers (`Mes`, `Agente`) son
elementos del DOM y no canvas. Si lo son, se resuelve con
`page.get_by_text('Julio').click()` — sin OCR ni coordenadas. Falta confirmarlo.

**Otros errores de este módulo:**

- **Tesseract not found** → Ver sección 2.3 (instalación única).
- **`Failed loading language 'spa'`** → Falta el pack Spanish de Tesseract.
  Re-instalar marcando "Spanish" en "Additional language data".

### 9.7. Errores generales de git

- **`Unable to create '.git/index.lock': File exists`** → Cerrar procesos que
  puedan tener el repo abierto (VS Code, Excel de algún output).
  Luego: `Remove-Item .git\index.lock -Force` (PowerShell) o
  `del .git\index.lock` (CMD).

### 9.8. GitHub rechaza el push (archivo >100 MB)

- **`File X is Y MB; this exceeds GitHub's file size limit of 100.00 MB`** →
  Algún output se pasó del límite. Ejemplos conocidos:
  - `Temas_Consultados/output/temas_consultados_<mes>_<año>.csv` (~500 MB)
    → Ya está en `.gitignore` (`Temas_Consultados/output/temas_consultados_*.csv`).
  - `No_Entendidos/temp/*.csv` (varios GB) → Ya está en `.gitignore`.

  Si aparece otro archivo grande, agregar patrón al `.gitignore` y hacer
  `git rm --cached <archivo>` para removerlo del tracking sin borrarlo del disco.

---

## 10. Anexo: mapeo de celdas del consolidado

### Repo WEB → `ba_metricas_consolidado_<mes-año>.xlsx`

Estructura del template Excel (columna B = Indicador, columna C = Valor):

| Fila | Indicador | Poblado por |
|---:|---|---|
| C3 | Visitas | Principales |
| C4 | Tasa de Efectividad | Satisfacción |
| C5 | Usuarios únicos | Principales |
| C6 | Usuarios que inician sesión | Principales |
| C7 | Sesiones | Principales |
| C8 | Tiempo de permanencia | Principales |
| C9 | Uptime/Downtime (% General) | Caidas_Server |
| C10 | Uptime/Downtime (Home hh:mm:ss) | Caidas_Server |
| C11 | Indicador de satisfacción (Home) | Satisfacción |
| C12 | Indicador de satisfacción (Resto webs) | Satisfacción |
| C13 | Sitios más visitados | Ranking |

### Repo BOTI → `Boti_Consolidado_<mes>_<año>.xlsx`

| Fila | Indicador | Poblado por |
|---:|---|---|
| D2 | Q Conversaciones | Usuarios y Conversaciones |
| D3 | Q Usuarios únicos | Usuarios y Conversaciones |
| D4 | Q Sesiones abiertas por Push | Sesiones Abiertas por Pushes |
| D5 | Q Sesiones alcanzadas por Push | Sesiones Alcanzadas por Pushes |
| D6 | Q Mensajes Pushes | Pushes Enviadas |
| D7 | Q Contenidos activos | Contenidos del Bot |
| D8 | Q Contenidos vs usuario | Contenidos del Bot |
| D11 | Top 10 Contenidos consultados | Contenidos mas disparados |
| D13 | Q No entendimiento | No_Entendidos (manual) |
| D14 | Tasa de Efectividad | Feedback Efectividad |
| D15 | CES | Feedback CES |
| D16 | CSAT | Feedback CSAT |
| D17 | Uptime servidor | Disponibilidad WhatsApp |

---

## Última actualización

**2026-09-11** (generado originalmente el 2026-07-05).

Cambios de esta revisión:

- Nueva sección **5.1** con los outputs que no van al consolidado y hay que
  buscar a mano (ranking de temas para el tablero, BAX sesiones, LINDA,
  BAProductiva, DescubrirBA-Agente).
- **9.6 reescrita**: documentado que la automatización de DescubrirBA-Agente
  no es confiable, con el detalle del bug de julio 2026 y qué hacer mientras
  tanto.
- **3.6 corregida** en línea con lo anterior.

Cuando cambien módulos, se agreguen fuentes de datos o cambie el proceso,
actualizar este archivo en **ambos repos** para mantenerlos sincronizados.

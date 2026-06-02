# 📊 Sistema de Métricas Boti - No Entendimiento

Sistema automatizado para cálculo de métricas de No Entendimiento del chatbot Boti de la Ciudad de Buenos Aires.

---

## 📋 Tabla de Contenidos

- [Descripción General](#-descripción-general)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso - Guía Rápida](#-uso---guía-rápida)
- [Archivos Generados](#-archivos-generados)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Métricas Calculadas](#-métricas-calculadas)
- [Documentación Técnica](#-documentación-técnica)
- [Solución de Problemas](#-solución-de-problemas)
- [Changelog](#-changelog)

---

## 🎯 Descripción General

Este sistema procesa datos del chatbot Boti para calcular métricas de efectividad, específicamente la métrica **D13 (No Entendimiento)**.

### Componentes del Sistema

#### 1. `athena_connector.py`
**Función:** Descarga datos desde AWS Athena

**Características:**
- Ejecuta 3 queries SQL automáticamente (Mensajes, Clicks, Botones)
- Manejo automático de expiración de tokens AWS
- Reintentos automáticos en caso de error
- Muestra progreso en tiempo real

**Duración:** 10-20 minutos

#### 2. `No_Entendidos.py`
**Función:** Calcula métricas de No Entendimiento

**Características:**
- Procesamiento optimizado (PASO 6: 60 min → 2 seg)
- Genera JSON + 2 archivos Excel
- Filtrado automático de testers
- Dashboard con 17 indicadores

**Duración:** 20-30 minutos

### Flujo de Trabajo

```
config_fechas.txt  →  athena_connector.py  →  No_Entendidos.py
     (MES/AÑO)            (descarga CSVs)        (calcula métricas)
                                                   ↓
                                          JSON + 2 Excel en output/
```

---

## 🔧 Requisitos

### Software

```
Python 3.8+
AWS CLI
aws-azure-login
```

### Librerías Python

```bash
pip install boto3 awswrangler pandas numpy openpyxl
```

O con archivo requirements.txt:

```bash
pip install -r requirements.txt
```

**Contenido de requirements.txt:**
```
boto3>=1.26.0
awswrangler>=2.19.0
pandas>=1.5.0
numpy>=1.23.0
openpyxl>=3.0.0
```

### Accesos AWS

- **Workgroup:** Production-caba-piba-athena-boti-group
- **Database:** caba-piba-consume-zone-db
- **Rol:** PIBADataScientist

---

## ⚙️ Instalación

### 1. Clonar o Descargar el Proyecto

```bash
git clone <url-del-repo>
cd Metricas_Boti_Mensual
```

O descargar y descomprimir en:
```
C:\GCBA\Metricas_Boti_Mensual\
```

### 2. Instalar Dependencias

```bash
cd No_Entendidos
pip install boto3 awswrangler pandas numpy openpyxl
```

### 3. Configurar AWS Azure Login

**Primera vez (solo una vez):**

```bash
aws-azure-login --configure --profile default
```

Completar con:
- **Azure Tenant ID:** (proporcionado por IT)
- **Azure App ID URI:** (proporcionado por IT)
- **Default Role ARN:** PIBADataScientist

### 4. Verificar Estructura de Directorios

```
Metricas_Boti_Mensual/                 ← Raíz del repo
├── config_fechas.txt                  ← Debe existir aquí
└── No_Entendidos/                     ← Tu ubicación de trabajo
    ├── athena_connector.py
    ├── No_Entendidos.py
    └── queries/
        ├── Mensajes.sql
        ├── Clicks.sql
        └── Botones.sql
```

**Nota:** Las carpetas `temp/` y `output/` se crean automáticamente.

---

## 📝 Configuración

### Archivo: `config_fechas.txt` (Raíz del Repositorio)

Este archivo está en **la raíz del repositorio** (`Metricas_Boti_Mensual/config_fechas.txt`) y es **compartido por todos los proyectos de métricas**.

**Ubicación:**
```
Metricas_Boti_Mensual/
└── config_fechas.txt              ← ESTE ARCHIVO
```

**Por qué está en la raíz:**
- ✅ Todos los proyectos de métricas lo comparten
- ✅ Configuras el período una sola vez
- ✅ Garantiza consistencia entre reportes

### Opciones de Configuración

#### Opción 1: Mes Completo (Recomendado)

Editar `Metricas_Boti_Mensual/config_fechas.txt`:

```
MES=12
AÑO=2025
```

Esto procesará **todo el mes** de diciembre 2025.

#### Opción 2: Rango Personalizado

```
FECHA_INICIO=2025-12-01
FECHA_FIN=2025-12-15
```

Esto procesará **solo las primeras 2 semanas** de diciembre.

**Nota:** Si especificas FECHA_INICIO y FECHA_FIN, se ignorarán MES y AÑO.

### Cómo Editar el Archivo

**Desde la raíz del repo:**
```bash
cd C:\GCBA\Metricas_Boti_Mensual
notepad config_fechas.txt
```

**Desde No_Entendidos/:**
```bash
cd C:\GCBA\Metricas_Boti_Mensual\No_Entendidos
notepad ..\config_fechas.txt
```

---

## 🚀 Uso - Guía Rápida

### Ejecución Mensual (3 Pasos)

#### PASO 1: Configurar Mes

Editar `config_fechas.txt` en **la raíz del repositorio**:

```bash
# Opción A: Desde la raíz
cd C:\GCBA\Metricas_Boti_Mensual
notepad config_fechas.txt

# Opción B: Desde No_Entendidos/
cd C:\GCBA\Metricas_Boti_Mensual\No_Entendidos
notepad ..\config_fechas.txt
```

Contenido:
```
MES=12
AÑO=2025
```

#### PASO 2: Login AWS

```bash
aws-azure-login --profile default --mode=gui
```

Esto abre el navegador para autenticación. Completar el login.

#### PASO 3A: Descargar Datos

```bash
cd C:\GCBA\Metricas_Boti_Mensual\No_Entendidos
python athena_connector.py
```

**Resultado esperado:**
```
✅ TODAS LAS QUERIES EJECUTADAS EXITOSAMENTE
📂 Archivos generados:
   ├─ temp/mensajes_temp.csv      (13 GB)
   ├─ temp/clicks_temp.csv         (9 GB)
   └─ temp/botones_temp.csv        (3 GB)
```

**Duración:** 10-20 minutos

#### PASO 3B: Calcular Métricas

```bash
python No_Entendidos.py
```

**Resultado esperado:**
```
📦 ARCHIVOS GENERADOS:
  [1] JSON:               metricas_boti_diciembre_2025.json
  [2] Excel Detallado:    output/no_entendimiento_detalle_diciembre_2025.xlsx
  [3] Dashboard Master:   output/no_entendimiento_diciembre_2025.xlsx

  🎯 D13 (No Entendimiento): 11.70%
```

**Duración:** 20-30 minutos

---

## 📁 Archivos Generados

### 1. JSON (Raíz del proyecto)

**Archivo:** `metricas_boti_diciembre_2025.json`

**Contenido:**
```json
{
  "periodo": "diciembre 2025",
  "modo": "mes",
  "fecha_inicio": "2025-12-01 00:00:00",
  "fecha_fin": "2026-01-01 00:00:00",
  "metricas": {
    "one": 0.651,
    "click": 0.130,
    "texto": 0.048,
    "abandonos": 0.054,
    "nada": 0.055,
    "ne": 0.062,
    "letra": 0.001
  },
  "timestamp": "2026-01-13T15:30:00"
}
```

**Uso:** Datos crudos para análisis programático, integración con otros sistemas.

---

### 2. Excel Detallado (Carpeta output/)

**Archivo:** `output/no_entendimiento_detalle_diciembre_2025.xlsx`

**Estructura:**

```
╔════════════════════════════════════════════════╗
║  NO ENTENDIMIENTO - Análisis Detallado        ║
║  Período: diciembre 2025                      ║
╚════════════════════════════════════════════════╝

CATEGORÍAS
OneShots:     65.10%
Clicks:       13.00%
Texto:         4.80%
Abandonos:     5.40%
Nada:          5.50%
NE:            6.20%
Letra:         0.10%
─────────────────────
TOTAL:       100.00%

MÉTRICAS
Resolución (One+Click+Texto):     82.90%
Problemas (Abandonos+Letra):       5.50%

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ D13 - NO ENTENDIMIENTO:  11.70% ┃  ← Verde
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

**Uso:** Reporte mensual detallado, análisis interno, presentaciones.

---

### 3. Dashboard Master (Carpeta output/)

**Archivo:** `output/no_entendimiento_diciembre_2025.xlsx`

**Estructura:** Dashboard con 17 indicadores

| Fila | Indicador | Descripción | Valor |
|------|-----------|-------------|-------|
| 1 | **Headers** | | **dic-25** |
| 2 | Conversaciones | Q Conversaciones | (vacío) |
| 3 | Usuarios | Q Usuarios únicos | (vacío) |
| ... | ... | ... | ... |
| **13** | **No entendimiento** | **Performance motor de búsqueda del nuevo modelo de IA** | **11.70%** |
| 14 | Tasa de Efectividad | Mide el % de usuarios que lograron su objetivo | (vacío) |
| 15 | CES | Mide la facilidad de interacción | (vacío) |
| 16 | Satisfacción (CSAT) | Escala de 1 a 5 | (vacío) |
| 17 | Uptime servidor | Disponibilidad del servidor | (vacío) |

**Uso:** Dashboard consolidado, integración con otros scripts de métricas.

**Nota:** Este script solo llena la fila 13 (No Entendimiento). Las otras filas se llenan con otros scripts del sistema.

### Integración con Otros Proyectos

El Dashboard Master está diseñado para consolidar métricas de **múltiples proyectos**:

| Proyecto | Fila(s) que Llena |
|----------|-------------------|
| **No_Entendidos** | 13 - No entendimiento |
| Metricas_Boti_Conversaciones_Usuarios | 2, 3 - Conversaciones, Usuarios |
| Pushes_Enviadas | 6 - Mensajes Pushes Enviados |
| Sesiones_Abiertas_Pushes | 4 - Sesiones abiertas por Pushes |
| Sesiones_alcanzadas_pushes | 5 - Sesiones Alcanzadas por Pushes |
| Feedback_Efectividad | 14 - Tasa de Efectividad |
| Feedback_CES | 15 - CES (Customer Effort Score) |
| Feedback_CSAT | 16 - Satisfacción (CSAT) |
| Metricas_Boti_Disponibilidad | 17 - Uptime servidor |

**Workflow Completo:**
```bash
# 1. Configurar mes en la raíz (UNA VEZ)
cd C:\GCBA\Metricas_Boti_Mensual
notepad config_fechas.txt

# 2. Ejecutar cada proyecto (cada uno actualiza su fila)
cd No_Entendidos
python No_Entendidos.py              # → D13

cd ..\Feedback_CSAT
python feedback_csat.py               # → D16

cd ..\Feedback_CES
python feedback_ces.py                # → D15

# etc.

# Resultado: Dashboard con todas las métricas
```

**Importante:** Cada script:
- ✅ Lee el Dashboard existente (si existe)
- ✅ Actualiza **solo su fila**
- ✅ Preserva las demás filas sin tocarlas

---

## 📂 Estructura del Proyecto

### Repositorio Completo

```
Metricas_Boti_Mensual/                 ← Repositorio raíz
│
├── config_fechas.txt                  ← Configuración compartida (EDITAR ESTE)
│
├── No_Entendidos/                     ← Este proyecto
│   ├── athena_connector.py            ← Programa 1: Descarga de datos
│   ├── No_Entendidos.py               ← Programa 2: Cálculo de métricas
│   │
│   ├── queries/                       ← Queries SQL para Athena
│   │   ├── Mensajes.sql
│   │   ├── Clicks.sql
│   │   └── Botones.sql
│   │
│   ├── temp/                          ← Archivos temporales (auto-creado)
│   │   ├── mensajes_temp.csv          (13 GB - se puede borrar después)
│   │   ├── clicks_temp.csv            (9 GB - se puede borrar después)
│   │   └── botones_temp.csv           (3 GB - se puede borrar después)
│   │
│   ├── output/                        ← Archivos finales (auto-creado)
│   │   ├── no_entendimiento_detalle_diciembre_2025.xlsx
│   │   └── no_entendimiento_diciembre_2025.xlsx
│   │
│   └── metricas_boti_diciembre_2025.json  ← JSON con datos crudos
│
├── Feedback_CES/                      ← Otros proyectos de métricas
├── Feedback_CSAT/
├── Feedback_Efectividad/
├── Metricas_Boti_Conversaciones_Usuarios/
├── Metricas_Boti_Disponibilidad/
├── Pushes_Enviadas/
├── Sesiones_Abiertas_Pushes/
└── Sesiones_alcanzadas_pushes/
```

### Archivos Opcionales (No_Entendidos/)

Si existen, el script los usará automáticamente:

```
No_Entendidos/
├── testers.csv                        ← Lista de usuarios de prueba (opcional)
└── Actualizacion_Lista_Blanca.csv     ← Intenciones válidas (opcional)
```

### Nota Importante

**Todos los proyectos** comparten el mismo `config_fechas.txt` en la raíz del repositorio. Esto permite:
- ✅ Configurar el período **una sola vez**
- ✅ Ejecutar múltiples scripts de métricas para el mismo mes
- ✅ Mantener consistencia entre todos los reportes

---

## 📊 Métricas Calculadas

### Métricas Principales

| Métrica | Descripción | Típico |
|---------|-------------|--------|
| **OneShots** | Consultas resueltas directamente con un botón | ~65% |
| **Clicks** | Consultas resueltas con clicks en búsqueda | ~13% |
| **Texto** | Consultas resueltas escribiendo texto | ~5% |
| **Abandonos** | Sesiones abandonadas sin resolver | ~5% |
| **Nada** | Sin respuesta válida del sistema | ~6% |
| **NE (No Entendidos)** | Score ≤ 5.36 (no entendió la consulta) | ~6% |
| **Letra** | Letra inexistente en WhatsApp | ~0.1% |

### Métricas Agregadas

```
Resolución = OneShots + Clicks + Texto
           ≈ 82-85%

Problemas = Abandonos + Letra
          ≈ 5-6%

D13 = Nada + NE  ← MÉTRICA PRINCIPAL
    ≈ 11-12%
```

### Métrica D13 - No Entendimiento

**Fórmula:**
```
D13 = % Nada + % NE
```

**Interpretación:**

| D13 | Significado |
|-----|-------------|
| < 10% | ✅ Excelente - El chatbot entiende muy bien |
| 10-15% | ⚠️ Aceptable - Hay margen de mejora |
| > 15% | ❌ Problema - Requiere atención urgente |

**Objetivo:** Reducir D13 mes a mes para mejorar la comprensión del chatbot.

---

## 📘 Documentación Técnica

### athena_connector.py

#### Funcionalidades Principales

1. **Lectura Automática de Configuración**
   - Lee `config_fechas.txt`
   - Soporta mes completo o rango personalizado
   - Valida formato de fechas

2. **Ejecución de Queries**
   - 3 queries SQL pre-configuradas
   - Reemplazo automático de variables de fecha
   - Monitoreo de progreso en tiempo real

3. **Manejo de Tokens AWS**
   - Detección automática de token expirado
   - Sistema de reintentos (3 intentos)
   - Instrucciones claras para renovación manual
   - Recarga de credenciales sin reiniciar

4. **Descarga de Resultados**
   - Descarga directa desde S3
   - Archivos guardados en `temp/`
   - Muestra tamaño de archivos descargados

#### Parámetros Configurables

```python
CONFIG = {
    'region': 'us-east-1',
    'workgroup': 'Production-caba-piba-athena-boti-group',
    'database': 'caba-piba-consume-zone-db'
}
```

---

### No_Entendidos.py

#### Funcionalidades Principales

1. **Lectura de Configuración**
   - Busca `config_fechas.txt` en múltiples ubicaciones
   - Soporta ejecución desde cualquier directorio
   - Validación de fechas

2. **Procesamiento de Datos**
   - Carga por chunks (optimizado para RAM)
   - Filtrado automático de testers
   - Filtrado de intenciones según lista blanca

3. **Optimización PASO 6**
   - Eliminación de mensajes consecutivos
   - Método vectorizado (shift)
   - 60 minutos → 2 segundos (100x más rápido)

4. **Generación de Archivos**
   - JSON con datos crudos
   - Excel detallado con formato
   - Dashboard Master con 17 indicadores

#### Pasos del Proceso

```
PASO 1: Configuración
PASO 2: Archivos auxiliares (testers, lista blanca)
PASO 3: Procesar mensajes (10-15 min)
PASO 4: Procesar clicks (5-10 min)
PASO 5: Procesar botones (2-5 min)
PASO 6: Limpieza (2 segundos - optimizado)
PASO 7: Análisis y cálculo de métricas (1-2 min)
```

#### Constantes del Sistema

```python
RULE_NE = 'PLBWX5XYGQ2B3GP7IN8Q-nml045fna3@b.m-1669990832420'
INTENT_NADA = 'RuleBuilder:PLBWX5XYGQ2B3GP7IN8Q-alfafc@gmail.com-1536777380652'
SCORE_NE_THRESHOLD = 5.36
CHUNK_SIZE = 50000
```

---

## ⚠️ Solución de Problemas

### 1. Token AWS Expirado

**Síntoma:**
```
⚠️  TOKEN AWS EXPIRADO
```

**Solución:**
1. Abrir **otra terminal** (no cerrar la actual)
2. Ejecutar: `aws-azure-login --profile default --mode=gui`
3. Completar el login en el navegador
4. Volver a la terminal original
5. Presionar **ENTER**

El script detectará automáticamente las nuevas credenciales y continuará.

---

### 2. Error de Memoria RAM

**Síntoma:**
```
Unable to allocate X.XX GiB for an array
```

**Causa:** No hay suficiente RAM disponible (se necesitan ~8-16 GB)

**Soluciones:**

**Opción A - Liberar memoria:**
```
1. Cerrar Chrome/Edge/Firefox
2. Cerrar Excel y otros programas pesados
3. Reiniciar el script
```

**Opción B - Aumentar memoria virtual:**
```
1. Panel de Control → Sistema → Configuración avanzada
2. Opciones avanzadas → Rendimiento → Configuración
3. Opciones avanzadas → Memoria virtual → Cambiar
4. Aumentar tamaño del archivo de paginación
```

**Requerimientos:**
- Mínimo: 8 GB RAM
- Recomendado: 16 GB RAM

---

### 3. No Se Encuentra config_fechas.txt

**Síntoma:**
```
[ERROR] No se encuentra config_fechas.txt en ninguna ubicación
```

**Causa:** El archivo no existe en la raíz del repositorio.

**Solución:**

El archivo **debe estar en la raíz** del repositorio:

```
Metricas_Boti_Mensual/
└── config_fechas.txt              ← AQUÍ
```

**Crear el archivo:**

```bash
# Desde la raíz del repo
cd C:\GCBA\Metricas_Boti_Mensual
echo MES=12 > config_fechas.txt
echo AÑO=2025 >> config_fechas.txt
```

**El programa lo busca en:**
```
1. ../config_fechas.txt           (un nivel arriba - RAÍZ DEL REPO)
2. config_fechas.txt              (directorio actual)
3. ../../config_fechas.txt        (dos niveles arriba)
```

Si el archivo está en otro lugar, muévelo a la raíz:
```bash
move <ubicación-actual>\config_fechas.txt C:\GCBA\Metricas_Boti_Mensual\
```

---

### 4. Queries SQL No Encontradas

**Síntoma:**
```
[ERROR] No se encuentra queries/Mensajes.sql
```

**Solución:**

Verificar que existe el directorio `queries/` con los 3 archivos:

```
queries/
├── Mensajes.sql
├── Clicks.sql
└── Botones.sql
```

---

### 5. Archivos Auxiliares No Encontrados

**Síntoma:**
```
⚠️  Archivo testers.csv no encontrado
⚠️  Archivo Actualizacion_Lista_Blanca.csv no encontrado
```

**Solución:**

Esto es **normal**. Los archivos son **opcionales**:

- **Sin testers.csv:** Procesará TODOS los usuarios (incluyendo cuentas de prueba)
- **Sin Actualizacion_Lista_Blanca.csv:** Procesará TODAS las intenciones

Si quieres usarlos, colócalos en el directorio raíz:
```
No_Entendidos/
├── testers.csv
└── Actualizacion_Lista_Blanca.csv
```

---

### 6. Script Muy Lento

**Síntoma:** El PASO 3 tarda más de 30 minutos

**Causas posibles:**
- Disco duro lento (usar SSD)
- Poca RAM (cerrar programas)
- CSV muy grandes (diciembre típicamente es más pesado)

**Solución:**
- Verificar espacio en disco (necesitas ~30 GB libres)
- Cerrar todos los programas que no uses
- Ejecutar en horario de baja carga en AWS (madrugada)

---

### 7. Error al Crear Carpeta output/

**Síntoma:**
```
PermissionError: [Errno 13] Permission denied: 'output'
```

**Solución:**
```bash
# Dar permisos a la carpeta
mkdir output
# O ejecutar como administrador
```

---

## 📊 Ejemplo de Ejecución Completa

### Escenario: Métricas de Diciembre 2025

```powershell
# ========================
# PASO 1: CONFIGURACIÓN
# ========================

# Editar config_fechas.txt en la raíz del repo
PS C:\GCBA\Metricas_Boti_Mensual> notepad config_fechas.txt
# Editar:
# MES=12
# AÑO=2025

# ========================
# PASO 2: LOGIN AWS
# ========================

PS C:\GCBA\Metricas_Boti_Mensual> aws-azure-login --profile default --mode=gui
[Navegador se abre]
[Completar login]
Assuming role...
✓ Success

# ========================
# PASO 3: DESCARGAR DATOS
# ========================

PS C:\GCBA\Metricas_Boti_Mensual> cd No_Entendidos
PS C:\GCBA\Metricas_Boti_Mensual\No_Entendidos> python athena_connector.py

╔═══════════════════════════════════════════════════════════════════════════╗
║                      ATHENA CONNECTOR - MODO PRUEBA                       ║
╚═══════════════════════════════════════════════════════════════════════════╝

🔐 Verificando credenciales AWS...
✓ Credenciales AWS activas

📄 Leyendo config_fechas.txt...
[INFO] Usando: C:\GCBA\Metricas_Boti_Mensual\config_fechas.txt
✓ Modo: Mes completo
  Mes: 12/2025
  Desde: 2025-12-01
  Hasta: 2026-01-01

============================================================
  Mensajes.sql
============================================================
☁️  Ejecutando en Athena...
  🚀 Iniciando query en Athena...
  📋 Query ID: abc123...
  ⏳ Ejecutando... (30s)
  ⏳ Ejecutando... (60s)
  ...
  ✅ Query exitosa
💾 Descargando resultado...
  ✅ Descargado: temp/mensajes_temp.csv (13029.30 MB)

============================================================
  Clicks.sql
============================================================
[Similar proceso...]
  ✅ Descargado: temp/clicks_temp.csv (8966.41 MB)

============================================================
  Botones.sql
============================================================
[Similar proceso...]
  ✅ Descargado: temp/botones_temp.csv (3245.12 MB)

================================================================================
  ✅ TODAS LAS QUERIES EJECUTADAS EXITOSAMENTE
================================================================================
📂 Archivos generados:
   ├─ temp/mensajes_temp.csv
   ├─ temp/clicks_temp.csv
   └─ temp/botones_temp.csv

# ========================
# PASO 4: CALCULAR MÉTRICAS
# ========================

PS C:\GCBA\Metricas_Boti_Mensual\No_Entendidos> python No_Entendidos.py

================================================================================
  MÉTRICAS BOTI - VERSIÓN AUTO CONFIG
  Lee configuración automática desde config_fechas.txt
  PASO 6 Optimizado: 100x más rápido
================================================================================

📋 [PASO 0] Leyendo configuración...
[INFO] Usando: C:\GCBA\Metricas_Boti_Mensual\config_fechas.txt
[INFO] Modo: MES COMPLETO

✓ Configuración leída correctamente:
   Modo: MES
   Período: diciembre 2025
   Fecha inicio: 2025-12-01 00:00:00
   Fecha fin: 2026-01-01 00:00:00

================================================================================
  PASO 1: CONFIGURACIÓN
================================================================================
[14:35:00] ✓ Directorio: C:\GCBA\Metricas_Boti_Mensual\No_Entendidos\temp
📅 Período: 2025-12-01 00:00:00 a 2026-01-01 00:00:00
💾 Chunk size: 50,000

================================================================================
  PASO 2: ARCHIVOS AUXILIARES
================================================================================
[14:35:00] ✓ Testers (desde directorio padre): 234
[14:35:00] ✓ Intenciones mostrables (desde directorio padre): 668

================================================================================
  PASO 3: PROCESAR MENSAJES
================================================================================
[14:35:01] Cargando mensajes_temp.csv...
[14:35:45] ✓ 43,250,123 leídos → 42,125,456 después de filtrar

================================================================================
  PASO 4: PROCESAR CLICKS
================================================================================
[14:42:15] Cargando clicks_temp.csv...
[14:47:30] ✓ 28,456,789 leídos → 27,823,456 después de filtrar

================================================================================
  PASO 5: PROCESAR BOTONES
================================================================================
[14:47:31] Cargando botones_temp.csv...
[14:49:05] ✓ 12,345,678 registros

================================================================================
  PASO 6: LIMPIEZA (OPTIMIZADO)
================================================================================
[14:49:06] Identificando mensajes consecutivos...
[14:49:08] ✓ Eliminados: 3,256,585 mensajes consecutivos

================================================================================
  PASO 7: ANÁLISIS
================================================================================
[14:49:08] Calculando métricas...

================================================================================
  MÉTRICAS FINALES
================================================================================
  OneShots:       65.10%
  Clicks:         13.00%
  Texto:            4.80%
  Abandonos:        5.40%
  Nada:             5.50%
  No Entendidos:    6.20%
  Letra:            0.10%
  
  ✓ Suma: 100.00%
  ✅ VALIDACIÓN EXITOSA
  
  Resolución:     82.90%
  Problemas:       5.50%
  Nada + NE:      11.70% ← Tu métrica clave

================================================================================
✅ COMPLETADO
================================================================================

⏱️ Tiempo total: 0:23:42

💾 promedios1 = {'abandonos': 0.054, 'click': 0.130, 'one': 0.651, 
                 'texto': 0.048, 'nada': 0.055, 'letra': 0.001, 'ne': 0.062}

📁 Archivo JSON: metricas_boti_diciembre_2025.json

📊 Generando archivos Excel...
  📁 Carpeta output: C:\GCBA\Metricas_Boti_Mensual\No_Entendidos\output
  ✅ Excel detallado: output\no_entendimiento_detalle_diciembre_2025.xlsx
  ✅ Dashboard creado: output\no_entendimiento_diciembre_2025.xlsx (D13 = 11.70%)

================================================================================
📦 ARCHIVOS GENERADOS:
================================================================================
  [1] JSON:               metricas_boti_diciembre_2025.json
  [2] Excel Detallado:    output\no_entendimiento_detalle_diciembre_2025.xlsx
  [3] Dashboard Master:   output\no_entendimiento_diciembre_2025.xlsx

  🎯 D13 (No Entendimiento): 11.70%
================================================================================
```

---

## 💡 Tips y Buenas Prácticas

### Configuración Compartida

**Importante:** El archivo `config_fechas.txt` está en la raíz y es **compartido por todos los proyectos** de métricas:

```
Metricas_Boti_Mensual/
├── config_fechas.txt              ← Compartido por todos
├── No_Entendidos/
├── Feedback_CES/
├── Feedback_CSAT/
└── ...
```

**Ventaja:** Configuras el período **una vez** y puedes ejecutar múltiples scripts de métricas.

**Ejemplo de workflow mensual:**
```bash
# 1. Configurar mes (UNA VEZ)
cd C:\GCBA\Metricas_Boti_Mensual
notepad config_fechas.txt
# MES=12, AÑO=2025

# 2. Login AWS (UNA VEZ)
aws-azure-login --profile default --mode=gui

# 3. Ejecutar múltiples proyectos
cd No_Entendidos
python athena_connector.py
python No_Entendidos.py

cd ..\Feedback_CSAT
python feedback_csat.py

cd ..\Feedback_CES
python feedback_ces.py
# etc.
```

### Ejecución Mensual

**Mejor momento:** Primera semana del mes (para procesar el mes anterior)

**Ejemplo:** Primera semana de enero 2026 → Procesar diciembre 2025

### Limpieza de Archivos Temporales

Los archivos en `temp/` son **muy grandes** (~25 GB) y se pueden borrar después:

```bash
# Después de generar los Excel, puedes borrar:
cd No_Entendidos
del temp\*.csv

# O mantener los temp\ por si necesitas reprocesar
```

### Backup de Resultados

Los archivos en `output/` son **importantes**, hacer backup mensual:

```bash
# Crear carpeta de backup
mkdir backup\diciembre_2025

# Copiar archivos
copy output\*.xlsx backup\diciembre_2025\
copy metricas_boti_diciembre_2025.json backup\diciembre_2025\
```

### Automatización (Opcional)

Crear un script `.bat` para ejecutar todo:

**ejecutar_metricas_no_entendidos.bat:**
```batch
@echo off
echo ====================================
echo MÉTRICAS BOTI - NO ENTENDIMIENTO
echo ====================================

REM Verificar que config_fechas.txt existe en la raíz
if not exist "..\config_fechas.txt" (
    echo ERROR: No se encuentra config_fechas.txt en la raiz del repo
    echo Crea el archivo: Metricas_Boti_Mensual\config_fechas.txt
    pause
    exit /b 1
)

echo.
echo Configuracion actual:
type ..\config_fechas.txt
echo.
pause

echo.
echo [1/3] Login AWS...
aws-azure-login --profile default --mode=gui
if errorlevel 1 goto error

echo.
echo [2/3] Descargando datos de Athena...
python athena_connector.py
if errorlevel 1 goto error

echo.
echo [3/3] Calculando métricas...
python No_Entendidos.py
if errorlevel 1 goto error

echo.
echo ====================================
echo ✓ PROCESO COMPLETADO
echo ====================================
echo.
echo Archivos generados en:
echo   - output\no_entendimiento_detalle_*.xlsx
echo   - output\no_entendimiento_*.xlsx
echo   - metricas_boti_*.json
echo.
pause
exit

:error
echo.
echo ====================================
echo ✗ ERROR EN EL PROCESO
echo ====================================
pause
exit /b 1
```

**Uso:**
```bash
# 1. Editar config_fechas.txt en la raíz
# 2. Ir a No_Entendidos/
cd C:\GCBA\Metricas_Boti_Mensual\No_Entendidos

# 3. Ejecutar:
ejecutar_metricas_no_entendidos.bat
```

---

## 🔄 Changelog

### v2.1 (Enero 2026)
- ✅ Generación automática de Excel (detallado + dashboard)
- ✅ Dashboard completo con 17 indicadores
- ✅ Carpeta output/ para archivos finales
- ✅ Búsqueda flexible de config_fechas.txt

### v2.0 (Enero 2026)
- ✅ Integración automática con config_fechas.txt
- ✅ Manejo robusto de expiración de tokens AWS
- ✅ Optimización PASO 6 (60 min → 2 seg)
- ✅ Generación de JSON con resultados

### v1.0 (Diciembre 2025)
- ✅ Versión inicial con configuración manual
- ✅ Scripts separados sin integración

---

## 👥 Soporte

Para reportar problemas o sugerir mejoras:

1. Documentar el error con logs completos
2. Incluir versión de Python y librerías
3. Especificar pasos para reproducir

---

## 📄 Licencia

Uso interno - Gobierno de la Ciudad de Buenos Aires

---

## 🙏 Agradecimientos

**Equipo:** Data Analytics - GCBA  
**Proyecto:** Métricas Boti  
**Autor:** Damian

---

**Última actualización:** 13 de enero de 2026  
**Versión:** 2.1

# 📊 Sistema de Métricas Boti - GCBA

[![GitHub](https://img.shields.io/badge/GitHub-EdVeralli%2FMetricas__Boti__Mensual-blue?logo=github)](https://github.com/EdVeralli/Metricas_Boti_Mensual)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-GCBA-green)]()

Sistema automatizado para cálculo de métricas mensuales del chatbot Boti de la Ciudad de Buenos Aires.

**🔗 Repositorio:** https://github.com/EdVeralli/Metricas_Boti_Mensual

---

## 📋 Tabla de Contenidos

- [Descripción General](#-descripción-general)
- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso - Guía Rápida](#-uso---guía-rápida)
- [Módulos Implementados](#-módulos-implementados)
- [Dashboard de Métricas](#-dashboard-de-métricas)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Scripts Principales](#-scripts-principales)
- [Solución de Problemas](#-solución-de-problemas)
- [Changelog](#-changelog)

---

## 🎯 Descripción General

Este sistema procesa datos del chatbot Boti para calcular **17 métricas clave de rendimiento** que se consolidan en un dashboard unificado. Cada métrica es calculada por un módulo independiente que genera archivos Excel con formato estandarizado.

**Repositorio GitHub:** https://github.com/EdVeralli/Metricas_Boti_Mensual

### Características Principales

- ✅ **9 módulos independientes** que calculan 10 métricas diferentes
- ✅ **Configuración centralizada** a través de `config_fechas.txt`
- ✅ **Ejecución automatizada** con `run_all.py`
- ✅ **Consolidación automática** de todas las métricas en un dashboard único
- ✅ **Integración con AWS Athena** para procesamiento de big data
- ✅ **Formato Excel estandarizado** compatible con reportes institucionales

---

## 🏗️ Arquitectura del Sistema

### Flujo de Trabajo General

```
┌─────────────────────────────────────────────────────────────┐
│  1. CONFIGURACIÓN                                           │
│     config_fechas.txt (MES=12, AÑO=2025)                   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  2. EJECUCIÓN DE MÓDULOS (run_all.py)                      │
│     ├─ Usuarios_Conversaciones      → D2, D3               │
│     ├─ Pushes_Enviadas              → D6                   │
│     ├─ Sesiones_Abiertas_Pushes     → D4                   │
│     ├─ Sesiones_Alcanzadas_Pushes   → D5                   │
│     ├─ No_Entendidos                → D13                  │
│     │  ├─ 1. athena_connector.py (descarga CSVs)          │
│     │  └─ 2. No_Entendidos.py (calcula métrica)           │
│     ├─ Feedback_Efectividad         → D14                  │
│     ├─ Feedback_CES                 → D15                  │
│     ├─ Feedback_CSAT                → D16                  │
│     └─ Metricas_Boti_Disponibilidad → D17                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  3. CONSOLIDACIÓN (consolidar_excel.py)                    │
│     Genera: Boti_Consolidado_diciembre_2025.xlsx           │
│     Con todas las métricas unificadas                       │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  4. EFECTIVIDAD WEB+BOTI (calcular_efectividad_web_boti.py)│
│     Combina datos de Metricas_Boti + Metricas_Web          │
│     Genera: efectividad_web_boti_{mes}_{año}.xlsx          │
└─────────────────────────────────────────────────────────────┘
```

### Componentes del Sistema

#### 1. **config_fechas.txt** (Configuración Centralizada)
- Ubicación: Raíz del repositorio
- Define el período a procesar (mes completo o rango personalizado)
- Compartido por todos los módulos

#### 2. **run_all.py** (Orquestador Maestro)
- Ejecuta los 9 módulos secuencialmente
- Verifica credenciales AWS
- Muestra progreso y resumen de ejecución
- Duración total: 30-60 minutos

#### 3. **Módulos Independientes** (9 carpetas)
- Cada módulo calcula una o más métricas específicas
- Genera Excel con estructura de dashboard estandarizada
- Llena solo sus celdas correspondientes (D2-D17)

#### 4. **consolidar_excel.py** (Generador de Dashboard Unificado)
- Lee todos los Excel de los módulos
- Extrae las métricas de cada celda
- Genera un único dashboard consolidado
- Ubicación: Raíz del repositorio

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
pip install boto3 awswrangler pandas numpy openpyxl selenium
```

O con archivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Accesos AWS

- **Workgroup:** Production-caba-piba-athena-boti-group
- **Database:** caba-piba-consume-zone-db
- **Rol:** PIBAConsumeBoti
- **Region:** us-east-1

---

## ⚙️ Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/EdVeralli/Metricas_Boti_Mensual.git
cd Metricas_Boti_Mensual
```

### 2. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar AWS Azure Login

**Primera vez (solo una vez):**

```bash
aws-azure-login --configure --profile default
```

Completar con:
- **Azure Tenant ID:** (proporcionado por IT)
- **Azure App ID URI:** (proporcionado por IT)
- **Default Role ARN:** PIBAConsumeBoti

---

## 📝 Configuración

### Archivo: `config_fechas.txt` (Raíz del Repositorio)

Este archivo es **compartido por todos los módulos** y define el período a procesar.

**Ubicación:**
```
Metricas_Boti_Mensual/
└── config_fechas.txt              ← ESTE ARCHIVO
```

### Opciones de Configuración

#### Opción 1: Mes Completo (Recomendado)

```ini
MES=12
AÑO=2025
```

Procesa todo el mes de diciembre 2025.

#### Opción 2: Rango Personalizado

```ini
FECHA_INICIO=2025-12-01
FECHA_FIN=2025-12-15
```

Procesa solo las primeras 2 semanas de diciembre.

**Nota:** Si especificas `FECHA_INICIO` y `FECHA_FIN`, se ignorarán `MES` y `AÑO`.

---

## 🚀 Uso - Guía Rápida

### Ejecución Mensual Completa (3 Pasos)

#### PASO 1: Configurar Período

Editar `config_fechas.txt`:

```bash
cd C:\GCBA\Metricas_Boti_Mensual
notepad config_fechas.txt
```

Contenido:
```ini
MES=12
AÑO=2025
```

#### PASO 2: Login AWS

```bash
aws-azure-login --profile default --mode=gui
```

Esto abre el navegador para autenticación.

#### PASO 3: Ejecutar Todos los Módulos

```bash
python run_all.py
```

**Resultado esperado:**
```
================================================================================
  SCRIPT MAESTRO - Metricas_Boti_Mensual
================================================================================

Ejecutará los siguientes módulos:
  1. Usuarios y Conversaciones (D2, D3)
  2. Pushes Enviadas (D6)
  3. Sesiones Abiertas por Pushes (D4)
  4. Sesiones Alcanzadas por Pushes (D5)
  5. No Entendimiento (D13)
  6. Feedback - Efectividad (D14)
  7. Feedback - CES (D15)
  8. Feedback - CSAT (D16)
  9. Disponibilidad WhatsApp (D17)

⚠️  IMPORTANTE: Este proceso puede tardar varios minutos

[Proceso de ejecución...]

================================================================================
RESUMEN DE EJECUCIÓN
================================================================================
📊 Total de módulos: 9
✅ Exitosos: 9
❌ Fallidos: 0
⏱️  Tiempo total: 45.3 minutos

🎉 ¡TODOS LOS MÓDULOS SE EJECUTARON EXITOSAMENTE!

💡 Próximo paso: Ejecutar el consolidador de Excel
   python consolidar_excel.py
```

**Duración:** 30-60 minutos (dependiendo de la cantidad de datos)

#### PASO 4: Consolidar Resultados

```bash
python consolidar_excel.py
```

**Resultado esperado:**
```
================================================================================
  CONSOLIDADOR DE EXCEL - Metricas_Boti_Mensual
================================================================================

📋 Módulos a consolidar:
  • Usuarios y Conversaciones (D2, D3)
  • Sesiones Abiertas (D4)
  • Sesiones Alcanzadas (D5)
  • Pushes Enviadas (D6)
  • No Entendimiento (D13)
  • Feedback - Efectividad (D14)
  • Feedback - CES (D15)
  • Feedback - CSAT (D16)
  • Disponibilidad WhatsApp (D17)

[Proceso de consolidación...]

✅ Dashboard consolidado creado: Boti_Consolidado_diciembre_2025.xlsx

================================================================================
RESUMEN DE MÉTRICAS CONSOLIDADAS
================================================================================

📊 Métricas extraídas:
  ✅ Conversaciones (D2): 125,450
  ✅ Usuarios (D3): 45,823
  ✅ Sesiones Abiertas (D4): 12,345
  ✅ Sesiones Alcanzadas (D5): 15,678
  ✅ Pushes Enviadas (D6): 45,890
  ✅ No Entendimiento (D13): 11.70%
  ✅ Efectividad (D14): 87.5%
  ✅ CES (D15): 2.35
  ✅ CSAT (D16): 4.2
  ✅ Availability (D17): 99.8%

📈 Total de métricas: 10
✅ Con valor: 10
⚠️  Sin valor: 0

✨ CONSOLIDACIÓN COMPLETADA
```

#### PASO 5: Calcular Tasa de Efectividad WEB+BOTI (Opcional)

Este paso combina métricas de **Metricas_Boti_Mensual** y **Metricas_Web_Mensual** para calcular la tasa de efectividad ponderada.

**Requisito:** Debe haberse ejecutado también el proceso de `Metricas_Web_Mensual` para el mismo período.

```bash
python calcular_efectividad_web_boti.py
```

**Resultado esperado:**
```
Procesando: Diciembre 2025
==================================================
Leyendo: feedback_efectividad_diciembre_2025_efectividad.xlsx
Leyendo: conteo_completo_diciembre_2025.xlsx

Valores de entrada:
  Efectividad Positiva Boti: 0.6012 (60.12%)
  Total Boti: 43,170
  Total Web: 25,478
  Tasa Efectividad WEB: 80.17

Calculos intermedios:
  Total General: 68,648
  Ponderacion Feedback Boti: 0.6289 (62.89%)
  Primer Parcial General: 0.3781
  Ponderacion Feedback WEB: 0.3711 (37.11%)
  Segundo Parcial General: 0.2975

==================================================
TASA DE EFECTIVIDAD WEB+BOTI: 67.56%
==================================================
Excel generado: efectividad_web_boti/efectividad_web_boti_diciembre_2025.xlsx

Proceso completado exitosamente.
```

**Archivo generado:**
```
efectividad_web_boti/efectividad_web_boti_{mes}_{año}.xlsx
```

---

## 📊 Módulos Implementados

### Resumen de Módulos

| # | Módulo | Carpeta | Celda(s) | Métrica | AWS |
|---|--------|---------|----------|---------|-----|
| 1 | Usuarios y Conversaciones | `Metricas_Boti_Conversaciones_Usuarios/` | D2, D3 | Conversaciones, Usuarios únicos | ✅ |
| 2 | Pushes Enviadas | `Pushes_Enviadas/` | D6 | Mensajes push enviados | ✅ |
| 3 | Sesiones Abiertas | `Sesiones_Abiertas_Pushes/` | D4 | Sesiones iniciadas por push | ✅ |
| 4 | Sesiones Alcanzadas | `Sesiones_alcanzadas_pushes/` | D5 | Sesiones que recibieron push | ✅ |
| 5 | No Entendimiento | `No_Entendidos/` | D13 | Tasa de no comprensión | ✅ |
| 6 | Efectividad | `Feedback_Efectividad/` | D14 | % usuarios que lograron objetivo | ✅ |
| 7 | CES | `Feedback_CES/` | D15 | Customer Effort Score | ✅ |
| 8 | CSAT | `Feedback_CSAT/` | D16 | Customer Satisfaction | ✅ |
| 9 | Disponibilidad | `Metricas_Boti_Disponibilidad/` | D17 | Uptime del servidor WhatsApp | ❌ |

### Descripción de Cada Módulo

#### 1. Usuarios y Conversaciones
**Script:** `Usuarios_Conversaciones.py`
**Query:** Cuenta sesiones únicas y usuarios únicos
**Duración:** ~2 minutos

#### 2. Pushes Enviadas
**Script:** `Pushes_Enviadas.py`
**Query:** Cuenta mensajes enviados con formato Template
**Duración:** ~3 minutos

#### 3. Sesiones Abiertas por Pushes
**Script:** `Sesiones_Abiertas_porPushes.py`
**Query:** Sesiones con `starting_cause = 'WhatsAppTemplate'`
**Duración:** ~2 minutos

#### 4. Sesiones Alcanzadas por Pushes
**Script:** `Sesiones_Alcanzadas.py`
**Query:** Sesiones que recibieron al menos un push
**Duración:** ~2 minutos

#### 5. No Entendimiento (Módulo Complejo)
**Scripts:**
1. `athena_connector.py` - Descarga 3 CSVs grandes (~25 GB)
2. `No_Entendidos.py` - Procesa y calcula D13

**Duración:**
- athena_connector: 10-20 minutos
- No_Entendidos: 20-30 minutos

**Métricas Calculadas:**
- OneShots: ~65%
- Clicks: ~13%
- Texto: ~5%
- Abandonos: ~5%
- Nada: ~6%
- NE (No Entendidos): ~6%
- Letra: ~0.1%
- **D13 = Nada + NE ≈ 11-12%**

#### 6. Feedback - Efectividad
**Script:** `Feedback_Efectividad.py`
**Query:** Tasa de transacciones completadas
**Duración:** ~2 minutos

#### 7. Feedback - CES (Customer Effort Score)
**Script:** `Feedback_CES.py`
**Query:** Promedio ponderado de facilidad de uso (1-5)
**Duración:** ~2 minutos

#### 8. Feedback - CSAT (Customer Satisfaction)
**Script:** `Feedback_CSAT.py`
**Query:** Promedio de satisfacción del usuario (1-5)
**Duración:** ~2 minutos

#### 9. Disponibilidad WhatsApp
**Script:** `WhatsApp_Availability.py`
**Tecnología:** Web scraping con Selenium
**Fuente:** https://metastatus.com/whatsapp-business-api
**Duración:** ~1 minuto

---

## 📈 Dashboard de Métricas

### Estructura del Dashboard Consolidado

El dashboard final contiene **17 filas** de indicadores. **10 están implementadas** (D2-D6, D13-D17), las restantes (D7-D12) son responsabilidad de otro equipo.

| Fila | Indicador | Descripción | Valor | Estado |
|------|-----------|-------------|-------|--------|
| **1** | **Headers** | Indicador / Descripción / Período | **dic-25** | **Header** |
| **2** | Conversaciones | Q Conversaciones | 125,450 | ✅ Implementado |
| **3** | Usuarios | Q Usuarios únicos | 45,823 | ✅ Implementado |
| **4** | Sesiones abiertas por Pushes | Sesiones iniciadas con push | 12,345 | ✅ Implementado |
| **5** | Sesiones Alcanzadas por Pushes | Sesiones que recibieron push | 15,678 | ✅ Implementado |
| **6** | Mensajes Pushes Enviados | Q de mensajes push | 45,890 | ✅ Implementado |
| **7** | Contenidos en Botmaker | Contenidos activos | - | ⚠️ Otro equipo |
| **8** | Contenidos Prendidos para el USUARIO | Contenidos visibles | - | ⚠️ Otro equipo |
| **9** | Interacciones | Q Interacciones | - | ⚠️ Otro equipo |
| **10** | Trámites, solicitudes y turnos | Q Trámites disponibles | - | ⚠️ Otro equipo |
| **11** | Contenidos más consultados | Top 10 | - | ⚠️ Otro equipo |
| **12** | Derivaciones | Q Derivaciones | - | ⚠️ Otro equipo |
| **13** | No entendimiento | Performance motor IA | 11.70% | ✅ Implementado |
| **14** | Tasa de Efectividad | % usuarios que lograron objetivo | 87.5% | ✅ Implementado |
| **15** | CES (Customer Effort Score) | Facilidad de interacción (1-5) | 2.35 | ✅ Implementado |
| **16** | Satisfacción (CSAT) | Satisfacción usuario (1-5) | 4.2 | ✅ Implementado |
| **17** | Uptime servidor | Disponibilidad WhatsApp | 99.8% | ✅ Implementado |

### Cómo Funciona el Dashboard

1. **Cada módulo** crea un Excel con la **estructura completa** (17 filas)
2. **Solo llena** las celdas que le corresponden (columna D)
3. **El consolidador** lee todos los Excel y extrae los valores
4. **Genera un único Excel** con todas las métricas unificadas

---

## 📂 Estructura del Proyecto

```
Metricas_Boti_Mensual/                          ← Repositorio raíz
│
├── README.md                                   ← Este documento
├── config_fechas.txt                           ← Configuración centralizada
├── run_all.py                                  ← Script maestro
├── consolidar_excel.py                         ← Consolidador de métricas
├── calcular_efectividad_web_boti.py            ← Efectividad WEB+BOTI (NUEVO)
├── diagnosticar_excel.py                       ← Herramienta de diagnóstico
│
├── Boti_Consolidado_diciembre_2025.xlsx        ← Dashboard final (generado)
├── efectividad_web_boti/                       ← Output efectividad combinada
│   └── efectividad_web_boti_diciembre_2025.xlsx
│
├── Metricas_Boti_Conversaciones_Usuarios/      ← Módulo 1
│   ├── Usuarios_Conversaciones.py
│   ├── output/
│   │   └── usuarios_conversaciones_diciembre_2025.xlsx
│   └── requirements.txt
│
├── Pushes_Enviadas/                            ← Módulo 2
│   ├── Pushes_Enviadas.py
│   ├── output/
│   │   └── mensajes_pushes_enviados_diciembre_2025.xlsx
│   └── requirements.txt
│
├── Sesiones_Abiertas_Pushes/                   ← Módulo 3
│   ├── Sesiones_Abiertas_porPushes.py
│   ├── output/
│   │   └── sesiones_abiertas_pushes_diciembre_2025.xlsx
│   └── requirements.txt
│
├── Sesiones_alcanzadas_pushes/                 ← Módulo 4
│   ├── Sesiones_Alcanzadas.py
│   ├── output/
│   │   └── sesiones_alcanzadas_pushes_diciembre_2025.xlsx
│   └── requirements.txt
│
├── No_Entendidos/                              ← Módulo 5 (complejo)
│   ├── README.md                               ← Documentación detallada
│   ├── athena_connector.py                     ← Paso 1: Descarga datos
│   ├── No_Entendidos.py                        ← Paso 2: Calcula métricas
│   ├── Mensajes.sql                            ← Queries SQL
│   ├── Clicks.sql
│   ├── Botones.sql
│   ├── testers.csv                             (opcional)
│   ├── Actualizacion_Lista_Blanca.csv          (opcional)
│   ├── temp/                                   ← CSVs temporales (25 GB)
│   │   ├── mensajes_temp.csv
│   │   ├── clicks_temp.csv
│   │   └── botones_temp.csv
│   ├── output/                                 ← Resultados finales
│   │   ├── no_entendimiento_detalle_diciembre_2025.xlsx
│   │   └── no_entendimiento_diciembre_2025.xlsx
│   ├── metricas_boti_diciembre_2025.json       ← Datos crudos
│   └── requirements.txt
│
├── Feedback_Efectividad/                       ← Módulo 6
│   ├── Feedback_Efectividad.py
│   ├── output/
│   │   └── feedback_efectividad_diciembre_2025.xlsx
│   └── requirements.txt
│
├── Feedback_CES/                               ← Módulo 7
│   ├── Feedback_CES.py
│   ├── output/
│   │   ├── feedback_ces_detalle_diciembre_2025.xlsx
│   │   └── feedback_ces_diciembre_2025.xlsx
│   └── requirements.txt
│
├── Feedback_CSAT/                              ← Módulo 8
│   ├── Feedback_CSAT.py
│   ├── output/
│   │   ├── feedback_csat_detalle_diciembre_2025.xlsx
│   │   └── feedback_csat_diciembre_2025.xlsx
│   └── requirements.txt
│
└── Metricas_Boti_Disponibilidad/               ← Módulo 9
    ├── WhatsApp_Availability.py
    ├── output/
    │   └── whatsapp_availability_20251215_143000.xlsx
    └── requirements.txt
```

---

## 🔧 Scripts Principales

### 1. run_all.py

**Función:** Orquestador maestro que ejecuta todos los módulos secuencialmente.

**Uso:**
```bash
python run_all.py
```

**Características:**
- ✅ Verifica credenciales AWS antes de empezar
- ✅ Lee `config_fechas.txt` y valida configuración
- ✅ Ejecuta los 9 módulos en orden
- ✅ Para el módulo **No_Entendidos**, ejecuta primero `athena_connector.py` y luego `No_Entendidos.py`
- ✅ Muestra progreso en tiempo real
- ✅ Genera resumen final con métricas de ejecución
- ✅ Indica si todos los módulos se ejecutaron exitosamente

**Módulos ejecutados en orden:**
1. Usuarios y Conversaciones
2. Pushes Enviadas
3. Sesiones Abiertas por Pushes
4. Sesiones Alcanzadas por Pushes
5. No Entendimiento (athena_connector.py → No_Entendidos.py)
6. Feedback - Efectividad
7. Feedback - CES
8. Feedback - CSAT
9. Disponibilidad WhatsApp

**Duración Total:** 30-60 minutos

---

### 2. consolidar_excel.py

**Función:** Consolida todos los Excel parciales en un dashboard único.

**Uso:**
```bash
python consolidar_excel.py
```

**Proceso:**
1. Busca los Excel más recientes en cada carpeta `output/`
2. Lee las métricas específicas de cada Excel
3. Crea un dashboard consolidado con todas las métricas
4. Guarda el archivo en la raíz: `Boti_Consolidado_[periodo].xlsx`

**Características:**
- ✅ Busca automáticamente archivos más recientes
- ✅ Excluye archivos `*_detalle_*`
- ✅ Aplica formato y estilos al dashboard
- ✅ Muestra resumen de métricas extraídas

**Archivo generado:**
```
Boti_Consolidado_diciembre_2025.xlsx
```

---

### 3. calcular_efectividad_web_boti.py

**Función:** Calcula la Tasa de Efectividad combinada WEB+BOTI.

**Uso:**
```bash
python calcular_efectividad_web_boti.py
```

**Fuentes de datos:**
- `Metricas_Boti_Mensual/Feedback_Efectividad/output/feedback_efectividad_{mes}_{año}_efectividad.xlsx`
  - Celda C28: Efectividad Positiva Boti
  - Celda B30: Total Boti
- `Metricas_Web_Mensual/Satisfaccion/data/conteo_completo_{mes}_{año}.xlsx`
  - Columna Total_General (S2): Total Web
  - Columna Tasa_Efectividad (T2): Tasa Efectividad WEB

**Fórmulas:**
```
Total General = Total Boti + Total Web
Ponderacion Feedback Boti = Total Boti / Total General
Primer Parcial General = Efectividad Positiva Boti × Ponderacion Feedback Boti
Ponderacion Feedback WEB = Total Web / Total General
Segundo Parcial General = Ponderacion Feedback WEB × Tasa Efectividad WEB
Tasa de Efectividad WEB+BOTI = Primer Parcial General + Segundo Parcial General
```

**Archivo generado:**
```
efectividad_web_boti/efectividad_web_boti_{mes}_{año}.xlsx
```

---

### 4. diagnosticar_excel.py

**Función:** Herramienta de diagnóstico para verificar archivos Excel.

**Uso:**
```bash
python diagnosticar_excel.py
```

Ayuda a identificar problemas con archivos Excel corruptos o mal formateados.

---

## ⚠️ Solución de Problemas

### 1. Token AWS Expirado

**Síntoma:**
```
⚠️  TOKEN AWS EXPIRADO
```

**Solución:**
```bash
# En otra terminal
aws-azure-login --profile default --mode=gui

# El script detectará las nuevas credenciales automáticamente
```

---

### 2. Error en Módulo No_Entendidos

**Síntoma:**
```
[ERROR] No se encuentra mensajes_temp.csv
```

**Causa:** `athena_connector.py` no se ejecutó o falló.

**Solución:**
El `run_all.py` ahora ejecuta `athena_connector.py` automáticamente antes de `No_Entendidos.py`. Si ejecutas manualmente, asegúrate de ejecutar primero:

```bash
cd No_Entendidos
python athena_connector.py
python No_Entendidos.py
```

---

### 3. Consolidador No Encuentra Archivos

**Síntoma:**
```
❌ No se encontraron archivos en [módulo]
```

**Causa:** El módulo no se ejecutó correctamente.

**Solución:**
1. Verificar que `run_all.py` completó todos los módulos exitosamente
2. Revisar que existen archivos en las carpetas `output/` de cada módulo
3. Ejecutar el módulo faltante manualmente

---

### 4. Error de Memoria RAM

**Síntoma:**
```
Unable to allocate X.XX GiB for an array
```

**Causa:** No hay suficiente RAM (se necesitan ~8-16 GB)

**Solución:**
```
1. Cerrar Chrome/Edge/Firefox
2. Cerrar Excel y otros programas pesados
3. Reiniciar el script
```

**Requerimientos:**
- Mínimo: 8 GB RAM
- Recomendado: 16 GB RAM

---

### 5. No Se Encuentra config_fechas.txt

**Síntoma:**
```
[ERROR] No se encuentra config_fechas.txt
```

**Solución:**

Crear el archivo en la **raíz del repositorio**:

```bash
cd C:\GCBA\Metricas_Boti_Mensual
echo MES=12 > config_fechas.txt
echo AÑO=2025 >> config_fechas.txt
```

---

## 💡 Tips y Buenas Prácticas

### Ejecución Mensual

**Mejor momento:** Primera semana del mes (para procesar el mes anterior)

**Ejemplo:** Primera semana de enero 2026 → Procesar diciembre 2025

### Workflow Recomendado

```bash
# Día 1 del mes siguiente
cd C:\GCBA\Metricas_Boti_Mensual

# 1. Configurar mes anterior
notepad config_fechas.txt
# MES=12, AÑO=2025

# 2. Login AWS
aws-azure-login --profile default --mode=gui

# 3. Ejecutar todos los módulos (30-60 min)
python run_all.py

# 4. Consolidar resultados
python consolidar_excel.py

# 5. Verificar dashboard generado
# Abrir: Boti_Consolidado_diciembre_2025.xlsx
```

### Limpieza de Archivos Temporales

Los archivos en `No_Entendidos/temp/` son **muy grandes** (~25 GB) y se pueden borrar después:

```bash
cd No_Entendidos
del temp\*.csv
```

### Backup de Resultados

```bash
# Crear carpeta de backup mensual
mkdir backup\diciembre_2025

# Copiar dashboard consolidado
copy Boti_Consolidado_diciembre_2025.xlsx backup\diciembre_2025\

# Copiar outputs individuales (opcional)
xcopy Metricas_Boti_Conversaciones_Usuarios\output\*.xlsx backup\diciembre_2025\ /S
xcopy No_Entendidos\output\*.xlsx backup\diciembre_2025\ /S
# etc.
```

---

## 🔄 Changelog

### v2.3 (Enero 2026) - **ACTUAL**
- ✅ **NUEVO:** `calcular_efectividad_web_boti.py` - Calcula tasa de efectividad combinada WEB+BOTI
- ✅ Integración con repositorio `Metricas_Web_Mensual`
- ✅ Genera Excel con cálculos intermedios y resultado final ponderado
- ✅ README actualizado con documentación del nuevo script

### v2.2 (Enero 2026)
- ✅ **run_all.py:** Ejecución automática de `athena_connector.py` antes de `No_Entendidos.py`
- ✅ **consolidar_excel.py:** Corregido path del módulo No_Entendidos
- ✅ **Soporte para múltiples scripts** por módulo
- ✅ README actualizado con documentación completa del sistema

### v2.1 (Enero 2026)
- ✅ Sistema modular con 9 módulos independientes
- ✅ Script maestro `run_all.py`
- ✅ Consolidador automático de métricas
- ✅ Dashboard con 17 indicadores

### v2.0 (Enero 2026)
- ✅ Integración con `config_fechas.txt` centralizado
- ✅ Optimización PASO 6 en No_Entendidos (60 min → 2 seg)
- ✅ Generación automática de Excel con formato

### v1.0 (Diciembre 2025)
- ✅ Versión inicial con módulos independientes

---

## 👥 Soporte

**Repositorio GitHub:** https://github.com/EdVeralli/Metricas_Boti_Mensual

Para reportar problemas o sugerir mejoras:

1. Abrir un **Issue** en GitHub
2. Documentar el error con logs completos
3. Incluir versión de Python y librerías
4. Especificar pasos para reproducir

**Contacto:**
- **Repositorio:** https://github.com/EdVeralli/Metricas_Boti_Mensual
- **Equipo:** Data Analytics - GCBA
- **Mantenedor:** @EdVeralli

---

## 📄 Licencia

Uso interno - Gobierno de la Ciudad de Buenos Aires

---

## 🙏 Agradecimientos

**Repositorio:** https://github.com/EdVeralli/Metricas_Boti_Mensual
**Equipo:** Data Analytics - GCBA
**Proyecto:** Métricas Boti
**Mantenedor:** @EdVeralli

---

**Última actualización:** 20 de enero de 2026
**Versión:** 2.3

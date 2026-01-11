# 📊 Sistema de Métricas Boti - GCBA

Sistema automatizado para descarga y procesamiento de métricas del chatbot Boti de la Ciudad de Buenos Aires.

---

## 📋 Tabla de Contenidos

- [Descripción General](#-descripción-general)
- [Requisitos](#-requisitos)
- [Configuración Inicial](#-configuración-inicial)
- [Uso](#-uso)
- [Estructura de Archivos](#-estructura-de-archivos)
- [Métricas Calculadas](#-métricas-calculadas)
- [Solución de Problemas](#-solución-de-problemas)

---

## 🎯 Descripción General

Este sistema consta de **2 programas principales** que trabajan en conjunto:

### 1. `athena_connector.py`
- Descarga datos desde AWS Athena
- Ejecuta 3 queries SQL automáticamente
- Genera 3 archivos CSV en `temp/`

### 2. `metricas_boti_AUTO_CONFIG.py`
- Procesa los CSVs descargados
- Calcula métricas de efectividad del chatbot
- Genera archivo JSON con resultados

**Ambos programas leen automáticamente desde `config_fechas.txt`** - solo necesitas editar este archivo para cambiar el período a procesar.

---

## 🔧 Requisitos

### Software Necesario

```
Python 3.8+
AWS CLI
aws-azure-login
```

### Librerías Python

```bash
pip install boto3 awswrangler pandas numpy openpyxl
```

### Accesos AWS

- **Rol:** PIBAConsumeBoti
- **Workgroup:** Production-caba-piba-athena-boti-group
- **Database:** caba-piba-consume-zone-db

---

## ⚙️ Configuración Inicial

### 1. Configurar AWS Azure Login

**Primera vez:**
```bash
aws-azure-login --configure --profile default
```

Completa:
- Azure Tenant ID: `{tenant_id}`
- Azure App ID URI: `{app_id}`
- Default Role ARN: PIBAConsumeBoti

### 2. Estructura de Directorios

```
Proyecto/
│
├── config_fechas.txt              ← Editas este archivo
├── athena_connector.py            ← Programa 1
├── metricas_boti_AUTO_CONFIG.py   ← Programa 2
│
├── queries/                       ← Queries SQL
│   ├── Mensajes.sql
│   ├── Clicks.sql
│   └── Botones.sql
│
├── testers.csv                    ← Archivos auxiliares (opcionales)
├── Actualizacion_Lista_Blanca.csv
│
└── temp/                          ← Carpeta temporal (se crea automática)
    ├── mensajes_temp.csv
    ├── clicks_temp.csv
    └── botones_temp.csv
```

### 3. Configurar Período

Edita `config_fechas.txt`:

**Opción 1: Mes completo**
```
MES=12
AÑO=2025
```

**Opción 2: Rango personalizado**
```
FECHA_INICIO=2025-12-01
FECHA_FIN=2025-12-15
```

---

## 🚀 Uso

### Flujo de Trabajo Completo

```bash
# 1. Configurar período (una sola vez)
# Editar config_fechas.txt: MES=12, AÑO=2025

# 2. Login AWS (antes de cada ejecución)
aws-azure-login --profile default --mode=gui

# 3. Descargar datos desde Athena
python athena_connector.py

# 4. Calcular métricas
python metricas_boti_AUTO_CONFIG.py
```

---

## 📂 Estructura de Archivos

### Entrada

| Archivo | Descripción | Ubicación |
|---------|-------------|-----------|
| `config_fechas.txt` | Configuración de período | Raíz |
| `Mensajes.sql` | Query de mensajes | `queries/` |
| `Clicks.sql` | Query de clicks | `queries/` |
| `Botones.sql` | Query de botones | `queries/` |
| `testers.csv` | Lista de usuarios testers (opcional) | Raíz |
| `Actualizacion_Lista_Blanca.csv` | Intenciones mostrables (opcional) | Raíz |

### Temporales

| Archivo | Descripción | Tamaño Aprox |
|---------|-------------|--------------|
| `temp/mensajes_temp.csv` | Mensajes del chatbot | 10-15 GB |
| `temp/clicks_temp.csv` | Clicks de usuarios | 5-10 GB |
| `temp/botones_temp.csv` | Interacciones con botones | 1-3 GB |

### Salida

| Archivo | Descripción |
|---------|-------------|
| `metricas_boti_{mes}_{año}.json` | Métricas calculadas |

---

## 📊 Métricas Calculadas

El sistema calcula las siguientes métricas de efectividad:

### Métricas Principales

| Métrica | Descripción | Fórmula |
|---------|-------------|---------|
| **OneShots** | Consultas resueltas directamente | ~65% |
| **Clicks** | Consultas resueltas con clicks | ~13% |
| **Texto** | Consultas resueltas escribiendo | ~5% |
| **Abandonos** | Sesiones abandonadas | ~5% |
| **Nada** | Sin respuesta válida | ~6% |
| **No Entendidos** | Score ≤ 5.36 | ~6% |
| **Letra** | Letra inexistente en WA | ~0.1% |

### Métricas Agregadas

```
Resolución = OneShots + Clicks + Texto
           ≈ 82-85%

Problemas = Abandonos + Letra
          ≈ 5-6%

Métrica Clave = Nada + No Entendidos
              ≈ 11-12%
```

### Archivo JSON de Salida

```json
{
  "periodo": "diciembre 2025",
  "modo": "mes",
  "fecha_inicio": "2025-12-01 00:00:00",
  "fecha_fin": "2026-01-01 00:00:00",
  "metricas": {
    "abandonos": 0.054,
    "click": 0.130,
    "one": 0.651,
    "texto": 0.048,
    "nada": 0.055,
    "letra": 0.001,
    "ne": 0.062
  },
  "timestamp": "2026-01-11T14:30:00"
}
```

---

## 🔍 Detalles Técnicos

### athena_connector.py

**Función:** Descarga datos desde AWS Athena

**Características:**
- ✅ Manejo automático de expiración de tokens
- ✅ Reintentos automáticos en caso de error
- ✅ Detección automática de bucket S3
- ✅ Muestra progreso en tiempo real
- ✅ Genera sesiones frescas de boto3 (sin cache)

**Duración:** 10-20 minutos (dependiendo del tamaño de datos)

**Salida:**
```
temp/mensajes_temp.csv   (10-15 GB)
temp/clicks_temp.csv     (5-10 GB)
temp/botones_temp.csv    (1-3 GB)
```

### metricas_boti_AUTO_CONFIG.py

**Función:** Calcula métricas de efectividad

**Características:**
- ✅ Procesamiento por chunks (optimizado para memoria)
- ✅ PASO 6 optimizado: 60 minutos → 2 segundos
- ✅ Filtrado automático de testers
- ✅ Filtrado de intenciones según lista blanca
- ✅ Generación de JSON con resultados

**Duración:** 20-30 minutos

**Pasos del proceso:**
1. Configuración y lectura de fechas
2. Carga de archivos auxiliares
3. Procesamiento de mensajes (más lento)
4. Procesamiento de clicks
5. Procesamiento de botones
6. Limpieza de mensajes consecutivos (optimizado)
7. Análisis y cálculo de métricas

**Salida:**
```
metricas_boti_diciembre_2025.json
```

---

## ⚠️ Solución de Problemas

### Token AWS Expirado

**Síntoma:**
```
⚠️  TOKEN AWS EXPIRADO
```

**Solución:**
1. Abre **otra terminal**
2. Ejecuta: `aws-azure-login --profile default --mode=gui`
3. Completa el login en el navegador
4. Vuelve a la terminal original
5. Presiona ENTER

El script detectará automáticamente las nuevas credenciales y continuará.

---

### Error de Memoria RAM

**Síntoma:**
```
Unable to allocate X.XX GiB for an array
```

**Causa:** No hay suficiente RAM disponible

**Soluciones:**

**Opción A:** Liberar memoria
```bash
# Cerrar programas pesados:
- Chrome/Edge
- Excel
- Otros programas grandes

# Reiniciar el script
python metricas_boti_AUTO_CONFIG.py
```

**Opción B:** Optimizar el código (contactar a desarrollo)

**Requerimiento mínimo:** 8 GB RAM  
**Recomendado:** 16 GB RAM

---

### Archivos Auxiliares No Encontrados

**Síntoma:**
```
⚠️  Archivo testers.csv no encontrado
⚠️  Archivo Actualizacion_Lista_Blanca.csv no encontrado
```

**Soluciones:**

**Opción A:** Colocar archivos en el directorio raíz
```
Proyecto/
├── testers.csv                    ← AQUÍ
├── Actualizacion_Lista_Blanca.csv ← AQUÍ
└── ...
```

**Opción B:** Continuar sin ellos
- El script funciona sin estos archivos
- Procesará TODOS los usuarios (sin filtrar testers)
- Procesará TODAS las intenciones (sin filtrar)

---

### No Se Encuentra config_fechas.txt

**Síntoma:**
```
[ERROR] No se encuentra el archivo: config_fechas.txt
```

**Solución:**
Crear el archivo en el directorio raíz:

```bash
# Windows
echo MES=12 > config_fechas.txt
echo AÑO=2025 >> config_fechas.txt

# Linux/Mac
cat > config_fechas.txt << EOF
MES=12
AÑO=2025
EOF
```

---

### Queries SQL No Encontradas

**Síntoma:**
```
[ERROR] No se encuentra queries/Mensajes.sql
```

**Solución:**
Verificar que existe el directorio `queries/` con los 3 archivos SQL:
```
queries/
├── Mensajes.sql
├── Clicks.sql
└── Botones.sql
```

---

## 📝 Notas Adicionales

### Frecuencia de Ejecución

Típicamente se ejecuta **mensualmente** para generar reportes del mes anterior.

### Tiempo Total

```
Login AWS:          2-5 min
athena_connector:   10-20 min
metricas_boti:      20-30 min
─────────────────────────────
TOTAL:              30-55 min
```

### Consideraciones de Almacenamiento

- **Temporales:** 15-25 GB (se pueden borrar después)
- **Resultados:** < 1 MB (JSON)

Los archivos en `temp/` se pueden eliminar después de generar las métricas.

---

## 🤝 Contribuciones

Para reportar problemas o sugerir mejoras:

1. Documentar el error con capturas
2. Incluir logs completos
3. Especificar versión de Python y librerías

---

## 📄 Licencia

Uso interno - Gobierno de la Ciudad de Buenos Aires

---

## 👥 Contacto

**Equipo:** Data Analytics - GCBA  
**Proyecto:** Métricas Boti

---

## 🔄 Historial de Versiones

### v2.0 (Enero 2026)
- ✅ Integración automática con config_fechas.txt
- ✅ Manejo robusto de expiración de tokens
- ✅ Optimización PASO 6 (60 min → 2 seg)
- ✅ Búsqueda automática de archivos auxiliares

### v1.0 (Diciembre 2025)
- ✅ Versión inicial con configuración manual
- ✅ Scripts separados sin integración

---

**Última actualización:** 11 de enero de 2026

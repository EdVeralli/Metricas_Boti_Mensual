# 🔄 FLUJO DE TRABAJO - Métricas Boti Mensuales

## 📋 Proceso Completo Paso a Paso

---

## 🎯 CADA MES - Cuando Necesites Calcular Métricas

### ⏱️ Tiempo estimado: 25-30 minutos (mayoría automático)

---

## 📍 PASO 1: Login en AWS (2 minutos)

### Abrir terminal y ejecutar:

```bash
aws-azure-login --profile default --mode=gui
```

### Qué sucede:
- Se abre una ventana del navegador
- Login con tu usuario Azure (GCBA)
- Cuando veas "Success" → Cierra la ventana
- Las credenciales quedan activas por unas horas

### ✅ Verificar que funcionó:

```bash
aws sts get-caller-identity
```

Debe devolver JSON con tu identidad.

### ⚠️ Si algo sale mal:

**Error: "aws-azure-login: command not found"**
```bash
npm install -g aws-azure-login
```

**Error: "Not configured"**
```bash
aws-azure-login --configure --profile default
```

---

## 📍 PASO 2: Configurar Fechas (30 segundos)

### Editar el archivo `config_fechas.txt`

#### Opción A: Mes completo (lo más común)

```txt
MES=11
AÑO=2025
```

Esto calculará del 1 de noviembre al 1 de diciembre.

#### Opción B: Rango personalizado

```txt
FECHA_INICIO=2025-11-01
FECHA_FIN=2025-11-15
```

Esto calculará solo la primera quincena de noviembre.

### Ejemplos:

| Qué quiero | Config |
|------------|--------|
| Noviembre 2025 completo | `MES=11` `AÑO=2025` |
| Octubre 2025 completo | `MES=10` `AÑO=2025` |
| Primera quincena noviembre | `FECHA_INICIO=2025-11-01` `FECHA_FIN=2025-11-15` |
| Solo un día | `FECHA_INICIO=2025-11-15` `FECHA_FIN=2025-11-15` |

### ✅ Verificar:

Abre `config_fechas.txt` y confirma que tiene las fechas correctas.

---

## 📍 PASO 3: Ejecutar Queries de Athena (15-20 minutos automático)

### En la misma terminal:

```bash
python athena_connector.py
```

### Qué sucede:

```
1. Verifica que tengas credenciales AWS activas
2. Lee las fechas de config_fechas.txt
3. Ejecuta query de Mensajes en Athena (2-5 min)
4. Descarga mensajes_temp.csv
5. Ejecuta query de Clicks en Athena (5-10 min)
6. Descarga clicks_temp.csv
7. Ejecuta query de Botones en Athena (1-3 min)
8. Descarga botones_temp.csv
9. ✅ Completo
```

### Salida esperada:

```
================================================================================
  AWS ATHENA - EJECUCIÓN AUTOMÁTICA DE QUERIES
================================================================================

🔐 Verificando credenciales AWS...
✓ Credenciales AWS activas

📄 Leyendo config_fechas.txt...
✓ Modo: Mes completo
  Mes: 11/2025
  Desde: 2025-11-01
  Hasta: 2025-12-01

⚠️  IMPORTANTE:
   Las queries pueden tardar 5-15 minutos
   No interrumpas el proceso

Presiona Enter para continuar...

============================================================
  Mensajes.sql
============================================================
📖 Leyendo query...
📅 Reemplazando fechas...
  ✓ Fechas reemplazadas en query
☁️  Ejecutando en Athena...
  🚀 Iniciando query en Athena...
  📋 Query ID: abc-123-def-456
  ⏳ Ejecutando... (30s)
  ⏳ Ejecutando... (60s)
  ⏳ Ejecutando... (90s)
  ✅ Query exitosa
💾 Descargando resultado...
  📥 Descargando desde S3...
     Bucket: aws-athena-query-results-xxxxx
     Key: abc-123-def-456.csv
  ✅ Descargado: temp/mensajes_temp.csv (45.23 MB)
✅ Completado: temp/mensajes_temp.csv

============================================================
  Clicks.sql
============================================================
[... proceso similar, tarda 5-10 minutos ...]
✅ Completado: temp/clicks_temp.csv

============================================================
  Botones.sql
============================================================
[... proceso similar, tarda 1-3 minutos ...]
✅ Completado: temp/botones_temp.csv

================================================================================
  ✅ TODAS LAS QUERIES EJECUTADAS EXITOSAMENTE
================================================================================

📂 Archivos generados:
   ├─ temp/mensajes_temp.csv
   ├─ temp/clicks_temp.csv
   └─ temp/botones_temp.csv
```

### ⚠️ Si algo sale mal:

**Error: "❌ No hay credenciales AWS activas"**
```bash
# Vuelve al PASO 1
aws-azure-login --profile default --mode=gui
```

**Error: "ExpiredToken"**
```bash
# Las credenciales expiraron durante el proceso
# Vuelve a hacer login y ejecuta de nuevo
aws-azure-login --profile default --mode=gui
python athena_connector.py
```

**Error: "Access Denied"**
- Contacta al administrador de AWS
- Necesitas permisos de Athena y S3

---

## 📍 PASO 4: Procesar Métricas (5-20 minutos)

### En la misma terminal:

```bash
python metricas_boti_noviembre_2025_RAPIDO.py
```

O si tienes otra versión del script:

```bash
python metricas_boti_octubre_2025_RAPIDO.py
```

### Qué sucede:

```
1. Carga testers.csv
2. Carga Actualizacion_Lista_Blanca.csv
3. Procesa temp/mensajes_temp.csv (12 min)
4. Procesa temp/clicks_temp.csv (2-30 min según volumen)
5. Procesa temp/botones_temp.csv (1 min)
6. Limpia datos
7. Analiza y categoriza
8. Calcula porcentajes
9. ✅ Muestra promedios1
```

### Salida esperada (al final):

```
================================================================================
  RESULTADOS - PROMEDIOS1
================================================================================

📅 Período: 2025-11-01 00:00:00 a 2025-12-01 00:00:00
👥 Usuarios: 535

────────────────────────────────────────────────────────────────────────────────
  OneShots............   0.673  ( 67.30%) █████████████████████████████████
  Clicks..............   0.143  ( 14.30%) ███████
  Texto...............   0.038  (  3.80%) █
  Abandonos...........   0.044  (  4.40%) ██
  Nada................   0.050  (  5.00%) ██
  No entendidos.......   0.051  (  5.10%) ██
  Letra...............   0.001  (  0.10%) 
────────────────────────────────────────────────────────────────────────────────

✓ Suma: 1.000 (100.00%)
✅ VALIDACIÓN EXITOSA

  Resolución: 85.40%
  Problemas: 9.50%

================================================================================
✅ COMPLETADO
================================================================================

⏱️ Tiempo: 0:17:23.456789

💾 promedios1 = {
    'abandonos': 0.044,
    'click': 0.143,
    'one': 0.673,
    'texto': 0.038,
    'nada': 0.050,
    'letra': 0.001,
    'ne': 0.051
}

================================================================================
```

### 🎯 Tu Métrica Clave:

```python
nada + ne = 0.050 + 0.051 = 0.101 = 10.1%
```

**Esto es el porcentaje de interacciones problemáticas** (respuestas vacías + no entendidos).

---

## 📍 PASO 5: Guardar Resultados (opcional)

### Copiar promedios1 a Excel/archivo:

```python
# Manual: Copia el diccionario y pégalo donde necesites

# O crea un archivo:
import json
from datetime import datetime

resultado = {
    'fecha': datetime.now().isoformat(),
    'periodo': 'noviembre_2025',
    'usuarios': 535,
    'metricas': promedios1,
    'nada_mas_ne': 0.101
}

with open('resultado_nov2025.json', 'w') as f:
    json.dump(resultado, f, indent=2)
```

---

## 📊 RESUMEN VISUAL

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUJO DE TRABAJO                         │
└─────────────────────────────────────────────────────────────┘

1. Login AWS
   aws-azure-login --profile default --mode=gui
   ↓ (2 min)
   
2. Configurar Fechas
   Editar config_fechas.txt
   ↓ (30 seg)
   
3. Ejecutar Athena
   python athena_connector.py
   ↓ (15-20 min automático)
   
4. Procesar Métricas
   python metricas_boti_noviembre_2025_RAPIDO.py
   ↓ (5-20 min automático)
   
5. ✅ Obtener promedios1
   nada + ne = tu métrica clave
```

---

## 🔄 CALENDARIO MENSUAL SUGERIDO

### Primer día hábil de cada mes:

| Día | Actividad | Tiempo |
|-----|-----------|--------|
| **1 de mes** | Calcular métricas del mes anterior | 30 min |
| | 1. Login AWS | 2 min |
| | 2. Configurar fechas (mes anterior) | 30 seg |
| | 3. Ejecutar athena_connector.py | 20 min |
| | 4. Ejecutar script de métricas | 7 min |
| | 5. Guardar resultados | 30 seg |

### Ejemplo concreto:

| Hoy es | Calcular | Config |
|--------|----------|--------|
| 1 Dic 2025 | Noviembre 2025 | `MES=11` `AÑO=2025` |
| 2 Ene 2026 | Diciembre 2025 | `MES=12` `AÑO=2025` |
| 3 Feb 2026 | Enero 2026 | `MES=1` `AÑO=2026` |

---

## ⚠️ PROBLEMAS COMUNES Y SOLUCIONES

### Problema: "ExpiredToken" durante ejecución

**Causa:** Las credenciales AWS expiraron (duran 1-12 horas)

**Solución:**
```bash
aws-azure-login --profile default --mode=gui
python athena_connector.py  # Ejecuta de nuevo
```

---

### Problema: "Muchos registros mantenidos, puede tardar..."

**Causa:** Ese mes tiene mucha más actividad que otros meses

**Solución:** Es normal, déjalo terminar (puede tardar 30-45 min en lugar de 15-20 min)

---

### Problema: Error en PASO 6 (Limpieza)

**Causa:** El script antiguo tiene un loop lento

**Solución:** Usa la versión RAPIDO que tiene el PASO 6 optimizado

---

### Problema: No hay credenciales al ejecutar athena_connector

**Causa:** No hiciste el PASO 1 (login)

**Solución:**
```bash
aws-azure-login --profile default --mode=gui
```

---

## 📝 CHECKLIST PRE-EJECUCIÓN

Antes de empezar, verifica:

- [ ] ✅ Hice login en AWS hace menos de 1 hora
- [ ] ✅ config_fechas.txt tiene las fechas correctas
- [ ] ✅ Los archivos .sql están en el directorio
- [ ] ✅ testers.csv está presente
- [ ] ✅ Actualizacion_Lista_Blanca.csv está presente
- [ ] ✅ Tengo 30 minutos libres
- [ ] ✅ No voy a apagar la computadora

---

## 🎯 COMANDOS RÁPIDOS (copiar/pegar)

### Flujo completo en 4 comandos:

```bash
# 1. Login
aws-azure-login --profile default --mode=gui

# 2. Configurar fechas (edita el archivo manualmente)
# config_fechas.txt → MES=11, AÑO=2025

# 3. Descargar datos
python athena_connector.py

# 4. Calcular métricas
python metricas_boti_noviembre_2025_RAPIDO.py
```

---

## 💡 TIPS ÚTILES

### Tip 1: Renovar credenciales preventivamente

Si sabes que vas a tardar más de 1 hora:

```bash
# Cada hora, en otra terminal:
aws-azure-login --profile default --mode=gui
```

### Tip 2: Procesar múltiples meses

```bash
# Mes por mes
for mes in 7 8 9 10 11; do
    echo "MES=$mes" > config_fechas.txt
    echo "AÑO=2025" >> config_fechas.txt
    python athena_connector.py
    python metricas_boti_noviembre_2025_RAPIDO.py
done
```

### Tip 3: Verificar estado

```bash
# Ver si hay credenciales activas
aws sts get-caller-identity

# Ver archivos descargados
ls -lh temp/
```

---

## 📞 ¿NECESITAS AYUDA?

### Si algo no funciona:

1. **Lee el mensaje de error completo**
2. **Busca el error en este documento**
3. **Si dice "ExpiredToken" → Vuelve a hacer login**
4. **Si dice "Access Denied" → Contacta al admin de AWS**
5. **Para otros errores → Revisa GUIA_AZURE_SSO.md**

---

## ✅ FIN DEL PROCESO

Cuando veas:

```
💾 promedios1 = {...}
```

**¡Ya terminaste!** Tienes las métricas del mes. 🎉

---

**Fecha de última actualización:** 30 Diciembre 2025  
**Versión:** 1.0 - Con Azure SSO

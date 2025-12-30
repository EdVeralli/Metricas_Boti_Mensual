# ⚡ INICIO RÁPIDO - athena_connector.py

## ✅ Configuración Simplificada (Sin Bucket Manual)

Ya que usas **aws-azure-login**, el bucket de Athena se configura **automáticamente** desde tu perfil. No necesitas editar nada en el código.

---

## 🚀 Uso (3 Pasos)

### 1. Login en AWS
```bash
aws-azure-login --profile default --mode=gui
```

### 2. Configurar Fechas
Edita `config_fechas.txt`:
```txt
MES=11
AÑO=2025
```

### 3. Ejecutar
```bash
python athena_connector.py
```

**¡Eso es todo!** El script:
- ✅ Verifica credenciales
- ✅ Lee fechas del archivo
- ✅ Ejecuta las 3 queries
- ✅ Usa el bucket de tu perfil automáticamente
- ✅ Descarga los CSVs a `temp/`

---

## ⏱️ Tiempo Estimado

| Query | Tiempo |
|-------|--------|
| Mensajes | 2-5 min |
| Clicks | 5-10 min |
| Botones | 1-3 min |
| **Total** | **10-20 min** |

---

## 📋 Ejemplo de Salida

```bash
$ python athena_connector.py

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

✓ Carpeta 'temp/' creada

⚠️  IMPORTANTE:
   Las queries en Athena pueden tardar 5-15 minutos
   Escanean millones de registros
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
  📋 Query ID: 1a2b3c4d-5e6f-7g8h
  ⏳ Ejecutando... (30s)
  ⏳ Ejecutando... (60s)
  ✅ Query exitosa
💾 Descargando resultado...
  📥 Descargando desde S3...
     Bucket: aws-athena-query-results-xxxxx
     Key: 1a2b3c4d-5e6f-7g8h.csv
  ✅ Descargado: temp/mensajes_temp.csv (52.34 MB)
✅ Completado: temp/mensajes_temp.csv

[... Clicks ...]
[... Botones ...]

================================================================================
  ✅ TODAS LAS QUERIES EJECUTADAS EXITOSAMENTE
================================================================================

📂 Archivos generados:
   ├─ temp/mensajes_temp.csv
   ├─ temp/clicks_temp.csv
   └─ temp/botones_temp.csv
```

---

## 🔍 Verificar Credenciales

### Antes de ejecutar, verifica que tengas credenciales:

```bash
aws sts get-caller-identity
```

Si devuelve tu identidad (JSON) → ✅ Listo  
Si da error → Ejecuta `aws-azure-login --profile default --mode=gui`

---

## ⚠️ Si Algo Sale Mal

### Error: "No hay credenciales AWS activas"

**Solución:**
```bash
aws-azure-login --profile default --mode=gui
```

### Error: "ExpiredToken"

**Causa:** Credenciales expiraron (duran 1-12 horas)

**Solución:**
```bash
aws-azure-login --profile default --mode=gui
python athena_connector.py  # Ejecutar de nuevo
```

### Error: "Access Denied"

**Causa:** Tu usuario no tiene permisos de Athena/S3

**Solución:** Contacta al administrador de AWS

---

## 📁 Estructura de Archivos

```
📁 Tu directorio/
├── 📄 athena_connector.py          ← El módulo
├── 📄 config_fechas.txt             ← Configurar fechas aquí
├── 📄 Mensajes.sql                  ← Query de mensajes
├── 📄 Clicks.sql                    ← Query de clicks
├── 📄 Botones.sql                   ← Query de botones
│
├── 📄 testers.csv                   ← Para el script de métricas
├── 📄 Actualizacion_Lista_Blanca.csv
│
└── 📁 temp/                         ← CSVs descargados (se crea auto)
    ├── mensajes_temp.csv
    ├── clicks_temp.csv
    └── botones_temp.csv
```

---

## 🎯 Siguiente Paso

Después de ejecutar `athena_connector.py`, procesa las métricas:

```bash
python metricas_boti_OPTIMIZADO.py
```

O el script que uses normalmente.

---

## 💡 Tip: Flujo Completo en 4 Comandos

```bash
# 1. Login
aws-azure-login --profile default --mode=gui

# 2. (Edita config_fechas.txt con tus fechas)

# 3. Descargar datos
python athena_connector.py

# 4. Calcular métricas
python metricas_boti_OPTIMIZADO.py
```

**Tiempo total:** ~25-30 minutos

---

## ❓ FAQ

### ¿Necesito configurar el bucket S3?

**No.** El bucket se obtiene automáticamente de tu perfil AWS (aws-azure-login).

### ¿Puedo cambiar la región?

**Sí.** Edita la línea 18 de `athena_connector.py`:
```python
ATHENA_REGION = 'us-east-1'  # Cambiar aquí
```

### ¿Puedo cambiar la base de datos?

**Sí.** Edita la línea 17 de `athena_connector.py`:
```python
ATHENA_DATABASE = 'caba-piba-consume-zone-db'  # Cambiar aquí
```

### ¿Cuánto duran las credenciales?

Entre 1-12 horas dependiendo de tu configuración Azure. Si expiran, simplemente vuelve a hacer login.

### ¿Puedo ejecutar queries personalizadas?

**Sí.** El módulo ejecuta cualquier archivo `.sql`. Solo asegúrate de que tenga dos fechas en formato `'YYYY-MM-DD HH:MM:SS'` que el script pueda reemplazar.

---

**¿Listo?** Solo 3 pasos: Login → Configurar fechas → Ejecutar 🚀

# ⚡ Guía Rápida - Métricas Boti

## 🚀 Ejecución Mensual (3 Pasos)

### 1️⃣ Configurar Mes
```bash
# Editar config_fechas.txt
MES=12
AÑO=2025
```

### 2️⃣ Login AWS
```bash
aws-azure-login --profile default --mode=gui
```

### 3️⃣ Ejecutar Scripts
```bash
# Paso A: Descargar datos
python athena_connector.py

# Paso B: Calcular métricas
python metricas_boti_AUTO_CONFIG.py
```

---

## 📊 Resultado

```
metricas_boti_diciembre_2025.json
```

Contiene:
- OneShots: ~65%
- Clicks: ~13%
- Texto: ~5%
- Resolución: ~83%
- Nada + NE: ~12% (métrica clave)

---

## ⚠️ Problemas Comunes

### Token Expirado
```
⚠️  TOKEN AWS EXPIRADO
```
**Solución:** Renovar en otra terminal → presionar ENTER

### Sin Memoria
```
Unable to allocate X.XX GiB
```
**Solución:** Cerrar Chrome/Excel → reintentar

### Tarda Mucho
**Normal:** 30-55 minutos total  
**Mensajes:** 10-20 min  
**Clicks:** 5-10 min  
**Análisis:** 5-10 min

---

## 📁 Archivos Requeridos

```
✅ config_fechas.txt         (configuración)
✅ queries/Mensajes.sql      (SQL)
✅ queries/Clicks.sql        (SQL)
✅ queries/Botones.sql       (SQL)
⚠️  testers.csv              (opcional)
⚠️  Actualizacion_Lista_Blanca.csv (opcional)
```

---

## 🔧 Primera Vez (Setup)

```bash
# 1. Instalar dependencias
pip install boto3 awswrangler pandas numpy openpyxl

# 2. Configurar AWS
aws-azure-login --configure --profile default

# 3. Crear estructura
mkdir queries temp
```

---

## 💡 Tips

- ✅ Ejecutar a primera hora (menos carga en AWS)
- ✅ Cerrar programas pesados antes de ejecutar
- ✅ No interrumpir el proceso
- ✅ Los CSVs en temp/ se pueden borrar después

---

**README completo:** Ver `README.md`

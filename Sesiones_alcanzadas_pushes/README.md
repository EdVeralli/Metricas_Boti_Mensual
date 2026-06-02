# Sesiones Alcanzadas por Pushes

Script automatizado para generar reportes de sesiones que recibieron mensajes push del chatbot del Gobierno de la Ciudad de Buenos Aires (GCBA). Soporta consultas de **meses completos** y **rangos de fechas personalizados**.

## 📋 Descripción

Este proyecto consulta las métricas de sesiones que recibieron al menos un mensaje push a través de AWS Athena, procesando datos de la tabla `boti_message_metrics_2`. Genera automáticamente reportes en formato CSV y Excel con la estructura de dashboard requerida por GCBA.

## ✨ Características

- ✅ **Dos modos de consulta:** Mes completo o rango personalizado de fechas
- ✅ Consulta automática a AWS Athena con filtrado de mensajes Template
- ✅ Generación de reportes en CSV y Excel
- ✅ Dashboard Excel con estructura predefinida del GCBA
- ✅ Configuración flexible mediante archivo de texto
- ✅ Validación de credenciales y permisos AWS
- ✅ Manejo robusto de errores con mensajes descriptivos

## 🔧 Requisitos Previos

### Software Necesario

- **Python 3.7+**
- **AWS CLI** configurado
- **aws-azure-login** para autenticación con Azure AD

### Librerías Python

```bash
pip install boto3 awswrangler pandas openpyxl
```

### Permisos AWS

- **Rol requerido:** `PIBADataScientist`
- **Workgroup:** `Production-caba-piba-athena-boti-group`
- **Base de datos:** `caba-piba-consume-zone-db`
- **Región:** `us-east-1`

## 🚀 Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/EdVeralli/Sesiones_alcanzadas_pushes
   cd Sesiones_alcanzadas_pushes
   ```

2. **Instalar dependencias:**
   ```bash
   pip install boto3 awswrangler pandas openpyxl
   ```

3. **Configurar AWS:**
   ```bash
   aws-azure-login --configure --profile default
   ```

## 📝 Configuración

El script se configura mediante el archivo `config_fechas.txt` y soporta dos modos:

### Modo 1: Mes Completo
```ini
MES=10
AÑO=2025
```
→ Consulta del 1 al 31 de octubre 2025

### Modo 2: Rango Personalizado
```ini
FECHA_INICIO=2025-10-01
FECHA_FIN=2025-10-15
```
→ Consulta del 1 al 15 de octubre 2025

**Reglas:**
- Formato de fecha: `YYYY-MM-DD` (ej: 2025-10-15)
- Si ambos modos están configurados, se usa el rango personalizado
- El mes debe estar entre 1 y 12
- FECHA_INICIO debe ser ≤ FECHA_FIN

## 🎯 Uso

### 1. Autenticarse en AWS

```bash
aws-azure-login --profile default --mode=gui
```

⚠️ **Importante:** Seleccionar el rol `PIBADataScientist` durante la autenticación.

### 2. Configurar el período

Editar `config_fechas.txt` según el modo deseado (ver sección Configuración arriba).

### 3. Ejecutar el script

```bash
python Sesiones_Alcanzadas.py
```

El script mostrará claramente qué modo está usando y el período configurado.

## 📊 Salida

El script genera dos archivos en la carpeta `output/`:

### Nombres de Archivo

**Modo mes completo:**
- `sesiones_alcanzadas_octubre_2025.csv`
- `sesiones_alcanzadas_octubre_2025.xlsx` (Header: `oct-25`)

**Modo rango personalizado:**
- `sesiones_alcanzadas_20251001_a_20251015.csv`
- `sesiones_alcanzadas_20251001_a_20251015.xlsx` (Header: `01/10-15/10/25`)

### Estructura del Dashboard Excel

| Columna B | Columna C | Columna D |
|-----------|-----------|-----------|
| **Indicador** | **Descripción/Detalle** | **[período]** |
| Conversaciones | Q Conversaciones | - |
| Usuarios | Q Usuarios únicos | - |
| Sesiones abiertas por Pushes | Q Sesiones que se abrieron con una Push | - |
| **Sesiones Alcanzadas por Pushes** | Q Sesiones que recibieron al menos 1 Push | **[VALOR]** |
| Mensajes Pushes Enviados | Q de mensajes enviados bajo el formato push | - |
| ... | ... | - |

> **Nota:** Solo la celda D5 (Sesiones Alcanzadas por Pushes) se completa automáticamente. Las demás métricas deben llenarse con otros scripts o manualmente.

## 🔍 Query Ejecutada

El script ejecuta la siguiente consulta SQL en Athena:

```sql
SELECT count(distinct session_id) as count_sessions
FROM "caba-piba-consume-zone-db"."boti_message_metrics_2" 
WHERE CAST(creation_time AS DATE) BETWEEN date '[fecha_inicio]' and date '[fecha_fin]'
AND regexp_like(message, '^Template')
```

**Parámetros dinámicos:**
- `fecha_inicio`: Fecha de inicio del período
- `fecha_fin`: Fecha de fin del período

**¿Qué mide?**
- Cuenta las **sesiones únicas** que recibieron al menos un mensaje con formato Template
- Un mensaje Template indica que se envió una notificación push a esa sesión

## 💡 Casos de Uso

### Reportes Mensuales
```ini
MES=10
AÑO=2025
```
Reportes mensuales tradicionales de sesiones alcanzadas por push.

### Reportes Quincenales
```ini
FECHA_INICIO=2025-10-01
FECHA_FIN=2025-10-15
```
Primera o segunda quincena del mes.

### Análisis de Campañas
```ini
FECHA_INICIO=2025-10-05
FECHA_FIN=2025-10-20
```
Medir alcance de campañas de push específicas.

### Comparación Semanal
```ini
FECHA_INICIO=2025-10-01
FECHA_FIN=2025-10-07
```
Seguimiento semanal de sesiones alcanzadas.

### Análisis de Día Específico
```ini
FECHA_INICIO=2025-10-15
FECHA_FIN=2025-10-15
```
Análisis de un día particular.

## 🛠️ Troubleshooting

### Error: Credenciales expiradas

```
[ERROR] ExpiredToken
```

**Solución:**
```bash
aws-azure-login --profile default --mode=gui
```

### Error: Rol incorrecto

```
[ADVERTENCIA] No estas usando el rol correcto
```

**Solución:** Verificar que se seleccionó `PIBADataScientist` durante la autenticación.

### Error: Formato de fecha inválido

```
[ERROR] Formato de fecha invalido. Use YYYY-MM-DD
```

**Solución:** Usar el formato correcto:
```ini
FECHA_INICIO=2025-10-01  # ✅ Correcto
# FECHA_INICIO=01-10-2025  # ❌ Incorrecto
```

### Error: Tabla no encontrada

**Solución:** Verificar permisos sobre la tabla `boti_message_metrics_2`.

## 📁 Estructura del Proyecto

```
Sesiones_alcanzadas_pushes/
│
├── Sesiones_Alcanzadas.py          # Script principal
├── config_fechas.txt                # Configuración de fechas
├── README.md                        # Esta documentación
│
└── output/                          # Carpeta de salida (se crea automáticamente)
    ├── sesiones_alcanzadas_octubre_2025.csv
    ├── sesiones_alcanzadas_octubre_2025.xlsx
    ├── sesiones_alcanzadas_20251001_a_20251015.csv
    └── sesiones_alcanzadas_20251001_a_20251015.xlsx
```

## 🔐 Seguridad

- Las credenciales AWS se manejan mediante `aws-azure-login`
- No se almacenan credenciales en el código
- Se requiere autenticación mediante Azure AD
- Solo usuarios con rol `PIBADataScientist` pueden ejecutar el script

## 🔄 Workflow Típico

```bash
# 1. Autenticarse
aws-azure-login --profile default --mode=gui

# 2. Configurar período (editar config_fechas.txt)

# 3. Ejecutar
python Sesiones_Alcanzadas.py

# 4. Verificar archivos en output/
ls output/

# 5. Para otro período, repetir desde el paso 2
```

## 🆘 Validaciones Automáticas

El script valida automáticamente:

- ✅ Formato de fechas (YYYY-MM-DD)
- ✅ Mes entre 1 y 12
- ✅ Año razonable (2020-2030)
- ✅ FECHA_INICIO ≤ FECHA_FIN
- ✅ Existencia de configuración válida
- ✅ Credenciales AWS válidas
- ✅ Rol correcto (PIBADataScientist)

## 📊 Relación con Otros Proyectos

Este script forma parte del dashboard de métricas de push del GCBA:

| Proyecto | Celda | Métrica |
|----------|-------|---------|
| [Sesiones Abiertas](https://github.com/EdVeralli/Sesiones_Abiertas_Pushes) | D4 | Sesiones iniciadas por push |
| **Sesiones Alcanzadas** (este) | **D5** | **Sesiones que recibieron push** |
| [Pushes Enviadas](https://github.com/EdVeralli/Pushes_Enviadas) | D6 | Mensajes push enviados |

**Diferencias:**
- **D4 (Abiertas):** Sesiones donde el usuario **abrió** el chatbot desde una push
- **D5 (Alcanzadas):** Sesiones que **recibieron** al menos una push (más amplio)
- **D6 (Enviadas):** Cantidad total de mensajes push enviados

**Ejemplo:**
- Se enviaron 1,000 mensajes (D6)
- Alcanzaron 400 sesiones (D5)
- Se abrieron 300 sesiones (D4)

## 🤝 Contribuciones

Este es un proyecto interno del GCBA. Para contribuir:

1. Fork el proyecto
2. Crear una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abrir un Pull Request

## 👤 Autor

**Eduardo Veralli**
- GitHub: [@EdVeralli](https://github.com/EdVeralli)

## 📄 Licencia

Proyecto del Gobierno de la Ciudad de Buenos Aires (GCBA).

## 📞 Soporte

Para problemas o consultas:
- [Abrir un issue en GitHub](https://github.com/EdVeralli/Sesiones_alcanzadas_pushes/issues)
- Contactar al equipo de Data Analytics GCBA

## 📊 Información Técnica

### Versión

**Versión:** 2.0  
**Última actualización:** Noviembre 2025

### Cambios Principales V2.0

- ✅ Soporte para rangos de fechas personalizados
- ✅ Detección automática del modo de operación
- ✅ Query adaptada para usar BETWEEN con fechas en lugar de year/month
- ✅ Nombres de archivo adaptativos según el modo
- ✅ Headers de Excel dinámicos
- ✅ 100% compatible con configuraciones V1.0

### Configuración AWS

- **Región:** `us-east-1`
- **Workgroup:** `Production-caba-piba-athena-boti-group`
- **Database:** `caba-piba-consume-zone-db`
- **Rol requerido:** `PIBADataScientist`
- **Tabla:** `boti_message_metrics_2`

### Dependencias

```
boto3>=1.26.0         # Cliente AWS
awswrangler>=3.0.0    # Integración Pandas-Athena
pandas>=1.5.0         # Procesamiento de datos
openpyxl>=3.0.0       # Generación de Excel
```

---

**Gobierno de la Ciudad de Buenos Aires - Área de Data Analytics**

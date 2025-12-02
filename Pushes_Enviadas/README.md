# Pushes Enviadas

Script automatizado para generar reportes de mensajes push enviados por el chatbot del Gobierno de la Ciudad de Buenos Aires (GCBA). Soporta consultas de **meses completos** y **rangos de fechas personalizados**.

## Descripción

Este proyecto consulta las métricas de mensajes push enviados a través de AWS Athena, procesando datos de las tablas `boti_event_metrics_2` y `boti_message_metrics_2`. Genera automáticamente reportes en formato CSV y Excel con la estructura de dashboard requerida por GCBA.

## Características

- ✅ **Dos modos de consulta:** Mes completo o rango personalizado de fechas
- ✅ Consulta automática a AWS Athena con filtrado flexible
- ✅ Generación de reportes en CSV y Excel
- ✅ Dashboard Excel con estructura predefinida del GCBA
- ✅ Configuración flexible mediante archivo de texto
- ✅ Validación de credenciales y permisos AWS
- ✅ Manejo robusto de errores con mensajes descriptivos
- ✅ Generación automática de nombres de archivo descriptivos

## Requisitos Previos

### Software Necesario

- **Python 3.7+**
- **AWS CLI** configurado
- **aws-azure-login** para autenticación con Azure AD

### Librerías Python

```bash
pip install boto3 awswrangler pandas openpyxl
```

O usando el archivo de requisitos:

```bash
pip install -r requirements.txt
```

### Permisos AWS

- **Rol requerido:** `PIBAConsumeBoti`
- **Workgroup:** `Production-caba-piba-athena-boti-group`
- **Base de datos:** `caba-piba-consume-zone-db`
- **Región:** `us-east-1`

## Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/EdVeralli/Pushes_Enviadas
   cd Pushes_Enviadas
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar AWS:**
   ```bash
   aws-azure-login --configure --profile default
   ```

## Configuración

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

## Uso

### 1. Autenticarse en AWS

```bash
aws-azure-login --profile default --mode=gui
```

⚠️ **Importante:** Seleccionar el rol `PIBAConsumeBoti` durante la autenticación.

### 2. Configurar el período

Editar `config_fechas.txt` según el modo deseado (ver sección Configuración arriba).

### 3. Ejecutar el script

```bash
python Pushes_Enviadas.py
```

El script mostrará claramente qué modo está usando y el período configurado.

## Salida

El script genera dos archivos en la carpeta `output/`:

### Nombres de Archivo

**Modo mes completo:**
- `mensajes_pushes_enviados_octubre_2025.csv`
- `mensajes_pushes_enviados_octubre_2025.xlsx` (Header: `oct-25`)

**Modo rango personalizado:**
- `mensajes_pushes_enviados_20251001_a_20251015.csv`
- `mensajes_pushes_enviados_20251001_a_20251015.xlsx` (Header: `01/10-15/10/25`)

### Estructura del Dashboard Excel

| Columna B | Columna C | Columna D |
|-----------|-----------|-----------|
| **Indicador** | **Descripción/Detalle** | **[período]** |
| Conversaciones | Q Conversaciones | - |
| Usuarios | Q Usuarios únicos | - |
| Sesiones abiertas por Pushes | Q Sesiones que se abrieron con una Push | - |
| Sesiones Alcanzadas por Pushes | Q Sesiones que recibieron al menos 1 Push | - |
| **Mensajes Pushes Enviados** | Q de mensajes enviados bajo el formato push | **[VALOR]** |
| Contenidos en Botmaker | Contenidos prendidos en botmaker | - |
| Contenidos Prendidos para el USUARIO | Contenidos prendidos de cara al usuario | - |
| Interacciones | Q Interacciones | - |
| Trámites, solicitudes y turnos | Q Trámites, solicitudes y turnos disponibles | - |
| Contenidos mas consultados | Q Contenidos con más interacciones (Top 10) | - |
| Derivaciones | Q Derivaciones | - |
| No entendimiento | Performance motor de búsqueda del nuevo modelo de IA | - |
| Tasa de Efectividad | Transacciones realizadas sobre derivaciones | - |

> **Nota:** Solo la celda D6 (Mensajes Pushes Enviados) se completa automáticamente. Las demás métricas deben llenarse con otros scripts o manualmente.

## Query Ejecutada

El script ejecuta la siguiente consulta SQL en Athena:

```sql
SELECT count(distinct m.id) as count_messages
FROM "caba-piba-consume-zone-db"."boti_event_metrics_2" ev 
JOIN "caba-piba-consume-zone-db"."boti_message_metrics_2" m 
ON ev.session_id=m.session_id 
WHERE CAST(ev.creation_time AS DATE) BETWEEN date '[fecha_inicio]' and date '[fecha_fin]'  
AND regexp_like(m.message, '^Template') 
AND events_name in ('notification-status-sent')
```

**Parámetros dinámicos:**
- `fecha_inicio`: Fecha de inicio del período
- `fecha_fin`: Fecha de fin del período

## Casos de Uso

### Reportes Mensuales
```ini
MES=10
AÑO=2025
```
Reportes mensuales tradicionales (del 1 al 31).

### Reportes Quincenales
```ini
FECHA_INICIO=2025-10-01
FECHA_FIN=2025-10-15
```
Primera o segunda quincena del mes.

### Reportes Semanales
```ini
FECHA_INICIO=2025-10-01
FECHA_FIN=2025-10-07
```
Seguimiento semanal de métricas.

### Análisis de Campañas
```ini
FECHA_INICIO=2025-10-05
FECHA_FIN=2025-10-20
```
Medir impacto de campañas específicas.

### Trimestres
```ini
FECHA_INICIO=2025-10-01
FECHA_FIN=2025-12-31
```
Reportes trimestrales (Q4).

### Un Solo Día
```ini
FECHA_INICIO=2025-10-15
FECHA_FIN=2025-10-15
```
Análisis de días críticos o eventos puntuales.

## Troubleshooting

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

**Solución:** Verificar que se seleccionó `PIBAConsumeBoti` durante la autenticación y volver a autenticarse.

### Error: Formato de fecha inválido

```
[ERROR] Formato de fecha invalido. Use YYYY-MM-DD
```

**Solución:** Usar el formato correcto en `config_fechas.txt`:
```ini
FECHA_INICIO=2025-10-01  # ✅ Correcto
# FECHA_INICIO=01-10-2025  # ❌ Incorrecto
# FECHA_INICIO=10/01/2025  # ❌ Incorrecto
```

### Error: Fecha inicio posterior a fecha fin

```
[ERROR] FECHA_INICIO no puede ser posterior a FECHA_FIN
```

**Solución:** Verificar el orden de las fechas:
```ini
FECHA_INICIO=2025-10-01  # ✅ Correcto (antes)
FECHA_FIN=2025-10-15     # ✅ Correcto (después)
```

### Error: Workgroup no encontrado

El script intentará ejecutar sin especificar workgroup automáticamente.

### Error: Tabla no encontrada

```
[!] La tabla no existe o no tienes permisos
```

**Solución:** Verificar permisos sobre las tablas:
- `boti_event_metrics_2`
- `boti_message_metrics_2`

### Error: openpyxl no instalado

```
[!] Falta libreria openpyxl
```

**Solución:**
```bash
pip install openpyxl
```

### Query muy lenta

El JOIN entre tablas puede tardar varios minutos. Esto es normal para grandes volúmenes de datos.

## Estructura del Proyecto

```
Pushes_Enviadas/
│
├── Pushes_Enviadas.py       # Script principal
├── config_fechas.txt         # Configuración de fechas
├── requirements.txt          # Dependencias Python
├── README.md                 # Esta documentación
│
└── output/                   # Carpeta de salida (se crea automáticamente)
    ├── mensajes_pushes_enviados_octubre_2025.csv
    ├── mensajes_pushes_enviados_octubre_2025.xlsx
    ├── mensajes_pushes_enviados_20251001_a_20251015.csv
    └── mensajes_pushes_enviados_20251001_a_20251015.xlsx
```

## Seguridad

- Las credenciales AWS se manejan mediante `aws-azure-login`
- No se almacenan credenciales en el código
- Se requiere autenticación mediante Azure AD
- Solo usuarios con rol `PIBAConsumeBoti` pueden ejecutar el script

## Workflow Típico

```bash
# 1. Autenticarse
aws-azure-login --profile default --mode=gui

# 2. Configurar período (editar config_fechas.txt)

# 3. Ejecutar
python Pushes_Enviadas.py

# 4. Verificar archivos en output/
ls output/

# 5. Para otro período, repetir desde el paso 2
```

## Validaciones Automáticas

El script valida automáticamente:

- ✅ Formato de fechas (YYYY-MM-DD)
- ✅ Mes entre 1 y 12
- ✅ Año razonable (2020-2030)
- ✅ FECHA_INICIO ≤ FECHA_FIN
- ✅ Existencia de configuración válida
- ✅ Credenciales AWS válidas
- ✅ Rol correcto (PIBAConsumeBoti)

## Contribuciones

Este es un proyecto interno del GCBA. Para contribuir:

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Autor

**Eduardo Veralli**
- GitHub: [@EdVeralli](https://github.com/EdVeralli)

## Licencia

Proyecto del Gobierno de la Ciudad de Buenos Aires (GCBA).

## Soporte

Para problemas o consultas:
- [Abrir un issue en GitHub](https://github.com/EdVeralli/Pushes_Enviadas/issues)
- Contactar al equipo de Data Analytics GCBA

## Información Técnica

### Versión

**Versión:** 2.0  
**Última actualización:** Noviembre 2025

### Cambios Principales V2.0

- ✅ Soporte para rangos de fechas personalizados
- ✅ Detección automática del modo de operación
- ✅ Nombres de archivo adaptativos según el modo
- ✅ Headers de Excel dinámicos
- ✅ 100% compatible con configuraciones V1.0

### Configuración AWS

- **Región:** `us-east-1`
- **Workgroup:** `Production-caba-piba-athena-boti-group`
- **Database:** `caba-piba-consume-zone-db`
- **Rol requerido:** `PIBAConsumeBoti`

### Dependencias

```
boto3>=1.26.0         # Cliente AWS
awswrangler>=3.0.0    # Integración Pandas-Athena
pandas>=1.5.0         # Procesamiento de datos
openpyxl>=3.0.0       # Generación de Excel
```

---

**Gobierno de la Ciudad de Buenos Aires - Área de Data Analytics**

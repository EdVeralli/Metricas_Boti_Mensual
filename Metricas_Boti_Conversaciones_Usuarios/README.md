# Usuarios y Conversaciones

Script automatizado para generar reportes de usuarios únicos y conversaciones del chatbot del Gobierno de la Ciudad de Buenos Aires (GCBA). Soporta consultas de **meses completos** y **rangos de fechas personalizados**.

## Descripción

Este proyecto consulta las métricas de usuarios y conversaciones a través de AWS Athena, procesando datos de la tabla `boti_session_metrics_2`. Genera automáticamente reportes en formato CSV y Excel con la estructura de dashboard requerida por GCBA.

## Características

- ✅ **Dos modos de consulta:** Mes completo o rango personalizado de fechas
- ✅ Consulta automática a AWS Athena
- ✅ Generación de reportes en CSV y Excel
- ✅ Dashboard Excel con estructura predefinida del GCBA
- ✅ Configuración flexible mediante archivo de texto
- ✅ Validación de credenciales y permisos AWS
- ✅ Calcula usuarios únicos usando SUBSTR(session_id, 1, 20)
- ✅ Cuenta conversaciones (sesiones distintas)

## Requisitos Previos

### Software Necesario

- **Python 3.7+**
- **AWS CLI** configurado
- **aws-azure-login** para autenticación con Azure AD

### Librerías Python

```bash
pip install boto3 awswrangler pandas openpyxl
```

### Permisos AWS

- **Rol requerido:** `PIBAConsumeBoti`
- **Workgroup:** `Production-caba-piba-athena-boti-group`
- **Base de datos:** `caba-piba-consume-zone-db`
- **Región:** `us-east-1`

## Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/EdVeralli/Metricas_Boti_Conversaciones_Usuarios
   cd Metricas_Boti_Conversaciones_Usuarios
   ```

2. **Instalar dependencias:**
   ```bash
   pip install boto3 awswrangler pandas openpyxl
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

Editar `config_fechas.txt` según el modo deseado.

### 3. Ejecutar el script

```bash
python Usuarios_Conversaciones.py
```

## Salida

El script genera dos archivos en la carpeta `output/`:

### Nombres de Archivo

**Modo mes completo:**
- `usuarios_conversaciones_octubre_2025.csv`
- `usuarios_conversaciones_octubre_2025.xlsx` (Header: `oct-25`)

**Modo rango personalizado:**
- `usuarios_conversaciones_20251001_a_20251015.csv`
- `usuarios_conversaciones_20251001_a_20251015.xlsx` (Header: `01/10-15/10/25`)

### Estructura del Dashboard Excel

| Columna B | Columna C | Columna D |
|-----------|-----------|-----------|
| **Indicador** | **Descripción/Detalle** | **[período]** |
| **Conversaciones** | Q Conversaciones | **[VALOR D2]** |
| **Usuarios** | Q Usuarios únicos | **[VALOR D3]** |
| Sesiones abiertas por Pushes | Q Sesiones que se abrieron con una Push | - |
| Sesiones Alcanzadas por Pushes | Q Sesiones que recibieron al menos 1 Push | - |
| Mensajes Pushes Enviados | Q de mensajes enviados bajo el formato push | - |
| ... | ... | - |

> **Nota:** Este script llena las celdas D2 (Conversaciones) y D3 (Usuarios). Las demás métricas deben llenarse con otros scripts.

## Query Ejecutada

El script ejecuta la siguiente consulta SQL en Athena:

```sql
SELECT 
count(distinct SUBSTR(session_id, 1, 20)) as Cant_Usuario, 
count(distinct(session_id)) as Cant_Sesiones 
FROM "caba-piba-consume-zone-db"."boti_session_metrics_2" 
WHERE CAST(session_creation_time AS DATE) BETWEEN date '[fecha_inicio]' and date '[fecha_fin]'
```

**Parámetros dinámicos:**
- `fecha_inicio`: Fecha de inicio del período
- `fecha_fin`: Fecha de fin del período

**¿Qué mide?**
- **Cant_Usuario (D3):** Usuarios únicos, calculado con `SUBSTR(session_id, 1, 20)`
- **Cant_Sesiones (D2):** Conversaciones totales (sesiones distintas)

## Casos de Uso

### Reportes Mensuales
```ini
MES=10
AÑO=2025
```
Reportes mensuales tradicionales.

### Reportes Quincenales
```ini
FECHA_INICIO=2025-10-01
FECHA_FIN=2025-10-15
```
Primera o segunda quincena.

### Análisis Semanal
```ini
FECHA_INICIO=2025-10-01
FECHA_FIN=2025-10-07
```
Seguimiento semanal de usuarios y conversaciones.

### Análisis de Campañas
```ini
FECHA_INICIO=2025-10-05
FECHA_FIN=2025-10-20
```
Medir impacto en usuarios y conversaciones.

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

**Solución:** Verificar que se seleccionó `PIBAConsumeBoti` durante la autenticación.

### Error: Formato de fecha inválido

**Solución:** Usar formato `YYYY-MM-DD`:
```ini
FECHA_INICIO=2025-10-01  # ✅ Correcto
```

### Error: Tabla no encontrada

**Solución:** Verificar permisos sobre la tabla `boti_session_metrics_2`.

## Estructura del Proyecto

```
Metricas_Boti_Conversaciones_Usuarios/
│
├── Usuarios_Conversaciones.py   # Script principal
├── config_fechas.txt             # Configuración de fechas
├── README.md                     # Esta documentación
│
└── output/                       # Carpeta de salida
    ├── usuarios_conversaciones_octubre_2025.csv
    └── usuarios_conversaciones_octubre_2025.xlsx
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
python Usuarios_Conversaciones.py

# 4. Verificar archivos en output/
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

## Relación con Otros Proyectos

Este script forma parte del dashboard de métricas del GCBA:

| Proyecto | Celda | Métrica |
|----------|-------|---------|
| **Usuarios y Conversaciones** (este) | **D2, D3** | **Conversaciones y Usuarios** |
| Sesiones Abiertas | D4 | Sesiones iniciadas por push |
| Sesiones Alcanzadas | D5 | Sesiones que recibieron push |
| Pushes Enviadas | D6 | Mensajes push enviados |

## Información Técnica

### Versión

**Versión:** 1.0  
**Última actualización:** Noviembre 2025

### Configuración AWS

- **Región:** `us-east-1`
- **Workgroup:** `Production-caba-piba-athena-boti-group`
- **Database:** `caba-piba-consume-zone-db`
- **Rol requerido:** `PIBAConsumeBoti`
- **Tabla:** `boti_session_metrics_2`

### Dependencias

```
boto3>=1.26.0         # Cliente AWS
awswrangler>=3.0.0    # Integración Pandas-Athena
pandas>=1.5.0         # Procesamiento de datos
openpyxl>=3.0.0       # Generación de Excel
```

### Diferencia entre Usuarios y Conversaciones

- **Usuarios (D3):** Se calcula con `SUBSTR(session_id, 1, 20)` para obtener el identificador único del usuario
- **Conversaciones (D2):** Son las sesiones totales (`count(distinct session_id)`)

**Ejemplo:**
- Un usuario puede tener múltiples conversaciones
- Si hay 100 usuarios y 250 conversaciones, significa que cada usuario tuvo en promedio 2.5 conversaciones

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
- [Abrir un issue en GitHub](https://github.com/EdVeralli/Metricas_Boti_Conversaciones_Usuarios/issues)
- Contactar al equipo de Data Analytics GCBA

---

**Gobierno de la Ciudad de Buenos Aires - Área de Data Analytics**

# Contenidos Consultados

Script automatizado para generar el reporte de contenidos mas consultados del chatbot Boti del Gobierno de la Ciudad de Buenos Aires (GCBA). Descarga datos de AWS Athena, calcula el ranking completo de contenidos con porcentaje del total, y genera una serie temporal diaria.

## Descripcion

Este modulo consulta la vista `boti_vw_buscador_rulename` en AWS Athena, que contiene las sesiones diarias por contenido (rulename). Procesa los datos para generar:

1. **Tabla completa de contenidos** con suma de sesiones y % del total (replica la pagina "Buscador de contenidos" del Power BI "Consultas por dia 1.pbix")
2. **Serie temporal diaria** con sesiones por dia (replica la pagina "Historico" del Power BI)
3. **Dashboard** con celda D11 conteniendo el Top 10 de contenidos formateado

## Caracteristicas

- Consulta automatica a AWS Athena (vista `boti_vw_buscador_rulename`)
- Dos modos de consulta: mes completo o rango personalizado de fechas
- Lista de 117 exclusiones configurable (onboardings, pushes, bifurcadores, etc.)
- Flag `APLICAR_EXCLUSIONES` para activar/desactivar exclusiones facilmente
- Generacion de CSV con datos crudos para control
- Excel detallado con 2 hojas: "Buscador de contenidos" + "Historico"
- Dashboard Excel con Top 10 en celda D11

## Requisitos Previos

### Software Necesario

- **Python 3.7+**
- **AWS CLI** configurado
- **aws-azure-login** para autenticacion con Azure AD

### Librerias Python

```bash
pip install boto3 awswrangler pandas openpyxl
```

### Permisos AWS

- **Rol requerido:** `PIBAConsumeBoti`
- **Workgroup:** `Production-caba-piba-athena-boti-group`
- **Base de datos:** `caba-piba-consume-zone-db`
- **Region:** `us-east-1`

## Configuracion

El script usa el archivo `config_fechas.txt` de la raiz del proyecto (`../config_fechas.txt`).

### Modo 1: Mes Completo
```ini
MES=1
AÑO=2026
```
Consulta del 1 al 31 de enero 2026.

### Modo 2: Rango Personalizado
```ini
FECHA_INICIO=2026-01-01
FECHA_FIN=2026-01-15
```
Consulta del 1 al 15 de enero 2026.

**Nota:** Si ambos modos estan configurados, el rango personalizado tiene prioridad.

### Exclusiones

La lista de contenidos a excluir esta en la constante `CONTENIDOS_EXCLUIR` dentro del script. Para desactivar las exclusiones:

```python
APLICAR_EXCLUSIONES = False  # Linea 40
```

## Uso

### 1. Autenticarse en AWS

```bash
aws-azure-login --profile default --mode=gui
```

### 2. Configurar el periodo

Editar `config_fechas.txt` en la raiz del proyecto.

### 3. Ejecutar el script

```bash
cd Contenidos_Consultados
python Contenidos_Consultados.py
```

## Salida

El script genera 3 archivos en la carpeta `output/`:

### 1. CSV - Datos crudos
`contenidos_consultados_enero_2026.csv`
- Resultado completo de la query de Athena sin procesar
- Para controles y auditorias futuras

### 2. Excel Detalle (2 hojas)
`contenidos_consultados_detalle_enero_2026.xlsx`

**Hoja "Buscador de contenidos":**

| Rulename | Suma de Sesiones | % del Total |
|----------|-----------------|-------------|
| Confirmacion Turnos Salud | 491,135 | 15.23% |
| Infracciones | 160,845 | 4.99% |
| ... | ... | ... |
| TOTAL | 3,224,567 | 100.00% |

Cards en las primeras filas: "Cantidad de Rulenames" y "Total Sesiones".

**Hoja "Historico":**

| Fecha | Sesiones diarias |
|-------|-----------------|
| 01/01/2026 | 98,543 |
| 02/01/2026 | 102,311 |
| ... | ... |
| TOTAL | 3,224,567 |

### 3. Dashboard
`contenidos_consultados_enero_2026.xlsx`

Celda D11 con el Top 10 formateado:
```
1- Confirmacion Turnos Salud: (491.135)
2- Infracciones: (160.845)
3- Turnos Salud: (133.586)
...
10- Buscar donde esta permitido estacionar: (40.441)
```

## Query Ejecutada

```sql
SELECT * FROM "caba-piba-consume-zone-db"."boti_vw_buscador_rulename"
```

La vista retorna filas con columnas: `Fecha`, `Rulename`, `Sesiones_diarias` (una fila por contenido por dia).

## Logica de Procesamiento

Extraida del Power BI "Consultas por dia 1.pbix":

1. **Filtrar por fecha:** Solo registros dentro del periodo configurado
2. **Excluir contenidos no relevantes:** 117 reglas (onboardings, pushes, bifurcadores, feedback, login, menus internos)
3. **Agrupar por Rulename:** `SUM(Sesiones_diarias)` por cada contenido
4. **Ordenar descendente:** Por suma de sesiones
5. **Calcular %GT:** `SUM(Sesiones) / ScopedEval(SUM(Sesiones), [])` (porcentaje del gran total)
6. **Serie temporal:** Agrupar por fecha para obtener sesiones diarias totales

### Origen del %GT

En el Power BI, la columna "%TG Suma de Sesiones_diarias" usa:
```
Arithmetic: Operator 3 (Division)
  Left:  SUM(Sesiones_diarias)                          -- sesiones del rulename
  Right: ScopedEval(SUM(Sesiones_diarias), [])          -- gran total (scope vacio)
```

En Python se traduce a:
```python
df['% del Total'] = df['Suma de Sesiones'] / df['Suma de Sesiones'].sum()
```

## Estructura del Proyecto

```
Contenidos_Consultados/
|
├── Contenidos_Consultados.py              # Script principal
├── README.md                              # Esta documentacion
├── Consultas por dia 1.pbix               # Power BI nuevo (referencia)
├── Buscador de Contenidos mas Consultados.pbix  # Power BI viejo (referencia)
|
└── output/                                # Carpeta de salida
    ├── contenidos_consultados_enero_2026.csv
    ├── contenidos_consultados_detalle_enero_2026.xlsx
    └── contenidos_consultados_enero_2026.xlsx
```

## Relacion con Otros Modulos

| Modulo | Celda | Metrica |
|--------|-------|---------|
| Usuarios y Conversaciones | D2, D3 | Conversaciones y Usuarios |
| Sesiones Abiertas | D4 | Sesiones iniciadas por push |
| Sesiones Alcanzadas | D5 | Sesiones que recibieron push |
| Pushes Enviadas | D6 | Mensajes push enviados |
| Contenidos del Bot | D7, D8 | Contenidos activos y relevantes |
| **Contenidos Consultados** (este) | **D11** | **Top 10 contenidos mas consultados** |
| No Entendimiento | D13 | Tasa de no comprension |
| Efectividad | D14 | % usuarios que lograron objetivo |
| CES | D15 | Customer Effort Score |
| CSAT | D16 | Customer Satisfaction |
| Disponibilidad | D17 | Uptime servidor WhatsApp |

## Troubleshooting

### Error: Credenciales expiradas
```
ExpiredTokenException: The security token included in the request is expired
```
**Solucion:**
```bash
aws-azure-login --profile default --mode=gui
```

### Error: No se encuentra config_fechas.txt
El script busca `../config_fechas.txt` (raiz del proyecto). Si no existe, crea uno de ejemplo.

### Error: No se encontro columna de rulename/sesiones
La vista de Athena cambio de estructura. Verificar las columnas disponibles en el log y actualizar las listas de deteccion en `procesar_contenidos()`.

## Informacion Tecnica

### Configuracion AWS

- **Region:** `us-east-1`
- **Workgroup:** `Production-caba-piba-athena-boti-group`
- **Database:** `caba-piba-consume-zone-db`
- **Vista:** `boti_vw_buscador_rulename`
- **Rol requerido:** `PIBAConsumeBoti`

### Dependencias

```
boto3>=1.26.0         # Cliente AWS
awswrangler>=3.0.0    # Integracion Pandas-Athena
pandas>=1.5.0         # Procesamiento de datos
openpyxl>=3.0.0       # Generacion de Excel
```

---

**Gobierno de la Ciudad de Buenos Aires - Area de Data Analytics**

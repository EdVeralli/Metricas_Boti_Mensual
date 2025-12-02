# WhatsApp Business API - Availability (Automático)

Script **completamente automático** para extraer el porcentaje de Availability (Disponibilidad) de la página de WhatsApp Business API Status usando **Selenium + ChromeDriver**. Guarda el resultado en la celda **D17** del Excel con estructura de Dashboard del GCBA.

## Descripción

Este proyecto usa **Selenium** para controlar un navegador Chrome real que ejecuta JavaScript y extrae automáticamente el porcentaje de disponibilidad del servicio WhatsApp Business API desde https://metastatus.com/whatsapp-business-api

## Características

- ✅ **100% AUTOMÁTICO** - No requiere intervención manual
- ✅ **Maneja JavaScript** - Usa Selenium para ejecutar JavaScript en la página
- ✅ Web scraping de la página oficial de Meta Status
- ✅ Generación de reportes en CSV y Excel
- ✅ Dashboard Excel con estructura predefinida del GCBA
- ✅ **Solo llena la celda D17** (Uptime servidor / Availability)
- ✅ Timestamp automático en nombres de archivo
- ✅ Múltiples estrategias de extracción

## Requisitos Previos

### Software Necesario

- **Python 3.7+**
- **Google Chrome** (navegador)

### Librerías Python

```bash
pip install selenium pandas openpyxl
```

O usando el archivo de requisitos:

```bash
pip install -r requirements.txt
```

**Nota:** Selenium 4+ instala automáticamente ChromeDriver compatible con tu versión de Chrome.

## Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone git@github.com:EdVeralli/Metricas_Boti_Disponibilidad.git
   cd Metricas_Boti_Disponibilidad
   ```

2. **Instalar Google Chrome** (si no lo tienes)

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

## Uso

### Ejecutar el script (Automático)

```bash
python WhatsApp_Availability.py
```

El script:
1. Abre Chrome automáticamente (en modo headless, sin ventana visible)
2. Accede a https://metastatus.com/whatsapp-business-api
3. Espera 10 segundos a que cargue el JavaScript
4. Extrae el porcentaje de Availability
5. Genera archivos CSV y Excel
6. Cierra el navegador automáticamente

**¡Todo automático, sin intervención manual!**

## Salida

El script genera dos archivos en la carpeta `output/`:

### Nombres de Archivo

Con timestamp automático:
- `whatsapp_availability_20251127_180000.csv`
- `whatsapp_availability_20251127_180000.xlsx`

### Estructura del Dashboard Excel

| Columna B | Columna C | Columna D |
|-----------|-----------|-----------|
| **Indicador** | **Descripción/Detalle** | **[mes-año]** |
| Conversaciones | Q Conversaciones | - |
| Usuarios | Q Usuarios únicos | - |
| Sesiones abiertas por Pushes | Q Sesiones que se abrieron con una Push | - |
| Sesiones Alcanzadas por Pushes | Q Sesiones que recibieron al menos 1 Push | - |
| Mensajes Pushes Enviados | Q de mensajes enviados bajo el formato push | - |
| Contenidos en Botmaker | Contenidos prendidos en botmaker | - |
| Contenidos Prendidos para el USUARIO | Contenidos prendidos de cara al usuario | - |
| Interacciones | Q Interacciones | - |
| Trámites, solicitudes y turnos | Q Trámites, solicitudes y turnos disponibles | - |
| contenidos mas consultados | Q Contenidos con más interacciones | - |
| Derivaciones | Q Derivaciones | - |
| No entendimiento | Performance motor de búsqueda | - |
| Tasa de Efectividad | Mide el porcentaje de usuarios que lograron su objetivo | - |
| CES (Customer Effort Score) | Mide la facilidad con la que los usuarios pueden interactuar | - |
| Satisfacción (CSAT) | Mide la satisfacción usando una escala de 1 a 5 | - |
| **Uptime servidor** | **Disponibilidad del servidor (% tiempo activo)** | **[VALOR %]** |

> **Nota:** Solo la celda D17 (Uptime servidor) se completa automáticamente con el porcentaje de Availability. El resto queda vacío para otros scripts.

## Configuración Avanzada

Puedes editar el archivo `WhatsApp_Availability.py` para ajustar:

```python
CONFIG = {
    'url': 'https://metastatus.com/whatsapp-business-api',
    'output_folder': 'output',
    'headless': True,  # False = ver ventana del navegador
    'wait_time': 10  # Segundos de espera para que cargue
}
```

- `headless`: `True` = sin ventana visible, `False` = con ventana (útil para debugging)
- `wait_time`: Aumentar si la página tarda en cargar

## Estrategias de Extracción

El script busca el porcentaje de Availability usando múltiples estrategias:

1. **Búsqueda por texto:** Busca "Availability: XX%" en todo el contenido
2. **Búsqueda por porcentaje:** Busca porcentajes entre 90-100%
3. **Búsqueda por clases CSS:** Busca elementos con clases "metric", "availability", "uptime"

Si encuentra un porcentaje válido (90-100%), lo usa. Si todas fallan, muestra ERROR.

## Troubleshooting

### Error: ChromeDriver no encontrado

```
[ERROR] No se pudo iniciar ChromeDriver
```

**Solución:**
```bash
# Selenium 4+ instala ChromeDriver automáticamente
pip install --upgrade selenium

# Si sigue fallando, instalar Chrome:
# Windows: Descargar de https://www.google.com/chrome/
# Linux: sudo apt install google-chrome-stable
# Mac: brew install --cask google-chrome
```

### Error: No se pudo extraer el porcentaje

```
[ERROR] NO SE PUDO EXTRAER EL PORCENTAJE
```

**Solución:**
1. Aumentar `wait_time` en CONFIG (de 10 a 20 segundos)
2. Cambiar `headless` a `False` para ver qué carga el navegador
3. Verificar manualmente la URL: https://metastatus.com/whatsapp-business-api

### Error: Chrome ya está ejecutándose

**Solución:** Cerrar todas las ventanas de Chrome y ejecutar nuevamente.

## Estructura del Proyecto

```
Metricas_Boti_Disponibilidad/
│
├── WhatsApp_Availability.py  # Script principal con Selenium
├── requirements.txt           # Dependencias (selenium, pandas, openpyxl)
├── README.md                  # Esta documentación
│
└── output/                    # Carpeta de salida
    ├── whatsapp_availability_20251127_180000.csv
    └── whatsapp_availability_20251127_180000.xlsx
```

## Ventajas de Usar Selenium

- ✅ **Ejecuta JavaScript:** Puede cargar páginas dinámicas
- ✅ **100% automático:** No requiere intervención manual
- ✅ **Más confiable:** Funciona como un navegador real
- ✅ **Fácil debugging:** Puedes ver qué carga con `headless=False`

## Relación con Otros Proyectos

Este script forma parte del dashboard de métricas del GCBA:

| Proyecto | Celda | Métrica |
|----------|-------|---------|
| [Usuarios y Conversaciones](https://github.com/EdVeralli/Metricas_Boti_Conversaciones_Usuarios) | D2, D3 | Conversaciones y Usuarios |
| [Sesiones Abiertas](https://github.com/EdVeralli/Sesiones_Abiertas_Pushes) | D4 | Sesiones iniciadas por push |
| [Sesiones Alcanzadas](https://github.com/EdVeralli/Sesiones_alcanzadas_pushes) | D5 | Sesiones que recibieron push |
| [Pushes Enviadas](https://github.com/EdVeralli/Pushes_Enviadas) | D6 | Mensajes push enviados |
| **WhatsApp Availability** (este) | **D17** | **Uptime servidor / Disponibilidad** |

## Consideraciones

- **Requiere Chrome:** El script usa Chrome, debe estar instalado
- **Selenium 4+:** Instala ChromeDriver automáticamente
- **Tiempo de ejecución:** ~15 segundos (10 seg espera + 5 seg procesamiento)
- **Headless mode:** Por defecto no abre ventana visible

## Contribuciones

Este es un proyecto interno del GCBA. Para contribuir:

1. Fork el proyecto
2. Crear una rama (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add some AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Autor

**Eduardo Veralli**
- GitHub: [@EdVeralli](https://github.com/EdVeralli)

## Licencia

Proyecto del Gobierno de la Ciudad de Buenos Aires (GCBA).

## Soporte

Para problemas o consultas:
- [Abrir un issue en GitHub](https://github.com/EdVeralli/Metricas_Boti_Disponibilidad/issues)
- Contactar al equipo de Data Analytics GCBA

## Información Técnica

### Versión

**Versión:** 2.0 (Selenium)
**Última actualización:** Noviembre 2025

### Dependencias

```
selenium>=4.15.0      # Navegador automatizado
pandas>=1.5.0         # Procesamiento de datos
openpyxl>=3.0.0       # Generación de Excel
```

### URL Consultada

- **Página oficial:** https://metastatus.com/whatsapp-business-api
- **Método:** Selenium + ChromeDriver
- **Métrica extraída:** Availability percentage (%)

### Celda Excel

- **Ubicación:** D17
- **Indicador:** Uptime servidor (Disponibilidad)
- **Formato:** `XX.X%` (ej: `99.9%`)

---

**Gobierno de la Ciudad de Buenos Aires - Área de Data Analytics**

# Metricas_Boti_Mensual

Sistema completo de reportería automatizada para el chatbot "Boti" del GCBA. Genera métricas mensuales y las consolida en dashboards Excel.

## 🎯 Módulos del Proyecto

El proyecto está compuesto por 5 módulos independientes que extraen diferentes métricas:

| Módulo | Celda Excel | Métrica | Fuente |
|--------|-------------|---------|--------|
| [Usuarios_Conversaciones](./Metricas_Boti_Conversaciones_Usuarios/) | D2, D3 | Usuarios únicos y Conversaciones | AWS Athena |
| [Pushes_Enviadas](./Pushes_Enviadas/) | D6 | Mensajes push enviados | AWS Athena |
| [Sesiones_Abiertas_Pushes](./Sesiones_Abiertas_Pushes/) | D4 | Sesiones iniciadas por push | AWS Athena |
| [Sesiones_alcanzadas_pushes](./Sesiones_alcanzadas_pushes/) | D5 | Sesiones que recibieron push | AWS Athena |
| [WhatsApp_Availability](./Metricas_Boti_Disponibilidad/) | D17 | Uptime servidor / Disponibilidad | Web Scraping |

💡 **Ayuda Rápida:** Ejecutá `python ayuda.py` para ver todos los comandos y el workflow completo.

## 🚀 Ejecución Rápida (Recomendado)

### Script Maestro - Ejecutar Todo de Una Vez

El **script maestro** ejecuta automáticamente todos los módulos y genera el dashboard consolidado:

```bash
# 1. Autenticarse en AWS
aws-azure-login --profile default --mode=gui

# 2. Configurar fechas (si es necesario)
nano config_fechas.txt

# 3. Ejecutar todo automáticamente
python run_all.py

# 4. Consolidar en un único Excel (se ejecuta después del maestro)
python consolidar_excel.py
```

**Ventajas:**
- ✅ Ejecuta los 5 módulos secuencialmente
- ✅ Verifica credenciales AWS antes de empezar
- ✅ Muestra progreso en tiempo real
- ✅ Genera resumen de ejecución
- ✅ El consolidador crea un dashboard completo en la raíz

**Resultado:** Archivo `Dashboard_Boti_Consolidado_YYYYMMDD_HHMMSS.xlsx` en la raíz del proyecto con todas las métricas unificadas.

## ⚙️ Configuración Centralizada

**IMPORTANTE:** Todos los módulos utilizan un **archivo de configuración centralizado** ubicado en la raíz del proyecto:

```
./config_fechas.txt
```

### Formato del Archivo

El archivo soporta dos modos de consulta:

#### Modo 1: Mes Completo
```ini
MES=11
AÑO=2025
```
→ Consulta del 1 al 30 de noviembre 2025

#### Modo 2: Rango Personalizado
```ini
FECHA_INICIO=2025-11-01
FECHA_FIN=2025-11-15
```
→ Consulta del 1 al 15 de noviembre 2025

**Reglas:**
- Si ambos modos están configurados, se usa el **Modo 2** (rango)
- Formato de fecha: `YYYY-MM-DD` (ej: 2025-11-15)
- FECHA_INICIO debe ser ≤ FECHA_FIN
- El mes debe estar entre 1 y 12

## 🔐 Autenticación AWS (OBLIGATORIO)

**IMPORTANTE:** Antes de ejecutar cualquier script, debes autenticarte en AWS. Estos comandos son necesarios para TODOS los módulos que consultan Athena.

### Primera vez (Configuración inicial):
```bash
aws-azure-login --configure --profile default
```

### Antes de cada sesión de trabajo:
```bash
aws-azure-login --profile default --mode=gui
```

⚠️ **CRÍTICO:** Durante la autenticación, seleccionar el rol `PIBAConsumeBoti`

💡 **Nota:** La sesión de AWS expira después de algunas horas. Si ves errores de autenticación, ejecutá nuevamente el comando `aws-azure-login`.

---

## 🚀 Uso Rápido

### 1. Configurar el Período

Editar `./config_fechas.txt` en la raíz del proyecto:

```bash
nano config_fechas.txt
```

### 2. Ejecutar Scripts

**Opción A: Automática (Recomendado) 🚀**

Ejecutar todos los módulos de una vez:
```bash
python run_all.py
```

Luego consolidar todos los Excel:
```bash
python consolidar_excel.py
```

**Opción B: Manual (Módulo por Módulo)**

Si preferís ejecutar módulos específicos:

### 3. Ejecutar los Scripts

Cada módulo se ejecuta independientemente:

```bash
# Usuarios y Conversaciones
cd Metricas_Boti_Conversaciones_Usuarios
python Usuarios_Conversaciones.py

# Pushes Enviadas
cd ../Pushes_Enviadas
python Pushes_Enviadas.py

# Sesiones Abiertas
cd ../Sesiones_Abiertas_Pushes
python Sesiones_Abiertas_porPushes.py

# Sesiones Alcanzadas
cd ../Sesiones_alcanzadas_pushes
python Sesiones_Alcanzadas.py

# Disponibilidad WhatsApp
cd ../Metricas_Boti_Disponibilidad
python WhatsApp_Availability.py
```

## 📦 Requisitos Previos

### Software
- **Python 3.7+**
- **AWS CLI** configurado
- **aws-azure-login** para autenticación con Azure AD
- **Google Chrome** (solo para WhatsApp_Availability)

### Librerías Python

```bash
pip install boto3 awswrangler pandas openpyxl selenium
```

### Permisos AWS
- **Rol requerido:** `PIBAConsumeBoti`
- **Workgroup:** `Production-caba-piba-athena-boti-group`
- **Base de datos:** `caba-piba-consume-zone-db`
- **Región:** `us-east-1`

## 📁 Estructura del Proyecto

```
Metricas_Boti_Mensual/
│
├── config_fechas.txt                          # ⭐ Config centralizado (TODOS los scripts)
├── README.md                                  # Documentación principal
├── CAMBIOS.md                                 # Log de cambios y mejoras
├── ayuda.py                                   # 💡 Script de ayuda rápida (python ayuda.py)
├── run_all.py                                 # 🚀 Script maestro - ejecuta todos los módulos
├── consolidar_excel.py                        # 📊 Consolidador - unifica todos los Excel
├── cleanup_local_configs.py                   # Script para limpiar configs locales antiguos
├── Dashboard_Boti_Consolidado_*.xlsx          # 📈 Dashboard consolidado (generado automáticamente)
│
├── Metricas_Boti_Conversaciones_Usuarios/
│   ├── Usuarios_Conversaciones.py
│   ├── output/
│   └── README.md
│
├── Pushes_Enviadas/
│   ├── Pushes_Enviadas.py
│   ├── output/
│   ├── requirements.txt
│   └── README.md
│
├── Sesiones_Abiertas_Pushes/
│   ├── Sesiones_Abiertas_porPushes.py
│   ├── output/
│   └── README.md
│
├── Sesiones_alcanzadas_pushes/
│   ├── Sesiones_Alcanzadas.py
│   ├── output/
│   └── README.md
│
└── Metricas_Boti_Disponibilidad/
    ├── WhatsApp_Availability.py
    ├── output/
    ├── requirements.txt
    └── README.md
```

## 📊 Salida

Cada módulo genera:
- **CSV** con datos crudos en carpeta `output/`
- **Excel** con estructura de dashboard del GCBA

Los archivos tienen timestamp automático:
- `usuarios_conversaciones_20251127_153000.csv`
- `usuarios_conversaciones_20251127_153000.xlsx`

## ⚠️ Troubleshooting Común

### Error: "No credentials found" o "Unable to locate credentials"
**Causa:** No estás autenticado en AWS o la sesión expiró.

**Solución:**
```bash
aws-azure-login --profile default --mode=gui
```
Asegurate de seleccionar el rol `PIBAConsumeBoti`.

### Error: "Access Denied" al ejecutar queries en Athena
**Causa:** No seleccionaste el rol correcto durante la autenticación.

**Solución:**
1. Volver a autenticarte: `aws-azure-login --profile default --mode=gui`
2. Seleccionar específicamente el rol: `PIBAConsumeBoti`

### Error: "Connection timeout" o "Network error"
**Causa:** Problemas de red o VPN.

**Solución:**
1. Verificar conexión a internet
2. Si usás VPN corporativa, asegurate de estar conectado

### La sesión AWS expiró
**Síntoma:** Los scripts funcionaban pero ahora dan error de credenciales.

**Solución:** Las sesiones de AWS expiran después de unas horas. Ejecutá nuevamente:
```bash
aws-azure-login --profile default --mode=gui
```

## 🤝 Contribuciones

Este es un proyecto interno del GCBA. Para contribuir:

1. Fork el proyecto
2. Crear una rama (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add some AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 👤 Autor

**Eduardo Veralli**
- GitHub: [@EdVeralli](https://github.com/EdVeralli)

## 📝 Licencia

Proyecto del Gobierno de la Ciudad de Buenos Aires (GCBA).

---

**Gobierno de la Ciudad de Buenos Aires - Área de Data Analytics**

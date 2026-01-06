# Reporte de Analisis de Codigo - Metricas_Boti_Mensual

**Fecha de revision:** 2026-01-04
**Proyecto:** Metricas_Boti_Mensual
**Autor del analisis:** Claude Code

---

## Resumen Ejecutivo

Se revisaron todos los scripts Python del proyecto buscando errores graves o criticos. Se encontraron **14 problemas** clasificados por prioridad:

| Prioridad | Cantidad | Descripcion |
|-----------|----------|-------------|
| CRITICO | 3 | Memory leaks, recursos no liberados, divisiones por cero silenciosas |
| ALTO | 4 | Except genericos, SQL interpolado, estado corrupto del programa |
| MEDIO | 7 | Timeouts, encodings, eficiencia |

---

## CRITICO

### 1. Division por Cero Potencial

**Archivos afectados:**
- `Feedback_CES/Feedback_CES.py` - lineas 259-262
- `Feedback_CSAT/Feedback_CSAT.py` - lineas 264-267
- `No_Entendidos/No_Entendimiento.py` - lineas 434-439

**Codigo problematico:**

```python
# Feedback_CES.py:259
if total_sesiones > 0:
    ces = total_ponderado / total_sesiones
else:
    ces = 0  # OK - pero se usa sin validar despues
```

**Problema:** El valor `0` se propaga sin advertencia, generando metricas incorrectas silenciosamente. El usuario no sabe si el CES es realmente 0 o si no habia datos.

**Solucion recomendada:**

```python
if total_sesiones > 0:
    ces = total_ponderado / total_sesiones
else:
    ces = None  # O usar float('nan')
    print("[ADVERTENCIA] No hay sesiones para calcular CES")
```

---

### 2. WebDriver de Selenium No Se Cierra en Todas las Rutas

**Archivo:** `Metricas_Boti_Disponibilidad/WhatsApp_Availability.py` - lineas 68-153

**Codigo problematico:**

```python
def extract_availability_selenium(url):
    driver = None
    try:
        driver = setup_chrome_driver()
        # ... codigo ...
        driver.quit()  # Solo se cierra aqui
        return percentage, datetime.now()
    except:
        pass  # driver.quit() nunca se llama aqui
```

**Problema:** Si ocurre una excepcion en el bloque interno (linea 126), el `except: pass` atrapa todo pero no cierra el driver, causando **memory leaks** de procesos ChromeDriver que quedan huerfanos en el sistema.

**Solucion recomendada:**

```python
def extract_availability_selenium(url):
    driver = None
    try:
        driver = setup_chrome_driver()
        # ... codigo ...
        return percentage, datetime.now()
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return None, None
    finally:
        if driver:
            driver.quit()  # Siempre se cierra
```

---

### 3. Archivos Excel No Se Cierran Correctamente

**Archivos afectados:** Todos los modulos que usan `openpyxl`

**Codigo problematico:**

```python
# consolidar_excel.py:229-247
wb = openpyxl.load_workbook(archivo_excel, data_only=True)
ws = wb.active
valor = ws[celda].value
# ...
wb.close()  # Solo se cierra si no hay excepcion
```

**Problema:** Si `ws[celda].value` lanza una excepcion, el workbook queda abierto bloqueando el archivo Excel en Windows.

**Solucion recomendada:**

```python
# Usar context manager (Python 3.8+)
with openpyxl.load_workbook(archivo_excel, data_only=True) as wb:
    ws = wb.active
    valor = ws[celda].value

# O usar try/finally
wb = openpyxl.load_workbook(archivo_excel, data_only=True)
try:
    ws = wb.active
    valor = ws[celda].value
finally:
    wb.close()
```

---

## ALTO

### 4. Except Generico que Atrapa Todo

**Archivos afectados:**
- `Metricas_Boti_Disponibilidad/WhatsApp_Availability.py` - linea 126
- `consolidar_excel.py` - linea 293
- `run_all.py` - verificaciones varias

**Codigo problematico:**

```python
# WhatsApp_Availability.py:126
except:
    pass  # Silencia TODOS los errores incluyendo KeyboardInterrupt
```

**Problema:** Los `except:` sin tipo especifico atrapan incluso `SystemExit` y `KeyboardInterrupt`, haciendo el debugging imposible y evitando que el usuario pueda cancelar el programa con Ctrl+C.

**Solucion recomendada:**

```python
except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {str(e)}")
    # Manejar el error apropiadamente
```

---

### 5. Queries SQL con Fechas Inyectadas

**Archivos afectados:** Todos los modulos de Athena
- `Feedback_CES/Feedback_CES.py`
- `Feedback_CSAT/Feedback_CSAT.py`
- `Feedback_Efectividad/Feedback_Efectividad.py`
- `Pushes_Enviadas/Pushes_Enviadas.py`
- `Sesiones_Abiertas_Pushes/Sesiones_Abiertas_porPushes.py`
- `Sesiones_alcanzadas_pushes/Sesiones_Alcanzadas.py`
- `Metricas_Boti_Conversaciones_Usuarios/Usuarios_Conversaciones.py`
- `No_Entendidos/No_Entendimiento.py`

**Codigo problematico:**

```python
# Feedback_CES.py:182-188
query = """SELECT ...
WHERE CAST(session_creation_time AS DATE) BETWEEN date '{fecha_inicio}' and date '{fecha_fin}'
""".format(fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
```

**Problema:** Las fechas se interpolan directamente en el SQL usando `.format()`. Aunque vienen de `config_fechas.txt` (no de input de usuario directo), un archivo malformado podria causar problemas de parsing o errores inesperados.

**Nota:** No es SQL Injection clasico porque Athena es read-only y no hay input de usuario directo, pero es **mala practica**.

**Solucion recomendada:** Validar el formato de fecha antes de interpolar:

```python
from datetime import datetime

def validar_fecha(fecha_str):
    try:
        datetime.strptime(fecha_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

if not validar_fecha(fecha_inicio) or not validar_fecha(fecha_fin):
    raise ValueError("Formato de fecha invalido")
```

---

### 6. Reconexion Boto3 Incompleta

**Archivo:** `No_Entendidos/athena_connector.py` - lineas 429-433

**Codigo problematico:**

```python
# Intenta recargar botocore
import importlib
import botocore.session
importlib.reload(botocore.session)
```

**Problema:** `importlib.reload()` de `botocore.session` no garantiza que las credenciales se refresquen correctamente. Las credenciales cacheadas en la sesion actual de boto3 pueden persistir.

**Solucion recomendada:**

```python
# Crear una nueva sesion completamente nueva
import boto3
boto3.setup_default_session()  # Reset de la sesion default
session = boto3.Session(region_name=ATHENA_REGION)
```

---

### 7. Directorio de Trabajo No Restaurado en Errores

**Archivo:** `run_all.py` - lineas 192-239

**Codigo problematico:**

```python
os.chdir(modulo['carpeta'])
# ... subprocess.run() ...
os.chdir('..')  # Solo se ejecuta si no hay excepcion

# En el except:
except Exception as e:
    os.chdir('..')  # Bien, pero duplicado y fragil
```

**Problema:** Si `subprocess.run()` falla con un error inesperado antes del primer `chdir('..')`, el programa queda en el directorio incorrecto para el resto de los modulos.

**Solucion recomendada:**

```python
import os
from contextlib import contextmanager

@contextmanager
def cambiar_directorio(nuevo_dir):
    dir_original = os.getcwd()
    try:
        os.chdir(nuevo_dir)
        yield
    finally:
        os.chdir(dir_original)

# Uso:
with cambiar_directorio(modulo['carpeta']):
    result = subprocess.run([sys.executable, modulo['script']], ...)
```

---

## MEDIO

### 8. Timeout Sin Configurar en Consultas AWS

**Archivos afectados:** Todos los modulos Athena

**Codigo problematico:**

```python
# No hay timeout configurado en awswrangler
df = wr.athena.read_sql_query(
    sql=query,
    database=CONFIG['database'],
    # ... sin timeout
)
```

**Problema:** Las queries podrian correr indefinidamente sin timeout, consumiendo recursos y dejando el programa colgado.

**Solucion recomendada:**

```python
# Configurar timeout en boto3 config
from botocore.config import Config

config = Config(
    connect_timeout=30,
    read_timeout=300  # 5 minutos
)

session = boto3.Session(region_name=CONFIG['region'])
# Pasar config al cliente
```

---

### 9. Input() Sin Timeout

**Archivos:**
- `No_Entendidos/athena_connector.py` - lineas 421-424
- `No_Entendidos/No_Entendimiento.py` - linea 615

**Codigo problematico:**

```python
input("Presiona ENTER cuando hayas renovado el token...")
```

**Problema:** Si se ejecuta en un ambiente automatizado (CI/CD, cron, scheduled task), el programa cuelga indefinidamente esperando input.

**Solucion recomendada:**

```python
import sys
import select

def input_con_timeout(prompt, timeout=300):
    print(prompt)
    if sys.platform == 'win32':
        # En Windows, usar threading
        import threading
        resultado = [None]
        def leer_input():
            resultado[0] = input()
        thread = threading.Thread(target=leer_input)
        thread.daemon = True
        thread.start()
        thread.join(timeout)
        if thread.is_alive():
            raise TimeoutError("Timeout esperando input")
        return resultado[0]
    else:
        # En Unix, usar select
        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        if ready:
            return sys.stdin.readline().strip()
        raise TimeoutError("Timeout esperando input")
```

---

### 10. Manejo Inconsistente de Encodings

**Archivos afectados:** Multiples

**Codigo problematico:**

```python
# Algunos archivos usan:
df.to_csv(path, encoding='utf-8-sig')  # Con BOM para Excel

# Otros usan:
with open(config_file, 'r', encoding='utf-8') as f:  # Sin BOM
```

**Problema:** Inconsistencia puede causar problemas con caracteres especiales (tildes, n con virgulilla) en diferentes contextos, especialmente al abrir CSVs en Excel.

**Solucion recomendada:** Estandarizar en todo el proyecto:
- Para CSVs que se abren en Excel: `utf-8-sig`
- Para archivos de configuracion/codigo: `utf-8`

---

### 11. Time.sleep() para Esperar Carga de Pagina

**Archivo:** `Metricas_Boti_Disponibilidad/WhatsApp_Availability.py` - linea 88

**Codigo problematico:**

```python
time.sleep(CONFIG['wait_time'])  # 10 segundos fijos
```

**Problema:** Espera fija de 10 segundos en lugar de usar `WebDriverWait` con condiciones explicitas. Puede ser insuficiente con conexiones lentas o excesivo con conexiones rapidas.

**Solucion recomendada:**

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

wait = WebDriverWait(driver, 30)
element = wait.until(
    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'availability')]"))
)
```

---

### 12. Patrones Regex Demasiado Permisivos

**Archivo:** `Metricas_Boti_Disponibilidad/WhatsApp_Availability.py` - lineas 97-101

**Codigo problematico:**

```python
patterns = [
    r'(\d{2,3}\.\d+)\s*%',  # Matchea cualquier porcentaje
]
```

**Problema:** El regex puede matchear porcentajes no relacionados con availability (ej: "50.00% off sale", "Battery: 85.5%").

**Solucion recomendada:**

```python
patterns = [
    r'(?:Uptime|Availability|availability)[\s:]+(\d{2,3}\.\d+)\s*%',
    r'(\d{2,3}\.\d+)\s*%\s*(?:uptime|availability)',
]
```

---

### 13. DataFrames Grandes Sin Chunking

**Archivo:** `No_Entendidos/No_Entendimiento.py` - lineas 373-391

**Codigo problematico:**

```python
mm1 = mensajes.copy()  # Puede ser millones de registros
search = clicks.copy()
os = botones.copy()
```

**Problema:** Para periodos largos (varios meses), cargar todo en memoria puede causar `MemoryError` en maquinas con RAM limitada.

**Solucion recomendada:**

```python
# Procesar en chunks si el DataFrame es muy grande
CHUNK_SIZE = 100000

if len(mensajes) > CHUNK_SIZE:
    print(f"[INFO] Procesando {len(mensajes)} registros en chunks...")
    # Implementar procesamiento por chunks
```

---

### 14. Shutil.rmtree Sin Proteccion

**Archivo:** `No_Entendidos/No_Entendimiento.py` - lineas 102-103

**Codigo problematico:**

```python
import shutil
shutil.rmtree(progress_folder)
```

**Problema:** Si `progress_folder` contuviera una ruta incorrecta por un bug, podria borrar archivos importantes. Falta validacion de la ruta.

**Solucion recomendada:**

```python
def limpiar_progreso(output_folder):
    progress_folder = os.path.join(output_folder, '.progress')

    # Validar que es una ruta segura
    abs_progress = os.path.abspath(progress_folder)
    abs_output = os.path.abspath(output_folder)

    if not abs_progress.startswith(abs_output):
        raise ValueError(f"Ruta sospechosa: {progress_folder}")

    if os.path.exists(progress_folder) and os.path.isdir(progress_folder):
        shutil.rmtree(progress_folder)
```

---

## Recomendaciones Generales

### 1. Usar Context Managers

Para todos los recursos (archivos, drivers, conexiones), usar `with` para garantizar que se cierren correctamente:

```python
# Bien
with open(archivo, 'r') as f:
    contenido = f.read()

# Mal
f = open(archivo, 'r')
contenido = f.read()
f.close()  # No se ejecuta si hay excepcion
```

### 2. Logging en Lugar de Print

Reemplazar `print()` por el modulo `logging` para mejor control:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("Mensaje informativo")
logger.error("Mensaje de error")
```

### 3. Validacion de Inputs

Validar todos los inputs externos (archivos de configuracion, respuestas de APIs):

```python
def validar_config(config):
    required_keys = ['MES', 'ANO']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Falta configuracion requerida: {key}")
```

### 4. Tests Unitarios

Agregar tests para las funciones criticas, especialmente:
- Calculo de metricas (CES, CSAT, etc.)
- Parsing de configuracion
- Construccion de queries SQL

---

## Archivos Revisados

| Archivo | Lineas | Estado |
|---------|--------|--------|
| `run_all.py` | 334 | Revisado |
| `consolidar_excel.py` | 531 | Revisado |
| `Usuarios_Conversaciones.py` | 466 | Revisado |
| `Pushes_Enviadas.py` | 552 | Revisado |
| `Sesiones_Abiertas_porPushes.py` | 565 | Revisado |
| `Sesiones_Alcanzadas.py` | 445 | Revisado |
| `Feedback_Efectividad.py` | 729 | Revisado |
| `Feedback_CES.py` | 813 | Revisado |
| `Feedback_CSAT.py` | 840 | Revisado |
| `WhatsApp_Availability.py` | 345 | Revisado |
| `No_Entendimiento.py` | 754 | Revisado |
| `athena_connector.py` | 608 | Revisado |

**Total:** ~6,982 lineas de codigo revisadas

---

*Generado automaticamente por Claude Code*

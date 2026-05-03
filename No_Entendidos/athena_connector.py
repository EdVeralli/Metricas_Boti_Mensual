#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo para conectar con AWS Athena y ejecutar queries automáticamente
Autor: GCBA - Boti Analytics Team
"""

import boto3
import time
import re
import os
from datetime import datetime

# =============================================================================
# CONFIGURACIÓN - EDITAR ESTAS VARIABLES
# =============================================================================

ATHENA_DATABASE = 'caba-piba-consume-zone-db'
ATHENA_WORKGROUP = 'Production-caba-piba-athena-boti-group'  # Tu workgroup con permisos
ATHENA_OUTPUT_BUCKET = None  # Se obtiene automáticamente del perfil AWS
ATHENA_REGION = 'us-east-1'  # Cambiar si usas otra región

# =============================================================================
# FUNCIONES PRINCIPALES
# =============================================================================

def leer_config_fechas(archivo='../config_fechas.txt'):
    """
    Lee config_fechas.txt y retorna (fecha_inicio, fecha_fin)

    Soporta dos modos:
    1. MES=10, AÑO=2025 → Calcula todo el mes
    2. FECHA_INICIO=2025-10-01, FECHA_FIN=2025-10-31 → Rango específico

    Returns:
        tuple: (fecha_inicio, fecha_fin) en formato 'YYYY-MM-DD'
    """
    # Buscar el archivo en múltiples ubicaciones
    rutas_posibles = [
        archivo,                    # Ruta especificada (por defecto ../config_fechas.txt)
        'config_fechas.txt',        # Directorio actual
        '../config_fechas.txt',     # Directorio padre (raíz del repo)
        '../../config_fechas.txt',  # Dos niveles arriba
    ]

    archivo_encontrado = None
    for ruta in rutas_posibles:
        if os.path.exists(ruta):
            archivo_encontrado = ruta
            break

    if not archivo_encontrado:
        raise FileNotFoundError(
            f"No se encuentra config_fechas.txt en ninguna ubicación.\n"
            f"Ubicaciones buscadas: {rutas_posibles}\n"
            f"Crea el archivo en la raíz del repositorio."
        )

    config = {}

    print(f"📄 Leyendo {archivo_encontrado}...")

    with open(archivo_encontrado, 'r', encoding='utf-8') as f:
        for linea in f:
            linea = linea.strip()
            
            # Ignorar comentarios y vacías
            if not linea or linea.startswith('#'):
                continue
            
            # Parsear key=value
            if '=' in linea:
                key, value = linea.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Remover comentarios inline
                if '#' in value:
                    value = value.split('#')[0].strip()
                
                config[key] = value
    
    # PRIORIDAD: Rango personalizado
    if 'FECHA_INICIO' in config and 'FECHA_FIN' in config:
        fecha_inicio = config['FECHA_INICIO']
        fecha_fin = config['FECHA_FIN']
        print(f"✓ Modo: Rango personalizado")
        print(f"  Desde: {fecha_inicio}")
        print(f"  Hasta: {fecha_fin}")
        return fecha_inicio, fecha_fin
    
    # SECUNDARIO: Mes completo
    elif 'MES' in config and 'AÑO' in config:
        mes = int(config['MES'])
        anio = int(config['AÑO'])
        
        # Primer día del mes
        fecha_inicio_dt = datetime(anio, mes, 1)
        
        # Primer día del mes siguiente
        if mes == 12:
            fecha_fin_dt = datetime(anio + 1, 1, 1)
        else:
            fecha_fin_dt = datetime(anio, mes + 1, 1)
        
        fecha_inicio = fecha_inicio_dt.strftime('%Y-%m-%d')
        fecha_fin = fecha_fin_dt.strftime('%Y-%m-%d')
        
        print(f"✓ Modo: Mes completo")
        print(f"  Mes: {mes}/{anio}")
        print(f"  Desde: {fecha_inicio}")
        print(f"  Hasta: {fecha_fin}")
        
        return fecha_inicio, fecha_fin
    
    else:
        raise ValueError(
            "config_fechas.txt inválido. "
            "Debe tener (MES + AÑO) o (FECHA_INICIO + FECHA_FIN)"
        )


def reemplazar_fechas_en_query(query_sql, fecha_inicio, fecha_fin):
    """
    Reemplaza las fechas hardcodeadas en la query SQL
    
    Busca patrones: '2025-10-01 00:00:00'
    Reemplaza:
      - Primera ocurrencia  → fecha_inicio 00:00:00
      - Segunda ocurrencia → fecha_fin 00:00:00
    
    Args:
        query_sql: String con el SQL completo
        fecha_inicio: 'YYYY-MM-DD'
        fecha_fin: 'YYYY-MM-DD'
    
    Returns:
        str: Query con fechas actualizadas
    """
    # Agregar hora a las fechas
    fecha_inicio_completa = f"{fecha_inicio} 00:00:00"
    fecha_fin_completa = f"{fecha_fin} 00:00:00"
    
    # Patrón: 'YYYY-MM-DD HH:MM:SS'
    patron = r"'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'"
    fechas_encontradas = re.findall(patron, query_sql)
    
    if len(fechas_encontradas) >= 2:
        # Reemplazar primera fecha (fecha_inicio)
        query_sql = query_sql.replace(
            fechas_encontradas[0], 
            f"'{fecha_inicio_completa}'", 
            1
        )
        
        # Reemplazar segunda fecha (fecha_fin)
        query_sql = query_sql.replace(
            fechas_encontradas[1], 
            f"'{fecha_fin_completa}'", 
            1
        )
        
        print(f"  ✓ Fechas reemplazadas en query")
    else:
        print(f"  ⚠ No se encontraron fechas para reemplazar")
    
    return query_sql


def ejecutar_query_athena_con_reintentos(query_sql, max_intentos=3):
    """
    Ejecuta una query con reintentos automáticos si el token expira
    
    Args:
        query_sql: String con el SQL a ejecutar
        max_intentos: Número máximo de reintentos
    
    Returns:
        str: Ubicación S3 del archivo de resultado
    
    Raises:
        Exception: Si la query falla después de todos los reintentos
    """
    # Crear sesión inicial FRESCA (sin cache)
    session = crear_session_boto3_fresca()
    
    for intento in range(1, max_intentos + 1):
        try:
            # Verificar credenciales antes de ejecutar
            if not verificar_credenciales_aws():
                print(f"\n⚠️  Credenciales inválidas antes del intento {intento}/{max_intentos}")
                if intento < max_intentos:
                    if solicitar_renovacion_token():
                        # CLAVE: Recrear sesión COMPLETAMENTE NUEVA
                        print("🔄 Recreando sesión de boto3 con nuevas credenciales...")
                        session = crear_session_boto3_fresca()
                        continue
                    else:
                        raise Exception("No se pudo renovar el token AWS")
                else:
                    raise Exception("Credenciales inválidas - se agotaron los intentos")
            
            # Ejecutar query usando la sesión actual (con credenciales frescas)
            result_location = ejecutar_query_athena(query_sql, boto3_session=session)
            return result_location
        
        except Exception as e:
            error_msg = str(e)
            
            # Detectar si es un error de token expirado
            if 'ExpiredToken' in error_msg or 'expired' in error_msg.lower():
                print(f"\n⚠️  Token expiró durante la ejecución")
                
                if intento < max_intentos:
                    print(f"   Intento {intento}/{max_intentos}")
                    
                    if solicitar_renovacion_token():
                        # CLAVE: Recrear sesión COMPLETAMENTE NUEVA
                        print("🔄 Recreando sesión de boto3 con nuevas credenciales...")
                        session = crear_session_boto3_fresca()
                        print(f"   Reintentando query...")
                        continue
                    else:
                        raise Exception("No se pudo renovar el token AWS")
                else:
                    raise Exception("Se agotaron los intentos para renovar el token")
            else:
                # Otro tipo de error, propagar
                raise


def ejecutar_query_athena(query_sql, output_location=None, boto3_session=None):
    """
    Ejecuta una query en AWS Athena y espera el resultado
    
    Args:
        query_sql: String con el SQL a ejecutar
        output_location: Bucket S3 para resultados (opcional, usa perfil si None)
        boto3_session: Sesión de boto3 (opcional, crea una nueva si None)
    
    Returns:
        str: Ubicación S3 del archivo de resultado
    
    Raises:
        Exception: Si la query falla
    """
    # Cliente de Athena con sesión específica si se provee
    if boto3_session is not None:
        client = boto3_session.client('athena', region_name=ATHENA_REGION)
    else:
        client = boto3.client('athena', region_name=ATHENA_REGION)
    
    # Preparar parámetros de ejecución
    print(f"  🚀 Iniciando query en Athena (workgroup: {ATHENA_WORKGROUP})...")
    
    execution_params = {
        'QueryString': query_sql,
        'QueryExecutionContext': {'Database': ATHENA_DATABASE},
        'WorkGroup': ATHENA_WORKGROUP  # ← CLAVE: Usar el workgroup con permisos
    }
    
    # El workgroup ya tiene configurado el bucket de salida
    # Solo agregamos ResultConfiguration si se especifica explícitamente
    if output_location is not None:
        execution_params['ResultConfiguration'] = {'OutputLocation': output_location}
    elif ATHENA_OUTPUT_BUCKET is not None:
        execution_params['ResultConfiguration'] = {'OutputLocation': ATHENA_OUTPUT_BUCKET}
    
    response = client.start_query_execution(**execution_params)
    
    query_id = response['QueryExecutionId']
    print(f"  📋 Query ID: {query_id}")
    
    # Esperar resultado
    estado = 'RUNNING'
    iteracion = 0
    
    while estado in ['RUNNING', 'QUEUED']:
        time.sleep(5)
        iteracion += 1
        
        response = client.get_query_execution(QueryExecutionId=query_id)
        estado = response['QueryExecution']['Status']['State']
        
        if iteracion % 6 == 0:  # Cada 30 segundos
            if estado == 'RUNNING':
                print(f"  ⏳ Ejecutando... ({iteracion * 5}s)")
            elif estado == 'QUEUED':
                print(f"  📥 En cola... ({iteracion * 5}s)")
    
    # Verificar resultado
    if estado == 'SUCCEEDED':
        result_location = response['QueryExecution']['ResultConfiguration']['OutputLocation']
        print(f"  ✅ Query exitosa")
        return result_location
    else:
        error = response['QueryExecution']['Status'].get(
            'StateChangeReason', 
            'Error desconocido'
        )
        raise Exception(f"❌ Query falló: {error}")


def descargar_desde_s3(s3_path, archivo_local, boto3_session=None):
    """
    Descarga un archivo desde S3 a disco local
    
    Args:
        s3_path: Ruta S3 completa (s3://bucket/path/file.csv)
        archivo_local: Ruta local donde guardar el archivo
        boto3_session: Sesión de boto3 (opcional, crea una nueva si None)
    """
    # Parsear S3 path
    s3_path_limpio = s3_path.replace('s3://', '')
    bucket, key = s3_path_limpio.split('/', 1)
    
    print(f"  📥 Descargando desde S3...")
    print(f"     Bucket: {bucket}")
    print(f"     Key: {key}")
    
    # Cliente S3 con sesión específica si se provee
    if boto3_session is not None:
        s3_client = boto3_session.client('s3', region_name=ATHENA_REGION)
    else:
        s3_client = boto3.client('s3', region_name=ATHENA_REGION)
    
    # Descargar
    s3_client.download_file(bucket, key, archivo_local)
    
    # Verificar tamaño
    tamanio_mb = os.path.getsize(archivo_local) / (1024 * 1024)
    print(f"  ✅ Descargado: {archivo_local} ({tamanio_mb:.2f} MB)")


def ejecutar_y_descargar(query_file, fecha_inicio, fecha_fin, output_file):
    """
    Proceso completo: Leer SQL → Reemplazar fechas → Ejecutar → Descargar
    Con verificación de credenciales y reintentos automáticos
    
    Args:
        query_file: Archivo .sql a ejecutar
        fecha_inicio: 'YYYY-MM-DD'
        fecha_fin: 'YYYY-MM-DD'
        output_file: Donde guardar el CSV resultante
    
    Returns:
        str: Ruta del archivo descargado
    """
    print(f"\n{'='*60}")
    print(f"  {query_file}")
    print(f"{'='*60}")
    
    # Verificar credenciales antes de empezar esta query
    print(f"🔐 Verificando credenciales antes de {query_file}...")
    if not verificar_credenciales_aws():
        print(f"⚠️  Credenciales inválidas o expiradas")
        if solicitar_renovacion_token():
            print(f"✓ Credenciales renovadas, continuando...\n")
        else:
            raise Exception("No se pudo renovar el token AWS")
    else:
        print(f"✓ Credenciales válidas\n")
    
    # 1. Leer query SQL
    print(f"📖 Leyendo query...")
    with open(query_file, 'r', encoding='utf-8') as f:
        query_sql = f.read()
    
    # 2. Reemplazar fechas
    print(f"📅 Reemplazando fechas...")
    query_sql = reemplazar_fechas_en_query(query_sql, fecha_inicio, fecha_fin)
    
    # 3. Ejecutar en Athena (con reintentos automáticos)
    print(f"☁️  Ejecutando en Athena...")
    result_location = ejecutar_query_athena_con_reintentos(query_sql, max_intentos=3)
    
    # 4. Descargar resultado (con reintentos si falla)
    print(f"💾 Descargando resultado...")
    max_intentos_descarga = 3
    session_descarga = boto3.Session(region_name=ATHENA_REGION)
    
    for intento in range(1, max_intentos_descarga + 1):
        try:
            descargar_desde_s3(result_location, output_file, boto3_session=session_descarga)
            break
        except Exception as e:
            error_msg = str(e)
            if 'ExpiredToken' in error_msg or 'expired' in error_msg.lower():
                print(f"\n⚠️  Token expirado durante descarga")
                if intento < max_intentos_descarga:
                    print(f"   Intento {intento}/{max_intentos_descarga}")
                    if solicitar_renovacion_token():
                        # CLAVE: Recrear sesión con nuevas credenciales
                        print("🔄 Recreando sesión de boto3 para descarga...")
                        session_descarga = boto3.Session(region_name=ATHENA_REGION)
                        print(f"   Reintentando descarga...")
                        continue
                    else:
                        raise Exception("No se pudo renovar el token AWS")
                else:
                    raise Exception("Se agotaron los intentos para descargar")
            else:
                raise
    
    print(f"✅ Completado: {output_file}\n")
    
    return output_file


def crear_session_boto3_fresca():
    """
    Crea una sesión boto3 completamente nueva forzando recarga de credenciales
    """
    # Limpiar TODAS las variables de entorno de AWS
    for key in list(os.environ.keys()):
        if key.startswith('AWS_'):
            del os.environ[key]
    
    # Limpiar el DEFAULT_SESSION global de boto3
    import boto3
    boto3.DEFAULT_SESSION = None
    
    # Crear nueva sesión SIN cache
    session = boto3.Session(region_name=ATHENA_REGION)
    
    return session


def verificar_credenciales_aws():
    """
    Verifica si las credenciales de AWS están activas
    IMPORTANTE: Usa sesión fresca para evitar cache
    
    Returns:
        bool: True si las credenciales están activas, False si no
    """
    try:
        # Crear sesión fresca para verificar (sin cache)
        session = crear_session_boto3_fresca()
        sts_client = session.client('sts')
        sts_client.get_caller_identity()
        return True
    except Exception:
        return False


def solicitar_renovacion_token():
    """
    Pausa el programa y solicita renovación del token AWS
    
    Returns:
        bool: True si el token fue renovado, False si no
    """
    print("\n" + "=" * 80)
    print("⚠️  TOKEN AWS EXPIRADO")
    print("=" * 80)
    print("\nEl token de seguridad AWS ha expirado durante la ejecución.")
    print("\n📋 Para continuar:")
    print("   1. Abre OTRA TERMINAL (no esta)")
    print("   2. Ejecuta: aws-azure-login --profile default --mode=gui")
    print("   3. Completa el login en el navegador")
    print("   4. Espera ver 'Assuming role...' en esa terminal")
    print("   5. Vuelve AQUÍ y presiona ENTER\n")
    print("=" * 80)
    
    input("Presiona ENTER cuando hayas renovado el token...")
    
    # Esperar propagación
    print("\n⏳ Esperando 5 segundos para que las credenciales se propaguen...")
    time.sleep(5)
    
    # Forzar recarga COMPLETA
    print("🔄 Recargando credenciales de boto3...")
    
    # Verificar token con sesión completamente nueva
    print("🔐 Verificando token renovado...")
    
    max_verificaciones = 3
    for intento in range(1, max_verificaciones + 1):
        try:
            # Crear sesión NUEVA para cada verificación
            test_session = crear_session_boto3_fresca()
            sts = test_session.client('sts')
            sts.get_caller_identity()
            print("✅ Token renovado correctamente. Continuando...\n")
            return True
        except Exception as e:
            if intento < max_verificaciones:
                print(f"⚠️  Intento {intento}/{max_verificaciones} - Token aún no válido")
                print(f"   Esperando 3 segundos más...")
                time.sleep(3)
            else:
                print("\n❌ El token sigue sin ser válido después de varios intentos.")
                print("\n📋 Diagnóstico:")
                print("   Abre OTRA TERMINAL y ejecuta:")
                print("   aws sts get-caller-identity")
                print("\n   Si funciona → Las credenciales están OK, es problema de timing")
                print("   Si falla → El login no funcionó correctamente\n")
                
                respuesta = input("¿Intentar continuar de todas formas? (s/n): ").strip().lower()
                return respuesta == 's'
    
    return False




def obtener_datos_athena():
    """
    FUNCIÓN PRINCIPAL
    
    Ejecuta las 3 queries (Mensajes, Clicks, Botones) y descarga los resultados
    
    Returns:
        tuple: (mensajes_csv, clicks_csv, botones_csv)
    """
    print("\n" + "=" * 80)
    print("  AWS ATHENA - EJECUCIÓN AUTOMÁTICA DE QUERIES")
    print("=" * 80 + "\n")
    
    # Verificar credenciales AWS
    print("🔐 Verificando credenciales AWS...")
    if not verificar_credenciales_aws():
        print("\n❌ No hay credenciales AWS activas")
        print("\n⚠️  IMPORTANTE: Debes autenticarte primero con:")
        print("   aws-azure-login --profile default --mode=gui")
        print("\nEjecuta ese comando y luego vuelve a intentar.\n")
        raise Exception("Credenciales AWS no válidas o expiradas")
    
    print("✓ Credenciales AWS activas\n")
    
    # Leer configuración de fechas
    fecha_inicio, fecha_fin = leer_config_fechas()
    
    # Crear carpeta temporal si no existe
    if not os.path.exists('temp'):
        os.makedirs('temp')
        print(f"✓ Carpeta 'temp/' creada\n")
    
    # Advertencia
    print("\n⚠️  IMPORTANTE:")
    print("   Las queries en Athena pueden tardar 5-15 minutos cada una")
    print("   Escanean millones de registros")
    print("   ANTES de cada query se te pedirá revalidar credenciales AWS\n")

    # Ejecutar las 3 queries
    try:
        # Query 1: Mensajes
        print("\n" + "=" * 60)
        print("  QUERY 1 de 3: Mensajes.sql")
        print("=" * 60)
        print("\n🔐 ANTES DE CONTINUAR, revalida tus credenciales AWS:")
        print("   Ejecuta en otra terminal: aws-azure-login --profile default --mode=gui\n")
        input("Presiona Enter cuando hayas revalidado las credenciales...")

        mensajes_csv = ejecutar_y_descargar(
            'Mensajes.sql',
            fecha_inicio,
            fecha_fin,
            'temp/mensajes_temp.csv'
        )

        # Query 2: Clicks
        print("\n" + "=" * 60)
        print("  QUERY 2 de 3: Clicks.sql")
        print("=" * 60)
        print("\n🔐 ANTES DE CONTINUAR, revalida tus credenciales AWS:")
        print("   Ejecuta en otra terminal: aws-azure-login --profile default --mode=gui\n")
        input("Presiona Enter cuando hayas revalidado las credenciales...")

        clicks_csv = ejecutar_y_descargar(
            'Clicks.sql',
            fecha_inicio,
            fecha_fin,
            'temp/clicks_temp.csv'
        )

        # Query 3: Botones
        print("\n" + "=" * 60)
        print("  QUERY 3 de 3: Botones.sql")
        print("=" * 60)
        print("\n🔐 ANTES DE CONTINUAR, revalida tus credenciales AWS:")
        print("   Ejecuta en otra terminal: aws-azure-login --profile default --mode=gui\n")
        input("Presiona Enter cuando hayas revalidado las credenciales...")

        botones_csv = ejecutar_y_descargar(
            'Botones.sql',
            fecha_inicio,
            fecha_fin,
            'temp/botones_temp.csv'
        )
        
        # Resumen
        print("\n" + "=" * 80)
        print("  ✅ TODAS LAS QUERIES EJECUTADAS EXITOSAMENTE")
        print("=" * 80)
        print(f"\n📂 Archivos generados:")
        print(f"   ├─ {mensajes_csv}")
        print(f"   ├─ {clicks_csv}")
        print(f"   └─ {botones_csv}\n")
        
        return mensajes_csv, clicks_csv, botones_csv
    
    except Exception as e:
        print("\n" + "=" * 80)
        print("  ❌ ERROR EN EJECUCIÓN")
        print("=" * 80)
        print(f"\n{str(e)}\n")
        raise


# =============================================================================
# MODO PRUEBA
# =============================================================================

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                      ATHENA CONNECTOR - MODO PRUEBA                       ║
╚═══════════════════════════════════════════════════════════════════════════╝

Este módulo ejecutará las 3 queries de Athena y descargará los resultados.

Requisitos:
  ✓ aws-azure-login configurado
  ✓ Sesión activa de AWS (ejecutar login antes)
  ✓ config_fechas.txt con fechas configuradas
  ✓ Mensajes.sql, Clicks.sql, Botones.sql presentes

⚠️  AUTENTICACIÓN AWS-AZURE:
   Primera vez (configuración):
     aws-azure-login --configure --profile default
   
   Antes de ejecutar este script:
     aws-azure-login --profile default --mode=gui

Configuración actual:
  Database:  {ATHENA_DATABASE}
  Workgroup: {ATHENA_WORKGROUP}
  Bucket:    Configurado en workgroup
  Región:    {ATHENA_REGION}

""")
    
    # Verificar credenciales
    print("🔐 Verificando credenciales AWS...")
    if not verificar_credenciales_aws():
        print("\n❌ No hay credenciales AWS activas")
        print("\n⚠️  Ejecuta primero:")
        print("   aws-azure-login --profile default --mode=gui")
        print("\nLuego vuelve a ejecutar este script.\n")
        exit(1)
    
    print("✓ Credenciales AWS activas\n")
    input("Presiona Enter para continuar...")
    
    # Ejecutar
    try:
        mensajes, clicks, botones = obtener_datos_athena()
        
        print("╔═══════════════════════════════════════════════════════════════════════════╗")
        print("║                             ✅ PROCESO EXITOSO                            ║")
        print("╚═══════════════════════════════════════════════════════════════════════════╝")
        print("\nLos archivos están listos para ser procesados por el script de métricas.\n")
        
    except Exception as e:
        print("╔═══════════════════════════════════════════════════════════════════════════╗")
        print("║                              ❌ ERROR FATAL                               ║")
        print("╚═══════════════════════════════════════════════════════════════════════════╝")
        print(f"\n{str(e)}\n")
        exit(1)

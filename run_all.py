#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Script Maestro - Ejecuta todos los módulos de Metricas_Boti_Mensual

Este script:
1. Verifica autenticación AWS
2. Lee configuración de fechas
3. Ejecuta todos los módulos secuencialmente
4. Genera reporte consolidado
5. Muestra resumen de ejecución

Uso:
    python run_all.py
'''
import subprocess
import sys
import os
from datetime import datetime
import time

# ==================== CONFIGURACIÓN ====================
MODULOS = [
    {
        'nombre': 'Usuarios y Conversaciones',
        'carpeta': 'Metricas_Boti_Conversaciones_Usuarios',
        'script': 'Usuarios_Conversaciones.py',
        'celdas': 'D2, D3',
        'requiere_aws': True
    },
    {
        'nombre': 'Pushes Enviadas',
        'carpeta': 'Pushes_Enviadas',
        'script': 'Pushes_Enviadas.py',
        'celdas': 'D6',
        'requiere_aws': True
    },
    {
        'nombre': 'Sesiones Abiertas por Pushes',
        'carpeta': 'Sesiones_Abiertas_Pushes',
        'script': 'Sesiones_Abiertas_porPushes.py',
        'celdas': 'D4',
        'requiere_aws': True
    },
    {
        'nombre': 'Sesiones Alcanzadas por Pushes',
        'carpeta': 'Sesiones_alcanzadas_pushes',
        'script': 'Sesiones_Alcanzadas.py',
        'celdas': 'D5',
        'requiere_aws': True
    },
    {
        'nombre': 'No Entendimiento',
        'carpeta': 'No_Entendidos',
        'scripts': ['athena_connector.py', 'No_Entendidos.py'],  # Ejecutar ambos en orden
        'celdas': 'D13',
        'requiere_aws': True
    },
    {
        'nombre': 'Feedback - Efectividad',
        'carpeta': 'Feedback_Efectividad',
        'script': 'Feedback_Efectividad.py',
        'celdas': 'D14',
        'requiere_aws': True
    },
    {
        'nombre': 'Feedback - CES',
        'carpeta': 'Feedback_CES',
        'script': 'Feedback_CES.py',
        'celdas': 'D15',
        'requiere_aws': True
    },
    {
        'nombre': 'Feedback - CSAT',
        'carpeta': 'Feedback_CSAT',
        'script': 'Feedback_CSAT.py',
        'celdas': 'D16',
        'requiere_aws': True
    },
    {
        'nombre': 'Disponibilidad WhatsApp',
        'carpeta': 'Metricas_Boti_Disponibilidad',
        'script': 'WhatsApp_Availability.py',
        'celdas': 'D17',
        'requiere_aws': False
    }
]

# ==================== FUNCIONES ====================

def print_header(text, char='='):
    '''Imprime un header formateado'''
    print("\n" + char * 70)
    print(f"  {text}")
    print(char * 70 + "\n")

def print_section(text):
    '''Imprime una sección'''
    print(f"\n{'─' * 70}")
    print(f"  {text}")
    print('─' * 70)

def verificar_aws_auth():
    '''Verifica si hay credenciales AWS válidas'''
    print("🔐 Verificando autenticación AWS...")
    try:
        result = subprocess.run(
            ['aws', 'sts', 'get-caller-identity'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ Autenticación AWS válida")
            return True
        else:
            print("❌ No hay credenciales AWS válidas")
            return False
    except FileNotFoundError:
        print("❌ AWS CLI no está instalado")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Timeout al verificar credenciales AWS")
        return False
    except Exception as e:
        print(f"❌ Error al verificar AWS: {str(e)}")
        return False

def verificar_config():
    '''Verifica que exista el archivo de configuración'''
    print("⚙️  Verificando configuración de fechas...")
    if os.path.exists('config_fechas.txt'):
        print("✅ Archivo config_fechas.txt encontrado")
        return True
    else:
        print("❌ No se encuentra config_fechas.txt")
        return False

def leer_config_fechas():
    '''Lee y muestra la configuración de fechas'''
    try:
        with open('config_fechas.txt', 'r', encoding='utf-8') as f:
            mes = None
            anio = None
            fecha_inicio = None
            fecha_fin = None
            
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if line.startswith('MES='):
                    mes = line.split('=')[1].strip()
                elif line.startswith('AÑO=') or line.startswith('ANO='):
                    anio = line.split('=')[1].strip()
                elif line.startswith('FECHA_INICIO='):
                    fecha_inicio = line.split('=')[1].strip()
                elif line.startswith('FECHA_FIN='):
                    fecha_fin = line.split('=')[1].strip()
            
            if fecha_inicio and fecha_fin:
                print(f"📅 Período: {fecha_inicio} al {fecha_fin} (rango personalizado)")
                return True
            elif mes and anio:
                meses = {
                    '1': 'enero', '2': 'febrero', '3': 'marzo', '4': 'abril',
                    '5': 'mayo', '6': 'junio', '7': 'julio', '8': 'agosto',
                    '9': 'septiembre', '10': 'octubre', '11': 'noviembre', '12': 'diciembre'
                }
                mes_nombre = meses.get(mes, f"mes {mes}")
                print(f"📅 Período: {mes_nombre} {anio} (mes completo)")
                return True
            else:
                print("⚠️  No se pudo leer la configuración de fechas")
                return False
    except Exception as e:
        print(f"❌ Error al leer config: {str(e)}")
        return False

def ejecutar_modulo(modulo, numero, total):
    '''Ejecuta un módulo específico (soporta uno o múltiples scripts)'''
    print_section(f"[{numero}/{total}] {modulo['nombre']}")
    print(f"📊 Celdas Excel: {modulo['celdas']}")
    print(f"📂 Carpeta: {modulo['carpeta']}")

    # Determinar si hay uno o múltiples scripts
    if 'scripts' in modulo:
        scripts = modulo['scripts']
        print(f"🐍 Scripts: {', '.join(scripts)}")
    else:
        scripts = [modulo['script']]
        print(f"🐍 Script: {modulo['script']}")

    if modulo['requiere_aws']:
        print(f"🔐 Requiere AWS: Sí")
    else:
        print(f"🔐 Requiere AWS: No")

    print("\n⏳ Ejecutando...")

    inicio = time.time()

    try:
        # Cambiar al directorio del módulo
        os.chdir(modulo['carpeta'])

        # Ejecutar todos los scripts en orden
        for idx, script in enumerate(scripts, 1):
            if len(scripts) > 1:
                print(f"\n  [{idx}/{len(scripts)}] Ejecutando {script}...")

            result = subprocess.run(
                [sys.executable, script],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )

            if result.returncode != 0:
                # Volver al directorio raíz
                os.chdir('..')
                fin = time.time()
                duracion = fin - inicio

                print(f"  ❌ Error en {script}")
                print(f"\n  Salida de error:")
                print(result.stderr[-500:] if len(result.stderr) > 500 else result.stderr)
                return {
                    'nombre': modulo['nombre'],
                    'exitoso': False,
                    'duracion': duracion,
                    'mensaje': f'Error en {script}'
                }
            else:
                if len(scripts) > 1:
                    print(f"  ✅ {script} completado")

        # Volver al directorio raíz
        os.chdir('..')

        fin = time.time()
        duracion = fin - inicio

        print(f"✅ Completado en {duracion:.1f} segundos")
        return {
            'nombre': modulo['nombre'],
            'exitoso': True,
            'duracion': duracion,
            'mensaje': 'OK'
        }

    except Exception as e:
        os.chdir('..')  # Asegurar que volvemos a raíz
        fin = time.time()
        duracion = fin - inicio
        print(f"❌ Excepción: {str(e)}")
        return {
            'nombre': modulo['nombre'],
            'exitoso': False,
            'duracion': duracion,
            'mensaje': str(e)
        }

def mostrar_resumen(resultados, tiempo_total):
    '''Muestra un resumen de la ejecución'''
    print_header("RESUMEN DE EJECUCIÓN", '=')
    
    exitosos = sum(1 for r in resultados if r['exitoso'])
    fallidos = len(resultados) - exitosos
    
    print(f"📊 Total de módulos: {len(resultados)}")
    print(f"✅ Exitosos: {exitosos}")
    print(f"❌ Fallidos: {fallidos}")
    print(f"⏱️  Tiempo total: {tiempo_total:.1f} segundos ({tiempo_total/60:.1f} minutos)")
    
    print("\n📋 Detalle por módulo:")
    print("-" * 70)
    
    for i, r in enumerate(resultados, 1):
        estado = "✅" if r['exitoso'] else "❌"
        print(f"{i}. {estado} {r['nombre']}")
        print(f"   ⏱️  {r['duracion']:.1f}s - {r['mensaje']}")
    
    if exitosos == len(resultados):
        print("\n" + "=" * 70)
        print("🎉 ¡TODOS LOS MÓDULOS SE EJECUTARON EXITOSAMENTE!")
        print("=" * 70)
        print("\n💡 Próximo paso: Ejecutar el consolidador de Excel")
        print("   python consolidar_excel.py")
    else:
        print("\n" + "=" * 70)
        print("⚠️  ALGUNOS MÓDULOS FALLARON")
        print("=" * 70)
        print("\n📝 Revisar los errores arriba y corregir antes de consolidar")

def main():
    '''Función principal'''
    print_header("SCRIPT MAESTRO - Metricas_Boti_Mensual")
    
    print("Este script ejecutará los siguientes módulos:")
    for i, modulo in enumerate(MODULOS, 1):
        print(f"  {i}. {modulo['nombre']} ({modulo['celdas']})")
    
    print("\n⚠️  IMPORTANTE: Este proceso puede tardar varios minutos")
    
    # Verificaciones previas
    print_section("VERIFICACIONES PREVIAS")
    
    if not verificar_config():
        print("\n❌ Configuración inválida. Abortando.")
        sys.exit(1)
    
    if not leer_config_fechas():
        print("\n❌ No se pudo leer el período. Abortando.")
        sys.exit(1)
    
    # Verificar AWS solo si hay módulos que lo requieren
    requiere_aws = any(m['requiere_aws'] for m in MODULOS)
    if requiere_aws:
        if not verificar_aws_auth():
            print("\n❌ Autenticación AWS requerida. Ejecutar:")
            print("   aws-azure-login --profile default --mode=gui")
            print("\nAbortando.")
            sys.exit(1)
    
    # Iniciar ejecución automáticamente
    print("\n" + "=" * 70)
    print("🚀 Iniciando ejecución automática...")
    print("=" * 70)
    
    # Ejecutar módulos
    print_header("EJECUTANDO MÓDULOS")
    
    inicio_total = time.time()
    resultados = []
    
    for i, modulo in enumerate(MODULOS, 1):
        resultado = ejecutar_modulo(modulo, i, len(MODULOS))
        resultados.append(resultado)
        
        if i < len(MODULOS):
            print("\n⏸️  Pausa de 2 segundos antes del siguiente módulo...")
            time.sleep(2)
    
    fin_total = time.time()
    tiempo_total = fin_total - inicio_total
    
    # Mostrar resumen
    mostrar_resumen(resultados, tiempo_total)
    
    print("\n" + "=" * 70)
    print(f"🕐 Finalizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()

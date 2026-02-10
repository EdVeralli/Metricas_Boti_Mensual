# -*- coding: utf-8 -*-
'''
Script para descargar y procesar Contenidos Consultados desde Athena
Descarga la vista boti_vw_buscador_rulename y genera tabla completa de contenidos.

Lógica extraída del Power BI "Consultas por dia 1.pbix":
1. Filtrar por rango de fechas del período
2. Excluir contenidos no relevantes (onboardings, pushes, bifurcadores, etc.)
3. Agrupar por rulename y sumar sesiones
4. Mostrar TODOS los contenidos con % del total
5. Generar serie temporal diaria (Histórico)

MODOS SOPORTADOS:
1. MES COMPLETO: Especificar MES y AÑO
2. RANGO PERSONALIZADO: Especificar FECHA_INICIO y FECHA_FIN

Workgroup: Production-caba-piba-athena-boti-group
Rol: PIBAConsumeBoti
'''
import boto3
import awswrangler as wr
import pandas as pd
from datetime import datetime
from calendar import monthrange
import os
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill

# ==================== CONFIGURACION ====================
CONFIG = {
    'region': 'us-east-1',
    'workgroup': 'Production-caba-piba-athena-boti-group',
    'database': 'caba-piba-consume-zone-db',
    'output_folder': 'output',
    'config_file': '../config_fechas.txt'  # Config centralizado en raiz del proyecto
}

# Flag para activar/desactivar las exclusiones de contenidos.
# Poner en False para ver TODOS los contenidos sin filtrar.
APLICAR_EXCLUSIONES = True

# Lista de contenidos a EXCLUIR (extraída del Power BI)
# Incluye: onboardings, pushes, bifurcadores, feedback, login, menús internos, etc.
CONTENIDOS_EXCLUIR = [
    # Onboardings
    'Onboarding Principal',
    'Onboarding Agendame soy Boti',
    'Onboarding Temporal en BA - Alerta Amarilla',
    'Onboarding Temporal en BA - Alerta Naranja',
    'Onboarding Coyuntura (21 de agosto - extensión línea D)',
    'Onboarding Coyuntura (5/8) - Semana Mundial de la Lactancia',
    'Onboarding Coyuntura (subte – cierre Plaza Italia 11/8)',
    'Onboarding Coyuntura Día de la Niñez - finde largo agosto',
    'Onboarding Coyuntura línea D (cierre de estación Agüero + partido River)',
    'Onboarding Coyuntura – Subte A, estación Loria (cierre 20/10)',
    'Coyuntura (cierre de estación Carlos Gardel línea B)',

    # Bifurcadores
    'Bifurcador OB trámites y turnos',
    'BOT02CUX03 Bifurcador',
    'DDHH03CUX01 Bifurcador corto derechos',
    'DDHH03CUX01 Bifurcador derechos',
    'DH11CUX01 Bifurcador',
    'SUA01CUX17 Bifurcador pintura o hidrolavado',
    'TU01CUX03 Bifurcador Colas Atención - Paso 2 Español',

    # Login y miBA
    '3. Login miBA',
    '3.1 Login miBA',
    'miBA - Login exitoso',
    'IN01CAT01 miBA Login para Infracciones',

    # Menús y navegación
    'MENU PRINCIPAL 2.0',
    'Menú show buttons',
    'Más temas post Menú 2.0',

    # Feedback (CXF)
    'CXF01CUX00 Preapertura',
    'CXF01CUX01 P1 Integraciones',
    'CXF01CUX02 P1 Estáticos',
    'CXF01CUX03 P2 Pushes',
    'CXF01CUX03 Sí Pushes',
    'cxf01push01_feedbackpushes2',

    # Atención y cierre
    'Atiende agente',
    'Transferir con un agente',
    '147 - ¿Te puedo ayudar en algo más?',
    'Cierre sin despedida + Feed back',
    'Cancelar',

    # No entendidos
    'Instancia 1 | No entendidos',
    'No entendió letra no existente en WA',
    'No, nada de eso',
    'X. Buscaba otra cosa',

    # Otros internos
    'TUR01CUX13 Preguntar género',
    'MO05CUX01 - Sexo',
    'USIG - Preguntar calle y dirección (sin send location)',
    'Invocar servicio de infracciones',
    'Puede estacionar CTA',
    'Licencia prorroga  > Consultar',

    # Pushes de Salud
    'button_PushSalud_Confirmacion',
    'button_PushSalud_Cancelacion',
    'button_PushSalud_hayUnError',
    'SA01PUSH01 - Confirmar turno',
    'SA01PUSH03 Reprogramación',
    'SA06PUSH0 - Hay un error',
    'sa01push01_cancelar_turno_fallido',
    'sa01push01api_telefono',
    'sa01push01apiconfir_video',
    'sa01push01cc',
    'sa01push02api_presencial',
    'sa01push03_cancelacion_turno_api',
    'sa01push03apirec_video72',
    'sa01push04api_telefono',
    'sa01push05_demandainsatisfecha',
    'sa01push05api_presencial',
    'sa01push06api_video',
    'sa01push06apirec_video24',
    'sa01push09api_presencial',
    'sa01push10api_video',
    'sa01push11api_telefono',
    'sa03push03_telemedicina',

    # Pushes de Educación
    'edu06push02_ausentismo_mensajegeneral',
    'edu06push02_inicial_mensaje3',
    'edu06push02_primariaysecundaria_mensaje1',
    'edu06push02_primariaysecundaria_msj2',
    'edu06push02_primariaysecundaria_mensaje3_v2',
    'edu06push02_recordatorioinscripcion2026',
    'edu10push02_inscripcion_secundaria_v2',
    'edu10push02_tt2025_certificado',
    'edu10push02_tt2025_confirmacionvacante_adultos_v3',
    'edu10push02_tt2025_confirmacionvacante_secundaria_v4',
    'edu10push02_tt2025_primeraclase_adultos',

    # Pushes de Empleo
    'em01push01_expoempleo_confirmacion_agosto2025',
    'em01push01_expoempleo_confirmacion_agosto2025_v2',
    'em01push01_expoempleooctubre_confirmacion',

    # Pushes de SIGECI
    'sigeci_confirmacion_01',
    'sigeci_confirmacion_02',
    'sigeci_confirmacion_04',
    'sigeci_recordatorio_01',
    'sigeci_recordatorio_02',
    'sigeci_recordatorio_04',
    'testpush_audiencia_sigeci_v1',
    'testpush_sigeci_audiencia_demo',

    # Pushes de SUA
    'sua01push0api_iniciodesolicitud',
    'sua01push0api_solicitudrechazada',
    'sua01push0api_solicitudresuelta',

    # Pushes de Derechos Humanos
    'dh02push01api_encuesta',
    'dh02push01api_exito',
    'dh02push01api_intermedio_v2',
    'dh02push01api_persona_no_acepta_ayuda',
    'dh02push01api_persona_no_encontrada',
    'dh02push01api_seguimiento',

    # Otros pushes
    'bo01push02_baestademoda',
    'bo01push02_dinoenparquethays',
    'bo01push02_eventodiadelnino',
    'bo01push02_finde29agosto',
    'bo01push02_mundialdelalfajor',
    'bo01push02_mundialdetango2025',
    'bo02push03_recordatorioinscripcioncursos',
    'bo02push04_leypymes',
    'bo03push02_diadelaninez',
    'bo03push02_diadelaninez_v2',
    'bo03push03_escuelaenfamiliaprimaria',
    'bo03push04_inscripcionsecundaria_ultimosdias',
    'bo04push01_internetsegura',
    'bo06push01_parquechabuco_servicios',
    'bo06push01_serviciosenbarrios_general',
    'ciu01push01_encuestahorares',
    'mo05push01_renovacionproxavencer_ut',
    'PUSH00CUX01 Desuscripción',
]

# ==================== FUNCIONES ====================

def read_date_config(config_file):
    '''
    Lee el archivo de configuracion y determina el modo:
    - MODO 1: MES + AÑO (mes completo)
    - MODO 2: FECHA_INICIO + FECHA_FIN (rango personalizado)

    Retorna: (modo, fecha_inicio, fecha_fin, mes, anio, descripcion)
    '''
    try:
        if not os.path.exists(config_file):
            print("[ERROR] No se encuentra el archivo: {}".format(config_file))
            print("    Creando archivo de ejemplo...")

            with open(config_file, 'w', encoding='utf-8') as f:
                f.write("# Configuracion de fechas para el reporte\n")
                f.write("# MODO 1: Mes completo\n")
                f.write("MES=1\n")
                f.write("AÑO=2026\n\n")
                f.write("# MODO 2: Rango personalizado\n")
                f.write("# FECHA_INICIO=2026-01-01\n")
                f.write("# FECHA_FIN=2026-01-31\n")

            print("    Archivo creado: {}".format(config_file))
            return 'mes', None, None, 1, 2026, "enero 2026"

        mes = None
        anio = None
        fecha_inicio_str = None
        fecha_fin_str = None

        with open(config_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                if line.startswith('MES='):
                    mes_str = line.split('=')[1].strip()
                    mes = int(mes_str)

                if line.startswith('AÑO=') or line.startswith('ANO='):
                    anio_str = line.split('=')[1].strip()
                    anio = int(anio_str)

                if line.startswith('FECHA_INICIO='):
                    fecha_inicio_str = line.split('=')[1].strip()

                if line.startswith('FECHA_FIN='):
                    fecha_fin_str = line.split('=')[1].strip()

        # PRIORIDAD: Si hay FECHA_INICIO y FECHA_FIN, usar MODO 2
        if fecha_inicio_str and fecha_fin_str:
            try:
                fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
                fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d')

                if fecha_inicio > fecha_fin:
                    print("[ERROR] FECHA_INICIO no puede ser posterior a FECHA_FIN")
                    return None, None, None, None, None, None

                descripcion = "{} al {}".format(
                    fecha_inicio.strftime('%d/%m/%Y'),
                    fecha_fin.strftime('%d/%m/%Y')
                )

                print("[INFO] Modo: RANGO PERSONALIZADO")
                return 'rango', fecha_inicio_str, fecha_fin_str, None, None, descripcion

            except ValueError as e:
                print("[ERROR] Formato de fecha invalido. Use YYYY-MM-DD (ej: 2026-01-01)")
                return None, None, None, None, None, None

        # Si no hay rango, usar MODO 1 (mes completo)
        if mes is not None and anio is not None:
            if mes < 1 or mes > 12:
                print("[ERROR] Mes invalido: {}. Debe estar entre 1 y 12".format(mes))
                return None, None, None, None, None, None

            if anio < 2020 or anio > 2030:
                print("[ADVERTENCIA] Año inusual: {}".format(anio))

            primer_dia = 1
            ultimo_dia = monthrange(anio, mes)[1]
            fecha_inicio_str = "{:04d}-{:02d}-{:02d}".format(anio, mes, primer_dia)
            fecha_fin_str = "{:04d}-{:02d}-{:02d}".format(anio, mes, ultimo_dia)

            mes_nombre = get_month_name(mes)
            descripcion = "{} {}".format(mes_nombre, anio)

            print("[INFO] Modo: MES COMPLETO")
            return 'mes', fecha_inicio_str, fecha_fin_str, mes, anio, descripcion

        print("[ERROR] El archivo {} no contiene configuracion valida".format(config_file))
        return None, None, None, None, None, None

    except Exception as e:
        print("[ERROR] Error leyendo archivo de configuracion: {}".format(str(e)))
        return None, None, None, None, None, None

def get_month_name(mes):
    '''Retorna el nombre del mes en español'''
    if mes is None:
        return 'rango'
    meses = {
        1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
        5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
        9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
    }
    return meses.get(mes, 'mes_invalido')

def get_month_abbr(mes):
    '''Retorna la abreviatura del mes en español'''
    if mes is None:
        return 'rango'
    meses = {
        1: 'ene', 2: 'feb', 3: 'mar', 4: 'abr',
        5: 'may', 6: 'jun', 7: 'jul', 8: 'ago',
        9: 'sep', 10: 'oct', 11: 'nov', 12: 'dic'
    }
    return meses.get(mes, 'mes')

def build_query():
    '''Construye la query para descargar la vista de contenidos consultados'''
    query = 'SELECT * FROM "caba-piba-consume-zone-db"."boti_vw_buscador_rulename"'
    return query

def generate_filename(modo, mes, anio, fecha_inicio, fecha_fin):
    '''Genera los nombres de archivos basados en el modo y las fechas'''
    if modo == 'mes':
        mes_nombre = get_month_name(mes)
        filename_csv = "contenidos_consultados_{0}_{1}.csv".format(mes_nombre, anio)
        filename_detalle = "contenidos_consultados_detalle_{0}_{1}.xlsx".format(mes_nombre, anio)
        filename_dashboard = "contenidos_consultados_{0}_{1}.xlsx".format(mes_nombre, anio)
    else:
        fecha_inicio_fmt = fecha_inicio.replace('-', '')
        fecha_fin_fmt = fecha_fin.replace('-', '')
        filename_csv = "contenidos_consultados_{0}_a_{1}.csv".format(fecha_inicio_fmt, fecha_fin_fmt)
        filename_detalle = "contenidos_consultados_detalle_{0}_a_{1}.xlsx".format(fecha_inicio_fmt, fecha_fin_fmt)
        filename_dashboard = "contenidos_consultados_{0}_a_{1}.xlsx".format(fecha_inicio_fmt, fecha_fin_fmt)

    return filename_csv, filename_detalle, filename_dashboard

def procesar_contenidos(df, fecha_inicio, fecha_fin):
    '''
    Procesa el DataFrame descargado y calcula las métricas de contenidos consultados.

    Lógica (extraída del Power BI "Consultas por dia 1"):
    1. Filtrar por rango de fechas
    2. Excluir contenidos no relevantes (si APLICAR_EXCLUSIONES está activo)
    3. Agrupar por rulename y sumar sesiones
    4. Calcular %GT (porcentaje del gran total)
    5. Agrupar por fecha para serie temporal diaria

    Retorna: (df_contenidos, total_contenidos, df_historico)
    '''
    print("    [INFO] Procesando datos...")

    # Normalizar nombres de columnas
    df.columns = df.columns.str.lower().str.strip()

    # Mostrar columnas disponibles
    print("    [INFO] Columnas disponibles: {}".format(', '.join(df.columns.tolist())))

    # Detectar columna de fecha
    fecha_col = None
    for col in ['fecha', 'date', 'session_date', 'dia']:
        if col in df.columns:
            fecha_col = col
            break

    # Detectar columna de rulename
    rulename_col = None
    for col in ['rulename', 'rule_name', 'rulename_con_max_sesiones', 'contenido']:
        if col in df.columns:
            rulename_col = col
            break

    # Detectar columna de sesiones
    sesiones_col = None
    for col in ['suma_de_sesiones_diarias', 'sesiones_diarias', 'max_sesiones_diarias', 'sesiones', 'cant_sesiones', 'count']:
        if col in df.columns:
            sesiones_col = col
            break

    if rulename_col is None:
        print("    [ERROR] No se encontró columna de rulename")
        return None, None, None

    if sesiones_col is None:
        print("    [ERROR] No se encontró columna de sesiones")
        return None, None, None

    print("    [INFO] Usando columnas: rulename='{}', sesiones='{}'".format(rulename_col, sesiones_col))

    df_filtrado = df.copy()

    # 1. Filtrar por fecha si existe la columna
    if fecha_col:
        print("    [INFO] Filtrando por fecha: {} a {}".format(fecha_inicio, fecha_fin))
        df_filtrado[fecha_col] = pd.to_datetime(df_filtrado[fecha_col])
        fecha_inicio_dt = pd.to_datetime(fecha_inicio)
        fecha_fin_dt = pd.to_datetime(fecha_fin)
        df_filtrado = df_filtrado[
            (df_filtrado[fecha_col] >= fecha_inicio_dt) &
            (df_filtrado[fecha_col] <= fecha_fin_dt)
        ]
        print("    [INFO] Registros después de filtro de fecha: {:,}".format(len(df_filtrado)))

    # 2. Excluir contenidos no relevantes
    if APLICAR_EXCLUSIONES:
        print("    [INFO] Excluyendo {} contenidos no relevantes...".format(len(CONTENIDOS_EXCLUIR)))
        df_filtrado = df_filtrado[~df_filtrado[rulename_col].isin(CONTENIDOS_EXCLUIR)]
        print("    [INFO] Registros después de exclusiones: {:,}".format(len(df_filtrado)))
    else:
        print("    [INFO] Exclusiones DESACTIVADAS (APLICAR_EXCLUSIONES = False)")

    # 3. Agrupar por rulename y sumar sesiones
    df_agrupado = df_filtrado.groupby(rulename_col)[sesiones_col].sum().reset_index()
    df_agrupado.columns = ['Rulename', 'Suma de Sesiones']

    # 4. Ordenar descendente
    df_agrupado = df_agrupado.sort_values('Suma de Sesiones', ascending=False).reset_index(drop=True)

    total_contenidos = len(df_agrupado)
    total_sesiones = df_agrupado['Suma de Sesiones'].sum()
    print("    [INFO] Total contenidos relevantes únicos: {:,}".format(total_contenidos))
    print("    [INFO] Total sesiones: {:,}".format(int(total_sesiones)))

    # 5. Calcular %GT (porcentaje del gran total)
    if total_sesiones > 0:
        df_agrupado['% del Total'] = df_agrupado['Suma de Sesiones'] / total_sesiones
    else:
        df_agrupado['% del Total'] = 0

    # 6. Serie temporal diaria (Histórico)
    df_historico = None
    if fecha_col:
        df_historico = df_filtrado.groupby(fecha_col)[sesiones_col].sum().reset_index()
        df_historico.columns = ['Fecha', 'Sesiones diarias']
        df_historico = df_historico.sort_values('Fecha').reset_index(drop=True)
        print("    [INFO] Días en serie temporal: {}".format(len(df_historico)))

    # Mostrar Top 10 en consola
    print("")
    print("    TOP 10 CONTENIDOS MÁS CONSULTADOS:")
    print("    " + "-" * 70)
    for idx, row in df_agrupado.head(10).iterrows():
        print("    {:2d}. {:45s} {:>10,}  ({:.2f}%)".format(
            idx + 1,
            row['Rulename'][:45],
            int(row['Suma de Sesiones']),
            row['% del Total'] * 100
        ))

    return df_agrupado, total_contenidos, df_historico

def create_detail_excel(filepath, df_contenidos, df_historico, descripcion):
    '''Crea un Excel con 2 hojas: Buscador de contenidos + Historico'''

    print("    [INFO] Creando Excel detallado...")

    wb = openpyxl.Workbook()

    # ===== HOJA 1: Buscador de contenidos =====
    ws = wb.active
    ws.title = 'Buscador de contenidos'

    # Estilos
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_font = Font(bold=True, size=11, color="FFFFFF")
    bold_font = Font(bold=True, size=11)
    card_font = Font(bold=True, size=12)
    card_value_font = Font(bold=True, size=14)

    total_contenidos = len(df_contenidos)
    total_sesiones = int(df_contenidos['Suma de Sesiones'].sum())

    # Cards en filas 1-2
    ws['A1'] = 'Cantidad de Rulenames'
    ws['A1'].font = card_font
    ws['B1'] = total_contenidos
    ws['B1'].font = card_value_font
    ws['B1'].number_format = '#,##0'

    ws['D1'] = 'Total Sesiones'
    ws['D1'].font = card_font
    ws['E1'] = total_sesiones
    ws['E1'].font = card_value_font
    ws['E1'].number_format = '#,##0'

    ws['A2'] = 'Período: {}'.format(descripcion)
    ws['A2'].font = Font(size=10, italic=True)

    # Headers de tabla (fila 4)
    ws['A4'] = 'Rulename'
    ws['B4'] = 'Suma de Sesiones'
    ws['C4'] = '% del Total'

    for col in ['A', 'B', 'C']:
        ws['{}4'.format(col)].font = header_font
        ws['{}4'.format(col)].fill = header_fill

    # Datos (todos los contenidos)
    for idx, row in df_contenidos.iterrows():
        fila = 5 + idx
        ws['A{}'.format(fila)] = row['Rulename']
        ws['B{}'.format(fila)] = int(row['Suma de Sesiones'])
        ws['B{}'.format(fila)].number_format = '#,##0'
        ws['C{}'.format(fila)] = row['% del Total']
        ws['C{}'.format(fila)].number_format = '0.00%'

    # Fila de totales
    fila_total = 5 + total_contenidos
    ws['A{}'.format(fila_total)] = 'TOTAL'
    ws['A{}'.format(fila_total)].font = bold_font
    ws['B{}'.format(fila_total)] = total_sesiones
    ws['B{}'.format(fila_total)].font = bold_font
    ws['B{}'.format(fila_total)].number_format = '#,##0'
    ws['C{}'.format(fila_total)] = 1.0
    ws['C{}'.format(fila_total)].font = bold_font
    ws['C{}'.format(fila_total)].number_format = '0.00%'

    # Ajustar anchos
    ws.column_dimensions['A'].width = 60
    ws.column_dimensions['B'].width = 18
    ws.column_dimensions['C'].width = 14
    ws.column_dimensions['D'].width = 18
    ws.column_dimensions['E'].width = 18

    # ===== HOJA 2: Historico =====
    if df_historico is not None and len(df_historico) > 0:
        ws2 = wb.create_sheet('Historico')

        # Headers
        ws2['A1'] = 'Fecha'
        ws2['B1'] = 'Sesiones diarias'
        ws2['A1'].font = header_font
        ws2['A1'].fill = header_fill
        ws2['B1'].font = header_font
        ws2['B1'].fill = header_fill

        # Datos
        for idx, row in df_historico.iterrows():
            fila = 2 + idx
            ws2['A{}'.format(fila)] = row['Fecha']
            ws2['A{}'.format(fila)].number_format = 'DD/MM/YYYY'
            ws2['B{}'.format(fila)] = int(row['Sesiones diarias'])
            ws2['B{}'.format(fila)].number_format = '#,##0'

        # Fila de total
        fila_total_hist = 2 + len(df_historico)
        ws2['A{}'.format(fila_total_hist)] = 'TOTAL'
        ws2['A{}'.format(fila_total_hist)].font = bold_font
        ws2['B{}'.format(fila_total_hist)] = int(df_historico['Sesiones diarias'].sum())
        ws2['B{}'.format(fila_total_hist)].font = bold_font
        ws2['B{}'.format(fila_total_hist)].number_format = '#,##0'

        # Ajustar anchos
        ws2.column_dimensions['A'].width = 15
        ws2.column_dimensions['B'].width = 18

    wb.save(filepath)
    print("    [OK] Excel detallado creado ({} contenidos, {} hojas)".format(
        total_contenidos,
        len(wb.sheetnames)
    ))

def format_top10_text(df_contenidos):
    '''
    Genera el texto formateado del Top 10 para la celda D11 del dashboard.
    Formato: "1- Nombre contenido: (123.456)\n2- Otro contenido: (78.901)\n..."
    '''
    top10 = df_contenidos.head(10)
    lines = []
    for idx, row in top10.iterrows():
        sesiones = int(row['Suma de Sesiones'])
        # Formato con punto como separador de miles (estilo argentino)
        sesiones_fmt = '{:,}'.format(sesiones).replace(',', '.')
        lines.append('{}- {}: ({})'.format(idx + 1, row['Rulename'], sesiones_fmt))
    return '\n'.join(lines)

def create_dashboard(filepath, valor_d11, modo, mes, anio, fecha_inicio, fecha_fin):
    '''
    Crea el Excel Dashboard con la estructura estándar.
    Llena SOLO la celda D11 (Contenidos más consultados - Top 10 formateado)
    '''

    print("    [INFO] Creando Dashboard...")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Dashboard'

    header_font = Font(bold=True)
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # Determinar el header de fecha
    if modo == 'mes':
        header_fecha = '{}-{}'.format(get_month_abbr(mes), str(anio)[-2:])
    else:
        fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d')
        header_fecha = '{}-{}'.format(
            fecha_inicio_obj.strftime('%d/%m'),
            fecha_fin_obj.strftime('%d/%m/%y')
        )

    # FILA 1: Encabezados
    ws['B1'] = 'Indicador'
    ws['C1'] = 'Descripción/Detalle'
    ws['D1'] = header_fecha
    ws['B1'].font = header_font
    ws['C1'].font = header_font
    ws['D1'].font = header_font

    # Filas 2-17: Indicadores
    ws['B2'] = 'Conversaciones'
    ws['C2'] = 'Q Conversaciones'

    ws['B3'] = 'Usuarios'
    ws['C3'] = 'Q Usuarios únicos'

    ws['B4'] = 'Sesiones abiertas por Pushes'
    ws['C4'] = 'Q Sesiones que se abrieron con una Push'

    ws['B5'] = 'Sesiones Alcanzadas por Pushes'
    ws['C5'] = 'Q Sesiones que recibieron al menos 1 Push'

    ws['B6'] = 'Mensajes Pushes Enviados'
    ws['C6'] = 'Q de mensajes enviados bajo el formato push'

    ws['B7'] = 'Contenidos en Botmaker'
    ws['C7'] = 'Contenidos prendidos en botmaker'

    ws['B8'] = 'Contenidos Prendidos para el USUARIO'
    ws['C8'] = 'Contenidos prendidos de cara al usuario (relevantes)'

    ws['B9'] = 'Interacciones'
    ws['C9'] = 'Q Interacciones'

    ws['B10'] = 'Trámites, solicitudes y turnos'
    ws['C10'] = 'Q Trámites, solicitudes y turnos disponibles'

    ws['B11'] = 'Contenidos más consultados'
    ws['C11'] = 'Q Contenidos con más interacciones en el mes'
    if valor_d11 is not None:
        ws['D11'] = valor_d11
        ws['D11'].alignment = Alignment(wrap_text=True, vertical='top')

    ws['B12'] = 'Derivaciones'
    ws['C12'] = 'Q Derivaciones'

    ws['B13'] = 'No entendimiento'
    ws['C13'] = 'Performance motor de búsqueda del nuevo modelo de IA'

    ws['B14'] = 'Tasa de Efectividad'
    ws['C14'] = 'Mide el porcentaje de usuarios que lograron su objetivo'

    ws['B15'] = 'CES (Customer Effort Score)'
    ws['C15'] = 'Mide la facilidad con la que los usuarios pueden interactuar'

    ws['B16'] = 'Satisfacción (CSAT)'
    ws['C16'] = 'Mide la satisfacción usando una escala de 1 a 5'

    ws['B17'] = 'Uptime servidor'
    ws['C17'] = 'Disponibilidad del servidor (% tiempo activo)'

    # Aplicar bordes a todas las celdas con datos
    for row in range(1, 18):
        for col in ['B', 'C', 'D']:
            ws['{}{}'.format(col, row)].border = border

    # Ajustar anchos
    ws.column_dimensions['B'].width = 35
    ws.column_dimensions['C'].width = 50
    ws.column_dimensions['D'].width = 50

    wb.save(filepath)

    if valor_d11 is not None:
        # Mostrar preview del Top 10
        preview = valor_d11.split('\n')[0]
        print("    [OK] Dashboard creado (D11 = Top 10, ej: {})".format(preview))
    else:
        print("    [OK] Dashboard creado (D11 vacío)")

def execute_query_and_save():
    '''Función principal que ejecuta la query y guarda los resultados'''

    print("Leyendo configuracion de fechas...")
    modo, fecha_inicio, fecha_fin, mes, anio, descripcion = read_date_config(CONFIG['config_file'])

    if modo is None:
        print("[ERROR] No se pudo obtener la configuracion. Abortando.")
        return None

    print("[OK] Configuracion leida correctamente")
    print("    Modo: {}".format(modo.upper()))
    print("    Periodo: {}".format(descripcion))
    print("    Fecha inicio: {}".format(fecha_inicio))
    print("    Fecha fin: {}".format(fecha_fin))

    query = build_query()

    print("")
    print("Configuracion AWS:")
    print("    Region: {}".format(CONFIG['region']))
    print("    Workgroup: {}".format(CONFIG['workgroup']))
    print("    Base de datos: {}".format(CONFIG['database']))

    print("")
    print("Query a ejecutar:")
    print("    {}".format(query))

    try:
        session = boto3.Session(region_name=CONFIG['region'])

        print("")
        print("Ejecutando consulta...")

        try:
            df = wr.athena.read_sql_query(
                sql=query,
                database=CONFIG['database'],
                workgroup=CONFIG['workgroup'],
                boto3_session=session,
                ctas_approach=False,
                unload_approach=False
            )
        except Exception as e:
            if 'workgroup' in str(e).lower():
                print("[ADVERTENCIA] Intentando sin workgroup...")
                df = wr.athena.read_sql_query(
                    sql=query,
                    database=CONFIG['database'],
                    boto3_session=session,
                    ctas_approach=False,
                    unload_approach=False
                )
            else:
                raise e

        print("[OK] Consulta ejecutada exitosamente!")

        # Verificar resultados
        if len(df) == 0:
            print("[ADVERTENCIA] La query no retornó resultados")
            return None

        print("")
        print("=" * 60)
        print("RESULTADO - {}".format(descripcion.upper()))
        print("=" * 60)
        print("Total de filas descargadas: {:,}".format(len(df)))

        # Generar nombres de archivo
        filename_csv, filename_detalle, filename_dashboard = generate_filename(modo, mes, anio, fecha_inicio, fecha_fin)
        output_folder = CONFIG['output_folder']

        os.makedirs(output_folder, exist_ok=True)

        local_path_csv = os.path.join(output_folder, filename_csv)
        local_path_detalle = os.path.join(output_folder, filename_detalle)
        local_path_dashboard = os.path.join(output_folder, filename_dashboard)

        # Guardar CSV con datos crudos
        print("")
        print("Guardando CSV con datos crudos...")
        df.to_csv(local_path_csv, index=False, encoding='utf-8-sig')
        print("    [OK] CSV guardado: {}".format(filename_csv))

        # Procesar datos
        print("")
        print("Procesando contenidos consultados...")
        df_contenidos, total_contenidos, df_historico = procesar_contenidos(df, fecha_inicio, fecha_fin)

        if df_contenidos is None:
            print("[ERROR] No se pudo procesar los datos")
            return None

        # Generar Excel detallado (2 hojas)
        print("")
        print("Generando Excel detallado...")
        create_detail_excel(local_path_detalle, df_contenidos, df_historico, descripcion)

        # Generar Dashboard
        print("")
        print("Generando Dashboard...")
        # D11 = Top 10 contenidos formateado como texto multilínea
        top10_text = format_top10_text(df_contenidos)
        create_dashboard(local_path_dashboard, top10_text, modo, mes, anio, fecha_inicio, fecha_fin)

        print("")
        print("=" * 60)
        print("ARCHIVOS GENERADOS:")
        print("=" * 60)
        print("    [CSV] {}".format(filename_csv))
        print("          - Datos crudos de la vista Athena")
        print("")
        print("    [EXCEL DETALLE] {}".format(filename_detalle))
        print("          - Hoja 'Buscador de contenidos': {} contenidos con %GT".format(total_contenidos))
        if df_historico is not None:
            print("          - Hoja 'Historico': {} días de serie temporal".format(len(df_historico)))
        print("          - Total sesiones: {:,}".format(int(df_contenidos['Suma de Sesiones'].sum())))
        print("")
        print("    [DASHBOARD] {}".format(filename_dashboard))
        print("          - Celda D11 = Top 10 contenidos más consultados")

        print("")
        print("=" * 60)
        print("PROCESO COMPLETADO EXITOSAMENTE")
        print("=" * 60)

        return df

    except Exception as e:
        print("")
        print("[ERROR] {}".format(str(e)))
        import traceback
        traceback.print_exc()
        return None

# ==================== EJECUCION PRINCIPAL ====================

if __name__ == "__main__":
    print("")
    print("=" * 60)
    print("SCRIPT: CONTENIDOS CONSULTADOS - QUERY ATHENA")
    print("=" * 60)
    print("Rol requerido: PIBAConsumeBoti")
    print("Salida: CSV + Excel Detalle (2 hojas) + Dashboard (celda D11)")
    print("Query: SELECT * FROM boti_vw_buscador_rulename")
    print("")
    print("LÓGICA:")
    print("  1. Descargar vista completa de Athena")
    print("  2. Filtrar por rango de fechas del período")
    if APLICAR_EXCLUSIONES:
        print("  3. Excluir contenidos no relevantes ({} reglas)".format(len(CONTENIDOS_EXCLUIR)))
    else:
        print("  3. Exclusiones DESACTIVADAS")
    print("  4. Agrupar por rulename y sumar sesiones")
    print("  5. Generar tabla completa con % del total")
    print("  6. Generar serie temporal diaria (Histórico)")
    print("")
    print("MODOS:")
    print("  [1] MES COMPLETO: MES + AÑO")
    print("  [2] RANGO PERSONALIZADO: FECHA_INICIO + FECHA_FIN")
    print("=" * 60)
    print("")

    result = execute_query_and_save()

    if result is not None:
        print("")
        print("Para procesar otro periodo, edita config_fechas.txt")
    else:
        print("")
        print("La ejecucion fallo. Revisa los errores arriba.")

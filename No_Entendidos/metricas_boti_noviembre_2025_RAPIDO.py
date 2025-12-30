#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
MÉTRICAS BOTI - NOVIEMBRE 2025 (VERSIÓN ULTRA-OPTIMIZADA)
=============================================================================
Versión 3.0: Optimizada para archivos masivos con filtrado agresivo

Optimizaciones clave:
- Filtrado de clicks/botones POR SESIÓN (no por tester)
- Chunk size ultra-reducido para clicks/botones (10,000)
- Procesamiento incremental más agresivo
- Liberación de memoria optimizada

Autor: Damian - GCBA
Versión: 3.0 (Ultra-optimizada)
=============================================================================
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
import os as os_module
import sys
import gc

warnings.filterwarnings('ignore')
pd.set_option("display.max_colwidth", None)

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

DIRECTORIO_TRABAJO = 'C:/GCBA/Metricas_Boti_Mensual/No_Entendidos'

# Período
FECHA_INICIO = '2025-11-01 00:00:00'
FECHA_FIN = '2025-12-01 00:00:00'

# Archivos
ARCHIVO_MENSAJES = 'mensajes.csv'
ARCHIVO_CLICKS = 'clicks.csv'
ARCHIVO_BOTONES = 'botones.csv'
ARCHIVO_TESTERS = 'testers.csv'
ARCHIVO_LISTA_BLANCA = 'Actualizacion_Lista_Blanca.csv'

# Chunk sizes optimizados
CHUNK_MENSAJES = 50000   # Para mensajes (filtrado por fecha)
CHUNK_OTROS = 10000      # Para clicks/botones (mucho más pequeño)

# Constantes
RULE_NE = 'PLBWX5XYGQ2B3GP7IN8Q-nml045fna3@b.m-1669990832420'
INTENT_NADA = 'RuleBuilder:PLBWX5XYGQ2B3GP7IN8Q-alfafc@gmail.com-1536777380652'
RULE_LETRA_NO_EXISTE = 'No entendió letra no existente en WA'
SCORE_NE_THRESHOLD = 5.36

# =============================================================================
# FUNCIONES
# =============================================================================

def imprimir_seccion(titulo):
    print("\n" + "=" * 80)
    print(f"  {titulo}")
    print("=" * 80)

def imprimir_progreso(mensaje):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {mensaje}")

def liberar_memoria():
    gc.collect()

def cargar_mensajes_optimizado(archivo, chunk_size, fecha_inicio, testers):
    """Carga mensajes con filtrado por fecha y testers"""
    imprimir_progreso(f"Cargando {archivo} (filtrado por fecha + testers)...")
    
    chunk_list = []
    total_rows = 0
    total_filtrado = 0
    
    columnas = [
        'session_id', 'id', 'creation_time', 'msg_from', 
        'message_type', 'message', 'rule_name', 'topic_path',
        'original_user_message', 'max_score'
    ]
    
    # Primera lectura para verificar columnas
    primera = pd.read_csv(archivo, nrows=0)
    columnas_validas = [c for c in columnas if c in primera.columns]
    
    for i, chunk in enumerate(pd.read_csv(archivo, chunksize=chunk_size, 
                                          usecols=columnas_validas, low_memory=True)):
        total_rows += len(chunk)
        
        # Filtro 1: Por fecha
        chunk['creation_time'] = pd.to_datetime(chunk['creation_time'], errors='coerce')
        chunk = chunk[chunk['creation_time'] >= fecha_inicio]
        
        # Filtro 2: Por testers
        if len(chunk) > 0:
            chunk['usuario'] = chunk.session_id.str[:20]
            chunk = chunk[~chunk.usuario.isin(testers)]
        
        if len(chunk) > 0:
            chunk_list.append(chunk)
            total_filtrado += len(chunk)
        
        if (i + 1) % 10 == 0:
            imprimir_progreso(f"  {total_rows:,} leídos → {total_filtrado:,} filtrados")
            liberar_memoria()
    
    df = pd.concat(chunk_list, ignore_index=True)
    del chunk_list
    liberar_memoria()
    
    imprimir_progreso(f"✓ {total_rows:,} leídos → {len(df):,} después de filtrar")
    return df

def cargar_por_sesiones(archivo, chunk_size, sesiones_validas):
    """
    Carga archivo filtrando SOLO por sesiones válidas
    
    Esta es la clave: clicks y botones SOLO de sesiones que pasaron en mensajes
    """
    imprimir_progreso(f"Cargando {archivo} (solo sesiones válidas)...")
    
    # Convertir a set para búsqueda rápida
    sesiones_set = set(sesiones_validas)
    
    chunk_list = []
    total_rows = 0
    total_mantenidos = 0
    
    for i, chunk in enumerate(pd.read_csv(archivo, chunksize=chunk_size, low_memory=True)):
        total_rows += len(chunk)
        
        # FILTRO CRÍTICO: Solo sesiones válidas
        chunk = chunk[chunk.session_id.isin(sesiones_set)]
        
        if len(chunk) > 0:
            chunk_list.append(chunk)
            total_mantenidos += len(chunk)
        
        if (i + 1) % 20 == 0:
            imprimir_progreso(f"  {total_rows:,} leídos → {total_mantenidos:,} mantenidos")
            liberar_memoria()
        
        # Límite de seguridad
        if total_mantenidos > 500000:
            imprimir_progreso(f"⚠ Muchos registros mantenidos, puede tardar...")
    
    if not chunk_list:
        imprimir_progreso("⚠ No hay datos que coincidan con sesiones válidas")
        return pd.DataFrame()
    
    df = pd.concat(chunk_list, ignore_index=True)
    del chunk_list
    liberar_memoria()
    
    imprimir_progreso(f"✓ {total_rows:,} leídos → {len(df):,} mantenidos")
    return df

def cargar_csv_simple(archivo):
    imprimir_progreso(f"Cargando {archivo}...")
    df = pd.read_csv(archivo)
    imprimir_progreso(f"✓ {archivo}: {len(df):,} registros")
    return df

# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================

def calcular_promedios_boti():
    try:
        # =================================================================
        # PASO 1: CONFIGURACIÓN
        # =================================================================
        imprimir_seccion("PASO 1: CONFIGURACIÓN")
        
        if os_module.path.exists(DIRECTORIO_TRABAJO):
            os_module.chdir(DIRECTORIO_TRABAJO)
            imprimir_progreso(f"✓ Directorio: {os_module.getcwd()}")
        else:
            imprimir_progreso(f"⚠ Usando: {os_module.getcwd()}")
        
        print(f"\n📅 Período: {FECHA_INICIO} a {FECHA_FIN}")
        print(f"💾 Chunk mensajes: {CHUNK_MENSAJES:,}")
        print(f"💾 Chunk clicks/botones: {CHUNK_OTROS:,}")
        
        fecha_inicio_dt = np.datetime64(FECHA_INICIO)
        
        # =================================================================
        # PASO 2: AUXILIARES
        # =================================================================
        imprimir_seccion("PASO 2: ARCHIVOS AUXILIARES")
        
        testers_df = cargar_csv_simple(ARCHIVO_TESTERS)
        testers = testers_df.iloc[:, 0].values
        imprimir_progreso(f"✓ Testers: {len(testers)}")
        del testers_df
        liberar_memoria()
        
        mos = cargar_csv_simple(ARCHIVO_LISTA_BLANCA)
        rules_mos = mos['Nombre de la intención'].str.strip().values
        imprimir_progreso(f"✓ Intenciones: {len(rules_mos)}")
        del mos
        liberar_memoria()
        
        # =================================================================
        # PASO 3: MENSAJES
        # =================================================================
        imprimir_seccion("PASO 3: MENSAJES")
        
        mm = cargar_mensajes_optimizado(
            ARCHIVO_MENSAJES,
            CHUNK_MENSAJES,
            fecha_inicio_dt,
            testers
        )
        
        imprimir_progreso("Procesando mensajes...")
        mm.creation_time = pd.to_datetime(mm.creation_time)
        mm.creation_time = mm.creation_time.dt.tz_localize(None)
        mm.creation_time = mm.creation_time.dt.ceil('s')
        
        mm1 = mm.copy()
        del mm
        liberar_memoria()
        
        mm1.drop_duplicates(['session_id', 'creation_time', 'msg_from', 'rule_name'], 
                           inplace=True)
        mm1.reset_index(inplace=True, drop=True)
        
        imprimir_progreso(f"✓ Mensajes: {len(mm1):,}")
        imprimir_progreso(f"✓ Usuarios: {mm1.usuario.nunique():,}")
        
        # GUARDAR SESIONES VÁLIDAS
        sesiones_validas_mm1 = mm1.session_id.unique()
        imprimir_progreso(f"✓ Sesiones válidas: {len(sesiones_validas_mm1):,}")
        
        # =================================================================
        # PASO 4: CLICKS (FILTRADO POR SESIÓN)
        # =================================================================
        imprimir_seccion("PASO 4: CLICKS (FILTRADO POR SESIÓN)")
        
        search = cargar_por_sesiones(
            ARCHIVO_CLICKS,
            CHUNK_OTROS,
            sesiones_validas_mm1
        )
        
        if len(search) == 0:
            raise ValueError("No hay clicks para sesiones válidas")
        
        imprimir_progreso("Procesando clicks...")
        search.drop_duplicates(['session_id', 'ts', 'id', 'message', 'mostrado', 
                               'response_message'], inplace=True)
        search.ts = pd.to_datetime(search.ts)
        search['fecha'] = search.ts.dt.date
        
        searchcl = search[
            'RuleBuilder:' + search.mostrado == search.response_intent_id
        ].drop_duplicates('id')
        
        imprimir_progreso(f"✓ Clicks: {len(search):,}")
        imprimir_progreso(f"✓ Clicks válidos: {len(searchcl):,}")
        
        # =================================================================
        # PASO 5: BOTONES (FILTRADO POR SESIÓN)
        # =================================================================
        imprimir_seccion("PASO 5: BOTONES (FILTRADO POR SESIÓN)")
        
        one = cargar_por_sesiones(
            ARCHIVO_BOTONES,
            CHUNK_OTROS,
            sesiones_validas_mm1
        )
        
        if len(one) == 0:
            raise ValueError("No hay botones para sesiones válidas")
        
        imprimir_progreso("Procesando botones...")
        os = one[np.logical_and(
            one.one_shot == True,
            one.type.isin(['oneShot', 'oneShotSearch'])
        )].copy()
        
        del one
        liberar_memoria()
        
        os.ts = pd.to_datetime(os.ts)
        os['fecha'] = os.ts.dt.date
        
        imprimir_progreso(f"✓ OneShots: {len(os):,}")
        
        # =================================================================
        # PASO 6: LIMPIEZA (OPTIMIZADO)
        # =================================================================
        imprimir_seccion("PASO 6: LIMPIEZA (OPTIMIZADO)")
        
        imprimir_progreso("Identificando mensajes consecutivos...")
        mm1.reset_index(inplace=True, drop=True)
        
        # OPTIMIZADO: Usar shift() en lugar de loop (100x más rápido)
        mm1['msg_from_next'] = mm1['msg_from'].shift(-1)
        mm1['session_id_next'] = mm1['session_id'].shift(-1)
        
        # Identificar duplicados consecutivos
        mask_duplicados = (
            (mm1['msg_from'] == mm1['msg_from_next']) & 
            (mm1['session_id'] == mm1['session_id_next'])
        )
        
        num_duplicados = mask_duplicados.sum()
        
        if num_duplicados > 0:
            mm1 = mm1[~mask_duplicados].copy()
            imprimir_progreso(f"✓ Eliminados: {num_duplicados:,} mensajes consecutivos")
        else:
            imprimir_progreso("✓ No hay mensajes consecutivos para eliminar")
        
        # Limpiar columnas auxiliares
        mm1.drop(['msg_from_next', 'session_id_next'], axis=1, inplace=True, errors='ignore')
        mm1.reset_index(inplace=True, drop=True)
        
        liberar_memoria()
        
        # =================================================================
        # PASO 7: ANÁLISIS
        # =================================================================
        imprimir_seccion("PASO 7: ANÁLISIS")
        
        mm = mm1.copy()
        mm.reset_index(inplace=True, drop=True)
        
        mmtex1 = mm[np.logical_and(mm.msg_from == 'user', mm.message_type == 'Text')][
            ['session_id', 'id', 'creation_time', 'msg_from', 'message_type', 
             'message', 'usuario']
        ].copy()
        
        if len(mmtex1) > 0:
            mmtex1 = mmtex1.iloc[:-1]
        
        mmtex1['rule_name'] = [
            r if su == sb and f == 'bot' else None
            for r, su, sb, f in zip(
                mm.loc[mmtex1.index + 1].rule_name.values,
                mmtex1.session_id.values,
                mm.loc[mmtex1.index + 1].session_id.values,
                mm.loc[mmtex1.index + 1].msg_from.values
            )
        ]
        
        letra1 = mmtex1[mmtex1.rule_name == RULE_LETRA_NO_EXISTE].copy()
        letra1.rename(columns={'id': 'message_id'}, inplace=True)
        
        del mmtex1
        liberar_memoria()
        
        search1 = search[search.session_id.isin(mm1.session_id.values)].copy()
        os1 = os[os.session_id.isin(mm1.session_id.values)].copy()
        
        del search, os
        liberar_memoria()
        
        primera_instancia1 = search1[
            ~search1.message_id.isin(
                pd.concat([
                    search1[
                        'RuleBuilder:' + search1.mostrado == search1.response_intent_id
                    ].message_id,
                    os1.message_id
                ]).values
            )
        ].drop_duplicates('id').copy()
        
        primera_instancia1.rename(columns={"score": "score"}, inplace=True, errors='ignore')
        if 'results_score' in primera_instancia1.columns:
            primera_instancia1.rename(columns={"results_score": "score"}, inplace=True)
        
        ne1 = primera_instancia1.groupby('id').max()[['session_id', 'message_id', 'score']]
        ne1 = ne1[ne1.score <= SCORE_NE_THRESHOLD].copy()
        
        primera_instancia1 = primera_instancia1[~primera_instancia1.id.isin(ne1.index)].copy()
        
        # =================================================================
        # PASO 8: CATEGORIZACIÓN
        # =================================================================
        imprimir_progreso("Categorizando...")
        
        os1 = os1.drop_duplicates('id')[['session_id', 'message_id']].copy()
        os1['categoria'] = 'one'
        
        click1 = search1[
            'RuleBuilder:' + search1.mostrado == search1.response_intent_id
        ].drop_duplicates('id')[['session_id', 'message_id']].copy()
        click1['categoria'] = 'click'
        
        abandonos1 = primera_instancia1[
            primera_instancia1.response_message.isna()
        ][['session_id', 'message_id']].copy()
        abandonos1['categoria'] = 'abandono'
        
        nada1 = primera_instancia1[
            primera_instancia1.response_intent_id == INTENT_NADA
        ][['session_id', 'message_id']].copy()
        nada1['categoria'] = 'nada'
        
        texto1 = primera_instancia1[np.logical_and(
            primera_instancia1.response_intent_id != INTENT_NADA,
            ~primera_instancia1.response_message.isna()
        )][['session_id', 'message_id']].copy()
        texto1['categoria'] = 'texto'
        
        ne1['categoria'] = 'ne'
        letra1 = letra1[['session_id', 'message_id']].copy()
        letra1['categoria'] = 'letra'
        
        del search1, primera_instancia1
        liberar_memoria()
        
        print(f"\n📊 Categorías:")
        print(f"   OneShots:    {len(os1):>7,}")
        print(f"   Clicks:      {len(click1):>7,}")
        print(f"   Abandonos:   {len(abandonos1):>7,}")
        print(f"   Nada:        {len(nada1):>7,}")
        print(f"   Texto:       {len(texto1):>7,}")
        print(f"   No entend:   {len(ne1):>7,}")
        print(f"   Letra:       {len(letra1):>7,}")
        
        # =================================================================
        # PASO 9: AGRUPACIÓN
        # =================================================================
        imprimir_seccion("PASO 9: AGRUPACIÓN")
        
        value1primera = pd.concat([os1, click1, abandonos1, nada1, texto1, ne1, letra1],
                                   ignore_index=True)
        
        del os1, click1, abandonos1, nada1, texto1, ne1, letra1
        liberar_memoria()
        
        value1primera['usuario'] = value1primera.session_id.str[:20]
        value1primera = value1primera[value1primera.usuario.isin(mm1.usuario.values)]
        
        imprimir_progreso(f"✓ Interacciones: {len(value1primera):,}")
        
        respuestas_por_usuario = value1primera.groupby(
            ['usuario', 'categoria'],
            as_index=False
        ).count()[['usuario', 'categoria', 'message_id']].pivot_table(
            'message_id',
            ['usuario'],
            'categoria'
        )
        
        del value1primera
        liberar_memoria()
        
        respuestas_por_usuario.fillna(0, inplace=True)
        respuestas_por_usuario = respuestas_por_usuario.reset_index(drop=False).reindex(
            ['usuario', 'one', 'click', 'texto', 'abandono', 'nada', 'ne', 'letra'],
            axis=1
        )
        
        # =================================================================
        # PASO 10: PORCENTAJES
        # =================================================================
        imprimir_seccion("PASO 10: PORCENTAJES")
        
        categorias = ['one', 'click', 'texto', 'abandono', 'nada', 'ne', 'letra']
        
        for categoria in categorias:
            respuestas_por_usuario[f'porcentaje_{categoria}'] = [
                respuestas_por_usuario.loc[i][categoria] /
                respuestas_por_usuario.loc[i][categorias].sum()
                for i in respuestas_por_usuario.index
            ]
        
        imprimir_progreso("✓ Calculados")
        
        # =================================================================
        # PASO 11: PROMEDIOS
        # =================================================================
        imprimir_seccion("PASO 11: PROMEDIOS FINALES")
        
        promedios1 = {
            'abandonos': round(respuestas_por_usuario['porcentaje_abandono'].mean(), 3) if 'porcentaje_abandono' in respuestas_por_usuario.columns else 0.0,
            'click': round(respuestas_por_usuario['porcentaje_click'].mean(), 3) if 'porcentaje_click' in respuestas_por_usuario.columns else 0.0,
            'one': round(respuestas_por_usuario['porcentaje_one'].mean(), 3) if 'porcentaje_one' in respuestas_por_usuario.columns else 0.0,
            'texto': round(respuestas_por_usuario['porcentaje_texto'].mean(), 3) if 'porcentaje_texto' in respuestas_por_usuario.columns else 0.0,
            'nada': round(respuestas_por_usuario['porcentaje_nada'].mean(), 3) if 'porcentaje_nada' in respuestas_por_usuario.columns else 0.0,
            'letra': round(respuestas_por_usuario['porcentaje_letra'].mean(), 3) if 'porcentaje_letra' in respuestas_por_usuario.columns and respuestas_por_usuario['porcentaje_letra'].notna().any() else 0.0,
            'ne': round(respuestas_por_usuario['porcentaje_ne'].mean(), 3) if 'porcentaje_ne' in respuestas_por_usuario.columns else 0.0
        }
        
        # =================================================================
        # RESULTADOS
        # =================================================================
        print("\n" + "=" * 80)
        print("  RESULTADOS - PROMEDIOS1")
        print("=" * 80)
        
        print(f"\n📅 Período: {FECHA_INICIO} a {FECHA_FIN}")
        print(f"👥 Usuarios: {len(respuestas_por_usuario):,}")
        
        print("\n" + "─" * 80)
        for key, label in [
            ('one', 'OneShots'),
            ('click', 'Clicks'),
            ('texto', 'Texto'),
            ('abandonos', 'Abandonos'),
            ('nada', 'Nada'),
            ('ne', 'No entendidos'),
            ('letra', 'Letra')
        ]:
            valor = promedios1[key]
            if pd.isna(valor) or valor == 0:
                pct = 0.0
                barra = ''
            else:
                pct = valor * 100
                barra = '█' * int(pct / 2)
            valor_display = valor if not pd.isna(valor) else 0.0
            print(f"  {label:.<20} {valor_display:>7.3f}  ({pct:>6.2f}%) {barra}")
        
        print("─" * 80)
        
        total = sum(v for v in promedios1.values() if not (pd.isna(v) or v == 0))
        print(f"\n✓ Suma: {total:.3f} ({total*100:.2f}%)")
        
        if abs(total - 1.0) < 0.01:
            print("✅ VALIDACIÓN EXITOSA")
        
        tasa_resolucion = promedios1['one'] + promedios1['click'] + promedios1['texto']
        tasa_problemas = promedios1['abandonos'] + promedios1['ne']
        
        print(f"\n  Resolución: {tasa_resolucion*100:.2f}%")
        print(f"  Problemas: {tasa_problemas*100:.2f}%")
        
        return promedios1
    
    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ ERROR")
        print("=" * 80)
        print(f"{str(e)}")
        import traceback
        traceback.print_exc()
        return None

# =============================================================================
# EJECUCIÓN
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("  MÉTRICAS BOTI - NOVIEMBRE 2025")
    print("  (Versión Ultra-Optimizada v3.0)")
    print("=" * 80)
    
    inicio = datetime.now()
    promedios1 = calcular_promedios_boti()
    fin = datetime.now()
    
    if promedios1:
        print("\n" + "=" * 80)
        print("✅ COMPLETADO")
        print("=" * 80)
        print(f"\n⏱️ Tiempo: {fin - inicio}")
        print(f"\n💾 promedios1 = {promedios1}")
        print("\n" + "=" * 80)
    else:
        sys.exit(1)

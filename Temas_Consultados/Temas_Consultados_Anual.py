# -*- coding: utf-8 -*-
"""
Temas Consultados ANUAL (YTD) - Ranking top 10 de categorias

Corre el mismo pipeline que Temas_Consultados.py pero sobre TODO el año
en curso: desde el 1 de enero hasta HOY (fecha del sistema).

NO hace comparaciones mes vs mes. Solo genera el ranking top 10.

Reutiliza la logica del script mensual (importa CATEGORIAS, limpieza,
clasificacion, etc.) - si cambia algo alli, se refleja aca automaticamente.

Genera:
  - output/temas_consultados_anual_<anio>.csv        Dataset crudo limpio
  - output/conteo_categorias_anual_<anio>.xlsx       Conteo total por categoria
  - output/ranking_temas_consultados_anual_<anio>.txt   Ranking top 10 para el tablero
  - output/ranking_temas_consultados_anual_<anio>.xlsx  Ranking en formato template
"""

import os
import sys
import pandas as pd
from datetime import date

# Reutilizo todo lo posible del script mensual
from Temas_Consultados import (
    CONFIG,
    CATEGORIAS_EXCLUIR_DEL_RANKING,
    TOP_N_RANKING,
    log,
    step,
    check_aws_credentials,
    ejecutar_query,
    build_query,
    procesar_df,
    construir_ranking_texto,
    generar_excel_ranking,
    aplicar_variante_sin_ambiguas,
)


def main():
    # ── Variante: sacar palabras clave ambiguas ──────────────────────────────
    # Uso:  python Temas_Consultados_Anual.py --sin-ayuda
    #
    # Saca "ayuda" de 'Interaccion Humana (Chatear)'. Esa palabra arrastra un
    # 28% de falsos positivos (ver PALABRAS_AMBIGUAS en Temas_Consultados.py),
    # sobre todo "ayudas tramitar certificado", que son subsidios.
    #
    # Los archivos de salida llevan sufijo _sin_ayuda para NO pisar los de la
    # version estandar: asi se pueden comparar las dos.
    sin_ayuda = '--sin-ayuda' in sys.argv

    log("=" * 60)
    log("TEMAS CONSULTADOS - RANKING ANUAL (YTD)")
    if sin_ayuda:
        log("           >>> VARIANTE: SIN LA PALABRA 'AYUDA' <<<")
    log("=" * 60)

    if sin_ayuda:
        sacadas = aplicar_variante_sin_ambiguas()
        for cat, palabras in sacadas.items():
            log("[VARIANTE] De '{}' se saco: {}".format(cat, ', '.join(palabras)))
        log("[VARIANTE] Los resultados NO son comparables con las corridas")
        log("           estandar ya entregadas (ene-sep 2026).")
        log("")

    # 1) Rango: 1 de enero del año en curso -> hoy
    hoy = date.today()
    anio = hoy.year
    fecha_inicio = "{:04d}-01-01".format(anio)
    fecha_fin = hoy.strftime("%Y-%m-%d")
    log("Periodo: {} a {}".format(fecha_inicio, fecha_fin))

    # 2) Credenciales AWS
    log("")
    log("Verificando credenciales AWS...")
    if not check_aws_credentials():
        return

    # 3) Query
    query = build_query(fecha_inicio, fecha_fin)
    log("")
    log("Query a ejecutar:")
    log(query)

    # 4) Ejecutar
    log("")
    log("ATENCION: la query escanea boti_message_metrics_2 por VARIOS MESES")
    log("          ({} meses aprox). Puede tardar bastante mas que la mensual.".format(hoy.month))
    with step("Query Athena (boti_message_metrics_2)"):
        df = ejecutar_query(query)
    log("[OK] {:,} filas descargadas".format(len(df)))

    if len(df) == 0:
        log("[ADVERTENCIA] La query no devolvio filas. Abortando.")
        return

    # 5) Procesar (limpieza + clasificacion)
    log("")
    with step("Procesando mensajes (filtros + limpieza + categorizacion)"):
        df = procesar_df(df)

    # 6) Setup nombres de archivo
    # El sufijo _sin_ayuda evita pisar los archivos de la version estandar.
    sufijo = "anual_{}{}".format(anio, "_sin_ayuda" if sin_ayuda else "")
    out_dir = CONFIG['output_folder']
    os.makedirs(out_dir, exist_ok=True)

    path_csv = os.path.join(out_dir, "temas_consultados_{}.csv".format(sufijo))
    path_conteo = os.path.join(out_dir, "conteo_categorias_{}.xlsx".format(sufijo))
    path_ranking_txt = os.path.join(out_dir, "ranking_temas_consultados_{}.txt".format(sufijo))
    path_ranking_xlsx = os.path.join(out_dir, "ranking_temas_consultados_{}.xlsx".format(sufijo))

    # 7) CSV crudo procesado
    log("")
    with step("Guardando CSV crudo procesado"):
        df_out = df.drop(columns=['mes'])
        df_out.to_csv(path_csv, index=False, encoding='utf-8-sig', sep=';')
    log("    [OK] {}".format(path_csv))

    # 8) Conteo por categoria (todo el periodo)
    with step("Conteo por categoria (YTD)"):
        conteo = df.groupby('categoria').size().reset_index(name='Q')
        conteo = conteo.sort_values('Q', ascending=False).reset_index(drop=True)
        total = int(conteo['Q'].sum())
        conteo['%'] = (conteo['Q'] / total * 100).round(2)

        # Formato lindo para el Excel (Q en miles, % con signo)
        conteo_fmt = conteo.copy()
        conteo_fmt.columns = ['Categoria', 'Q Mensajes', '% del total']
        conteo_fmt['Q Mensajes'] = conteo_fmt['Q Mensajes'].apply(lambda x: "{:,}".format(int(x)))
        conteo_fmt['% del total'] = conteo_fmt['% del total'].apply(lambda x: "{:.2f}%".format(x))
        with pd.ExcelWriter(path_conteo) as writer:
            conteo_fmt.to_excel(writer, sheet_name='Conteo_YTD', index=False)
    log("    [OK] {} (total: {:,} mensajes clasificados)".format(path_conteo, total))

    # Log del conteo en consola
    log("    Conteo por categoria:")
    for _, row in conteo.iterrows():
        log("        {:40s} | {:>10,} | {:>6.2f}%".format(
            row['categoria'], int(row['Q']), row['%']
        ))

    # 9) Ranking top 10 (excluye 'Otros' y 'Vacunacion' - igual que el mensual)
    with step("Ranking top {} + Excel para el TABLERO".format(TOP_N_RANKING)):
        # Conteo exacto por categoria, para que el ranking salga con numeros
        # igual que el mensual. Se arma ANTES del rename, que pisa 'categoria'.
        conteo_exacto = {
            str(cat): int(q)
            for cat, q in zip(conteo['categoria'], conteo['Q'])
        }
        # construir_ranking_texto espera columna llamada 'Tema Último Mes'
        resultado = conteo.rename(columns={'categoria': 'Tema Último Mes'})
        ranking_texto = construir_ranking_texto(resultado, conteo_exacto)
        with open(path_ranking_txt, 'w', encoding='utf-8') as f:
            f.write(ranking_texto)
        periodo_short = "YTD-{}".format(str(anio)[-2:])
        generar_excel_ranking(path_ranking_xlsx, ranking_texto, periodo_short)
    log("    [OK] {}".format(path_ranking_txt))
    log("    [OK] {}".format(path_ranking_xlsx))

    # 10) Resumen final
    log("")
    log("=" * 60)
    log("RANKING TOP {} - YTD {} ({} a {})".format(
        TOP_N_RANKING, anio, fecha_inicio, fecha_fin
    ))
    log("=" * 60)
    for linea in ranking_texto.split('\n'):
        log("    " + linea)
    log("=" * 60)
    log("")
    log("Texto guardado en: {}".format(path_ranking_txt))
    log("Excel guardado en: {}".format(path_ranking_xlsx))
    log("Pegalo / copialo en la celda 'Temas mas consultados' del tablero.")

    log("")
    log("=" * 60)
    log("ARCHIVOS GENERADOS en {}/".format(out_dir))
    log("=" * 60)
    for p in [path_csv, path_conteo, path_ranking_txt, path_ranking_xlsx]:
        log("    [OK] {}".format(os.path.basename(p)))

    log("")
    log("=" * 60)
    log("PROCESO COMPLETADO EXITOSAMENTE")
    log("=" * 60)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(line_buffering=True)
        sys.stderr.reconfigure(line_buffering=True)
    except AttributeError:
        pass

    print("")
    print("=" * 60)
    print("  IMPORTANTE: LOGIN AWS REQUERIDO")
    print("=" * 60)
    print("  Antes de continuar, asegurate de estar logueado en AWS.")
    print("  Si tu token expiró, ejecutá en otra terminal:")
    print("")
    print("      aws-azure-login --profile default --mode=gui")
    print("")
    print("  Rol requerido: PIBADataScientist")
    print("")
    print("  NOTA: Este script escanea TODO el año en curso,")
    print("        puede tardar bastante mas que el mensual.")
    print("=" * 60)
    try:
        input("  Presioná ENTER para continuar (o Ctrl+C para cancelar)...")
    except KeyboardInterrupt:
        print("\n  Cancelado por el usuario.")
        raise SystemExit(0)
    print("")

    main()

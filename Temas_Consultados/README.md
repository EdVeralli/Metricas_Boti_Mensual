# Temas Consultados

## Descripción

Reemplaza el flujo manual del notebook `mensajes.ipynb` del repo
[Tablero-de-mensajes-y-disparadores](https://github.com/EdVeralli/Tablero-de-mensajes-y-disparadores)
por un script standalone que:

1. Lee el período (`MES + AÑO`) desde `../config_fechas.txt`.
2. Calcula automáticamente el mes anterior.
3. Hace la query a Athena (rol `PIBADataScientist`) para esos 2 meses.
4. Limpia + clasifica + categoriza los mensajes de usuario.
5. Genera todos los outputs que alimentan el tablero.

## Estructura

```
Temas_Consultados/
├── Temas_Consultados.py     # Script principal
├── output/                  # Outputs auto-generados
│   ├── temas_consultados_<mes>_<año>.csv
│   ├── top_200_mensajes_<mes>_<año>.csv
│   ├── comparison_mensajes_<mes>_<año>.xlsx
│   ├── reporte_mensajes_<mes>_<año>.xlsx     (Comparativo + Top100 Otros)
│   ├── top_variaciones_<mes>_<año>.xlsx      (Top 3 ↑/↓ por categoría)
│   └── ranking_temas_<mes>_<año>.txt         (texto para el tablero)
└── README.md                # Este archivo
```

## Requisitos

```bash
pip install boto3 awswrangler pandas numpy openpyxl nltk
```

La primera vez que corre, el script descarga el pack de stopwords de NLTK en
español automáticamente (no hace falta correr `nltk.download` a mano).

## Configuración

El script lee el período del archivo centralizado:

```
C:\GCBA\Metricas_Boti_Mensual\config_fechas.txt
```

Solo soporta el modo **MES + AÑO** (el análisis es de meses completos).

## Uso

1. Asegurarse de tener sesión AWS activa con el rol correcto:
   ```powershell
   aws-azure-login --profile default --mode=gui
   ```
   Y seleccionar **PIBADataScientist**.

2. Ajustar `../config_fechas.txt` al mes que querés procesar:
   ```
   MES=3
   AÑO=2026
   ```

3. Ejecutar:
   ```powershell
   cd C:\GCBA\Metricas_Boti_Mensual\Temas_Consultados
   python Temas_Consultados.py
   ```

## Output principal: el ranking del tablero

El archivo **`output/ranking_temas_<mes>_<año>.txt`** contiene el texto formateado
exactamente como va en la celda **"Temas más consultados"** del tablero:

```
1-Infracciones y Multas
2-Trámites y Reclamos
3-Turnos (Generales)
4-Salud (Médicos/Salud)
5-Licencia de Conducir
6-Movilidad + Estacionamiento
7-MIBA y Validación
8-Impuestos (AGIP / Patentes / ABL)
9-Educación (Inscripciones/Becas)
10-Telepase
```

Copialo de ahí y pegalo en el tablero.

## Curado del ranking

En la cabecera del script hay una constante para curar el ranking:

```python
CATEGORIAS_EXCLUIR_DEL_RANKING = [
    'Otros',
    'Vacunación',
    # 'Interacción Humana (Chatear)',  # descomentar si tampoco se quiere
    # 'DNI y Partidas',                # descomentar si tampoco se quiere
    # 'Turismo + Cultura + Deporte',   # descomentar si tampoco se quiere
]
```

- `"Otros"` se excluye siempre (cajón de sastre).
- `"Vacunación"` se excluye por default porque es **estacional** — en meses de
  campaña puede dispararse y meterse en el top 5 distorsionando el ranking.
- Las otras 3 están comentadas para usar solo si el equipo lo decide.

## Categorías y prioridad

El script clasifica mensajes en 14 categorías + "Otros". El orden de prioridad
de clasificación (definido en `ORDEN_PRIORIDAD`) es importante porque un
mensaje puede contener palabras-clave de varias categorías y solo se asigna a
la primera que matchea.

Orden:

1. Salud (Médicos/Salud)
2. Vacunación
3. Infracciones y Multas
4. Licencia de Conducir
5. Telepase
6. Movilidad + Estacionamiento
7. MIBA y Validación  ← antes que Trámites (importante)
8. Educación (Inscripciones/Becas)
9. Impuestos (AGIP / Patentes / ABL)
10. DNI y Partidas
11. Turismo + Cultura + Deporte
12. Interacción Humana (Chatear)
13. Turnos (Generales)
14. Trámites y Reclamos
15. (resto) → "Otros"

Para modificar las palabras-clave de una categoría, editar el dict
`CATEGORIAS` en la cabecera del script.

## Relación con el repo del tablero

Este script **reemplaza** los notebooks del repo
[Tablero-de-mensajes-y-disparadores](https://github.com/EdVeralli/Tablero-de-mensajes-y-disparadores).
Antes el flujo era:

1. Correr la query manualmente en Athena.
2. Descargar el CSV resultante.
3. Renombrarlo a `input.csv`.
4. Correr `mensajes.ipynb` celda por celda.
5. Copiar los outputs al tablero.

Ahora todo eso lo hace un solo `python Temas_Consultados.py`. El repo del
tablero queda como **histórico / referencia** de la lógica original.

## Troubleshooting

- **`No estas usando el rol correcto`** → No estás autenticado con
  `PIBADataScientist`. Ejecutar `aws-azure-login --profile default --mode=gui`
  y seleccionar el rol correcto.
- **`ExpiredToken`** → Token AWS expirado. Re-autenticarse.
- **NLTK lookup error** → La primera vez tarda unos segundos descargando
  stopwords. Si falla, ejecutar manualmente:
  ```python
  import nltk
  nltk.download('stopwords')
  ```
- **Query lenta** → La query escanea 2 meses de `boti_message_metrics_2`. Es
  normal que tarde varios minutos. El script imprime timestamps en cada paso.

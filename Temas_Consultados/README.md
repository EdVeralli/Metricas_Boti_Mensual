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
├── Temas_Consultados_Anual.py  # Variante anual (mismo criterio, todo el año)
├── output/                  # Outputs auto-generados
│   ├── temas_consultados_<mes>_<año>.csv          (gitignored, ~500 MB)
│   ├── top_200_mensajes_<mes>_<año>.csv
│   ├── comparison_mensajes_<mes>_<año>.xlsx
│   ├── reporte_mensajes_<mes>_<año>.xlsx          (Comparativo + Top100 Otros)
│   ├── top_variaciones_<mes>_<año>.xlsx           (Top 3 ↑/↓ por categoría)
│   ├── ranking_temas_consultados_<mes>_<año>.txt  (texto para el tablero)
│   └── ranking_temas_consultados_<mes>_<año>.xlsx (el mismo, en template)
└── README.md                # Este archivo
```

## ⚠️ La tabla `boti_message_metrics_2` — leer antes de tocar las queries

Verificado en octubre 2026. Tres cosas que no son evidentes y que, si no se
conocen, llevan a conclusiones equivocadas sobre los informes.

### 1. Tiene ~8 filas por mensaje

Septiembre 2026, filtrando `msg_from='user'` y `message_type='Text'`:

```
filas      : 37.324.756
ids unicos :  4.479.516   →  ratio 8,3x
```

**Toda query necesita `SELECT DISTINCT` o `COUNT(DISTINCT id)`.** Sin eso
sobrecuenta por 8. La query de este módulo ya lo hace — no se lo saques.

Es la trampa más peligrosa: si alguien arma una query propia para contrastar
los números del informe, le va a dar 8 veces más y va a pensar que el informe
está mal.

### 2. El filtro de comprensión se come los NULL

```sql
AND COMPREHENSION_TYPE != 'Answer to question'
```

Si el campo viene NULL, `NULL != '...'` da NULL —que no es TRUE— y la fila se
descarta. En septiembre 2026 eso son **645.394 mensajes, el 2,6%** de lo que
debería entrar.

**Está así a propósito por ahora**: el filtro viene desde siempre y afecta a
todos los períodos por igual, así que las series son consistentes entre sí.
Corregirlo rompería la comparabilidad con todo lo entregado.

Si alguna vez se rehace la serie completa:

```sql
AND (COMPREHENSION_TYPE IS NULL OR COMPREHENSION_TYPE != 'Answer to question')
```

### 3. Antes del 1° de mayo de 2024 los datos están en otra tabla

Hubo migración de `boti_message_metrics` a `boti_message_metrics_2`:

| Período | Dónde están los datos |
|---|---|
| hasta el **2024-04-30** | `boti_message_metrics` (la vieja) |
| desde el **2024-05-01** | **`boti_message_metrics_2`** |

Corte exacto al día, sin solapamiento ni huecos: la misma query sobre el rango
28/04–03/05 devuelve 28, 29 y 30 de abril en la vieja, y 1, 2 y 3 de mayo en
la nueva.

> 🔧 **Si te piden 2024 (o un año anterior), NO corras el script tal cual.**
>
> `Temas_Consultados_Anual.py --hasta 2024-12-31` devolvería **solo 8 meses**
> (mayo a diciembre) y **no fallaría** — nadie se daría cuenta.
>
> Hay que partir la query en dos con `UNION ALL`, una rama por tabla. La
> receta paso a paso está en [`PROCESO_MENSUAL.md`](../PROCESO_MENSUAL.md),
> sección 9.4.b, "RECETA: qué hacer cuando pidan 2024". **2025 y 2026 están enteros en `_2`**, así
que los anuales de esos años están completos.

Para 2024 completo habría que unir las dos tablas con `UNION ALL`. Verificar
antes que la vieja tenga las mismas columnas.

El detalle con los números mes a mes está en
[`PROCESO_MENSUAL.md`](../PROCESO_MENSUAL.md), sección 9.4.b.

---

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

El archivo **`output/ranking_temas_consultados_<mes>_<año>.txt`** contiene el
texto formateado exactamente como va en la celda **"Temas más consultados"**
del tablero.

### ⚠️ La unidad es MENSAJES, no sesiones

El número de cada tema es la **cantidad de mensajes de usuario** clasificados
en esa categoría (una fila del dataset = un mensaje).

En el tablero esta celda queda al lado de **"Contenidos más consultados"**, que
cuenta **SESIONES** y sale de otro módulo
(`Contenidos_mas_disparados`, vista `boti_vw_buscador_rulename`).

| Celda del tablero | Unidad | Módulo |
|---|---|---|
| Contenidos más consultados (D11) | **Sesiones** | `Contenidos_mas_disparados` |
| Temas más consultados | **Mensajes** | `Temas_Consultados` (este) |

**Los dos rankings no son comparables ni sumables.** Un tema puede tener muchos
mensajes y pocas sesiones, o al revés. Por eso el ranking lleva el encabezado
`Q de mensajes` — está en la constante `ENCABEZADO_UNIDAD_RANKING`.

### Formato de salida

```
Q de mensajes
1-Infracciones y Multas: (284.531)
2-Trámites y Reclamos: (198.472)
3-Salud (Médicos/Salud): (156.203)
4-Turnos (Generales): (143.887)
5-Movilidad + Estacionamiento: (121.044)
6-Licencia de Conducir: (98.765)
7-Impuestos (AGIP / Patentes / ABL): (87.412)
8-MIBA y Validación: (74.190)
9-Educación (Inscripciones/Becas): (61.038)
10-Interacción Humana (Chatear): (45.627)
```

Copialo de ahí y pegalo en el tablero.

> **Los números se agregaron en octubre 2026**, a pedido de la Dirección. Antes
> el ranking salía solo con los nombres de las categorías.
>
> `construir_ranking_texto()` acepta el conteo como argumento **opcional**: si
> no se lo pasás, devuelve el formato viejo sin números. Por eso
> `Temas_Consultados_Anual.py`, que importa esa función y la llama con un solo
> argumento, sigue funcionando igual que antes.

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

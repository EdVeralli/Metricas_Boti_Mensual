# Contenidos del Bot

## Descripción

Cuenta los contenidos del bot y los compara contra el mes anterior, leyendo
**dos exportaciones TSV de Botmaker**. Es el único módulo del repo que **no usa
AWS Athena** — trabaja 100% con archivos que vos exportás a mano.

Alimenta dos celdas del consolidado:

| Celda | Indicador | Qué cuenta |
|---|---|---|
| **D7** | Contenidos en Botmaker | Topics únicos con `Active = true` |
| **D8** | Contenidos Prendidos para el USUARIO | Topics únicos que sobreviven al filtro de relevancia |

## Estructura

```
Contenidos_Bot/
├── Contenidos_Bot.py       # Script principal
├── README.md               # Este archivo
├── rules-*.tsv             # Exportados de Botmaker (los ponés vos)
└── output/                 # Auto-generado
    ├── contenidos_bot_<mes>_<año>.xlsx          # Dashboard (D7, D8)
    └── contenidos_bot_detalle_<mes>_<año>.xlsx  # Métricas completas
```

## Requisitos

```bash
pip install pandas numpy openpyxl
```

**No requiere AWS ni VPN.**

## REQUISITO OBLIGATORIO: los 2 TSV

Antes de ejecutar tenés que exportar **2 archivos TSV desde Botmaker** y
copiarlos en esta carpeta:

| Archivo | Qué es | Ejemplo |
|---|---|---|
| TSV **mes actual** | Estado del bot al cierre del mes que se reporta | `rules-2026.09.01-17.41.tsv` |
| TSV **mes anterior** | Estado del bot del mes previo | `rules-2026.08.01-10.00.tsv` |

Formato obligatorio: `rules-YYYY.MM.DD-HH.MM.tsv`

Sin los 2 archivos el script aborta y **D7 y D8 quedan vacías** en el
consolidado.

> **Cuidado con los TSV viejos.** El script ordena todos los `rules-*.tsv` de la
> carpeta alfabéticamente y toma **los 2 últimos**. Como el nombre arranca con
> la fecha en formato `YYYY.MM.DD`, el orden alfabético coincide con el
> cronológico — pero si dejás acumular archivos de meses anteriores, siempre va
> a comparar los 2 más nuevos. Conviene dejar solo el par que corresponde.

Si encuentra un solo TSV, el script te dice **cuál mes falta** y con qué nombre
esperarlo, deduciéndolo de la fecha del archivo que sí está.

## Configuración

Lee el período de `../config_fechas.txt` **solo para nombrar los archivos de
salida**. Los datos salen de los TSV, no del período.

```ini
MES=8
AÑO=2026
```

El script busca el config en varias rutas (`../config_fechas.txt`,
`config_fechas.txt`, `../../config_fechas.txt`), así que funciona lo corras
desde donde lo corras.

## Uso

```powershell
# 1. Exportar los 2 TSV desde Botmaker y copiarlos acá
# 2. Ejecutar
cd C:\GCBA\Metricas_Boti_Mensual\Contenidos_Bot
python Contenidos_Bot.py
```

**Duración:** segundos (no hay query, solo lectura de archivos).

## Columnas que usa del TSV

| Columna | Para qué |
|---|---|
| `ID` | Identifica una **intención** (lo que se cuenta como "Intenciones") |
| `Topic` | Identifica un **contenido** (lo que se cuenta como "Contenidos") |
| `Topic path` | Ruta jerárquica del topic — se usa para excluir |
| `Active` | Si el contenido está prendido o apagado |
| `Name` | Nombre de la intención — se usa para excluir pushes |
| `Bot Says` | Texto de respuesta — se usa para clasificar y detectar cambios |

Si falta alguna, el script avisa pero sigue con lo que tenga.

### Lectura tolerante

El TSV de Botmaker viene con codificación variable, así que el script prueba en
orden: `utf-8-sig`, `utf-8`, `latin-1`, `iso-8859-1`, `cp1252`. Además limpia
los nombres de columna de espacios, comillas y BOM (`\ufeff`) — sin eso, la
primera columna llegaría como `\ufeffActive` y no matchearía.

### Normalización de `Active`

La columna `Active` puede venir como booleano, número o string. El script acepta
como verdadero: `true`, `1`, `yes`, `si`, `verdadero`, `activo`, `activa`
(case-insensitive). Cualquier otra cosa, o vacío, cuenta como apagado.

## El filtro de relevancia (de dónde sale D8)

D7 es simple: todos los topics con `Active = true`.

D8 es el subconjunto "de cara al usuario". Se llega aplicando **cinco
exclusiones** en cadena:

**1. Apagados** — descarta todo lo que tenga `Active = false`.

**2. Topics internos** — descarta las filas cuyo `Topic path` **empieza** con
alguno de estos:

```
Core de bot                    Notificaciones
Revisar                        Z. Apagados, detonables
2. Onboardings                 Z. Apagados, reciclables
Derivaciones                   Test
Push                           Utilidades para intenciones
AWS Polly                      Prueba
```

(también un `' '` — un espacio — para atrapar paths mal cargados)

**3. Topic path vacío** — descarta las filas sin ruta.

**4. Login** — descarta cualquier `Topic path` que **contenga** `Login`.

**5. Pushes** — descarta cualquier fila cuyo `Name` contenga `push`, `PUSH` o
`Push`.

Lo que queda es "contenido relevante para el usuario". D8 es la cantidad de
`Topic` únicos ahí adentro.

La lista de exclusiones está en la constante `EXCLUDED_TOPICS` en la cabecera
del script. Si Botmaker suma una categoría interna nueva, hay que agregarla ahí.

## Clasificación wording vs action

Sobre los contenidos ya filtrados, el script los parte en dos según la columna
`Bot Says`:

- **`action`** → `Bot Says` está vacío o tiene 1 carácter o menos. El contenido
  dispara una acción, no responde texto.
- **`wording`** → `Bot Says` tiene texto. El contenido le contesta algo al
  usuario.

Estas categorías **no van al consolidado**, quedan en el Excel de detalle.

## Detección de cambios entre meses

Comparando los dos TSV, el script reporta seis números:

**Nuevas / Eliminadas** — diferencia de conjuntos de `ID` (y de `Topic`) entre
mes actual y anterior. Directo y confiable.

**Modificadas** — acá hay una **heurística grosera** que conviene conocer: para
cada ID que existe en ambos meses, concatena todos sus `Bot Says`, compara el
**largo en caracteres** de ambas versiones, y si difieren en **más de 5
caracteres** lo cuenta como modificado.

> Eso significa que un cambio de redacción que mantenga largo similar
> (corregir una palabra por otra parecida) **no se detecta**, y que un cambio
> de formato irrelevante sí cuenta como modificación. Sirve como señal gruesa
> de actividad, no como auditoría de cambios.

## Outputs

### Dashboard — el que consolida

`output/contenidos_bot_<mes>_<año>.xlsx`

Template estándar de 17 filas con **D7** y **D8** completadas. Es el que lee
`consolidar_excel.py`.

### Detalle — métricas completas

`output/contenidos_bot_detalle_<mes>_<año>.xlsx`

Hoja `Contenidos Bot`, con dos bloques.

**Bloque 1 — comparación mes actual vs anterior (12 filas):**

| Dato | Mes Actual | Mes Anterior |
|---|---|---|
| Total Intenciones en el Bot | | |
| Total Contenidos en el Bot | | |
| Intenciones Prendidas | | |
| Intenciones Apagadas | | |
| **Contenidos Prendidos** ← D7 | | |
| Contenidos Apagados | | |
| Total Intenciones Relevantes | | |
| **Total Contenidos Relevantes** ← D8 | | |
| Intenciones Relevantes de Wording | | |
| Intenciones Relevantes de Acciones | | |
| Contenidos Relevantes de Wording | | |
| Contenidos Relevantes de Acciones | | |

**Bloque 2 — cambios entre períodos (6 filas):** intenciones y topics nuevos,
eliminados y modificados.

> **Ojo con la nomenclatura.** "Intenciones" cuenta `ID` únicos; "Contenidos"
> cuenta `Topic` únicos. Un topic agrupa varias intenciones, así que los
> números de intenciones son siempre mayores.

## Troubleshooting

**`No hay ningún archivo TSV en esta carpeta`** → Faltan los 2 TSV. Exportalos
de Botmaker y copialos acá.

**`Solo se encontró 1 archivo TSV`** → El script te dice qué mes detectó y cuál
falta, con el nombre esperado. Exportá el que falta.

**`[ADVERTENCIA] Columnas faltantes`** → Cambió el formato de exportación de
Botmaker. El script imprime las columnas que sí llegaron; hay que ver a qué
corresponden y ajustar `columnas_requeridas` en `cargar_tsv()`.

**`No se pudo leer el archivo con ninguna codificación`** → El TSV está
corrupto o no es un TSV. Verificar que se exportó bien desde Botmaker y que
tiene tabs como separador.

**D7 o D8 dan un número que no cierra** → Revisar `EXCLUDED_TOPICS`. Si
Botmaker agregó una categoría interna nueva que no está en la lista, sus topics
se están contando como relevantes.

## Relación con el resto del repo

| Módulo | Celda | Métrica |
|---|---|---|
| Usuarios y Conversaciones | D2, D3 | Conversaciones y Usuarios |
| Sesiones Abiertas | D4 | Sesiones iniciadas por push |
| Sesiones Alcanzadas | D5 | Sesiones que recibieron push |
| Pushes Enviadas | D6 | Mensajes push enviados |
| **Contenidos del Bot** (este) | **D7, D8** | **Contenidos activos y relevantes** |
| Contenidos más disparados | D11 | Top 10 contenidos |
| No Entendimiento | D13 | Tasa de no comprensión |
| Efectividad | D14 | % usuarios que lograron objetivo |
| CES | D15 | Customer Effort Score |
| CSAT | D16 | Customer Satisfaction |
| Disponibilidad | D17 | Uptime servidor WhatsApp |
| BAX Sesiones | *Excel propio* | Sesiones canal webchat BAX - App |

---

**Gobierno de la Ciudad de Buenos Aires — Data Analytics**

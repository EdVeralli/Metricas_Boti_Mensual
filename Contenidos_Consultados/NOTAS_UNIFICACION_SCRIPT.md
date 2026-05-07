# Notas de unificación del script de Contenidos Consultados

Registro del análisis realizado el **2026-04-23** que terminó con la unificación
del código en un único script `Contenidos_Consultados.py`.

Este archivo existe para que futuras sesiones (propias o de Claude) no tengan
que volver a hacer el análisis desde cero.

---

## Contexto previo

Hasta el 2026-04-23 había dos scripts conviviendo:

| Script | Qué hacía |
|--------|-----------|
| `Contenidos_Consultados.py` (v1) | Una única lista estática de ~117 nombres exactos a excluir (constante `CONTENIDOS_EXCLUIR`). Hacía la separación por prefijo y agrupación por (prefijo, fecha). |
| `Contenidos_Consultados_v2.py` (v2) | Filtrado en **2 capas** (patrones dinámicos + lista manual), nombres amigables, agrupación especial TUR00CUX02. |

La spec autoritativa está en el Word:

> `Lógica de armado de contenidos más consultados.docx`
> (modificado el 2026-04-23)

---

## Checklist — spec del Word vs implementaciones

| Spec del Word (sección BOTI) | v1 | v2 |
|------------------------------|:--:|:--:|
| **CAPA 1** — Filtro dinámico por patrones (`CONTAINS`, case-insensitive) | ❌ **No existía** | ✅ |
| Patrones: push, recordatorio, confirmación, cancelacion, CXF, CAT, api, onboarding, menú, Invocar, Bifurcador, No entendidos / No, nada de eso / No entend, Orquestador, CTA, Atiende, Agente, V2, Instancia, SIGECI, USIG, Botonera, _autenticacion, Solicitud, Reconocer, `_`, Terminar, Cierre, Chau | ❌ | ✅ Todos |
| Separación por primer espacio → `RulenameUnique` (equivalente del DAX) | ✅ | ✅ |
| Agrupar por `(RulenameUnique, Fecha)` y quedarse con el de más sesiones | ✅ | ✅ |
| **Ajustes marzo 2026 — CAPA 2 manual:** | | |
| • `Licencia prorroga  > Consultar` (con doble espacio, así viene en los datos) | ❌ | ✅ |
| • `MO05CUX01 > Tiene que renovar` | ❌ | ✅ |
| • `LIC00CUX00 Validaciones` | ❌ | ✅ |
| • `MO08CUX03 Apertura` (subcontenido de TelePASE/AUSA) | ❌ | ✅ |
| **Ajustes marzo 2026 — CAPA 1 dinámica:** patrón `BOT0` (CONTAINS) | ❌ | ✅ |

**Conclusión:** `v2` implementaba el 100% de la spec. `v1` estaba desactualizado
(le faltaba toda la CAPA 1 dinámica y las 5 reglas de marzo 2026).

---

## Decisión

Unificar en un único script. La opción elegida fue **reemplazar `v1` con el
contenido de `v2`**, y quedarse con el nombre `Contenidos_Consultados.py`
(así `run_all.py`, que llamaba al v1, usa automáticamente el código correcto).

### Acciones aplicadas (2026-04-23)

1. `git rm Contenidos_Consultados.py` — borrado del v1 (git conserva la historia).
2. `git mv Contenidos_Consultados_v2.py Contenidos_Consultados.py` — promoción del v2.
3. Edición del header del script para remover referencias a "(v2)" / "VERSION 2".
4. Edición de `README.md`:
   - Se eliminó la sección "Versiones" (tabla v1 vs v2).
   - Se quitaron los bloques "(v1)" y "(v2)" de títulos y de la sección de Lógica de Procesamiento.
   - Se dejó un único comando de ejecución en la sección Uso.
   - Se actualizó la estructura del proyecto.
5. Edición de `exclusiones_capa2.md`: ahora apunta a `Contenidos_Consultados.py`.

### Archivos tocados

- `Contenidos_Consultados.py` (nuevo contenido = viejo v2, con header limpio)
- `Contenidos_Consultados_v2.py` (borrado)
- `README.md` (actualizado)
- `exclusiones_capa2.md` (actualizado)

`run_all.py` no se tocó (ya apuntaba al nombre correcto).

---

## Estado final

Hay **un único script** en la carpeta que implementa la totalidad de la spec
del Word, incluyendo los ajustes de marzo 2026. Si en una futura sesión ven
archivos `_v2.py` u otros sufijos de versión, probablemente alguien haya
vuelto a bifurcar — revisar contra este md y contra el `.docx` de lógica.

## Cómo validar en el futuro

Si se sospecha que el script volvió a atrasarse respecto de la spec:

1. Extraer el texto del `.docx` con `python-docx` (el `.pdf` puede estar
   desactualizado — en el análisis original lo estaba: el `.pdf` era del
   12-mar, el `.docx` del 23-abr).
2. Comparar la lista de `PATRONES_EXCLUIR` y `CONTENIDOS_EXCLUIR_MANUAL` del
   script contra la lista del Word.
3. Chequear que los "Ajustes al filtrado de contenidos (marzo 2026)" del Word
   estén todos reflejados.

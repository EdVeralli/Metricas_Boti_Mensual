# No Entendimiento - Módulo D13

## 📊 Descripción
Calcula el porcentaje de "No Entendimiento" del chatbot, sumando:
- **NE (No Entendimiento):** Casos con score de confianza ≤ 5.36
- **Nada:** Casos sin resultado válido

**Fórmula:** `D13 = % NE + % Nada`

---

## 📁 Estructura de Carpetas

```
No_Entendimiento/
├── data/                          ← ARCHIVOS DE ENTRADA (actualizar mensualmente)
│   ├── testers.csv               ← Lista de usuarios de prueba
│   └── Actualizacion_Lista_Blanca.csv  ← Lista de intenciones válidas
├── output/                        ← Salida (se genera automáticamente)
│   ├── no_entendimiento_octubre_2025.csv
│   ├── no_entendimiento_detalle_octubre_2025.xlsx
│   └── no_entendimiento_octubre_2025.xlsx  ← Dashboard con D13
├── No_Entendimiento.py           ← Programa principal
└── README.md                      ← Este archivo
```

---

## 📥 Archivos de Entrada (carpeta `data/`)

### 1. **testers.csv**
Lista de usuarios de prueba a excluir del análisis.

**Formato esperado:**
```
f0_
GE6NEV1ZHNDRXIAAQVGV
LU0VWVFLOK130EGKD1LR
S2311UDJQVQZ1B4L1LM2
...
```

**Proveedor:** [Área encargada]  
**Frecuencia:** Actualización mensual  
**Ubicación:** `No_Entendimiento/data/testers.csv`

---

### 2. **Actualizacion_Lista_Blanca.csv**
Lista de intenciones válidas del chatbot.

**Formato esperado:**
```
Nombre de la intención,Nombre corto de la intención,ID de la intencion
ED00CUX01 Estudiantes,Estudiantes,RuleBuilder:PLBWX5XYGQ2B3GP7IN8Q-...
TUR00CUX02 Turnos para salud,Turnos para salud,RuleBuilder:PLBWX5XYGQ2B3GP7IN8Q-...
...
```

**Proveedor:** [Área encargada]  
**Frecuencia:** Actualización mensual  
**Ubicación:** `No_Entendimiento/data/Actualizacion_Lista_Blanca.csv`

---

## ⚙️ Configuración

El programa lee las fechas desde: `../config_fechas.txt` (raíz del proyecto)

**Ejemplo - Mes completo:**
```
MES=10
AÑO=2025
```

**Ejemplo - Rango personalizado:**
```
FECHA_INICIO=2025-10-01
FECHA_FIN=2025-10-15
```

---

## 🚀 Ejecución

### Desde la carpeta del módulo:
```bash
cd No_Entendimiento
python No_Entendimiento.py
```

### Desde el script maestro (raíz del proyecto):
```bash
python run_all.py
```

---

## 📤 Archivos de Salida (carpeta `output/`)

1. **CSV:** `no_entendimiento_octubre_2025.csv`
   - Resultados en formato tabular

2. **Excel Detallado:** `no_entendimiento_detalle_octubre_2025.xlsx`
   - Análisis completo con todas las categorías
   - Porcentajes desglosados
   - Cálculo final de D13

3. **Dashboard Master:** `no_entendimiento_octubre_2025.xlsx`
   - Archivo con estructura de dashboard
   - **Celda D13:** Porcentaje de No Entendimiento (formato: `4.60%`)
   - Usado por el consolidador para generar el dashboard unificado

---

## ⚠️ Notas Importantes

### Si faltan los archivos de entrada:
- El programa **continuará ejecutándose**
- Mostrará **warnings** en la consola
- No aplicará filtros de testers ni lista blanca

### Comportamiento del programa:
```
[WARNING] No se encuentra data/testers.csv
          Continuando sin filtro de testers...

[WARNING] No se encuentra data/Actualizacion_Lista_Blanca.csv
          Continuando sin filtro de lista blanca...
```

### Valores de configuración fijos:
- **INTENT_NADA:** `RuleBuilder:PLBWX5XYGQ2B3GP7IN8Q-alfafc@gmail.com-1536777380652`
- **THRESHOLD_NE:** `5.36` (umbral de score para considerar "no entendimiento")

---

## 🔧 Integración con el Sistema

### En `run_all.py`:
```python
{
    'nombre': 'No Entendimiento',
    'carpeta': 'No_Entendimiento',
    'script': 'No_Entendimiento.py',
    'celdas': 'D13',
    'requiere_aws': True
}
```

### En `consolidar_excel.py`:
```python
'no_entendimiento': {
    'carpeta': 'No_Entendimiento/output',
    'patron': 'no_entendimiento_*.xlsx',
    'celdas': {'D13': 'No Entendimiento'},
    'excluir_patron': '*_detalle_*'
}
```

---

## 📊 Dashboard - Fila 13

| Columna B | Columna C | Columna D |
|-----------|-----------|-----------|
| No entendimiento | Performance motor de búsqueda | **4.60%** |

**Formato:** Porcentaje con 2 decimales (`0.00%`)

---

## 🔐 Requisitos AWS

- **Rol:** PIBAConsumeBoti
- **Workgroup:** Production-caba-piba-athena-boti-group
- **Database:** caba-piba-consume-zone-db
- **Tablas:** 
  - `boti_message_metrics_2`
  - `boti_intent_search`
  - `boti_intent_search_response`
  - `boti_intent_search_user_buttons`

---

## 📞 Contacto

Para actualización de archivos de entrada, contactar:
- **testers.csv:** [Área/Persona responsable]
- **Actualizacion_Lista_Blanca.csv:** [Área/Persona responsable]

---

**Última actualización:** Diciembre 2024

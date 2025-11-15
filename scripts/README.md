# scripts/ - Scripts de Procesamiento

Esta carpeta contiene scripts ejecutables para procesar datos, entrenar modelos ML y generar reportes.

## 📂 Estructura

```
scripts/
├── pipeline/                # Pipeline de procesamiento de datos
│   ├── main_pipeline.py     # Pipeline ETL principal
│   └── legacy_pipeline.py   # Pipeline legacy (referencia histórica)
├── train_ml_models.py       # Entrenamiento de modelos ML
├── ml/                      # Scripts ML adicionales
├── reporting/               # Generación de reportes
│   ├── generar_pdf.py
│   └── generar_pdf_simple.py
└── validation/              # Scripts de validación
    ├── check_columns.py
    ├── check_specific_columns.py
    ├── validacion_informes.py
    └── verificacion_completa.py
```

---

## 🚀 Scripts Principales

### 1. `pipeline/main_pipeline.py`

**Descripción:** Pipeline ETL modular que procesa datos crudos y genera todos los Parquet necesarios.

**Qué hace:**
1. Carga CSVs de `data/raw/`:
   - `SERIE_COMPROBANTES_COMPLETOS.csv` (transacciones)
   - `RENTABILIDAD.csv` (margen por producto)
   - `FERIADOS_2024_2025.csv` (calendario)

2. Ejecuta ETL principal (limpieza, normalización, enriquecimiento)

3. Calcula KPIs estandarizados:
   - KPI por día
   - KPI por tipo de día (feriado vs normal)
   - KPI por categoría
   - KPI por medio de pago

4. Ejecuta análisis avanzados:
   - Market Basket Analysis (Apriori)
   - Clasificación Pareto (ABC)
   - Clustering de tickets (K-Means)
   - Pronósticos semanales (Promedio Móvil + Tendencia)

5. Exporta Parquet a `data/processed/`:
   - `detalle_lineas.parquet`
   - `tickets.parquet`
   - `ventas_semanales_categoria.parquet`
   - `kpi_*.parquet` (varios)
   - `reglas.parquet`, `combos_recomendados.parquet`
   - `pareto_*.parquet`
   - `clusters_tickets.parquet`

**Uso:**
```bash
python -m scripts.pipeline.main_pipeline
```

**Duración estimada:** 1-2 horas (dependiendo del volumen de datos)

**Cuándo ejecutar:**
- Después de actualizar `SERIE_COMPROBANTES_COMPLETOS.csv`
- Después de cambios en datos de rentabilidad
- Para regenerar todos los Parquet desde cero

---

### 2. `train_ml_models.py`

**Descripción:** Entrena modelos ML y ejecuta simuladores de estrategias para calcular ROI.

**Qué hace:**
1. Carga datasets procesados desde `data/processed/`:
   - `tickets.parquet`
   - `detalle_lineas.parquet`
   - `reglas.parquet`
   - `pareto_categoria.parquet`

2. Ejecuta simuladores ML:
   - **TicketPredictor:** Modelo base (XGBoost) para predecir monto y margen
   - **ComboSimulator:** Estima ROI de combos focalizados
   - **MarcaPropiaEstimator:** Simula lanzamiento de marca propia
   - **CrossSellOptimizer:** Optimiza cross-merchandising
   - **UpsellingDetector:** Estima impacto de upselling en caja
   - **FidelizacionSimulator:** Simula programa de fidelización

3. Exporta resultados a `data/ml_results/`:
   - `strategy_roi_summary.parquet` (resumen consolidado)
   - `strategy_roi_details.json` (detalles por estrategia)

4. Muestra resumen de ROI en consola:
   ```
                   Estrategia  Inversión  Margen Incremental    ROI %
   Combos Focalizados           150000.0          22,952,500  183,620%
   Programa Fidelización        300000.0           7,633,335   30,533%
   Marca Propia                 500000.0           8,441,821   20,260%
   Cross-Merchandising           80000.0           1,011,252   15,169%
   Upselling en Caja            120000.0             381,500    3,815%
   ```

**Uso:**
```bash
python scripts/train_ml_models.py
```

**Duración estimada:** 10-30 segundos

**Cuándo ejecutar:**
- Después de ejecutar `main_pipeline.py`
- Cuando necesites actualizar estimaciones de ROI
- Antes de presentar dashboard a stakeholders

---

## 🛠️ Scripts Auxiliares

### `validation/`

Scripts para validar integridad y consistencia de datos:

- **`check_columns.py`**: Verifica columnas en Parquet
- **`check_specific_columns.py`**: Valida columnas específicas
- **`validacion_informes.py`**: Valida coherencia de KPIs
- **`verificacion_completa.py`**: Verificación integral de datos

**Uso:**
```bash
python scripts/validation/verificacion_completa.py
```

---

### `reporting/`

Scripts para generar reportes PDF:

- **`generar_pdf.py`**: Generación de PDFs con gráficos
- **`generar_pdf_simple.py`**: Versión simplificada

**Uso:**
```bash
python scripts/reporting/generar_pdf.py
```

---

## 🔄 Flujo Completo de Actualización

Cuando actualizas `SERIE_COMPROBANTES_COMPLETOS.csv`, ejecuta:

### Opción 1: Automática (Recomendado)
```bash
python actualizar_metricas.py
```

Este script ejecuta automáticamente:
1. `scripts/pipeline/main_pipeline.py`
2. Copia archivos a `data/app_dataset/`
3. `scripts/train_ml_models.py`

---

### Opción 2: Manual (Paso por paso)
```bash
# Paso 1: Procesar datos
python -m scripts.pipeline.main_pipeline

# Paso 2: Copiar archivos (PowerShell)
Copy-Item -Path "data\processed\*.parquet" -Destination "data\app_dataset\" -Force

# Paso 3: Entrenar modelos ML
python scripts/train_ml_models.py

# Paso 4: Iniciar dashboard
streamlit run dashboard_cientifico.py
```

---

## 📊 Outputs Generados

### Por `main_pipeline.py`:

**En `data/processed/`:**
- `detalle_lineas.parquet` (2.9M registros, ~35 MB)
- `tickets.parquet` (306K registros, ~6 MB)
- `ventas_semanales_categoria.parquet` (~50 KB)
- `kpi_dia.parquet`, `kpi_categoria.parquet`, etc.
- `reglas.parquet` (reglas de asociación)
- `combos_recomendados.parquet`
- `pareto_producto.parquet`, `pareto_categoria.parquet`
- `clusters_tickets.parquet`
- `adjacency_pairs.parquet` (para grafos de productos)

**En `data/predictivos/`:**
- `prediccion_ventas_semanal.parquet`
- `prediccion_ventas_semanal_modelos.parquet`

---

### Por `train_ml_models.py`:

**En `data/ml_results/`:**
- `strategy_roi_summary.parquet` - Tabla consolidada de ROI
- `strategy_roi_details.json` - Detalles y metadata de cada estrategia

---

## 🐛 Troubleshooting

### Error: "No module named 'src'"
**Solución:** Ejecuta desde la raíz del proyecto
```bash
cd "d:\OneDrive\GitHub\supermercado_nino definitivo claude"
python -m scripts.pipeline.main_pipeline
```

---

### Error: "File not found: SERIE_COMPROBANTES_COMPLETOS.csv"
**Solución:** Verifica que el CSV existe en `data/raw/`
```bash
ls data/raw/SERIE_COMPROBANTES_COMPLETOS.csv
```

---

### Pipeline toma mucho tiempo
**Normal:** Con 3M+ registros, el pipeline puede tardar 1-2 horas.
- ETL: ~5 minutos
- Market Basket: ~10 segundos
- Pareto: ~1 segundo
- **Clustering: 1+ hora** (es el más lento, procesa 300K tickets)
- Pronósticos: ~1 segundo

---

### Clustering se queda colgado
**Solución:** El clustering con K-Means es intensivo. Si tarda más de 2 horas:
1. Revisa logs en consola
2. Verifica que no haya otros procesos consumiendo CPU
3. Considera reducir el dataset temporalmente para testing

---

## 📝 Logs

Los scripts usan `logging` para mostrar progreso:

```
2025-11-05 10:08:22 | INFO | Iniciando pipeline modular
2025-11-05 10:08:22 | INFO | Cargando datasets base
2025-11-05 10:08:28 | INFO | Ejecutando ETL principal
2025-11-05 10:09:44 | INFO | Calculando KPIs estandarizados
2025-11-05 10:09:45 | INFO | Ejecutando market basket
2025-11-05 10:09:54 | INFO | Calculando Pareto de margen
2025-11-05 10:09:54 | INFO | Clustering de tickets
2025-11-05 11:18:39 | INFO | Generando pronosticos semanales
2025-11-05 11:18:39 | INFO | Pipeline finalizado correctamente
```

---

## 🎯 Mejores Prácticas

1. **Siempre ejecuta `main_pipeline.py` ANTES de `train_ml_models.py`**
   - Los modelos ML necesitan los Parquet procesados

2. **No interrumpas el clustering**
   - Puede tomar 1+ hora, pero es crucial para segmentación

3. **Verifica espacio en disco**
   - Los Parquet ocupan ~50 MB
   - El CSV crudo ocupa ~477 MB

4. **Usa `actualizar_metricas.py` para automatización**
   - Es más fácil y menos propenso a errores

---

## 📞 Soporte

Para problemas con scripts, contacta a: contacto@pymeinside.com

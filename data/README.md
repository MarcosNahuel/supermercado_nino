# data/ - Datos y Resultados

Esta carpeta contiene todos los datos del sistema: datos crudos, procesados, pronósticos y resultados de modelos ML.

## 📂 Estructura

```
data/
├── raw/                    # Datos crudos originales (CSV) - gitignored
├── processed/              # Datos procesados por el pipeline (Parquet)
├── predictivos/            # Pronósticos y predicciones
├── ml_results/             # Resultados de simuladores ML
└── app_dataset/            # Dataset optimizado que consume el dashboard
```

---

## 📊 Subcarpetas

### 1. `raw/` - Datos Crudos (Gitignored)

**Descripción:** CSVs originales sin procesar.

**Archivos principales:**

#### `SERIE_COMPROBANTES_COMPLETOS.csv` (477 MB)
- **Contenido:** 2,944,659 líneas de comprobantes de venta
- **Periodo:** Octubre 2024 - Octubre 2025
- **Columnas principales:**
  - `fecha`, `numero_comprobante`, `linea`
  - `producto`, `cantidad`, `precio_unitario`, `subtotal`
  - `categoria`, `departamento`
  - `medio_pago` (Efectivo, Débito, Crédito, etc.)
  - `descuento`, `iva`

**⚠️ IMPORTANTE:** Este es el archivo central. Cuando lo actualices, ejecuta:
```bash
python actualizar_metricas.py
```

#### `RENTABILIDAD.csv` (~100 KB)
- **Contenido:** Margen bruto por producto
- **Columnas:** `producto`, `costo`, `precio_venta`, `margen_porcentaje`, `margen_pesos`
- **Uso:** Enriquecer análisis con datos de rentabilidad

#### `FERIADOS_2024_2025.csv` (~1 KB)
- **Contenido:** Calendario de feriados argentinos
- **Columnas:** `fecha`, `descripcion`, `tipo`
- **Uso:** Marcar días especiales para análisis de estacionalidad

---

### 2. `processed/` - Datos Procesados

**Descripción:** Parquet generados por `scripts/pipeline/main_pipeline.py`

**Archivos generados:**

#### Datasets Principales
- **`detalle_lineas.parquet`** (~35 MB, 2.9M registros)
  - Cada línea de comprobante limpia y enriquecida
  - Incluye: fecha, producto normalizado, categoría, margen, medio de pago, es_feriado

- **`tickets.parquet`** (~6 MB, 306K registros)
  - Tickets agregados con métricas totales
  - Columnas: fecha, ventas_totales, margen_total, unidades_totales, productos_unicos, medio_pago

- **`ventas_semanales_categoria.parquet`** (~53 KB)
  - Series temporales semanales por categoría
  - Usado para pronósticos

#### KPIs
- **`kpi_dia.parquet`** (~31 KB)
  - KPIs diarios: ventas, margen, tickets, ticket promedio, items por ticket

- **`kpi_tipo_dia.parquet`** (~5 KB)
  - Comparación feriados vs días normales

- **`kpi_categoria.parquet`** (~58 KB)
  - Performance por categoría: top 48 categorías

- **`kpi_medio_pago.parquet`** (~9 KB) ⭐
  - **Este archivo se actualiza con cambios en medios de pago**
  - Métricas por forma de pago: Efectivo, Débito, Crédito, etc.

#### Market Basket Analysis
- **`reglas.parquet`** (~21 KB, 132 reglas)
  - Reglas de asociación Apriori: {A} → {B}
  - Métricas: support, confidence, lift
  - Ejemplo: {Fernet} → {Coca Cola}, lift=8.5

- **`combos_recomendados.parquet`** (~6 KB)
  - Top combos para promocionar
  - Ordenados por lift y frecuencia

- **`adjacency_pairs.parquet`** (~6 KB)
  - Pares de productos para visualización de grafos

#### Pareto (80/20)
- **`pareto_producto.parquet`** (~396 KB, ~10K productos)
  - Clasificación ABC de productos por margen
  - Columnas: producto, margen_acumulado, margen_pct_acumulado, categoria_pareto (A/B/C)

- **`pareto_categoria.parquet`** (~5 KB, 48 categorías)
  - Clasificación ABC de categorías

#### Clustering
- **`clusters_tickets.parquet`** (~6 MB, 306K registros)
  - Tickets con cluster_id asignado (K=4 óptimo)
  - Segmentación por comportamiento de compra

- **`clusters_tickets_centroides.parquet`** (~4 KB)
  - Centros de cada cluster (promedios de features)

---

### 3. `predictivos/` - Pronósticos

**Descripción:** Predicciones generadas por `src/features/predictivos_ventas_simple.py`

**Archivos:**

- **`prediccion_ventas_semanal.parquet`** (~12 KB)
  - Pronósticos de ventas para próximas 4 semanas
  - Por categoría
  - Modelo: Promedio Móvil (8 semanas) + Tendencia lineal

- **`prediccion_ventas_semanal_modelos.parquet`** (~5 KB)
  - Metadata de modelos: MAE, RMSE, tendencia estimada

**Metodología:**
- NO usa ARIMA (demasiado complejo)
- Usa Promedio Móvil + Tendencia (interpretable y auditable)
- Ver documentación en `src/features/predictivos_ventas_simple.py`

---

### 4. `ml_results/` - Resultados ML

**Descripción:** Outputs de `scripts/train_ml_models.py`

**Archivos:**

- **`strategy_roi_summary.parquet`** (~2 KB)
  - Tabla consolidada de ROI de estrategias
  - Columnas: estrategia, inversion, margen_incremental, roi_pct, payback_meses, confianza

- **`strategy_roi_details.json`** (~10 KB)
  - Detalles por estrategia:
    - Descripción
    - Metodología
    - Supuestos
    - Riesgos
    - Plan de implementación

**Estrategias simuladas:**
1. **Combos Focalizados** (ROI: 183,620%)
2. **Programa Fidelización** (ROI: 30,533%)
3. **Marca Propia** (ROI: 20,260%)
4. **Cross-Merchandising** (ROI: 15,169%)
5. **Upselling en Caja** (ROI: 3,815%)

---

### 5. `app_dataset/` - Dataset del Dashboard

**Descripción:** Subset optimizado de `processed/` que consume el dashboard.

**Qué contiene:**
- Copia de archivos clave de `processed/`
- Archivos adicionales específicos del dashboard
- Optimizado para carga rápida en Streamlit

**Archivos principales:**
- Todos los `kpi_*.parquet`
- `tickets.parquet`
- `reglas.parquet`, `combos_recomendados.parquet`
- `pareto_*.parquet`
- `clusters_tickets.parquet`
- Pronósticos

**Actualización:**
Automática cuando ejecutas:
```bash
python actualizar_metricas.py
```

---

## 🔄 Flujo de Datos

```
data/raw/SERIE_COMPROBANTES_COMPLETOS.csv
              ↓
    [Pipeline ETL]
              ↓
     data/processed/*.parquet
              ↓
    [Copia automática]
              ↓
     data/app_dataset/*.parquet
              ↓
     [Dashboard lee]
              ↓
   Visualizaciones en Streamlit
```

---

## 📏 Tamaños y Métricas

### Datos Crudos (raw/)
- **Total:** ~500 MB (gitignored)
- `SERIE_COMPROBANTES_COMPLETOS.csv`: 477 MB

### Datos Procesados (processed/)
- **Total:** ~47 MB
- Mayor: `detalle_lineas.parquet` (35 MB)
- Segundo: `tickets.parquet` (6 MB)

### App Dataset (app_dataset/)
- **Total:** ~19 MB
- Optimizado para carga rápida

### Métricas de negocio
- **Periodo:** Oct 2024 - Oct 2025 (13 meses)
- **Transacciones:** 2,944,659 líneas
- **Tickets:** 306,011
- **SKUs únicos:** 10,372
- **Categorías:** 48 activas
- **Ventas totales:** $8,218.5M ARS
- **Margen bruto:** $2,236.1M ARS (27.2%)

---

## 🔒 Seguridad y Privacidad

### Archivos gitignored
Los datos crudos NO se suben a Git (definido en `.gitignore`):
```
data/raw/
data/processed/
data/predictivos/
data/ml_results/
data/app_dataset/
```

Solo se suben:
- Scripts de procesamiento
- Estructura de carpetas
- README.md

**⚠️ No compartas CSVs crudos:** Contienen datos sensibles de ventas.

---

## 🛠️ Regenerar Datos

### Desde cero (todo)
```bash
python actualizar_metricas.py
```

### Solo pipeline
```bash
python -m scripts.pipeline.main_pipeline
```

### Solo modelos ML
```bash
python scripts/train_ml_models.py
```

---

## 📊 Formatos de Datos

### ¿Por qué Parquet?

**Ventajas:**
- **Compresión:** 477 MB CSV → ~50 MB Parquet (10x más pequeño)
- **Velocidad:** 10-100x más rápido de leer que CSV
- **Tipado:** Preserva tipos de datos (int, float, datetime)
- **Columnar:** Acceso eficiente a columnas específicas

**Desventajas:**
- No se puede abrir directamente en Excel
- Requiere bibliotecas como pandas o pyarrow

### Leer Parquet en Python
```python
import pandas as pd

# Leer archivo completo
df = pd.read_parquet("data/processed/tickets.parquet")

# Leer solo columnas específicas
df = pd.read_parquet(
    "data/processed/tickets.parquet",
    columns=["fecha", "ventas_totales", "margen_total"]
)
```

---

## 🗂️ Backup y Versionado

### Recomendaciones

1. **Backup del CSV crudo**
   ```bash
   # Crear backup con fecha
   cp data/raw/SERIE_COMPROBANTES_COMPLETOS.csv \
      data/raw/SERIE_COMPROBANTES_COMPLETOS_2025-11-05.csv
   ```

2. **Versionado semántico de Parquet**
   - Los Parquet se regeneran automáticamente
   - No necesitan versionado manual
   - Confía en Git para versionado de scripts

3. **Snapshot antes de cambios grandes**
   ```bash
   # Crear snapshot de processed/
   tar -czf data_processed_backup_2025-11-05.tar.gz data/processed/
   ```

---

## 🐛 Problemas Comunes

### "Out of Memory" al procesar
**Solución:** El CSV de 477 MB puede consumir 2-3 GB de RAM.
- Cierra otras aplicaciones
- Considera procesar por chunks si tienes < 4 GB RAM

### Parquet corrupto
**Solución:** Regenera desde cero
```bash
rm -rf data/processed/*.parquet
python -m scripts.pipeline.main_pipeline
```

### Datos desactualizados en dashboard
**Solución:** Recarga el dashboard (F5 o R en navegador)

---

## 📞 Soporte

Para problemas con datos, contacta a: contacto@pymeinside.com

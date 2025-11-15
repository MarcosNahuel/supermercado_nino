# src/ - Código Fuente Modular

Esta carpeta contiene todo el código fuente modular del sistema de análisis de Supermercado NINO, organizado por responsabilidades.

## 📂 Estructura

```
src/
├── __init__.py              # Inicializador del paquete
├── data_prep/               # Preparación y limpieza de datos
├── features/                # Generación de características y KPIs
├── ml_models/               # Modelos de Machine Learning
└── utils/                   # Utilidades y funciones auxiliares
```

## 📦 Módulos

### 1. `data_prep/` - Preparación de Datos

**Responsabilidad:** Limpieza, normalización y enriquecimiento de datos crudos.

**Archivos principales:**
- `etl_basico.py` - Pipeline ETL principal que:
  - Lee CSV de comprobantes
  - Normaliza texto (nombres de productos, categorías)
  - Enriquece con datos de rentabilidad
  - Marca días feriados
  - Calcula métricas agregadas por ticket
  - Genera datasets procesados (detalle_lineas, tickets, ventas_semanales)

**Output:** DataFrames limpios y normalizados listos para análisis.

---

### 2. `features/` - Generación de Características

**Responsabilidad:** Calcular KPIs, análisis avanzados y features para ML.

**Archivos principales:**

#### `kpis_basicos.py`
Calcula KPIs estándar del negocio:
- **KPI por día:** Ventas, margen, tickets por fecha
- **KPI por tipo de día:** Comparación feriados vs días normales
- **KPI por categoría:** Performance de cada categoría de productos
- **KPI por medio de pago:** Análisis por forma de pago (efectivo, débito, crédito, etc.)

#### `market_basket.py`
Análisis de asociación de productos (Market Basket Analysis):
- Algoritmo Apriori para encontrar reglas de asociación
- Métricas: support, confidence, lift
- Genera combos recomendados basados en co-ocurrencia
- Output: `reglas.parquet`, `combos_recomendados.parquet`, `adjacency_pairs.parquet`

#### `pareto_margen.py`
Clasificación ABC (Pareto 80/20):
- Identifica productos/categorías que generan el 80% del margen
- Clasifica en A (top 80%), B (15%), C (5%)
- Análisis por producto y por categoría
- Output: `pareto_producto.parquet`, `pareto_categoria.parquet`

#### `clustering_tickets.py`
Segmentación de tickets:
- K-Means clustering de tickets por comportamiento de compra
- Features: monto total, margen, unidades, productos únicos
- Búsqueda automática del mejor K usando silhouette score
- Output: `clusters_tickets.parquet`, `clusters_tickets_centroides.parquet`

#### `predictivos_ventas_simple.py`
Pronósticos de ventas semanales:
- Modelo interpretable basado en Promedios Móviles + Tendencia
- NO usa ARIMA (demasiado complejo para stakeholders)
- Genera pronósticos por categoría
- Output: `prediccion_ventas_semanal.parquet`, `prediccion_ventas_semanal_modelos.parquet`

**¿Por qué NO ARIMA?**
- Transparencia: "Promedio de últimas 8 semanas" es fácil de explicar
- Auditabilidad: Los gerentes pueden verificar cálculos manualmente
- Suficiencia: Para series cortas (<2 años), ARIMA no ofrece ventajas significativas

---

### 3. `ml_models/` - Modelos de Machine Learning

**Responsabilidad:** Simuladores ML para estimar ROI de estrategias comerciales.

**Archivos principales:**

#### `ticket_predictor.py`
Modelo base para predecir monto y margen de tickets:
- XGBoost Regressor
- Features: productos únicos, unidades, categorías, día de semana, medio de pago
- Usado como "contrafactual" para medir impacto de estrategias

#### `combo_simulator.py`
Simula impacto de combos focalizados:
- Identifica productos que aparecen juntos (ej: Fernet + Coca)
- Estima uplift en margen por promocionar combos
- ROI estimado: 183,620% (ejemplo: Fernet+Coca)

#### `marca_propia_estimator.py`
Simula lanzamiento de marca propia en categorías A:
- Identifica categorías Pareto A con mayor margen
- Estima sustitución de productos de marca externa
- ROI estimado: 20,260%

#### `cross_sell_optimizer.py`
Simula cross-merchandising guiado por reglas de asociación:
- Usa reglas de Market Basket para reordenar layout
- Estima incremento en ventas por productos complementarios
- ROI estimado: 15,169%

#### `upselling_detector.py`
Simula estrategia de upselling en línea de caja:
- Identifica productos de alto margen para promover
- Estima conversión en caja
- ROI estimado: 3,815%

#### `fidelizacion_simulator.py`
Simula programa de fidelización sin IDs de cliente:
- Usa clustering como proxy de segmentos de clientes
- Estima incremento en frecuencia de compra
- ROI estimado: 30,533%

#### `strategy_validator.py`
Orquestador que:
- Ejecuta todos los simuladores
- Consolida resultados de ROI
- Genera reportes en Parquet y JSON
- Output: `data/ml_results/strategy_roi_summary.parquet`, `strategy_roi_details.json`

---

### 4. `utils/` - Utilidades

**Responsabilidad:** Funciones auxiliares reutilizables.

**Archivos principales:**

#### `load_data.py`
Funciones de carga de datos:
- `load_sales_data()` - Carga CSV de comprobantes
- `load_rentabilidad_data()` - Carga datos de rentabilidad por producto
- `load_feriados()` - Carga calendario de feriados
- `ensure_directory()` - Crea directorios si no existen

---

## 🔧 Uso de los Módulos

### Ejemplo: ETL Básico
```python
from src.data_prep.etl_basico import run_etl
from src.utils.load_data import load_sales_data, load_rentabilidad_data, load_feriados

# Cargar datos
sales = load_sales_data("data/raw/SERIE_COMPROBANTES_COMPLETOS.csv")
rent = load_rentabilidad_data("data/raw/RENTABILIDAD.csv")
feriados = load_feriados("data/raw/FERIADOS_2024_2025.csv")

# Ejecutar ETL
artifacts = run_etl(sales, rent, feriados)

# Acceder a resultados
print(artifacts.detalle.head())  # Detalle de líneas
print(artifacts.tickets.head())  # Tickets agregados
```

### Ejemplo: Market Basket
```python
from src.features.market_basket import run_market_basket
from pathlib import Path

# Ejecutar análisis
run_market_basket(
    detalle_df=artifacts.detalle,
    output_dir=Path("data/processed")
)

# Lee resultados
import pandas as pd
reglas = pd.read_parquet("data/processed/reglas.parquet")
combos = pd.read_parquet("data/processed/combos_recomendados.parquet")
```

### Ejemplo: Simuladores ML
```python
from src.ml_models.strategy_validator import run_all_strategies

# Ejecuta todos los simuladores y genera ROI
run_all_strategies(
    tickets_path="data/processed/tickets.parquet",
    detalle_path="data/processed/detalle_lineas.parquet",
    output_dir="data/ml_results"
)
```

---

## 🎯 Principios de Diseño

1. **Modularidad:** Cada módulo tiene una responsabilidad única y clara
2. **Reutilización:** Funciones compartidas en `utils/`
3. **Dataclasses:** Uso de dataclasses para estructuras de datos
4. **Type Hints:** Anotaciones de tipos para mejor mantenibilidad
5. **Logging:** Logs informativos en operaciones críticas
6. **Parquet:** Output en formato Parquet para eficiencia

---

## 📊 Flujo de Datos

```
CSV Crudos (data/raw/)
    ↓
[src/data_prep/etl_basico.py]
    ↓
DataFrames Limpios
    ↓
[src/features/*.py]
    ↓
KPIs, Clustering, Market Basket, Pronósticos
    ↓
Parquet Procesados (data/processed/)
    ↓
[src/ml_models/*.py]
    ↓
Simulaciones de ROI (data/ml_results/)
    ↓
Dashboard (dashboard_cientifico.py)
```

---

## 🛠️ Mantenimiento

### Agregar un nuevo KPI

1. Crea función en `src/features/kpis_basicos.py`
2. Agrega export en `export_kpis()`
3. Actualiza `scripts/pipeline/main_pipeline.py`

### Agregar un nuevo simulador ML

1. Crea archivo en `src/ml_models/nuevo_simulador.py`
2. Implementa clase con método `run()`
3. Agrega en `src/ml_models/strategy_validator.py`
4. Ejecuta `python scripts/train_ml_models.py`

---

## 📞 Soporte

Para dudas sobre el código fuente, contacta a: contacto@pymeinside.com

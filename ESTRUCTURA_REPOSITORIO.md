# Estructura del Repositorio - Supermercado NINO

Documentación completa de la estructura organizada del repositorio después de la reorganización de Noviembre 2025.

## 📁 Estructura General

```
supermercado_nino/
│
├── 📱 ARCHIVOS PRINCIPALES
│   ├── dashboard_cientifico.py           # Dashboard científico principal (Streamlit)
│   ├── README.md                         # Documentación principal del proyecto
│   ├── requirements.txt                  # Dependencias Python
│   │
│   ├── actualizar_metricas.py            # Script de actualización automática
│   ├── actualizar_metricas.bat           # Script Windows (doble clic)
│   ├── iniciar_dashboard.bat             # Script para iniciar dashboard
│   └── ACTUALIZACION_AUTOMATICA.md       # Guía de actualización
│
├── 💻 src/                               # Código fuente modular
│   ├── README.md                         # Documentación del código fuente
│   ├── data_prep/                        # Preparación y limpieza de datos
│   ├── features/                         # Generación de KPIs y características
│   ├── ml_models/                        # Modelos de Machine Learning
│   └── utils/                            # Utilidades y helpers
│
├── 🛠️ scripts/                          # Scripts de procesamiento
│   ├── README.md                         # Documentación de scripts
│   ├── pipeline/                         # Pipeline ETL principal
│   │   └── main_pipeline.py              # Procesador de datos
│   ├── train_ml_models.py                # Entrenamiento de modelos ML
│   ├── ml/                               # Scripts ML adicionales
│   ├── reporting/                        # Generación de reportes
│   └── validation/                       # Scripts de validación
│
├── 📊 data/                              # Datos y resultados
│   ├── README.md                         # Documentación de datos
│   ├── raw/                              # CSVs originales (gitignored)
│   ├── processed/                        # Parquet procesados
│   ├── predictivos/                      # Pronósticos
│   ├── ml_results/                       # Resultados de modelos ML
│   └── app_dataset/                      # Dataset del dashboard
│
└── 🗃️ RESTO/                             # Archivos archivados
    ├── README.md                         # Documentación de archivos archivados
    ├── app/                              # Dashboard versión anterior
    ├── final/                            # Versión pre-reorganización
    ├── legacy/                           # Código legacy
    ├── docs/                             # Documentación histórica
    └── archivos_misc/                    # Scripts y archivos diversos
```

---

## 📖 Descripción de Carpetas Principales

### 🎯 Raíz del Proyecto

**Propósito:** Archivos ejecutables principales y documentación de alto nivel.

**Archivos clave:**
- **`dashboard_cientifico.py`** - Aplicación principal del sistema
- **`actualizar_metricas.py`** - Automatización de actualización de datos
- **`README.md`** - Punto de entrada de documentación

**Uso típico:**
```bash
# Iniciar dashboard
streamlit run dashboard_cientifico.py

# Actualizar métricas
python actualizar_metricas.py
```

**README:** [`README.md`](README.md)

---

### 💻 `src/` - Código Fuente

**Propósito:** Código Python modular organizado por responsabilidades.

**Subcarpetas:**
- **`data_prep/`** - ETL, limpieza y normalización
- **`features/`** - Cálculo de KPIs, Market Basket, Pareto, Clustering, Pronósticos
- **`ml_models/`** - Simuladores ML para estrategias de ROI
- **`utils/`** - Funciones reutilizables

**Uso típico:**
```python
from src.data_prep.etl_basico import run_etl
from src.features.market_basket import run_market_basket
from src.ml_models.strategy_validator import run_all_strategies
```

**README:** [`src/README.md`](src/README.md)

---

### 🛠️ `scripts/` - Scripts de Procesamiento

**Propósito:** Scripts ejecutables para procesar datos y entrenar modelos.

**Archivos principales:**
- **`pipeline/main_pipeline.py`** - Pipeline ETL completo (1-2 horas)
- **`train_ml_models.py`** - Entrenamiento de modelos ML (10-30 seg)

**Uso típico:**
```bash
# Procesar datos desde CSV
python -m scripts.pipeline.main_pipeline

# Entrenar modelos ML
python scripts/train_ml_models.py
```

**README:** [`scripts/README.md`](scripts/README.md)

---

### 📊 `data/` - Datos y Resultados

**Propósito:** Almacenamiento de datos crudos, procesados y resultados.

**Subcarpetas:**
- **`raw/`** - CSVs originales (477 MB, gitignored)
- **`processed/`** - Parquet procesados (~47 MB)
- **`predictivos/`** - Pronósticos semanales
- **`ml_results/`** - Resultados de simuladores ML
- **`app_dataset/`** - Dataset optimizado para dashboard (~19 MB)

**Archivos clave en raw/:**
- `SERIE_COMPROBANTES_COMPLETOS.csv` (2.9M registros)
- `RENTABILIDAD.csv`
- `FERIADOS_2024_2025.csv`

**README:** [`data/README.md`](data/README.md)

---

### 🗃️ `RESTO/` - Archivos Archivados

**Propósito:** Versiones anteriores y archivos no esenciales, conservados por referencia histórica.

**Subcarpetas:**
- **`app/`** - Dashboard versión Oct 2024
- **`final/`** - Versión pre-reorganización (Nov 2025)
- **`legacy/`** - Código y pipelines legacy
- **`docs/`** - Documentación histórica
- **`archivos_misc/`** - Scripts sueltos (PDFs, análisis, etc.)

**⚠️ Importante:** NO eliminar sin revisar. Contiene código histórico y decisiones técnicas documentadas.

**README:** [`RESTO/README.md`](RESTO/README.md)

---

## 🚀 Flujos de Trabajo Principales

### 1. Iniciar el Dashboard

```bash
# Opción 1: Comando directo
streamlit run dashboard_cientifico.py

# Opción 2: Script Windows (doble clic)
iniciar_dashboard.bat
```

**URL:** http://localhost:8501

---

### 2. Actualizar Datos (Después de modificar CSV)

```bash
# Opción 1: Script Python automático (recomendado)
python actualizar_metricas.py

# Opción 2: Script Windows (doble clic)
actualizar_metricas.bat
```

**Lo que hace:**
1. Ejecuta pipeline ETL completo
2. Copia archivos procesados a app_dataset
3. Entrena modelos ML
4. ✅ Listo para recargar dashboard

**Duración:** 1-2 horas

---

### 3. Desarrollo y Debugging

#### Procesar solo datos (sin ML)
```bash
python -m scripts.pipeline.main_pipeline
```

#### Entrenar solo modelos ML (requiere datos procesados)
```bash
python scripts/train_ml_models.py
```

#### Validar integridad de datos
```bash
python scripts/validation/verificacion_completa.py
```

---

## 📚 Documentación Disponible

| Archivo | Descripción |
|---------|-------------|
| [`README.md`](README.md) | Documentación principal del proyecto |
| [`ACTUALIZACION_AUTOMATICA.md`](ACTUALIZACION_AUTOMATICA.md) | Guía de actualización automática |
| [`ESTRUCTURA_REPOSITORIO.md`](ESTRUCTURA_REPOSITORIO.md) | Este archivo - Estructura del repositorio |
| [`src/README.md`](src/README.md) | Documentación del código fuente |
| [`scripts/README.md`](scripts/README.md) | Documentación de scripts |
| [`data/README.md`](data/README.md) | Documentación de datos |
| [`RESTO/README.md`](RESTO/README.md) | Documentación de archivos archivados |

---

## 🎯 Archivos por Propósito

### Para Usuarios/Stakeholders
- `README.md` - Entender el proyecto
- `ACTUALIZACION_AUTOMATICA.md` - Actualizar métricas
- `iniciar_dashboard.bat` - Abrir dashboard

### Para Desarrolladores
- `src/README.md` - Entender código fuente
- `scripts/README.md` - Ejecutar pipelines
- `data/README.md` - Trabajar con datos
- `ESTRUCTURA_REPOSITORIO.md` - Navegar repositorio

### Para Análisis Histórico
- `RESTO/README.md` - Versiones anteriores
- `RESTO/docs/` - Documentación archivada
- `RESTO/legacy/` - Código legacy

---

## 🔄 Cambios en la Reorganización (Nov 2025)

### ✅ Qué se movió

| Origen | Destino | Razón |
|--------|---------|-------|
| `final/streamlit_app/dashboard_cientifico.py` | `dashboard_cientifico.py` (raíz) | Simplificar acceso |
| `app/` | `RESTO/app/` | Versión antigua |
| `final/` | `RESTO/final/` | Versión anterior |
| `legacy/` | `RESTO/legacy/` | Ya era legacy |
| `docs/` | `RESTO/docs/` | Docs históricas |
| Scripts sueltos | `RESTO/archivos_misc/` | Ordenar raíz |
| `.claude/`, `.devcontainer/` | `RESTO/` | Configs IDE |

### ✅ Qué se creó

- **`actualizar_metricas.py`** - Script de automatización
- **`actualizar_metricas.bat`** - Script Windows
- **`iniciar_dashboard.bat`** - Lanzador de dashboard
- **`ACTUALIZACION_AUTOMATICA.md`** - Guía de actualización
- **`ESTRUCTURA_REPOSITORIO.md`** - Este documento
- **READMEs en cada carpeta** - Documentación modular

### ✅ Qué se actualizó

- **`README.md`** - Nueva estructura y comandos
- **`scripts/pipeline/main_pipeline.py`** - Fix de rutas
- **Todas las rutas de archivos** - Apuntan a nueva estructura

---

## 🔒 Archivos Gitignored

Estos archivos NO se suben a Git (contienen datos sensibles):

```
data/raw/
data/processed/
data/predictivos/
data/ml_results/
data/app_dataset/
.env
__pycache__/
*.pyc
```

Solo se versionan:
- Código fuente (`src/`, `scripts/`)
- Archivos de configuración
- Documentación
- Estructura de carpetas

---

## 🎓 Principios de Diseño

1. **Simplicidad:** Archivos principales en raíz
2. **Modularidad:** Código organizado por responsabilidad
3. **Documentación:** README en cada carpeta
4. **Automatización:** Scripts para tareas comunes
5. **Histórico:** Versiones anteriores en `RESTO/`

---

## 📞 Contacto y Soporte

- **Email:** contacto@pymeinside.com
- **Web:** https://pymeinside.com
- **Proyecto:** Supermercado NINO © 2025

---

**Última actualización:** Noviembre 5, 2025
**Versión:** 2.0 (Post-reorganización)

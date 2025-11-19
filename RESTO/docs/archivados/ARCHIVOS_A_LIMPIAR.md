# Archivos a Limpiar/Archivar - Supermercado NINO

## Archivos de Test Temporales (Eliminar o Mover a legacy/tests/)

Estos archivos fueron creados para validación puntual y ya no son necesarios:

1. **test_parquet.py**
   - Propósito: Verificar lectura de archivos parquet
   - Ubicación actual: Raíz del proyecto
   - Acción recomendada: Eliminar (funcionalidad ya integrada en pipeline)

2. **check_columns.py**
   - Propósito: Verificar columnas de datasets
   - Ubicación actual: Raíz del proyecto
   - Acción recomendada: Eliminar (chequeo ya incorporado en ETL)

3. **check_specific_columns.py**
   - Propósito: Validación específica de columnas
   - Ubicación actual: Raíz del proyecto
   - Acción recomendada: Eliminar

4. **test_data_loading.py**
   - Propósito: Test de carga de datos
   - Ubicación actual: Raíz del proyecto
   - Acción recomendada: Eliminar

5. **test_temporal_analysis.py**
   - Propósito: Test de análisis temporal
   - Ubicación actual: Raíz del proyecto
   - Acción recomendada: Eliminar

---

## Código Legacy (Mover a legacy/ y Renombrar)

Estos archivos fueron reemplazados por versiones mejoradas:

1. **src/features/predictivos_ventas.py**
   - Propósito: Pronósticos usando ARIMA (modelo antiguo)
   - Ubicación actual: src/features/
   - Reemplazado por: src/features/predictivos_ventas_simple.py
   - Acción recomendada: Renombrar a `predictivos_ventas_arima_legacy.py` y mover a `legacy/features/`

---

## Archivos que Mantener

NO eliminar estos archivos ya que son parte del pipeline activo:

✅ **pipeline_estrategias.py** - Pipeline alternativo (puede ser útil)
✅ **validacion_informes.py** - Validación de outputs
✅ **main_pipeline.py** - Pipeline principal
✅ **dashboard_cientifico.py** - Dashboard activo

---

## Plan de Limpieza Recomendado

### Paso 1: Crear estructura para archivos legacy

```bash
mkdir legacy/tests
mkdir legacy/features
```

### Paso 2: Mover archivos de test

```bash
# Desde la raíz del proyecto
del test_parquet.py
del check_columns.py
del check_specific_columns.py
del test_data_loading.py
del test_temporal_analysis.py
```

O si quieres conservarlos:

```bash
move test_*.py legacy/tests/
move check_*.py legacy/tests/
```

### Paso 3: Archivar modelo ARIMA antiguo

```bash
move src\features\predictivos_ventas.py legacy\features\predictivos_ventas_arima_legacy.py
```

### Paso 4: Actualizar .gitignore

Agregar las siguientes líneas a `.gitignore`:

```
# Test files temporales
test_*.py
check_*.py

# Archivos de datos no versionados
data/raw/*.csv
data/processed/*.parquet
data/predictivos/*.parquet

# Caches de Python
__pycache__/
*.py[cod]
*$py.class
*.so

# Entornos virtuales
.venv/
venv/
ENV/
env/

# Configuraciones IDE
.vscode/
.idea/
*.code-workspace

# Logs
*.log
logs/

# Archivos temporales Windows
Thumbs.db
Desktop.ini
```

### Paso 5: Verificar que todo funciona

```bash
python main_pipeline.py
streamlit run dashboard_cientifico.py
```

---

## Limpieza de Datos (Opcional - Liberar Espacio)

Si necesitas liberar espacio en disco:

### Archivos Parquet Intermedios

Estos pueden regenerarse ejecutando `main_pipeline.py`:

```bash
# ADVERTENCIA: Solo eliminar si estás seguro de poder regenerarlos
# del data\processed\*.parquet
# del data\predictivos\*.parquet
```

### CSV Raw (NUNCA ELIMINAR)

⚠️ **NO eliminar archivos en `data/raw/`** - son la fuente de verdad:

```
data/raw/SERIE_COMPROBANTES_COMPLETOS.csv
data/raw/RENTABILIDAD.csv
data/raw/FERIADOS_2024_2025.csv
data/raw/comprobantes_ventas_horario.csv
```

---

## Resultado Esperado Post-Limpieza

### Estructura Final del Proyecto

```
supermercado_nino/
├── data/
│   ├── raw/                      # CSV originales (CONSERVAR)
│   ├── processed/                # Parquet procesados (regenerables)
│   └── predictivos/              # Pronósticos (regenerables)
├── src/
│   ├── data_prep/
│   │   └── etl_basico.py
│   ├── features/
│   │   ├── kpis_basicos.py
│   │   ├── market_basket.py
│   │   ├── clustering_tickets.py
│   │   ├── pareto_margen.py
│   │   └── predictivos_ventas_simple.py  # ACTIVO
│   └── utils/
│       └── load_data.py
├── legacy/
│   ├── apps/                     # Dashboards antiguos
│   ├── pipelines/               # Pipelines antiguos
│   ├── features/                # Código legacy
│   │   └── predictivos_ventas_arima_legacy.py  # ARIMA antiguo
│   └── tests/                   # Tests temporales archivados
│       ├── test_parquet.py
│       ├── check_columns.py
│       └── ...
├── main_pipeline.py             # ACTIVO
├── dashboard_cientifico.py      # ACTIVO
├── README.md                    # ACTUALIZADO
├── GUIA_PRONOSTICOS.md         # NUEVO
├── RESUMEN_MEJORAS.md          # NUEVO
├── requirements.txt
└── .gitignore                   # CREAR/ACTUALIZAR
```

### Espacio Liberado Estimado

- Test files: ~50 KB
- Reorganización: 0 bytes (solo mover)
- Total: Mínimo (principalmente organización, no reducción)

---

## Verificación Post-Limpieza

Ejecutar estos comandos para verificar que todo sigue funcionando:

```bash
# 1. Verificar imports del pipeline
python -c "from src.features import predictivos_ventas_simple; print('OK')"

# 2. Ejecutar pipeline completo
python main_pipeline.py

# 3. Lanzar dashboard
streamlit run dashboard_cientifico.py
```

Si todo funciona correctamente, la limpieza fue exitosa.

---

## Notas Importantes

1. **Respaldo antes de eliminar**: Considera hacer commit de Git antes de eliminar archivos
2. **Pipeline activo**: Asegúrate de que `main_pipeline.py` usa `predictivos_ventas_simple` (ya está actualizado)
3. **Dashboard compatible**: El dashboard ya soporta ambos modelos (ARIMA legacy y Simple nuevo)
4. **Documentación preservada**: README.md y GUIA_PRONOSTICOS.md explican el cambio de modelo

---

**Fecha de creación:** 20 de Octubre de 2025
**Responsable:** Equipo pymeinside.com

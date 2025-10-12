# 📁 Data Directory

## Estructura

```
data/
├── raw/                        # Datos originales (gitignored)
│   ├── SERIE_COMPROBANTES_COMPLETOS2.csv  # Dataset principal (395MB)
│   └── RENTABILIDAD.csv                   # Rentabilidad por departamento
│
├── processed/FASE1_OUTPUT/     # Datos procesados (gitignored)
│   ├── 01_ITEMS_VENTAS.csv
│   ├── 02_TICKETS.csv
│   ├── 03_KPI_PERIODO.csv
│   ├── 04_KPI_CATEGORIA.csv
│   ├── 05_PARETO_PRODUCTOS.csv
│   ├── 06_REGLAS_ASOCIACION.csv
│   ├── 07_PERFILES_CLUSTERS.csv
│   └── 08_KPI_DIA_SEMANA.csv
│
├── app_dataset/                # Paquete Parquet usado por Streamlit
│   ├── clusters.parquet
│   ├── kpi_categoria.parquet
│   ├── kpi_dia.parquet
│   ├── kpi_periodo.parquet
│   ├── pareto.parquet
│   ├── reglas.parquet
│   └── tickets.parquet
│
└── sample/FASE1_OUTPUT_SAMPLE/ # Muestra liviana para demos
    └── (archivos CSV)
```

## Archivos Finales en `raw/`

### SERIE_COMPROBANTES_COMPLETOS2.csv
- **Descripción:** Dataset principal con todas las transacciones
- **Periodo:** Octubre 2024 - Octubre 2025
- **Registros:** 2.9M+ líneas
- **Tamaño:** ~395 MB
- **Formato:** CSV delimitado por `;`, decimal con `,`

### RENTABILIDAD.csv
- **Descripción:** Porcentaje de rentabilidad por departamento
- **Registros:** 45 categorías
- **Formato:** CSV con columnas Departamento, % Rentabilidad, Clasificación

## Generación de Datos Procesados

Para regenerar los archivos en `processed/`, ejecuta:

```bash
python FASE1_ANALISIS_COMPLETO.py
```

Este script lee los archivos de `raw/` y genera 8 archivos CSV optimizados para análisis y visualización.

## Uso en la Aplicación

La aplicación `app_streamlit_supabase.py` utiliza el contenido de `data/app_dataset/`
por defecto. Si esa carpeta no está disponible, cae automáticamente a la muestra
liviana en `data/sample/FASE1_OUTPUT_SAMPLE/`.

Para regenerar el paquete Parquet después de ejecutar el pipeline completo:

```bash
python scripts/build_app_dataset.py
```

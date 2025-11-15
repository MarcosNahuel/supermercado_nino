# Legacy directory

Componentes conservados para referencia histórica. Ninguno se ejecuta en el flujo oficial (`pipeline_estrategias.py` -> `dashboard_cientifico.py`), pero se mantienen para reproducir entregables anteriores o migraciones.

## Estructura

```
legacy/
|- apps/            # Dashboards Streamlit previos (Supabase, modo simple)
|- pipelines/       # FASE1_ANALISIS_COMPLETO.py (pipeline CSV original)
|- scripts/         # build_app_dataset.py (CSV -> Parquet) y caché
|- data/
|  |- processed/    # Salidas masivas (FASE1_OUTPUT)
|  \- sample/       # Dataset demo liviano (FASE1_OUTPUT_SAMPLE)
\- outputs/         # CSV auxiliares generados durante la fase 1
```

## Cuándo usarlos
- **Dashboards legacy (`apps/`)**: para demos con Supabase o la versión simplificada. Requieren los Parquet anteriores o la muestra en `legacy/data/sample/`.
- **Pipeline FASE1 (`pipelines/`)**: reproduce la primera versión basada en CSV. Solo es necesario si se quiere regenerar los archivos de `legacy/data/processed/`.
- **Scripts legacy (`scripts/`)**: utilidades ligadas al pipeline CSV (por ejemplo `build_app_dataset.py`). No son necesarias para el dashboard científico.
- **Datos legacy (`data/`, `outputs/`)**: conservan la evidencia histórica y pueden usarse como respaldo o casos de prueba.

> Consejo: mantener esta carpeta fuera de despliegues productivos para reducir peso y evitar confusiones. El flujo activo se encuentra en la raíz del repositorio.

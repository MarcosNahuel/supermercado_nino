# Supermercado NINO - Guia integral del repositorio

Este repositorio contiene el proyecto de analitica de ventas para Supermercado NINO. Incluye un pipeline de procesamiento que consolida mas de tres millones de transacciones, genera indicadores clave y empaqueta los datos en formato Parquet, junto con un dashboard interactivo construido en Streamlit para consumir esos resultados sin depender de servicios externos.

## Componentes principales
- `app_streamlit_supabase.py`: dashboard Streamlit con visualizaciones de KPIs, analisis Pareto, reglas de asociacion y segmentacion de tickets. Carga primero los Parquet de `data/app_dataset` y, si faltan, recurre a la muestra ligera en `data/sample/FASE1_OUTPUT_SAMPLE`.
- `FASE1_ANALISIS_COMPLETO.py`: pipeline ETL de la fase 1. Limpia datos POS, crea variables temporales, calcula KPIs, genera reglas Apriori y clusters K-Means, y exporta resultados listos para reporting.
- `data/`: contiene los insumos y salidas del pipeline. La subcarpeta `app_dataset` almacena los Parquet versionados que usa el dashboard; `sample/FASE1_OUTPUT_SAMPLE` conserva una muestra liviana en CSV.
- `scripts/`: utilidades para regenerar el dataset (`build_app_dataset.py`), preparar tablas en Supabase (`setup_supabase_tables.py`), migrar datos (`migrate_to_supabase.py`) y limpiar contenidos (`clean_supabase.py`).
- `docs/`: documentacion funcional y tecnica adicional (deploy en Supabase, resuenes ejecutivos e insights).
- `INICIAR_DASHBOARD.bat`: script de Windows que instala dependencias y levanta el dashboard con Streamlit.

## Flujo de datos resumido
1. Pipeline (`FASE1_ANALISIS_COMPLETO.py`) ingesta y depura los comprobantes POS.
2. Se calculan KPIs globales y por categoria, analisis Pareto, tickets enriquecidos y reglas de asociacion.
3. Los resultados se exportan a CSV en `data/processed` y luego a Parquet mediante `scripts/build_app_dataset.py`.
4. El dashboard carga los Parquet, valida columnas requeridas y expone visualizaciones interactivas con Plotly.
5. Si no encuentra los Parquet, utiliza la muestra demo para asegurar que la aplicacion siempre tenga datos disponibles.

## Dataset incluido
- `data/app_dataset/*.parquet`: paquete completo versionado en el repositorio. Ideal para usar el dashboard sin correr el pipeline.
- `data/sample/FASE1_OUTPUT_SAMPLE/*.csv`: subset liviano para demos, cargado automaticamente cuando falta el dataset principal.
- `data/raw` y `data/processed/FASE1_OUTPUT`: rutas esperadas por el pipeline para almacenar insumos y salidas completas (gitignored).

## Dependencias y requisitos
- Python 3.10 o superior (verificado por `INICIAR_DASHBOARD.bat`).
- Librerias listadas en `requirements.txt`: Streamlit, Plotly, Pandas, NumPy, Scikit-learn, MLxtend, PyArrow, entre otras.
- Para regenerar datos con el pipeline se necesita MLxtend para Apriori y Scikit-learn para clustering.
- Opcional: cuenta de Supabase si se desea desplegar el dataset en la nube usando los scripts del directorio `scripts/`.

## Como ejecutar el dashboard
1. Crear y activar un entorno virtual (recomendado): `python -m venv .venv` y `.venv\Scripts\activate`.
2. Instalar dependencias: `pip install -r requirements.txt`.
3. Ejecutar Streamlit de forma manual: `streamlit run app_streamlit_supabase.py`.
4. Alternativa rapida en Windows: doble clic en `INICIAR_DASHBOARD.bat`, que automatiza la instalacion y el arranque del servidor en `http://localhost:8501`.

## Scripts auxiliares
- `scripts/build_app_dataset.py`: transforma la salida CSV del pipeline a Parquet optimizado para la app.
- `scripts/setup_supabase_tables.py`: crea tablas en Supabase segun el esquema esperado por el dashboard.
- `scripts/migrate_to_supabase.py`: sube los datasets procesados a Supabase.
- `scripts/clean_supabase.py`: elimina datos previos en Supabase cuando se requiere una recarga completa.
- `scripts/create_tables.sql`: definicion SQL para levantar la estructura de datos en Supabase.

## Documentacion complementaria
- `docs/DEPLOY_SUPABASE.md`: guia paso a paso para desplegar la base en Supabase.
- `docs/SUPABASE_SQL_SCRIPTS.md`: scripts SQL listos para provisionar o limpiar tablas.
- `docs/RESUMEN_EJECUTIVO_ACTUALIZADO.md`, `docs/RESUMEN_PROYECTO_FINAL.md` y `docs/CONCLUSIONES_ESTRATEGIAS_FINALES.md`: resumenes ejecutivos y recomendaciones de negocio.

## Supabase (opcional)
El dashboard puede conectarse a Supabase, pero la version actual prioriza el uso de datos locales. Si se desea usar Supabase:
- Configurar credenciales en `.env` siguiendo `docs/DEPLOY_SUPABASE.md`.
- Ejecutar `scripts/setup_supabase_tables.py` para crear la estructura.
- Cargar datos con `scripts/migrate_to_supabase.py`.
- Ajustar la configuracion del dashboard (variables de entorno) para apuntar a Supabase en lugar de los Parquet locales.

## Buenas practicas recomendadas
- Mantener actualizado el dataset Parquet ejecutando `scripts/build_app_dataset.py` cada vez que se corra el pipeline completo.
- Verificar `data/app_dataset` antes de levantar el dashboard para evitar que quede en modo demo.
- Versionar solo los Parquet y scripts; los datos masivos de `data/raw` y `data/processed` deben permanecer fuera del control de versiones.
- Revisar los avisos en la barra lateral de Streamlit: indican si faltan columnas o si se esta utilizando el dataset de muestra.
- Documentar cambios analiticos o nuevos KPIs dentro de `docs/` para mantener alineados a los usuarios del dashboard.

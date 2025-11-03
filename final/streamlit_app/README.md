# Streamlit - Dashboard Cientifico NINO

Esta carpeta contiene la version preparada para entrega del dashboard cientifico del Supermercado NINO.

## Contenido

- `dashboard_cientifico.py`: aplicacion principal de Streamlit (copiada desde `app/dashboard.py`).
- `requirements.txt`: dependencias minimas para ejecutar la app.
- `.streamlit/config.toml`: configuracion visual base (opcional).
- Referencia adicional: `docs/guias/GUIA_DASHBOARD_CIENTIFICO.md` documenta la arquitectura completa.

## Pre requisitos

1. Python 3.10 o superior.
2. Dataset procesado en las rutas:
   - `data/app_dataset/*.parquet` (ver lista completa en la guia).
   - `data/processed/*.parquet`.
   - `data/predictivos/*.parquet`.
   - `data/raw/comprobantes_ventas_horario.csv`.

## Instalacion rapida

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux / macOS
pip install -r final/streamlit_app/requirements.txt
```

## Ejecucion

```bash
streamlit run final/streamlit_app/dashboard_cientifico.py
```

El script utiliza rutas relativas a la raiz del repositorio, por lo que es recomendable lanzar el comando desde la carpeta raiz.

## Notas

- Las visualizaciones usan el modo wide y un CSS custom incluido en el script.
- Si faltan archivos de datos, la vista relacionada mostrara un mensaje informativo y evitara errores.
- Ajustes adicionales de estilo pueden hacerse en `.streamlit/config.toml`.

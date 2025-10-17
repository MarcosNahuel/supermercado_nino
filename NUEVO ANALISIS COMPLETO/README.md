# NUEVO ANALISIS COMPLETO

Proyecto independiente para el analisis de rentabilidad del ticket de Supermercado NINO. Incluye pipeline reproducible y dashboard Streamlit con KPIs, Pareto y medios de pago.

## Estructura

`
/app
  /streamlit_app.py
  /components/
  /assets/
/config
  /settings.yaml
/data
  /raw/
  /processed/
/reports
  /cuaderno_agente.md
  /resumen_bullets.md
`

## Requisitos

`
python >= 3.10
pip install -r requirements.txt
`

## Configuracion

1. Ajusta config/settings.yaml si los paths de datos difieren del repositorio.
2. Asegurate de ubicar SERIE_COMPROBANTES_COMPLETOS3.csv y RENTABILIDAD.csv en data/raw/.

## Pipeline de datos

`
python app/pipeline.py
`

Genera salidas en `data/processed/` y un reporte de calidad en
`reports/data_quality.json`.

- items.csv: lineas de ticket normalizadas con margen estimado.
- tickets.csv: agregados por ticket con ventas, margen y unidades.
- kpi_ciclos_*.csv: ciclos anual, mensual, semanal ISO y diario.
- pareto_global.csv, pareto_mensual.csv, pareto_semana.csv.
- kpi_medios_pago.csv, data_dictionary.csv.

> Nota: el procesamiento completo sobre el dataset original (~2.6M filas) puede demorar entre 8 y 10 minutos en hardware de escritorio.

## Dashboard Streamlit

`
streamlit run app/streamlit_app.py
`

Funcionalidades principales:

- Filtros por fecha, departamento, medio de pago y emisor.
- KPIs de ticket rentable y desviaciones.
- Series ciclicas (mes, semana ISO, dia) y distribucion de tickets.
- Pareto global/mensual/semanal con clasificacion ABC.
- Analisis de medios de pago y descargas de datos filtrados.
- Visualizacion del diccionario de datos.

## Documentacion viva

- Bitacora del analista: `reports/cuaderno_agente.md`.
- Hallazgos y estrategias: `reports/resumen_bullets.md`.

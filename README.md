# Supermercado NINO – Analytics Dashboard

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

Dashboard interactivo para analizar 3M+ transacciones de Supermercado NINO, con KPIs ejecutivos, Pareto, Market Basket y segmentación de tickets.

## Características clave

- **KPIs ejecutivos** con métricas globales y tendencias mensuales.
- **Pareto 80/20** para identificar productos críticos y oportunidades de margen.
- **Market Basket** con reglas Apriori y filtros dinámicos.
- **Segmentación de tickets** basada en clustering K-Means.
- **Dataset ligero en Parquet** incluido en `data/app_dataset/` (sin depender de Supabase).
- **UI moderna** con Plotly y animaciones personalizadas en Streamlit.

## KPIs destacados

| Métrica | Valor |
| --- | --- |
| Ventas totales | $8.218,5M ARS |
| Margen bruto | $2.236,1M ARS (27,2%) |
| Tickets | 306.011 |
| Ticket promedio | $26.849 ARS |
| Items por ticket | 9,8 |
| Categorías activas | 45 |
| SKUs únicos | 10.372 |

Periodo analizado: octubre 2024 – octubre 2025.

## Quick start

```bash
git clone https://github.com/MarcosNahuel/supermercado_nino.git
cd supermercado_nino

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux / macOS

pip install -r requirements.txt

# Regenerar el paquete Parquet (usa pipeline unificado)
python pipeline_estrategias.py
# Alternativa legacy (CSV -> Parquet)
# python scripts/build_app_dataset.py

streamlit run dashboard_cientifico.py
```

El dashboard cargará por defecto los archivos Parquet de `data/app_dataset/`. Si esa carpeta no existe, se usa la muestra liviana `data/sample/FASE1_OUTPUT_SAMPLE/` para mantener la demo operativa.

> ¿Necesitas cargar la base completa en Supabase? El soporte sigue disponible en `docs/DEPLOY_SUPABASE.md` y `docs/SUPABASE_SQL_SCRIPTS.md`, pero ya no es obligatorio para desplegar en Streamlit Cloud.

## Estructura del proyecto

`
supermercado_nino/
|- dashboard_cientifico.py        # Dashboard final (storytelling + KPIs)
|- pipeline_estrategias.py        # Pipeline unificado (raw -> parquet)
|- app_streamlit_supabase.py      # Dashboard legacy (mantiene soporte Supabase)
|- dashboard.py                   # Dashboard legacy simplificado
|- FASE1_ANALISIS_COMPLETO.py     # Pipeline ETL fase 1 (legacy CSV)
|- scripts/
|  \- build_app_dataset.py       # Legacy conversor CSV -> Parquet
|- data/
|  |- raw/                       # Datasets originales (gitignored)
|  |- processed/FASE1_OUTPUT/    # Salida legacy del pipeline fase 1 (gitignored)
|  |- app_dataset/               # Parquet listos para la app (versionados)
|  \- sample/FASE1_OUTPUT_SAMPLE/# Muestra liviana para demos
|- docs/                          # Documentacion funcional y tecnica
|  |- DEPLOY_SUPABASE.md
|  |- SUPABASE_SQL_SCRIPTS.md
|  |- RESUMEN_EJECUTIVO_ACTUALIZADO.md
|  |- RESUMEN_PROYECTO_FINAL.md
|  \- CONCLUSIONES_ESTRATEGIAS_FINALES.md
|- requirements.txt
\- README.md
`

## Tecnologías

- **Streamlit + Plotly** para la capa de visualización.
- **Pandas, NumPy, Scikit-learn y MLxtend** para procesamiento analítico.
- **PyArrow** para empaquetar los datasets en Parquet (5,5 MB en vez de ~420 MB de CSV).
- **Scripts opcionales con Supabase** para quien desee escalar la base de datos en la nube.

## Metodología analítica

1. Limpieza y enriquecimiento de 3M+ comprobantes.
2. Cálculo de KPIs mensuales y por categoría.
3. Clasificación ABC para Pareto.
4. Reglas de asociación (Apriori) para Market Basket.
5. Clustering K-Means para segmentar tickets.
6. Empaquetado a Parquet + visualización en Streamlit.

## Roadmap

- [x] ETL fase 1 completo (Oct 2024 – Oct 2025).
- [x] Dashboard Streamlit v2 con UI moderna.
- [x] Paquete Parquet local para deploy sin Supabase.
- [ ] Sistema de alertas (stock y ventas).
- [ ] Modelos predictivos de demanda.
- [ ] Integración con ERP/POS en tiempo real.
- [ ] App mobile para gerencia.

## Documentación relacionada

- `docs/DEPLOY_SUPABASE.md` – guía opcional para usar Supabase.
- `docs/SUPABASE_SQL_SCRIPTS.md` – sentencias SQL para limpiar/repoblar Supabase.
- `docs/RESUMEN_EJECUTIVO_ACTUALIZADO.md` – KPIs consolidados.
- `docs/RESUMEN_PROYECTO_FINAL.md` y `docs/CONCLUSIONES_ESTRATEGIAS_FINALES.md` – insights y recomendaciones.

## Contacto y licencia

- Email: contacto@pymeinside.com
- Web: [https://pymeinside.com](https://pymeinside.com)

Proyecto propietario – Supermercado NINO © 2025. Desarrollado por pymeinside.com.

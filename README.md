# Supermercado NINO – Analytics Dashboard

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

Dashboard interactivo para analizar 3M+ transacciones de Supermercado NINO, con KPIs ejecutivos, Pareto, Market Basket y segmentación de tickets.

> 📖 **Nueva estructura:** Ver [`ESTRUCTURA_REPOSITORIO.md`](ESTRUCTURA_REPOSITORIO.md) para navegación completa del repositorio.

## Características clave

- **KPIs ejecutivos** con métricas globales y tendencias mensuales.
- **Pareto 80/20** para identificar productos críticos y oportunidades de margen.
- **Market Basket** con reglas Apriori y filtros dinámicos.
- **Segmentación de tickets** basada en clustering K-Means.
- **Simulador ML de ROI** para cuantificar combos, marca propia, cross-merchandising, upselling y fidelización con ML.
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

# Opción 1: Iniciar dashboard directamente
streamlit run dashboard_cientifico.py

# Opción 2: Usar script de inicio (Windows)
iniciar_dashboard.bat
```

### 🔄 Actualizar datos después de modificar el CSV central

Cuando actualices `data/raw/SERIE_COMPROBANTES_COMPLETOS.csv` (ej: cambios en medios de pago), ejecuta:

```bash
# Opción 1: Script Python automático (recomendado)
python actualizar_metricas.py

# Opción 2: Script batch Windows (doble clic)
actualizar_metricas.bat
```

Este script ejecutará automáticamente:
1. Pipeline de procesamiento de datos
2. Copia de archivos a app_dataset
3. Entrenamiento de modelos ML

Ver documentación completa en [`ACTUALIZACION_AUTOMATICA.md`](ACTUALIZACION_AUTOMATICA.md)

> Las versiones anteriores y archivos legacy se archivaron en `RESTO/` para referencia.

## Módulo ML ROI

El nuevo módulo de **Simulador ML de ROI** entrena seis modelos de machine learning para cuantificar el impacto financiero de las principales palancas comerciales:

- Combos focalizados (matching + uplift).
- Lanzamiento de marca propia en categorías Pareto A.
- Cross-merchandising guiado por reglas de asociación.
- Upselling en línea de caja.
- Programa de fidelización sin IDs de cliente (proxy por clúster).
- Predictor base de ticket para estimar el contrafactual.

Los resultados se guardan en `data/ml_results/` y se visualizan en la pestaña **“🤖 Simulador ML ROI”** del dashboard. Ejecutá `python scripts/train_ml_models.py` cada vez que refresques los Parquet para mantener las simulaciones al día.

## Estructura del proyecto

```
supermercado_nino/
├── dashboard_cientifico.py           # 🎯 Dashboard científico principal
├── actualizar_metricas.py            # 🔄 Script de actualización automática
├── actualizar_metricas.bat           # 🪟 Script Windows (doble clic)
├── iniciar_dashboard.bat             # 🚀 Iniciar dashboard (Windows)
├── ACTUALIZACION_AUTOMATICA.md       # 📘 Documentación de actualización
├── README.md                         # 📖 Documentación principal
├── requirements.txt                  # 📦 Dependencias Python
│
├── src/                              # 💻 Código fuente modular
│   ├── data_prep/                    #    - Limpieza y normalización
│   ├── features/                     #    - KPIs, clustering, market basket
│   ├── ml_models/                    #    - Modelos ML y simuladores ROI
│   └── utils/                        #    - Utilidades y helpers
│
├── scripts/                          # 🛠️ Scripts de procesamiento
│   ├── pipeline/                     #    - Pipeline ETL principal
│   │   └── main_pipeline.py          #      (scripts/pipeline/main_pipeline.py)
│   └── train_ml_models.py            #    - Entrenamiento de modelos ML
│
├── data/                             # 📊 Datos y resultados
│   ├── raw/                          #    - CSV originales (gitignored)
│   ├── processed/                    #    - Parquet procesados por pipeline
│   ├── predictivos/                  #    - Pronósticos semanales
│   ├── ml_results/                   #    - Resultados de simuladores ML
│   └── app_dataset/                  #    - Dataset que consume el dashboard
│
└── RESTO/                            # 🗃️ Archivos archivados
    ├── app/                          #    - Dashboard versión anterior
    ├── final/                        #    - Versión pre-reorganización
    ├── legacy/                       #    - Código y pipelines legacy
    ├── docs/                         #    - Documentación histórica
    └── archivos_misc/                #    - Scripts y archivos diversos
```

## Tecnologías

- **Streamlit + Plotly** para la capa de visualización.
- **Pandas, NumPy, Scikit-learn, MLxtend y XGBoost** para procesamiento analítico y simulaciones ML.
- **PyArrow** para empaquetar los datasets en Parquet (5,5 MB en vez de ~420 MB de CSV).
- **Scripts opcionales con Supabase** para quien desee escalar la base de datos en la nube.

## Metodología analítica

1. **Limpieza y enriquecimiento** de 3M+ comprobantes con datos de rentabilidad y feriados.
2. **Cálculo de KPIs** mensuales, por categoría, día de semana, tipo de día y medio de pago.
3. **Clasificación ABC** (Pareto 80/20) para identificar productos y categorías críticas.
4. **Reglas de asociación** (Apriori) para Market Basket y generación de combos recomendados.
5. **Clustering K-Means** para segmentar tickets por comportamiento de compra.
6. **Pronósticos simples e interpretables** usando Promedios Móviles + Tendencia (no ARIMA).
7. **Empaquetado a Parquet** + visualización interactiva en Streamlit con storytelling.

### ¿Por qué NO usamos ARIMA para pronósticos?

Este proyecto utiliza **Promedios Móviles con Tendencia** en lugar de modelos ARIMA porque:

- **Transparencia**: Es fácil explicar "promedio de últimas 8 semanas" vs. "ARIMA(1,1,2)"
- **Auditabilidad**: Los stakeholders pueden verificar los cálculos manualmente
- **Suficiencia**: Para series cortas (<2 años), ARIMA no ofrece ventajas significativas
- **Interpretabilidad**: Los gerentes entienden tendencias lineales mejor que parámetros técnicos

Ver documentación completa en `src/features/predictivos_ventas_simple.py`

## Roadmap

- [x] ETL fase 1 completo (Oct 2024 – Oct 2025).
- [x] Dashboard Streamlit v2 con UI moderna.
- [x] Paquete Parquet local para deploy sin Supabase.
- [ ] Sistema de alertas (stock y ventas).
- [ ] Modelos predictivos de demanda.
- [ ] Integración con ERP/POS en tiempo real.
- [ ] App mobile para gerencia.

## Documentación relacionada

- [`ACTUALIZACION_AUTOMATICA.md`](ACTUALIZACION_AUTOMATICA.md) - Guía completa de actualización automática de métricas
- [`RESTO/docs/`](RESTO/docs/) - Documentación histórica y técnica archivada
  - `PIPELINE_ESTRATEGIAS.md` - Blueprint del pipeline unificado
  - `VALIDACION_FINAL.txt` - Checklist de verificación de KPIs
  - `FASE1_OUTPUT.log` - Bitácora histórica de la fase 1
- [`RESTO/legacy/`](RESTO/legacy/) - Dashboards, scripts CSV y datasets archivados


## Contacto y licencia

- Email: contacto@pymeinside.com
- Web: [https://pymeinside.com](https://pymeinside.com)

Proyecto propietario – Supermercado NINO © 2025. Desarrollado por pymeinside.com.

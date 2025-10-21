# RESUMEN EJECUCIÓN MODELOS ML – 21/10/2025

## Datasets procesados

- Tickets enriquecidos (`data/processed/clusters_tickets.parquet`): **306,011**
- Líneas de detalle (`data/processed/detalle_lineas.parquet`): **2,944,659**
- Reglas de asociación (`data/processed/reglas.parquet`): **132**
- Pareto de categorías (`data/processed/pareto_categoria.parquet`): **48**

## Diagnóstico modelo base

- `TicketPredictor` R² monto: **0.9464**
- `TicketPredictor` R² margen: **0.9541**
- MAE monto: **AR$ 9,868**
- MAE margen: **AR$ 2,577**

## ROI estimado por estrategia (salidas ML)

| Estrategia                                   | Inversión (AR$) | Margen incremental mensual (AR$) | ROI anual (%) | Payback (meses) | Confianza |
|----------------------------------------------|----------------:|---------------------------------:|--------------:|----------------:|----------:|
| Combos Focalizados (Fernet+Coca)             |        150,000  |                 22,952,503       |      183,620% |            0.01 |      71%  |
| Programa Fidelización                        |        300,000  |                  7,633,335       |       30,533% |            0.04 |      75%  |
| Marca Propia en Categorías A                 |        500,000  |                  8,441,821       |       20,260% |            0.06 |      75%  |
| Cross-Merchandising (Layout Impulsor)        |         80,000  |                  1,011,252       |       15,169% |            0.08 |      75%  |
| Upselling en Caja                            |        120,000  |                    381,500       |        3,815% |            0.31 |      75%  |

> Los ROI se calculan en base al margen incremental anual modelado; payback expresado en meses.

## Artefactos generados

- `data/ml_results/strategy_roi_summary.parquet`
- `data/ml_results/strategy_roi_details.json`
- Nueva pestaña **“🤖 Simulador ML ROI”** en `dashboard_cientifico.py`
- Script de entrenamiento: `scripts/train_ml_models.py`
- Reorganización de documentación en `docs/`

## Pendientes de documentación visual

- Capturar pantallas de la pestaña **Simulador ML ROI** y anexarlas al repositorio (no disponibles en este entorno).

# TODO PENDIENTE – MODELOS ML ROI

## Optimización técnica

- Incorporar particiones de entrenamiento/validación para `TicketPredictor` y registrar métricas out-of-sample (actualmente solo in-sample).
- Ajustar supuestos de adopción y límites de uplift para `ComboSimulator`; los ROI > 100,000% sugieren necesidad de caps o escenarios conservadores.
- Calibrar la heurística de elasticidad en `MarcaPropiaEstimator` con datos históricos de precios si se vuelven disponibles.
- Añadir pruebas automatizadas para `src/ml_models/` (mocks con datasets reducidos) ahora que los archivos de test legacy se archivaron.

## Funcionalidad pendiente

- Permitir parámetros CLI en `scripts/train_ml_models.py` (por ejemplo, ruta de salida, adopción objetivo).
- Incorporar explicabilidad SHAP una vez instalado el paquete (actualmente sólo listado en `requirements.txt`).
- Exponer intervalos de confianza (p. ej., percentiles simulados) en `strategy_roi_details.json`.

## Documentación y storytelling

- Capturar y agregar capturas de pantalla de la pestaña **Simulador ML ROI** al repositorio.
- Documentar escenarios conservador/base/optimista en `README.md` para contextualizar los ROI extremos.

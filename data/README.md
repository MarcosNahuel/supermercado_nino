# Data Directory

## Estructura actual

```
data/
|- raw/          # CSV originales provistos por el POS (gitignored)
|- app_dataset/  # Parquet consumidos por dashboard_cientifico.py (versionados)
|- processed/    # Reservado para futuras salidas (vacío tras mover FASE1 a legacy/)
\- sample/       # Reservado (dataset demo archivado en legacy/)
```

### raw/
- `SERIE_COMPROBANTES_COMPLETOS.csv`: comprobantes y líneas de venta (oct 2024 - oct 2025).
- `RENTABILIDAD.csv`: rentabilidad objetivo por departamento.

### app_dataset/
Paquete generado por `pipeline_estrategias.py`. El dashboard científico utiliza estos archivos:

| Archivo | Contenido principal |
| ------- | ------------------- |
| `alcance_dataset.parquet` | tamaño del dataset (fechas, tickets, ítems, ventas) |
| `kpis_base.parquet` | KPIs globales (ticket medio, margen, rentabilidad) |
| `kpi_diario.parquet`, `kpi_semana.parquet`, `kpi_periodo.parquet`, `kpi_dia.parquet` | temporalidad diaria / semanal / mensual / día de semana |
| `pareto_cat_global.parquet`, `pareto_prod_global.parquet` | ranking ABC global |
| `reglas.parquet`, `combos_recomendados.parquet`, `adjacency_pairs.parquet` | market basket y adyacencias |
| `clusters_tickets.parquet`, `clusters_departamento.parquet` | segmentación de tickets y departamentos |
| `kpi_medio_pago.parquet` | mezcla de medios de pago y emisores |
| `rentabilidad_ticket.parquet` | margen estimado por ticket |

El paquete incluye otros archivos auxiliares (ej. `kpi_hora.parquet`, `clasificacion_productos.parquet`) que se mantienen para extender el dashboard en el futuro.

## Regenerar el paquete Parquet

1. Asegurarse de que los CSV estén en `data/raw/`.
2. Ejecutar:
   ```bash
   python pipeline_estrategias.py
   ```
3. Los Parquet se escribirán en `data/app_dataset/` y quedarán listos para `dashboard_cientifico.py`.

## Datos legacy

Las salidas masivas en CSV (fase FASE1) y la muestra demo ligera fueron trasladadas a `legacy/data/`:

- `legacy/data/processed/FASE1_OUTPUT/`
- `legacy/data/sample/FASE1_OUTPUT_SAMPLE/`

Si se necesita reconstruir esas carpetas, utilizar los scripts correspondientes en `legacy/pipelines/` y `legacy/scripts/`.

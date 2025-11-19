# Documentacion Analitica - Supermercado NINO

## Alcance
La nueva arquitectura modular reemplaza al pipeline monolitico y permite ejecutar de modo orquestado los pasos de ETL, generacion de KPIs, analitica avanzada y pronosticos sin almacenar informacion sensible de clientes. El archivo `main_pipeline.py` coordina los modulos ubicados en `src/`.

## Entradas
- `data/raw/SERIE_COMPROBANTES_COMPLETOS.csv`: ventas historicas linea por linea.
- `data/raw/RENTABILIDAD.csv`: margen porcentual por departamento.
- `data/raw/FERIADOS_2024_2025.csv`: calendario nacional utilizado para distinguir tipo de dia (habil, fin de semana, feriado).

## Salidas Clave
- ETL:
  - `data/processed/detalle_lineas.parquet`: tabla canonica de ventas con enriquecimiento temporal, margen estimado y clasificacion por tipo de dia.
  - `data/processed/tickets.parquet`: agregacion a nivel ticket (ventas, margen, unidades, medio de pago).
  - `data/processed/ventas_semanales_categoria.parquet`: ventas semanales por categoria para modelos de series de tiempo.
- KPIs:
  - `data/processed/kpi_dia.parquet`: ventas, margen, unidades, tickets, ticket promedio, UPT y margen porcentual por fecha y tipo de dia.
  - `data/processed/kpi_tipo_dia.parquet`: resumen consolidado por tipo de dia (HABIL, FDS, FERIADO).
  - `data/processed/kpi_categoria.parquet`: KPIs por categoria, mes y tipo de dia.
  - `data/processed/kpi_medio_pago.parquet`: comportamiento por medio de pago (venta, margen, ticket promedio).
- Analisis complementarios:
  - `data/processed/reglas.parquet`, `adjacency_pairs.parquet`, `combos_recomendados.parquet`: salidas del Market Basket.
  - `data/processed/pareto_categoria.parquet`, `pareto_producto.parquet`: clasificacion ABC por margen.
  - `data/processed/clusters_tickets.parquet`, `clusters_tickets_centroides.parquet`: resultados de KMeans sobre variables economicas del ticket.
- Pronosticos:
  - `data/predictivos/prediccion_ventas_semanal.parquet`: historico y proyeccion para 8 semanas por las 10 categorias con mayor volumen.
  - `data/predictivos/prediccion_ventas_semanal_modelos.parquet`: metadata de modelos (orden ARIMA, AIC, cantidad de observaciones).
- Validacion:
  - `validacion_informes.py` ejecuta controles de consistencia sobre los KPIs procesados.

## Metodologia
1. **ETL**  
   Normaliza texto, convierte unidades, incorpora rentabilidad y enriquece datos temporales calculando `es_fin_de_semana`, `es_feriado` y `tipo_dia` segun el calendario de feriados.
2. **KPIs Estandarizados**  
   Se calculan ticket promedio (`ventas_totales / tickets`), `upt` (`unidades_totales / tickets`) y `margen_pct` (`margen_total / ventas_totales`) para multiples dimensiones: fecha, tipo de dia, categoria y medio de pago.
3. **Market Basket**  
   Reduce dimensionalidad a productos de alto impacto y aplica Apriori (min support 0.5%, confianza 15%, lift >= 1). Produce reglas, pares adyacentes y combos sugeridos con precio objetivo y margen estimado.
4. **Clustering**  
   Estandariza ventas, margen, unidades y productos unicos por ticket; selecciona automaticamente el mejor `k` en el rango 3-6 segun silhouette, y expone centroides desescalados para interpretacion.
5. **Pareto de Margen**  
   Ordena contribucion de margen por categoria y producto, calcula participacion acumulada y etiqueta segmentos A/B/C.
6. **Pronosticos de Ventas**  
   Construye series semanales (frecuencia `W-MON`) para las 10 categorias principales. Se prueba una grilla de ordenes ARIMA `(p,d,q)` en `[0-2]x[0-1]x[0-2]` y se selecciona el modelo con menor AIC. Cada proyeccion incluye intervalo de confianza (80%) para 8 semanas futuras.

## Uso
1. Instalar dependencias (`pip install -r requirements.txt`).
2. Ejecutar pipeline: `python main_pipeline.py`.
3. Opcionalmente correr validaciones: `python validacion_informes.py`.

## Supuestos
- No se procesan datos de clientes ni identificadores personales.
- El calendario de feriados cubre al menos los anios presentes en las ventas.
- Los modelos ARIMA requieren >=12 observaciones semanales por categoria; categorias con menos datos se omiten del pronostico.
- Automatizaciones (alertas, scheduling) se abordaran en una fase posterior.

## Glosario
- **tipo_dia**: clasificacion del dia en HABIL, FDS (sabado/domingo) o FERIADO.
- **ticket_promedio**: ventas totales / cantidad de tickets en el agregado.
- **upt**: unidades promedio por ticket.
- **margen_pct**: margen total / ventas totales.
- **ventas_semana_lower / upper**: intervalos de confianza para el pronostico semanal.

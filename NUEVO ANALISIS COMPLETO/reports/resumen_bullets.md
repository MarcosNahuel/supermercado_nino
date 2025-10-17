# Informe base - puntos clave
- La crisis 2024-2025 obliga a elevar la rentabilidad del ticket en tienda fisica; competir con formatos express requiere surtido optimizado y experiencia consistente.
- KPIs prioritarios: ticket promedio, margen bruto, rotacion, ventas en promocion, merma, conversion a compradores y fidelidad.
- Estrategias recomendadas: promociones rentables (elasticidad segmentada), bundles basados en canastas frecuentes y control estricto de merma (<1%).
- Competidores (Carrefour Express, Vea, Atomo) ganan terreno con layouts eficientes, surtido acotado (<3k SKUs) y acuerdos financieros puntuales.
- Documentar decisiones en un cuaderno vivo y medir cada iniciativa con comparacion antes/despues.

# Hallazgos cuantitativos (2024-10-01 a 2025-10-10)
- Ventas totales ARS 7.01B con margen estimado ARS 1.85B (26.4%); 298k tickets y ticket promedio ARS 23.5k con desviacion 98k (tabla `tickets.csv`).
- Octubre 2025 lidera en ticket promedio (ARS 32.1k) y margen porcentual (26.6%), indicando estacionalidad a inicios de mes (tabla `kpi_ciclos_mensual.csv`).
- Tickets de fin de semana promedian ARS 25.2k vs. ARS 22.6k en dias habiles (+11%), confirmando ciclos de abastecimiento profundos (tabla `kpi_ciclos_semanal.csv`).
- Medios de pago: credito concentra 49.2% de ventas (ticket prom. ARS 34.3k), billeteras 19.7% (ARS 26.0k) y efectivo 31.1% (ARS 20.4k) segun `kpi_medios_pago.csv`.
- Pareto global: top 20 productos explican 13.8% del margen estimado; departamentos con mayor aporte son Almacen (ARS 406M), Lacteos (ARS 187M), Limpieza (ARS 171M) y Carniceria (ARS 159M) (`pareto_global.csv`).
- 16.8% de lineas presentan diferencia >0.05 entre importe y cantidad*precio (probables redondeos POS) y se detectaron 695k lineas duplicadas (reporte `data_quality.json`).

# Estrategias respaldadas por datos
1. **Priorizar facing en departamentos rentables**: reforzar Almacen, Lacteos y Limpieza en fines de semana; combinan >50% del margen estimado (Pareto global) y los tickets sabado-domingo crecen +11% (kpi_ciclos_semanal).
2. **Promos controladas por medio de pago**: billeteras promedian ARS 26k y credito 34k; alinear cashback selectivo en dias valle sin erosionar el margen >25% (kpi_medios_pago).
3. **Bundles ABC dinamicos**: baja concentracion (top 20 solo 13.8%) obliga a combos multidepartamento tomando Pareto mensual/semanal para capitalizar margen disperso (`pareto_mensual.csv`, `pareto_semana.csv`).
4. **Auditar reglas de POS**: documentar criterios de redondeo y duplicados para corregir 16.8% de diferencias y evitar ruido en KPIs de margen (data_quality.json).
5. **Planificar staffing y layout**: reforzar personal/cajas en fines de semana y primeros dias de mes, cuando ticket promedio y margen aumentan (kpi_ciclos_mensual + kpi_ciclos_semanal).
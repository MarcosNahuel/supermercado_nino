# Reporte QA - Supermercado NINO Dashboard - 2026-03-07

## Resumen Ejecutivo
- **Total secciones testeadas:** 10 (Resumen Ejecutivo, Análisis Temporal, Horarios, Pareto & Mix, Market Basket & Combos, Tribu Premium, Segmentación, Medios de Pago, Estrategias Priorizadas, Márgenes-Costos, Forecasting, Informe Ejecutivo)
- **Issues críticos:** 1
- **Issues medios:** 2
- **Issues menores:** 3
- **Estado general:** ⚠️ Funcional con issues puntuales

## Issues Técnicos

| # | Sección | Issue | Severidad | Screenshot |
|---|---------|-------|-----------|------------|
| 1 | Forecasting | `TypeError: deprecate_kwarg() missing 1 required positional argument: 'new_arg_name'` en `statsmodels.tsa.holtwinters` (línea 4797). Traceback completo visible al usuario. | **CRÍTICA** | `09_forecasting_ERROR.png` |
| 2 | Resumen Ejecutivo | Período truncado: muestra "01/10/24 ..." en lugar del rango completo | Media | `01_resumen_ejecutivo_top.png` |
| 3 | Resumen Ejecutivo | Label "CÓDIGOS DE PRODUCTO ..." truncado | Menor | `01_resumen_ejecutivo_top.png` |
| 4 | Horarios | Labels de KPIs truncados: "COMPROBANTES (...", "MEDIA DEMORA (...", "MEDIANA DEMORA..." | Menor | `02_horarios_kpis.png` |
| 5 | Márgenes-Costos | Columna "Margen Tot..." truncada en tabla de productos extremos | Menor | `08_margenes_costos.png` |

## Issues de Datos

| # | Sección | Problema | Impacto |
|---|---------|----------|---------|
| 1 | Informe Ejecutivo | Texto **hardcodeado** con datos estáticos (Efectivo 31.3%) vs Medios de Pago dinámico (43.9%). Los porcentajes no coinciden entre secciones. | **Media** - Confunde al usuario con datos contradictorios |
| 2 | Informe Ejecutivo | "Lunes concentra el 0.7% del total de ventas semanales" - dato sospechoso, debería ser ~14% si se refiere a participación del día | Baja - posible error de redacción hardcodeada |
| 3 | Informe Ejecutivo | Rentabilidad "27.8%" vs KPI dinámico "28.23%" - inconsistencia menor por texto estático | Baja |

## Issues de Producto

| Área | Issue | Recomendación |
|------|-------|---------------|
| Código muerto | `src/queue_analysis.py` y `src/queue_visualizations.py` no se importan en el dashboard. Son código muerto de una implementación anterior. | Eliminar o marcar como deprecated |

## Validación de Datos (Científico de Datos)

### Horarios - CORRECTO
- **Lógica de agregación:** Usa `mean()` correctamente para promediar tickets por día (no SUM). Verificado en líneas 789-800.
- **Demora entre tickets:** Calculada per punto-de-venta, intra-día, con cap 30 min. Metodología sólida.
- **Media (2.88 min) vs Mediana (2.00 min):** Distribución sesgada a la derecha, esperable para tiempos de servicio.
- **P75 (3.00 min):** Coherente con la distribución.
- **N=317.340 intervalos sobre 395 días:** ~803 intervalos/día, razonable para un supermercado.
- **Gráficos:** Banda P25-P75, línea de media y mediana, receso 13:00-16:00 correctamente identificado.

### Medios de Pago - CORRECTO
- Efectivo + Digitales = 43.9% + 56.1% = 100% ✓
- Desglose digital coherente: Débito 23.5% + Crédito 19.7% + Billetera 12.9% = 56.1% ✓

### Resumen Ejecutivo - CORRECTO
- 345.130 tickets, $9.550,2M ventas, 10.772 productos
- Ticket promedio $27.671 = $9.550M / 345K ✓ (aprox.)
- Rentabilidad 28.23%, Items/ticket 7.94, Margen/ticket 28.1%

### Pareto & Mix - CORRECTO
- Top producto MOLIDA ESPECIAL $188M ventas, % acumulado creciente
- Segmentación BCG coherente (Estrellas, Generadores, Joyas, A Revisar)

## Screenshots
- `01_resumen_ejecutivo_top.png` - KPIs principales con período truncado
- `02_horarios_kpis.png` - Horarios KPIs y selector de período
- `03_horarios_grafico_tickets.png` - Distribución de tickets por bloque 10 min
- `04_horarios_grafico_demora.png` - Demora entre tickets con banda P25-P75
- `05_horarios_tabla_estadisticas.png` - Tabla de estadísticas y metodología
- `06_analisis_temporal.png` - UPT semanal con tendencia
- `07_pareto_mix.png` - Tabla Pareto productos
- `08_margenes_costos.png` - Matriz de productos y productos extremos
- `09_forecasting_ERROR.png` - Error TypeError en Forecasting

## Recomendaciones Prioritarias

1. **[CRÍTICO] Arreglar Forecasting:** Error de compatibilidad con `statsmodels`. Opciones:
   - Actualizar `statsmodels` a versión compatible
   - Envolver el import en try/except con fallback gracioso
   - Pinear versión de statsmodels en requirements.txt

2. **[MEDIO] Dinamizar Informe Ejecutivo:** Reemplazar texto hardcodeado con valores calculados dinámicamente para evitar inconsistencias.

3. **[MENOR] Truncamiento de labels:** Los `st.metric()` con labels largos se truncan. Usar labels más cortos o tooltips.

4. **[MENOR] Limpiar código muerto:** Eliminar `src/queue_analysis.py` y `src/queue_visualizations.py` que no se usan.

## Cumplimiento de Objetivos (según README)

- [x] KPIs ejecutivos con métricas globales
- [x] Pareto 80/20 para productos y categorías
- [x] Market Basket con reglas Apriori
- [x] Segmentación de tickets con K-Means
- [x] Simulador ML de ROI
- [x] Dataset en Parquet
- [x] UI moderna con Plotly
- [x] Análisis de Horarios con demora entre tickets
- [ ] Forecasting (roto por error de statsmodels)
- [x] Medios de Pago
- [x] Márgenes y Costos

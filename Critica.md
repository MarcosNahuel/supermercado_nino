# Informe crítico de validación (octubre 2025)

## 1. Alcance y metodología
- Datasets auditados: `data/app_dataset/*.parquet` (KPIs temporales, medios de pago, rentabilidad, Pareto, clusters, etc.) y `data/raw/comprobantes_ventas_horario.csv` para reconstruir la curva horario-semanal.
- Código revisado: `dashboard_cientifico.py` completo y `Estrategias_Analitica.md`.
- Herramientas: Python 3.10 (`python -c` sobre Parquet/CSV), cálculos reproducibles documentados en consola, verificación de integridad con `python -m py_compile`.
- Alcance temporal: 01-10-2024 al 10-10-2025 (serie original). El último mes incompleto sólo se excluye en la vista mensual para evitar distorsiones visuales.

## 2. Métricas recalculadas

| Métrica | Valor | Observaciones |
| --- | --- | --- |
| Tickets | 306.011 | Coincide con dashboard y README. |
| Ventas | $8.216.314.170,99 | Sumatoria de `monto_total_ticket`. |
| Margen | $2.285.459.564,25 | Sumatoria de `margen_ticket`. |
| Ticket promedio | $26.849,73 | Ventas / tickets. |
| Ítems promedio | 10,07 | Promedio de `items_ticket`. |
| Margen promedio / ticket | $7.468,55 | Media de `margen_ticket`. |
| Rentabilidad (%) | 27,82 % | `margen_total / ventas_total`. |
| Ventas por medio de pago | Crédito 49,6 % · Efectivo 31,3 % · Billetera virtual 19,2 % | El dashboard ya normaliza tipografías; conviene corregir el CSV original. |
| Cuartiles rentabilidad | Q1 26,2 % · Mediana 28,6 % · Q3 30,0 % | Se usan en el histograma diario. |
| Segmentos ticket | `<$5K` 17,6 % · `$5K-$15K` 31,6 % · `$15K-$30K` 24,0 % · `>$30K` 26,8 % | Copy actualizado en el dashboard. |
| Top horas (comprobantes) | Sábado 12 h (9.379), Sábado 11 h (9.153), Domingo 12 h (8.344) | Nueva vista horario-semanal. |

## 3. Estado del dashboard

**Avances verificados**
- Se normalizan los medios de pago y se muestran métricas diferenciadas para crédito/efectivo/billetera (`dashboard_cientifico.py:941-1007`).
- El histograma de rentabilidad marca franjas por cuartiles y usa los valores correctos en la narrativa (`dashboard_cientifico.py:782-908`).
- La narrativa diaria ahora utiliza el ticket promedio real por día (`dashboard_cientifico.py:421-483`).
- Se incorpora el heatmap “Horario semanal - Comprobantes por hora” con resumen de picos y top global (`dashboard_cientifico.py:540-583`).
- El copy de segmentos refleja los cortes reales `>$30K`, `$15K-$30K`, etc. (`dashboard_cientifico.py:872-928`).

**Pendientes relevantes**
- El panel ejecutivo (tab 7) sigue reportando 306.011 tickets y fecha máxima 10/10/2025. De mantenerse el recorte visual, conviene explicitarlo allí o recalcular KPIs consolidados (`dashboard_cientifico.py:1094-1198`).
- El CSV `comprobantes_ventas_horario.csv` mezcla coma/decimal y formato de fecha; se limpia en memoria, pero es recomendable normalizarlo en el pipeline para evitar errores futuros.
- Varias cadenas provenientes de los parquets continúan con caracteres mal codificados (Miércoles, Sábado, etc.); sería útil centralizar una limpieza UTF-8 en la etapa de ETL.
- El pipeline `pipeline_estrategias.py` no se volvió a ejecutar; sigue pendiente modularizarlo para que cada bloque (KPIs, market basket, horarios) pueda regenerarse sin “full reload” ni errores de memoria.

## 4. Estrategias vs. cobertura de datos (`Estrategias_Analitica.md`)

| Estrategia | Soporte actual | Observaciones |
| --- | --- | --- |
| #1 Surtido alto margen | **Sí** | Pareto y margen por categoría permiten actuar sobre 9 categorías A. |
| #2 Promos inteligentes | **Sí / parcial** | Reglas de asociación y animación temporal disponibles; falta logging para comparar días con/sin promo. |
| #3 Marca propia / segundas marcas | **Parcial** | No existe indicador “marca propia”; sería útil etiquetar productos. |
| #4 Layout & cross-merchandising | **Sí** | Reglas (lift >3) y segmentos de ticket permiten definir planogramas. |
| #5 Upselling en caja | **Parcial** | Segmentos listos, pero no hay datos sobre aceptación de sugerencias o scripts de caja. |
| #6 Fidelización / personalización | **No** | Sin identificador de cliente ni histograma de recurrencia. |
| #7 Reducción de merma | **No** | No se registran pérdidas, vencimientos ni inventario. |
| #8 Extender horarios | **Ahora con data** | Nuevo heatmap da base; faltaría cruzar con ventas marginales vs costo operativo. |
| #9 Experiencia / servicio | **No** | Sin NPS, tiempos de espera ni encuestas. |

## 5. Datos adicionales recomendados
- **Identificador de cliente** (DNI/teléfono) para medir recurrencia, valor de vida y efectividad de fidelización.
- **Detalle de promociones** (tipo, financiación, proveedor) y flag en línea para distinguir ventas con/sin promo.
- **Merma e inventario**: registro diario de desperdicio, roturas y stock disponible por categoría.
- **Costos operativos por hora** (personal, energía) para evaluar ROI de horarios extendidos usando el nuevo heatmap.
- **Información de competencia / mercado**: precios de referencia, share de promos, tráfico por zona, inflación alimenticia.
- **Encuestas de experiencia**: NPS, tiempos en fila, comentarios cualitativos por tienda/turno.

## 6. Próximas acciones de consultoría
1. **Refinar el pipeline ETL**: limpieza de catálogos (medios de pago, categorías), normalización de CSV horarios y modularización de `pipeline_estrategias.py` para ejecuciones parciales.
2. **Instrumentar nuevos datos**: definir procesos en caja para capturar ID de cliente y resultado de upselling; incorporar módulo de merma/inventario con frecuencia diaria.
3. **Diseñar pilotos operativos**: ejecutar planogramas “Asado del finde”, “Aperitivos” y “Milanesas + pan” y medir el uplift usando las reglas top (lift >3). Documentar resultados en el dashboard.
4. **Añadir analítica de recurrencia**: una vez disponible el ID de cliente, construir cohortes, LTV y KPIs de fidelización; revisar Estrategia #6 con datos propios.
5. **Benchmark y riesgos externos**: recopilar informes de mercado (inflación alimentos, share promos, movimientos de competidores) para enriquecer narrativas y fijar comparativos.
6. **Plan de reporting**: establecer calendario mensual de actualización, checklist de validación (sumas totales, cuartiles, heatmap) y backlog de mejoras destacadas por el dashboard.

---
**Nota**: todas las cifras anteriores pueden reproducirse con los comandos `python -c` ejecutados en `D:\OneDrive\GitHub\supermercado_nino definitivo claude`. Se recomienda versionar estos scripts para asegurar trazabilidad y repetibilidad.

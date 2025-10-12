# PROMPT MAESTRO · Supermercado NINO · KPI **Rentabilidad por Ticket**
**Fecha:** 2025-10-12

Este documento es un **brief descargable para Codex**. Pégalo tal cual en el chat/CLI de Codex para que **modifique y expanda** el pipeline de Fase 1, incorporando los KPIs faro: **Rentabilidad Promedio por Ticket** y **Desviación Estándar de la Rentabilidad por Ticket**, más utilidades para evaluar estrategias (before/after).

---

## 0) Contexto del cliente (referencia para el código)
- **Empresa:** Supermercado **NINO**, independiente, mediano. Ubicación: **Chacras de Coria, Luján de Cuyo, Mendoza** (Argentina).
- **Datos disponibles:** 1 año de tickets con líneas de venta (\*\*Fecha/Hora\*\*, \*\*TicketID\*\*, \*\*ProductoID/Descripción\*\*, \*\*Cantidad\*\*, \*\*PrecioUnitario\*\*, \*\*ImporteTotal\*\*, **CostoUnitario** opcional).
- **Objetivo de negocio:** maximizar **Rentabilidad Promedio por Ticket** y **reducir su dispersión** (Desv. Estándar). Estos serán los **KPI faro** para evaluar si las tácticas implementadas funcionan.

---

## 1) Entregable requerido
Modificar/expandir `NINO_FASE1_pipeline.py` para:
1. **Calcular costo y margen** a nivel línea y ticket (merge con catálogo de costos; imputaciones controladas).
2. **Crear nuevos KPIs**:  
   - `RentabilidadTicket = Σ(ImporteTotal - CostoTotalLinea)` por TicketID.  
   - `RentabilidadPctTicket = RentabilidadTicket / MontoTotalTicket`.  
   - **Promedio** y **Desviación Estándar** de `RentabilidadTicket` por día/semana/mes/segmentos.
3. **Evaluar estrategias** con un módulo *before/after* (delta y significancia) para ver impacto en los KPIs faro.
4. **Exportar** datasets listos para Power BI y actualizar el **Resumen Ejecutivo**.

---

## 2) Cambios funcionales (paso a paso)

### A) Costos y margen (línea y ticket)
- **Nuevos CLI args:**
  - `--cost_file` (opcional): CSV con costos. Mínimo: `ProductoID`, `CostoUnitario`, opcional `FechaVigencia`.
  - `--cost_imputation` (*default*=`category`; opciones: `category|global|none`).  
  - `--margin_pct_fallback` (*default*=0.18) para imputar costo si no hay costo unitario (solo si `--cost_imputation != none`).
- **Reglas de costo (prioridad):**
  1. Si la línea trae `CostoUnitario`, **usar**.
  2. Si hay `--cost_file`: parsear `FechaVigencia`; por `ProductoID` hacer **merge asof** por `Fecha` (vigencia más reciente ≤ fecha de venta). Si no hay vigencia, usar último costo por producto.
  3. Si sigue faltando costo:
     - `category`: imputar con **ratio** de la categoría (mediana de `CostoUnitario/PrecioUnitario` en líneas con costo válido).  
     - `global`: ratio global.  
     - `none`: dejar nulo y **excluir** esas líneas de las métricas de margen (loggear conteos).
- **Cálculos en línea:**  
  - `CostoTotalLinea = CostoUnitario * Cantidad`  
  - `MargenLinea = ImporteTotal - CostoTotalLinea`  
  - `CostoImputado` = 1/0
- **Cálculos en ticket (en `build_ticket_fact`)**:  
  - `CostoTotalTicket = Σ CostoTotalLinea`  
  - `RentabilidadTicket = Σ MargenLinea`  
  - `RentabilidadPctTicket = RentabilidadTicket / MontoTotalTicket`  
  - `PctLineasConCosto`, `PctLineasConCostoImputado` (calidad de KPI por ticket)

### B) Nuevos KPIs y salidas
Generar y exportar:
- **Diario** → `13_kpi_rentabilidad_diaria.csv`  
  Campos: `Fecha`, `Tickets`, `RentabilidadPromedioTicket`, `DesvEstandarRentabilidadTicket`, `RentabilidadPctPromedio`, `P25_RentabTicket`, `P50_RentabTicket`, `P75_RentabTicket`, `PctTicketsConCosto`, `PctTicketsConCostoImputado`.
- **Semanal** → `14_kpi_rentabilidad_semanal.csv` (agrupar por `SemanaISO`) con los mismos campos.
- **Mensual** → `15_kpi_rentabilidad_mensual.csv` (agrupar por `Mes`) con los mismos campos.
- **Por cluster** → `52_clusters_profit_summary.csv` con: `Cluster`, `Tickets`, `RentabilidadPromedioTicket`, `DesvEstandarRentabilidadTicket`, `MontoProm`, `ItemsProm`, `SKUsProm`, `HoraProm`, `PctCostoImputado`.
- **Por categoría** → **ampliar** `21_ventas_por_categoria.csv` agregando `Costo`, `Margen`, `MargenPct`.

### C) Evaluación de estrategias (**before/after**)
Implementar función:
```python
evaluate_strategy_periods(df_tickets, before_start, before_end, after_start, after_end, control_matching='dow')
```
- Filtra tickets por rangos **antes** y **después**.
- Si `control_matching='dow'`, construir control emparejando **mismos días de la semana** del período “después” contra el “antes” (mitigar estacionalidad simple).
- Devolver métricas y exportar a `95_eval_estrategias.csv` con filas tipo:  
  `scope` (global / cluster / categoría), `metric`, `before`, `after`, `delta_abs`, `delta_pct`, `p_value`, `n_before`, `n_after`.
- **Significancia**: usar t-test de Welch (`scipy`) si disponible; si no, bootstrap de la media (5k).  
- **Guardrails**: si `PctTicketsConCosto < 0.70` en un período, imprimir `[WARN]` y marcar resultado **“interpretar con cautela”**.

### D) Resumen Ejecutivo (`90_resumen_ejecutivo.md`)
Agregar sección **KPI Faro — Rentabilidad por Ticket** con:
- Últimos 30 días: `RentabilidadPromedioTicket`, `DesvEstandarRentabilidadTicket`, `RentabilidadPctPromedio`.
- Top 3 **categorías por Margen** y su contribución.
- Resultado de `evaluate_strategy_periods` si hubo fechas CLI (`delta` y `p-valor`).
- Nota de **calidad**: % de tickets con costo vs imputado.

### E) Calidad de datos y diccionario
- Logs `[INFO]`:  
  - Cobertura de costo: `% líneas con costo real`, `% imputadas`, `% sin costo (excluidas)`; también por **categoría**.
- **Diccionario** (`00_data_dictionary.csv`): documentar nuevas columnas de costo/margen.
- Si `--cost_imputation != none`: exportar `23_cost_imputation_ratios.csv` con ratio por categoría y global.

---

## 3) Requisitos no funcionales
- Mantener **estilo actual**: funciones modulares, robustez regional (coma/punto), mensajes `[INFO]/[WARN]`.
- Compatibilidad: **no romper** nombres de archivos existentes de Fase 1.
- Si faltan librerías opcionales (`mlxtend`, `sklearn`, `pyarrow`, `scipy`): **continuar** y saltar sección con `[WARN]`.

---

## 4) CLI esperado (ejemplos)
```bash
python NINO_FASE1_pipeline.py   --input_dir "data/raw_ventas"   --output_dir "data/processed/FASE1_OUTPUT"   --min_support 0.005 --min_confidence 0.25   --k_min 3 --k_max 6   --cost_file "data/master_costos.csv"   --cost_imputation category   --margin_pct_fallback 0.18   --before_start 2025-07-01 --before_end 2025-08-15   --after_start 2025-08-16 --after_end 2025-09-30   --preview
```

---

## 5) Criterios de aceptación (no negociables)
- KPIs **Rentabilidad Promedio por Ticket** y **Desviación Estándar** correctos y exportados por **día/semana/mes** y **por cluster**.
- Merge de costos por vigencia operativo; **imputación** configurable y auditada.
- `evaluate_strategy_periods` produce deltas y **p-value** (o bootstrap) y exporta `95_eval_estrategias.csv`.
- **Resumen Ejecutivo** actualizado con KPIs faro y evaluación si se pasaron fechas.
- Pipeline corre **con y sin** `--cost_file`; si no hay costos, deja trazabilidad clara y permite imputación.

---

## 6) QA checklist (rápida)
- La suma de `RentabilidadTicket` = Σ `MargenLinea` del período.
- `DesvEstandarRentabilidadTicket` con `ddof=1`.
- Si **>70%** de líneas con costo real: ✅; si no, `[WARN]` y ratio/imputación documentada.
- CSV creados: `13_`, `14_`, `15_`, `21_` extendido, `52_`, `95_`, y `23_` (si aplica).  
- Parquet `tickets.parquet` incluye: `CostoTotalTicket`, `RentabilidadTicket`, `RentabilidadPctTicket`, `PctLineasConCosto`, `PctLineasConCostoImputado`.

---

## 7) Notas para Codex
- Usar **espñol** en comentarios y nombres de columnas.
- Mantener compatibilidad con la Fase 1 ya implementada.
- Si falta alguna dependencia, **no fallar**: registrar `[WARN]` y continuar.
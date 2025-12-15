# Plan de Nuevos Análisis y Escenarios para Dashboard Científico

## Resumen Ejecutivo

Basado en el análisis del dashboard actual (`dashboard_cientifico.py`), las investigaciones "Estrategias Supermercado Nino" y "Plan de Innovación", y los datasets disponibles, se identifican **10 nuevos escenarios de análisis** factibles con los datos existentes.

---

## Estado Actual del Dashboard

### Tabs Existentes:
1. **Análisis Temporal** - Evolución tickets, UPT, ticket promedio, margen %, heatmap horario
2. **Pareto & Mix** - Análisis 80/20 por categoría y productos
3. **Market Basket** - Reglas de asociación y combos sugeridos
4. **Segmentación** - Distribución rentabilidad y segmentos por cuartil
5. **Medios de Pago** - Análisis por método de pago
6. **Estrategias Priorizadas** - Plan de acción 90 días
7. **Márgenes-Costos** - Matriz productos volumen vs rentabilidad
8. **Informe Ejecutivo** - Resumen narrativo

### Datasets Disponibles:
- `rentabilidad_ticket.parquet` - 306,011 tickets con fecha, monto, margen, items
- `kpi_categoria.parquet`, `kpi_dia.parquet`, `kpi_hora.parquet`
- `pareto_prod_global.parquet`, `pareto_cat_global.parquet`
- `reglas.parquet`, `combos_recomendados.parquet`
- `clusters_tickets.parquet`, `clusters_departamento.parquet`
- `prediccion_ventas_semanal.parquet` (datos de forecast existentes)
- `FERIADOS_2024_2025.csv` - Calendario de feriados

---

## NUEVOS ANÁLISIS PROPUESTOS

### 1. Tab "Tribu Premium" (Prioridad: ALTA)

**Fundamento de la Investigación:**
> "El 15.6% de las transacciones (Tribu Premium) genera el 51.7% del margen. Esta dependencia requiere blindar estos clientes."

**Análisis Propuesto:**
- Filtrar tickets con monto > percentil 85 (aproximadamente >$45,000)
- Métricas específicas: ticket promedio, UPT, categorías preferidas
- Distribución por día de la semana y hora
- Top 10 productos más comprados por este segmento
- Comparativa vs "Tribu Diaria" (tickets <$10,000)

**Datos Necesarios:** `rentabilidad_ticket.parquet` (ya tiene todo)

**Insight Accionable:** Identificar qué productos/horarios defender para no perder clientes de alto valor

---

### 2. Tab "Forecasting Inteligente" (Prioridad: ALTA)

**Fundamento de la Investigación:**
> "Modelos predictivos de demanda para compras automatizadas y sugerencia de pedidos a proveedores"

**Análisis Propuesto:**
- Visualizar predicciones de `prediccion_ventas_semanal.parquet`
- Gráfico: histórico vs predicción próximas 4 semanas
- Métricas de error del modelo (MAPE, RMSE)
- Predicción por categoría top (si el modelo lo permite)
- Alertas: "semanas de alta demanda esperada"

**Datos Necesarios:** `prediccion_ventas_semanal.parquet`, `prediccion_ventas_semanal_modelos.parquet`

**Insight Accionable:** Planificación de abastecimiento y personal según demanda esperada

---

### 3. Tab "Estacionalidad y Eventos" (Prioridad: ALTA)

**Fundamento de la Investigación:**
> "Incorporar datos externos: si se pronostica ola de calor, aumentar stock de bebidas y helados; si se acerca feriado largo, aprovisionar más carnes para asados"

**Análisis Propuesto:**
- **Efecto Quincena:** Comparar ventas días 1-5 y 15-20 vs resto del mes
- **Efecto Feriados:** Cruzar con `FERIADOS_2024_2025.csv`
  - Ventas previo a feriado vs día normal
  - Categorías que más crecen en feriados
- **Efecto Fin de Semana:** Ya existe parcialmente, expandir análisis
- **Estacionalidad Mensual:** Detectar picos (vendimia, fiestas patrias, etc.)

**Datos Necesarios:** `rentabilidad_ticket.parquet` + `FERIADOS_2024_2025.csv`

**Insight Accionable:** Calendario de promociones alineado a eventos de alta demanda

---

### 4. Tab "Simulador de Combos" (Prioridad: MEDIA-ALTA)

**Fundamento de la Investigación:**
> "Crear 'Kit Milanesa Perfecta', 'Combo Desayuno Escolar'. Empaquetar productos complementarios eleva hasta +22% las ventas cruzadas"

**Análisis Propuesto:**
- Input: Seleccionar 2-4 productos del catálogo
- Output:
  - Lift promedio de la combinación (de `reglas.parquet`)
  - Frecuencia histórica de compra conjunta
  - Estimación de tickets afectados si se promociona
  - Simulador: "Si aplicamos 10% de descuento al combo, ¿cuántas ventas adicionales?"
- Sugerencias automáticas de combos rentables (top 5 por lift × margen)

**Datos Necesarios:** `reglas.parquet`, `combos_recomendados.parquet`, `pareto_prod_global.parquet`

**Insight Accionable:** Crear combos con base estadística, no por intuición

---

### 5. Tab "Análisis de Canasta Típica" (Prioridad: MEDIA)

**Fundamento de la Investigación:**
> "Análisis de canasta para entender qué porcentaje lleva al menos un snack impulsivo"

**Análisis Propuesto:**
- **Composición promedio del ticket:**
  - % tickets con al menos 1 producto de Carnicería
  - % tickets con al menos 1 producto de Panadería
  - % tickets con "impulso" (snacks, golosinas, bebidas frías)
- **Ticket "completo" vs "incompleto":**
  - Definir canasta ideal (ej: proteína + carbohidrato + bebida)
  - Qué % de tickets cumple el perfil
- **Oportunidades de cross-sell:**
  - "70% de tickets con carne NO incluyen carbón/vino"

**Datos Necesarios:** Requiere cruzar `rentabilidad_ticket` con detalle de líneas (si existe `detalle_lineas.parquet`)

**Insight Accionable:** Identificar productos faltantes en canastas típicas para sugerir en caja

---

### 6. Tab "Elasticidad y Simulador de Precios" (Prioridad: MEDIA)

**Fundamento de la Investigación:**
> "Precios dinámicos: ajustar precios según stock, horarios, demanda. Identificar productos con pricing subóptimo"

**Análisis Propuesto:**
- **Matriz Precio vs Volumen por Categoría:**
  - Eje X: precio promedio de la categoría
  - Eje Y: unidades vendidas
  - Identificar categorías "elásticas" (sensibles a precio)
- **Simulador What-If:**
  - Input: Subir/bajar precio 5-10-15% en categoría X
  - Output: Estimación de impacto en ventas y margen
  - Basado en correlación histórica precio-volumen
- **Productos con margen subóptimo:**
  - Alto volumen + bajo margen → revisar precio
  - Bajo volumen + alto margen → revisar visibilidad

**Datos Necesarios:** `pareto_prod_global.parquet`, `kpi_categoria.parquet`

**Insight Accionable:** Identificar dónde hay espacio para subir precios sin perder volumen

---

### 7. Tab "Benchmarking vs Industria" (Prioridad: MEDIA)

**Fundamento de la Investigación:**
> "NINO está por encima del promedio mendocino ($10,800 según INDEC)"

**Análisis Propuesto:**
- **Comparativa visual KPIs NINO vs Benchmark:**
  - Ticket promedio: NINO ($26,850) vs Industria ($10,800)
  - Margen bruto: NINO (27.8%) vs Típico supermercados (22-25%)
  - UPT: NINO (10.1) vs Industria (7-8)
- **Posicionamiento en escala:**
  - Gráfico tipo "termómetro" o gauge
- **Oportunidades de mejora:**
  - Si NINO está debajo en algún KPI, mostrar brecha

**Datos Necesarios:** `kpis_base.parquet` + benchmarks externos (hardcodeados de la investigación)

**Insight Accionable:** Comunicar fortalezas y áreas de mejora vs competencia

---

### 8. Tab "Alertas y Oportunidades" (Prioridad: MEDIA-BAJA)

**Fundamento de la Investigación:**
> "Alertas automáticas de quiebre de stock, merma excesiva, caída de ticket promedio"

**Análisis Propuesto:**
- **Sistema de Alertas Visuales:**
  - 🔴 Productos con caída >20% en ventas vs mes anterior
  - 🟡 Categorías con margen por debajo del promedio
  - 🟢 Productos "estrella" con tendencia positiva
- **Detector de Anomalías:**
  - Días con ventas inusualmente bajas/altas
  - Productos con cambio brusco de comportamiento
- **Oportunidades Identificadas:**
  - "Joyas ocultas": alto margen, bajo volumen → potencial de promoción
  - "Destructores de valor": bajo margen, bajo volumen → evaluar descatalogar

**Datos Necesarios:** `rentabilidad_ticket.parquet`, `pareto_prod_global.parquet`

**Insight Accionable:** Panel de control con indicadores semáforo para toma de decisiones rápida

---

### 9. Tab "Análisis por Clusters de Tickets" (Prioridad: BAJA)

**Fundamento de la Investigación:**
> "Segmentación conductual: 4 tribus con aportes radicalmente distintos"

**Análisis Propuesto:**
- Ya existe `clusters_tickets.parquet` - visualizar mejor
- **Perfil de cada cluster:**
  - Ticket promedio, UPT, margen %
  - Categorías dominantes
  - Horario típico de compra
- **Flujo entre clusters:**
  - ¿Los clientes "Diarios" pueden convertirse en "Premium"?
  - Qué diferencia a cada segmento
- **Recomendaciones por cluster:**
  - Diario → Combo de conveniencia
  - Reposición → Pack despensa
  - Premium → Fidelización, servicio personalizado

**Datos Necesarios:** `clusters_tickets.parquet`, `clusters_tickets_centroides.parquet`

**Insight Accionable:** Estrategias diferenciadas por tipo de cliente

---

### 10. Tab "ROI de Estrategias" (Prioridad: BAJA)

**Fundamento de la Investigación:**
> "Medir efectividad de promociones: calcular uplift de cada promo vs período similar sin promo"

**Análisis Propuesto:**
- Ya existe `strategy_roi_summary.parquet` en `data/ml_results/`
- **Visualizar resultados de estrategias:**
  - ROI estimado por iniciativa
  - Ranking de estrategias por impacto
- **Calculadora interactiva:**
  - Input: Inversión en estrategia X
  - Output: Retorno esperado basado en modelo

**Datos Necesarios:** `strategy_roi_summary.parquet`

**Insight Accionable:** Priorizar inversión en estrategias con mayor ROI demostrado

---

## MEJORAS A TABS EXISTENTES

### Tab "Market Basket" - Mejoras
- Agregar filtro por día de la semana (combos de fin de semana vs semana)
- Mostrar "Combo del Asado" específico (productos típicos para asado)
- Calculadora de impacto: "Si promocionamos este combo, potencial de $ adicional"

### Tab "Segmentación" - Mejoras
- Implementar la nomenclatura "Tribu" de la investigación
- Agregar % de aporte al margen por segmento
- Gráfico de flujo: distribución de tickets por tribu

### Tab "Estrategias" - Mejoras
- Agregar campo de seguimiento: "¿Se implementó? ¿Resultado?"
- Calculadora de ROI por estrategia
- Timeline de implementación interactivo

### Tab "Márgenes-Costos" - Mejoras
- Simulador de escenarios: "¿Qué pasa si reduzco costo logístico 2%?"
- Análisis de punto de equilibrio por categoría
- Comparativa margen bruto vs margen neto por producto

---

## PRIORIZACIÓN RECOMENDADA

| Prioridad | Nuevo Tab/Mejora | Impacto | Esfuerzo | Datos Listos |
|-----------|------------------|---------|----------|--------------|
| 1 | Tribu Premium | ALTO | BAJO | ✅ |
| 2 | Forecasting | ALTO | MEDIO | ✅ |
| 3 | Estacionalidad/Eventos | ALTO | MEDIO | ✅ |
| 4 | Simulador Combos | MEDIO-ALTO | MEDIO | ✅ |
| 5 | Benchmarking | MEDIO | BAJO | ✅ |
| 6 | Mejora Tab Segmentación (Tribus) | MEDIO | BAJO | ✅ |
| 7 | Elasticidad Precios | MEDIO | ALTO | ⚠️ Parcial |
| 8 | Canasta Típica | MEDIO | MEDIO | ⚠️ Requiere detalle líneas |
| 9 | Alertas y Oportunidades | MEDIO-BAJO | MEDIO | ✅ |
| 10 | Clusters Tickets | BAJO | BAJO | ✅ |
| 11 | ROI Estrategias | BAJO | BAJO | ✅ |

---

## RESUMEN DE DATASETS REQUERIDOS

### Ya Disponibles (Listos para usar):
- ✅ `rentabilidad_ticket.parquet` - Base para casi todos los análisis
- ✅ `prediccion_ventas_semanal.parquet` - Para forecasting
- ✅ `FERIADOS_2024_2025.csv` - Para estacionalidad
- ✅ `reglas.parquet`, `combos_recomendados.parquet` - Para simulador combos
- ✅ `clusters_tickets.parquet` - Para análisis de clusters
- ✅ `strategy_roi_summary.parquet` - Para ROI

### Parcialmente Disponibles:
- ⚠️ `detalle_lineas.parquet` - Existe pero no confirmado estructura para canasta típica
- ⚠️ Datos de precios históricos - Para elasticidad

### No Disponibles (Mencionados en investigación pero no implementables):
- ❌ ID de cliente único - No permite análisis RFM/CLV
- ❌ Datos de inventario/stock - No permite alertas de quiebre
- ❌ Datos de merma - No permite "Hora Nino"
- ❌ Costos reales por producto - Solo aproximaciones

---

## PRÓXIMOS PASOS SUGERIDOS

1. **Fase 1 (Semana 1-2):** Implementar Tab "Tribu Premium" + mejorar Segmentación con nomenclatura Tribus
2. **Fase 2 (Semana 3-4):** Implementar Tab "Forecasting" + Tab "Estacionalidad/Eventos"
3. **Fase 3 (Semana 5-6):** Implementar "Simulador de Combos" + mejoras a Market Basket
4. **Fase 4 (Semana 7-8):** Implementar "Benchmarking" + "Alertas y Oportunidades"

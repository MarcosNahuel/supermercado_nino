# Pipeline de Insights para Respaldar Estrategias — Supermercado NINO (Guía para implementación)

_Corte del alcance del dataset (auto en portada del dashboard): Periodo [min_fecha] a [max_fecha] · Tickets [n] · Ítems [n] · Ventas $[total]._

Este documento guía define el nuevo pipeline analítico para respaldar, con datos, las estrategias priorizadas. Está pensado para que un agente de codificación implemente los módulos y salidas indicadas, y para integrarse al dashboard Streamlit existente.

- Estado: borrador colaborativo v0.1 (co‑diseño)
- Fuente estrategia: Estrategias_Analitica.md
- Repositorio base v2: `pipeline_estrategias.py` + `dashboard_cientifico.py` + `data/app_dataset/*` (componentes legacy en `legacy/`)


## 1) Alcance del Dataset (PRIORIDAD: mostrar estado actual)

- Orígenes de datos
  - `data/raw/SERIE_COMPROBANTES_COMPLETOS.csv` (ventas POS, 2.99M+ líneas)
  - `data/raw/RENTABILIDAD.csv` (rentabilidad por departamento/categoría)
- Periodo analizado
  - Declarado: Octubre 2024 – Octubre 2025 (13 meses) según `data/raw/README.md`
  - Preciso: calcular y registrar `min(fecha)` y `max(fecha)` a partir del CSV maestro
- Dimensión del dataset (calcular y mostrar en el dashboard)
  - Tickets: `n_tickets = nunique(ticket_id)`
  - Ítems vendidos: `n_items = rows(items_ventas)`
  - Facturación total: `sum(importe_total)`
- Estructura mínima esperada (columnas)
  - Ítems POS: Fecha, Comprobante (`ticket_id`), Código/SKU (`producto_id`), Marca, Departamento (`categoria`), Nombre (`descripcion`), Cantidad, Importe (`importe_total`), Unitario (`precio_unitario`), TIPO FACTURA
  - Rentabilidad: Departamento, % Rentabilidad, Clasificación
- Enlaces clave
  - Join de cada línea de venta con `RENTABILIDAD.csv` por `Departamento`→`Departamento` (normalizado a mayúsculas y sin acentos)
  - Margen estimado por línea: `margen_linea = importe_total * rentabilidad_pct_departamento`
  - Margen por ticket: suma de `margen_linea` agrupado por `ticket_id`
  - Fallback de margen: usar el promedio global de `RENTABILIDAD.csv` para departamentos no mapeados (si no disponible, fallback 18%)


## 2) KPIs Base (PRIORIDAD: estado actual)

Calcular y exponer en tarjetas del dashboard:
- `rentabilidad_global = sum(margen) / sum(ventas)`
- `ticket_promedio = sum(ventas) / count(tickets)`
- `items_promedio_ticket = sum(cantidad) / count(tickets)`
- `rentabilidad_promedio_ticket = mean(margen_ticket / ventas_ticket)`
- `rentabilidad_diaria` y `rentabilidad_mensual` (por fecha y por periodo YYYY‑MM)

Datasets Parquet sugeridos:
- `kpi_diario.parquet` (fecha, ventas, margen, tickets, rentabilidad_pct)
- `kpi_hora.parquet` (fecha, hora, ventas, margen, tickets, rentabilidad_pct)
- `kpi_periodo.parquet` (YYYY‑MM, ventas, margen, tickets, rentabilidad_pct)
- `rentabilidad_ticket.parquet` (ticket_id, fecha, periodo, items_ticket, monto_total, margen_ticket, rentabilidad_pct_ticket)


## 3) Enriquecimiento y Normalización (soporte a todos los módulos)

- Normalizar texto (sin acentos, strip, upper), tipos y formatos (fechas, decimales)
- Derivar campos temporales: `anio`, `mes`, `periodo` (YYYY‑MM), `semana_iso` (YYYY‑WW), `dia_semana` (Mon..Sun), `es_fin_semana` (Sat/Sun)
- Completar `items_ticket` por ticket; asegurar `ticket_id` único por comprobante
- Verificación de calidad: nulos, duplicados, mapeo de categorías sin rentabilidad, outliers simples

- Medios de pago (normalización específica)
  - Columna: `tipo_medio_pago` (fuente: "Tipo medio de pago"). Si está ausente o nula, imputar `EFECTIVO`.
  - Columna: `emisor_tarjeta` (fuente: "Emisor tarjeta"). Si está ausente o nula, imputar `DESCONOCIDO`.
  - Estandarizar valores a conjunto reducido: `EFECTIVO`, `TARJETA_DEBITO`, `TARJETA_CREDITO`, `OTROS`.
  - Mantener ambos campos en mayúsculas y sin acentos.


## 4) Análisis Temporal y Estacionalidad (diaria, semanal, mensual, anual)

Objetivo: entender ciclos para planificación de stock, personal y reposición.
- Diario: `kpi_diario.parquet` (fecha) y `kpi_hora.parquet` (fecha x hora)
- Semanal: `kpi_semana.parquet` (YYYY‑WW, ventas, margen, tickets, rentabilidad_pct)
- Mensual y anual: `kpi_periodo.parquet`, `kpi_anio.parquet`
- Weekday vs fin de semana: `kpi_dow_weekend.parquet` (dia_semana, es_fin_semana, ventas, margen, tickets)
- Gráficos (dashboard): líneas/áreas por periodo; barras por día de semana; heatmap día×hora (confirmado)

Extensión solicitada: estacionalidad de clusters de productos para reposición por época del mes y año.
- Ver Sección 7 (Clusters de productos por patrón temporal)


## 5) Pareto (Categorías y Productos) — Global y por Weekday/Weekend

- Pareto global de categorías y productos: `pareto_cat_global.parquet`, `pareto_prod_global.parquet`
- Pareto separado por `'es_fin_semana'`:
  - `pareto_cat_weekday.parquet`, `pareto_cat_weekend.parquet`
  - `pareto_prod_weekday.parquet`, `pareto_prod_weekend.parquet`
- Columnas típicas: id/descripcion, categoria, ventas, margen, pct_acumulado (ventas), ABC por ventas y ABC por margen
- Gráficos: curvas de Pareto 80/20 y tablas Top‑N con ventas, margen y ABC


## 6) Market Basket y Adyacencias en Góndola (aceptado)

Objetivo: respaldar combos y layout con datos y explicar “cómo llegamos”.
- Reglas Apriori: `reglas.parquet` (antecedents, consequents, support, confidence, lift)
- Adyacencias de góndola: `adjacency_pairs.parquet` (par producto, lift, soporte) y opcional tríos
- Combos recomendados: `combos_recomendados.parquet` con:
  - antecedent, consequent, soporte, confianza, lift
  - `precio_combo_sugerido` (suma precios − descuento), `margen_combo_estimado` (vía rentabilidad categoría como proxy)
  - `adopcion_objetivo_pct` (parámetro configurable), ticket objetivo
- Gráficos “cómo llegamos” (dashboard):
  - Scatter Confidence vs Support (burbuja = Lift)
  - Red de co‑compra (top pares por lift)
  - Barras de frecuencia de co‑ocurrencia top‑N
  - Panel de combos con precio/margen estimado y supuestos

Notas de negocio: mantener la distribución de góndolas en el tiempo para facilitar recuerdo del cliente habitual; usar adyacencias para guiar re‑ubicación estable.


## 7) Clustering

7.0 Baseline por departamento
- Asumimos “clusters = departamentos” como vista base operativa
- Salida: `clusters_departamento.parquet` (departamento, ventas, margen, tickets, ticket_promedio, items_promedio, rentabilidad_pct)
- Gráficos: barras comparativas por departamento (ventas, margen, rentabilidad)

7.1 Clusters de tickets (ticket‑items)
- Variables base: `monto_total_ticket`, `items_ticket`, % fin de semana (si aplica), transformaciones robustas
- Salida: `clusters_tickets.parquet` (cluster, cantidad_tickets, ticket_promedio, items_promedio, pct_tickets, etiqueta)
- Gráficos: barras por cluster, distribución ticket/items, participación fin de semana

7.2 Clusters de medios de pago vs ticket (solicitado)
 - Columnas fuente: `tipo_medio_pago` (missing→EFECTIVO) y `emisor_tarjeta` (missing→DESCONOCIDO)
 - Variables: ticket_promedio por medio de pago, dispersión (p50/p90), % fin de semana, participación en ventas/margen
 - Salida: `clusters_pago_tickets.parquet` (cluster, tipo_medio_pago, emisor_top, KPIs) y tabla de apoyo `kpi_medio_pago.parquet`
 - Gráficos: barras comparativas por medio de pago, treemap de participación, tabla de emisores si aplica

7.3 Clusters de productos por patrón temporal (para reposición por época)
- Universo: Top‑N SKUs por ventas (ej. N=200) para series semanales
- Features: vector de ventas semanales normalizado (z‑score o % del máximo)
- Modelo: K‑Means/HDBSCAN (según desempeño), selección de K por silueta/codo
- Salida: `clusters_productos_temporales.parquet` (producto_id, cluster_temporal, etiqueta)
- Gráficos: mini‑series por cluster y recomendaciones de reposición por mes/época

7.4 Clasificación de productos con IA (no supervisada)
- Features sugeridas: margen relativo (percentil), frecuencia semanal, CV de ventas, precio unitario, estacionalidad (amplitud), pertenencia a reglas de basket (grado)
- Modelo: K‑Means (baseline) y evaluación por silueta; alternativa HDBSCAN si hay formas no esféricas
- Salida: `clasificacion_productos.parquet` (producto_id, cluster_ai, etiqueta)
- Uso: guiar surtido, facing y pricing táctico por familia emergente


## 8) Rentabilidad por Ticket (KPI transversal)

- Cálculo a partir de la vinculación con `RENTABILIDAD.csv` (Sección 1)
- Salida principal: `rentabilidad_ticket.parquet` (ver Sección 2)
- Uso: KPI de rentabilidad global y por ticket; ranking de tickets alto margen; distribución y evolución
- Gráficos: violín/histograma de rentabilidad_ticket; línea mensual; tarjetas con media y desviación


## 9) Entregables (datasets Parquet y vistas de dashboard)

Parquet para `data/app_dataset/`:
- Base/temporal: `kpi_dia.parquet`, `kpi_semana.parquet`, `kpi_periodo.parquet`, `kpi_anio.parquet`, `kpi_dow_weekend.parquet`
- Diario/hora: `kpi_diario.parquet`, `kpi_hora.parquet`
- Rentabilidad: `rentabilidad_ticket.parquet`
- Pareto: `pareto_cat_global.parquet`, `pareto_cat_weekday.parquet`, `pareto_cat_weekend.parquet`, análogos para productos
- Basket/layout: `reglas.parquet` (ya existe), `adjacency_pairs.parquet`, `combos_recomendados.parquet`
- Clusters: `clusters_departamento.parquet`, `clusters_tickets.parquet`, `clusters_pago_tickets.parquet`, `clusters_productos_temporales.parquet`, `clasificacion_productos.parquet`
- Pago: `kpi_medio_pago.parquet` (tipo_medio_pago, emisores, KPIs)

Dashboard (dashboard_cientifico.py):
- Nueva portada “Estado del Dataset”: periodo exacto, n_tickets, n_items, facturación, KPIs base
- Estacionalidad: vistas semanal, mensual y anual con filtros weekday/weekend
- Pareto global y por weekday/weekend (categorías y productos)
- Market Basket: explicación “cómo llegamos” + adyacencias + combos sugeridos
- Segmentación: clusters de tickets y medios de pago; estacionalidad de clusters de productos


## 10) Configuración, parámetros y dudas a resolver

Parámetros recomendados (FASE1): `min_support`, `min_confidence`, `min_lift`, Top‑N adyacencias, N=200 SKUs para clustering temporal (ajustable), K de clusters por silueta.

Definiciones confirmadas:
- Medios de pago: columna "Tipo medio de pago" → `tipo_medio_pago` (missing→EFECTIVO). "Emisor tarjeta" → `emisor_tarjeta` (missing→DESCONOCIDO).
- Fin de semana: por defecto Sábado‑Domingo (si se requiere, se puede extender a viernes noche en versiones siguientes).
- Formato portada: fechas DD/MM/AAAA; moneda ARS con separador miles “.” y decimales “,”.


## 11) Aceptación (Definition of Done)

- El dashboard muestra en portada el estado actual: periodo exacto (min/max fecha), n_tickets, n_items, ventas, margen, ticket_promedio, items_promedio_ticket, rentabilidad_global y rentabilidad_promedio_ticket.
- Existen Parquet generados para temporalidad semanal/mensual/anual y weekday/weekend.
- Pareto global y segmentado (weekday/weekend) para categorías y productos, con ABC correcto.
- Market Basket con reglas filtrables, adyacencias y lista de combos con precio/margen estimado, y gráficos que explican el proceso.
- Segmentación: clusters de tickets listos, y clusters de medios de pago si la columna está disponible.
- Estacionalidad de clusters de productos temporal implementada para Top‑N SKUs con recomendaciones básicas de reposición.
- Vinculación con `RENTABILIDAD.csv` validada (sin categorías huérfanas) y márgenes consistentes en todos los módulos.


## 12) Plan de implementación sugerido (orden)

1) Estado actual + KPIs base + rentabilidad_ticket (Secciones 1, 2 y 8)
2) Temporalidad semanal/mensual/anual + weekday/weekend (Sección 4)
3) Pareto global y segmentado (Sección 5)
4) Market Basket + adyacencias + combos (Sección 6)
5) Clusters de tickets y (si aplica) medios de pago (Sección 7.1 y 7.2)
6) Clusters de productos por patrón temporal (Sección 7.3)
7) Ajustes finos del dashboard y documentación


## 13) Referencias de código y datos

- Pipeline actual: `FASE1_ANALISIS_COMPLETO.py`
- App dashboard: `app_streamlit_supabase.py`
- Builder Parquet: `scripts/build_app_dataset.py`
- Datos app: `data/app_dataset/*.parquet`
- Datos crudos: `data/raw/SERIE_COMPROBANTES_COMPLETOS.csv`, `data/raw/RENTABILIDAD.csv`
- Documento estratégico: `Estrategias_Analitica.md`


## 14) Escenarios (simulación aceptada)

- Escenario Mix y Margen
  - Controles: mover ±1–5 pp de share por categoría; margen objetivo por categoría
  - Salida: Δ ventas, Δ margen, Δ rentabilidad global y por ticket; mantener suma 100%

- Escenario Combos y Adyacencias
  - Controles: adopción objetivo 0.5–5.0% de tickets; descuento 5–15%; seleccionar combos top por lift
  - Salida: tickets con combo, Δ unidades, Δ ventas, Δ margen (vínculo RENTABILIDAD.csv)
  - Gráficos: red de co‑compra, scatter Support/Confidence/Lift, panel combos con supuestos

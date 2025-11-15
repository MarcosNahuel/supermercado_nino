# Guia de `dashboard_cientifico.py`

Este documento resume como esta construido el dashboard cientifico de Supermercado NINO y que requiere para ejecutarse mediante Streamlit.

## Objetivos del dashboard

- Contar la historia de rentabilidad del ticket y las nueve estrategias priorizadas.
- Exponer datos descriptivos, segmentaciones y reglas de asociacion en una sola aplicacion.
- Entregar un informe ejecutivo reutilizable por direccion y un backlog accionable para operaciones.

## Archivos de datos requeridos

La aplicacion asume la existencia de los siguientes datasets:

- `data/app_dataset/alcance_dataset.parquet`
- `data/app_dataset/kpis_base.parquet`
- `data/app_dataset/kpi_diario.parquet`
- `data/app_dataset/kpi_periodo.parquet`
- `data/app_dataset/kpi_semana.parquet`
- `data/app_dataset/kpi_dia.parquet`
- `data/app_dataset/kpi_categoria.parquet`
- `data/app_dataset/kpi_hora.parquet`
- `data/app_dataset/pareto_cat_global.parquet`
- `data/app_dataset/pareto_prod_global.parquet`
- `data/app_dataset/reglas.parquet`
- `data/app_dataset/combos_recomendados.parquet`
- `data/app_dataset/adjacency_pairs.parquet`
- `data/app_dataset/clusters_tickets.parquet`
- `data/app_dataset/clusters_departamento.parquet`
- `data/app_dataset/kpi_medio_pago.parquet`
- `data/app_dataset/rentabilidad_ticket.parquet`
- `data/raw/comprobantes_ventas_horario.csv`

Ademas consulta la salida modular y predictiva en:

- `data/processed/kpi_dia.parquet`
- `data/processed/kpi_tipo_dia.parquet`
- `data/processed/kpi_categoria.parquet`
- `data/processed/kpi_medio_pago.parquet`
- `data/processed/tickets.parquet`
- `data/processed/ventas_semanales_categoria.parquet`
- `data/predictivos/prediccion_ventas_semanal.parquet`
- `data/predictivos/prediccion_ventas_semanal_modelos.parquet`

Si un archivo esta ausente se reemplaza por un `DataFrame` vacio y la vista se desactiva de forma segura.

## Dependencias tecnicas

- Python 3.10 o superior.
- Librerias clave: `streamlit`, `pandas`, `numpy`, `plotly`, `pathlib`, `calendar`, `json`.
- La configuracion de pagina usa `st.set_page_config` con layout `wide` y estilos CSS inyectados.
- Caching: `@st.cache_data` envuelve `load_all_data` y `load_processed_data` para evitar lecturas repetidas.

## Flujo de ejecucion

1. **Setup**: se configura la pagina y se definen helpers de formato en estilo argentino (`formatear_numero_argentino`, `formatear_moneda_argentina`).
2. **Carga de datos**: `load_all_data()` arma un diccionario `data` con archivos base y procesa el CSV horario. `load_processed_data()` suma agregados y forecasts.
3. **Header y resumen ejecutivo**: se renderizan metricas principales (`n_tickets`, ticket promedio, rentabilidad) y un insight destacado.
4. **Tabs**: `st.tabs` crea siete vistas principales que construyen la narrativa.

## Estructura de pestañas y visualizaciones

### Tab 1 – Analisis temporal

- **Selector Mensual/Quincenal/Semanal** (`construir_figura_tendencia`): grafico de lineas con pendientes calculadas. Permite leer tendencia de tickets en diferentes granularidades y cuantifica la aceleracion o desaceleracion con una anotacion de la pendiente.
- **UPT semanal**: line chart semanal sobre unidades por ticket. Revela si la mezcla de productos empuja mas items por compra y muestra UPT promedio como referencia narrativa.
- **KPIs por tipo de dia**: barras de tickets, ticket promedio, UPT y margen por tipo de dia (laboral, fin de semana, etc.). Facilita decidir donde colocar promociones o refuerzos de personal.
- **Cadencia diaria y heatmap**: combinacion de comparativo por dia de la semana, tabla de top horarios y un heatmap Dia x Hora de comprobantes. Permite detectar ventanas calientes para staffing y activaciones.
- **Analisis horario avanzado**: grafico de barras apiladas por franjas de 30 minutos con foco en horas pico y anotaciones sobre los mejores desempenos.

### Tab 2 – Pareto y mix

- **Curva 80/20 por categoria**: para Carnes, Almacen, Lacteos y Limpieza. El bar chart resalta productos core y la linea secundaria muestra el acumulado porcentual, permitiendo ver cuantos codigos explican 80% de la venta.
- **Tabla de productos core**: top 15 productos por categoria con ventas, margen y % acumulado. Sirve para decisiones de planograma, abastecimiento y control de precios.
- **Ventas vs margen % por categoria**: grafico combinado barras + linea donde se cruzan ventas absolutas y margen porcentual para las 15 categorias principales. Indica donde defender margen y donde sostener volumen.

### Tab 3 – Market Basket (Combos)

- **KPIs principales**: counters de cantidad de reglas, lift maximo y soporte promedio para evaluar calidad del modelo de asociaciones.
- **Tabla de combos sugeridos**: principales pares antecedente-consecuente con soporte, confianza y lift. Traducen los hallazgos del MBA en acciones de merchandising o combos promocionales.
- **Top 20 reglas**: tabla ordenada por lift que permite inspeccionar asociaciones con mayor capacidad de incremento.
- **Scatter Support vs Confidence**: scatter Plotly donde la burbuja escala con el lift. Muestra equilibrio entre frecuencia y precision; sirve para priorizar reglas explotables.
- **Tabs “Vista general” y “Sin carniceria”**: replican todos los componentes anteriores, la segunda excluye productos de carniceria segun la normalizacion definida.

### Tab 4 – Segmentacion

- **Histograma de rentabilidad**: distribution plot con 50 bins y sombreado por cuartiles, delimitando Q1/Median/Q3. Permite entender dispersion de margen en la base.
- **Histograma de ventas por ticket (bins $2.500)**: barras + linea acumulada 80/20. Responde cuanta venta concentra cada rango y donde se ubican tickets altos.
- **Segmentos por cuartil**: grafico de barras y tabla resumen que detallan ticket promedio, items, margen y peso relativo para segmentos Bajo/Medio/Alto/Premium.
- **Histogramas de margen por segmento**: facet de cuatro paneles comparando distribuciones de margen en cada segmento, util para planes de fidelizacion o ofertas.
- **Placeholder rotacion**: mensaje explicito cuando no se dispone de datos de rotacion, manteniendo la consigna del proyecto y el backlog de mejoras.

### Tab 5 – Medios de pago

- **Normalizacion de metodos**: mapping a Efectivo, Debito, Credito y Billetera; se utiliza en todas las visualizaciones posteriores.
- **Barras de ventas por metodo**: muestra participacion porcentual directa en barras con etiquetas de % sobre las ventas totales.
- **Metricas por metodo**: cards `st.metric` con participacion y tooltip de ticket promedio para una lectura rapida.
- **Comparativo Efectivo vs Digitales**: tabla con ventas, tickets, margen y ticket promedio, destacando la participacion de cada modalidad.
- **Histogramas de venta y margen por metodo**: overlays que comparan distribucion de montos y margenes individuales entre metodos para detectar sesgos o oportunidades de promo bancaria.
- **Bloque de lecturas clave**: glosa narrativa que resume participacion digital vs efectivo y vincula con decisiones comerciales.

### Tab 6 – Estrategias priorizadas

- **Plan de accion 90 dias**: tarjetas HTML con 6 estrategias, cada una mapea el hallazgo analitico (lift de combos, pareto, horarios, etc.) con acciones concretas, metas y ROI estimado.
- **Impacto acumulado estimado**: tablero de tres metricas (ticket promedio, margen, ventas incrementales) que cuantifica el efecto esperado del plan si se ejecuta integralmente.

### Tab 7 – Informe ejecutivo

- **Narrativa de trabajo interno**: recapitula las oleadas de procesamiento, con cifras automaticas (tickets depurados, periodos, ticket promedio, margen).
- **Benchmark competitivo**: lista comparativa con retailers locales para contextualizar las estrategias.
- **Aplicacion a NINO**: glosa final que enlaza cada insight del dataset con movimientos tacticos sugeridos, manteniendo foco en rentabilidad y experiencia de compra.

## Consideraciones para mantenimiento

- **Nuevos datasets**: agregar la ruta al diccionario `required_files` (para base) o a `_load` (para procesados). Mantener nombres consistentes.
- **Personalizacion visual**: los estilos se inyectan via `st.markdown` con CSS. Cambios globales deben hacerse alli para evitar duplicaciones.
- **Internacionalizacion**: todo el formato numerico esta orientado a ARG (puntos para miles). Ajustar helpers si se requiere otro locale.
- **Performance**: el dashboard maneja datasets grandes; preferir joins y agrupaciones precomputadas en el pipeline `scripts/pipeline` antes de agregarlas en Streamlit.

## Como ejecutar

```bash
streamlit run final/streamlit_app/dashboard_cientifico.py
```

Ejecutar el comando desde la raiz del repositorio con un entorno donde esten instaladas las dependencias declaradas en `requirements.txt`.

## Roadmap sugerido

- Automatizar pruebas ligeras (por ejemplo validar schema de Parquet) antes de levantar el dashboard.
- Parametrizar rutas de datos via variables de entorno para facilitar despliegues en otros entornos.
- Migrar textos largos o HTML a archivos Markdown o plantillas Jinja para mejorar mantenibilidad.

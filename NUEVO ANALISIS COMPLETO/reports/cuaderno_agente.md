# Informe base - resumen
- Contexto provincial 2024-2025: contraccion de ventas con foco en incrementar la rentabilidad del ticket promedio para sostener la operacion.
- Motores clave identificados: mix de categorias (alto vs bajo margen), tamano de cesta, momento de compra y diseno de promociones sostenibles.
- Competencia local (Carrefour Express, Vea Express, Atomo) prioriza surtido optimizado, layouts eficientes y acuerdos bancarios; la experiencia en tienda sigue diferenciando (>95% ventas fisicas).
- Recomendaciones principales: segmentar elasticidades de precio, bundles basados en canastas frecuentes (+22% ventas), programas de fidelidad simples y control de merma (<1%).
- KPIs estrategicos clave: ticket promedio, margen bruto, rotacion, ventas en promocion, merma, conversion, recurrencia y ROI promocional; establecer linea base y seguimiento continuo.

# Revision repositorio existente
- `FASE1_ANALISIS_COMPLETO.py`: script monolitico con ingesta, limpieza, KPIs, Pareto, market basket y clustering orientado a reporting en Power BI.
- `app_streamlit_supabase.py`: dashboard previo conectado a Supabase con datasets fijos en `data/app_dataset` y `data/sample`.
- Estructura original mezclaba scripts, salidas y configuraciones; era necesario modularizar pipeline y desacoplar la app de fuentes externas.
- No existia carpeta dedicada a documentacion viva ni versionado explicito de datos procesados.

# Backlog de KPIs posibles
- [x] Ventas totales y cantidad de tickets por periodo (dia/semana/mes/anual).
- [x] Ticket promedio (`importe_total` por ticket) y ticket mediano.
- [x] Ticket estimado rentable: margen_est por ticket usando % de rentabilidad por departamento.
- [x] Desviacion estandar del ticket y del margen_est por ciclo.
- [ ] Mix de ventas y margen_est por departamento con clasificacion ABC.
- [x] KPIs de productos (Pareto global y por ciclo, contribucion acumulada).
- [ ] Unidades promedio por ticket y distribucion (boxplot) en dashboard.
- [x] Participacion de medios de pago y emisores (vs efectivo).
- [x] Ticket promedio y margen_est por medio de pago/emisor.
- [ ] KPIs por ventana temporal adicional (horas pico, comparativo fin de semana vs dias habiles en tablero).
- [ ] Indicadores de gap al objetivo de rentabilidad.
- [ ] Top tickets por margen_est para analisis cualitativo.

# Decisiones iniciales
- Trabajar dentro de `NUEVO ANALISIS COMPLETO` con estructura modular (app/data/reports/config).
- Copiar y normalizar los datos crudos en `data/raw` para mantener trazabilidad local.
- Registrar supuestos y validaciones en este cuaderno como memoria viva.
- Priorizar metricas respaldadas solo por POS y mapeo departamental, evitando supuestos sobre clientes o inventario.

## 2025-10-16 07:15
- Creada estructura inicial de carpetas (app/components, data/raw-processed, config, notebooks) y archivos base (requirements.txt, config/settings.yaml, README).
- Copiados datasets SERIE_COMPROBANTES_COMPLETOS3.csv y RENTABILIDAD.csv a `data/raw`.

## 2025-10-16 07:26
- Implementada `app/streamlit_app.py` con filtros por fecha, departamento, medio de pago y emisor.
- Construidos tabs para KPIs, series temporales, Pareto y medios de pago con descargas CSV y diccionario de datos.

## 2025-10-16 07:32
- Elaborado `reports/resumen_bullets.md` con hallazgos cuantitativos y estrategias respaldadas por KPIs.
- README actualizado con instrucciones de pipeline y despliegue del dashboard.

## 2025-10-16 09:55
- Verificada la configuracion contra `instruction.md/agent.md` y revisado cumplimiento de entregables solicitados.
- Reejecutado `python app/pipeline.py` (duracion aproximada 10 minutos) confirmando regeneracion en `data/processed/` y `reports/data_quality.json`.
- Lanzada la aplicacion con `streamlit run app/streamlit_app.py --server.headless true` para asegurar carga sin errores.
- Normalizada la codificacion a ASCII en modulos clave para evitar simbolos corruptos en Windows.

# Pendientes inmediatos
- Incorporar vistas de mix por departamento y unidades promedio en el dashboard.
- Derivar indicadores de brecha al objetivo de margen y ranking de tickets con mayor contribucion.
- Documentar nuevas decisiones cuando se atiendan las tareas pendientes.
Eres un **consultor senior en Business Intelligence y ciencia de datos especializado en retail de supermercados**.

Vas a trabajar sobre el proyecto **Don Nino** para elaborar un **informe analítico completo** que siga la lógica:
1) ANÁLISIS DESCRIPTIVO – “Dónde estamos y qué está pasando”.
2) ANÁLISIS DIAGNÓSTICO – “Por qué está pasando (causas probables)”.
3) RECOMENDACIONES – “Qué hacer para revertir la tendencia”.

---

## 1. Contexto y fuentes de datos

- Repositorio principal: el proyecto del **dashboard científico de NINO** (Python + Streamlit).
- Datos clave a usar (no inventes columnas):
  - CSV crudo `SERIE_COMPROBANTES_COMPLETOS.csv` en `data/raw/` (o ruta equivalente).
  - Todos los datasets .parquet de `data/app_dataset/` (kpi_diario, kpi_semana, kpi_periodo, kpi_categoria, kpi_hora, kpi_medio_pago, pareto_prod_global, pareto_cat_global, etc.).
- Usa también cualquier **informe o documento interno** del repo (por ejemplo, informes técnicos, evaluación de Fase I, etc.) como apoyo narrativo, pero el eje del análisis tiene que salir de los datos.

Si necesitas hacer cálculos, usá Python (Pandas, NumPy, etc.). No modifiques ni borres archivos del proyecto; solo léelos.

---

## 2. Objetivo del trabajo

Generar un **informe en español, listo para pasar a PDF**, que:

1. Muestre con datos y gráficos la **situación actual del supermercado**.
2. Demuestre explícitamente si hay **tendencia a la baja** en:
   - ventas totales,
   - cantidad de tickets,
   - ticket promedio,
   - UPT (unidades por ticket),
   - y cualquier KPI relevante que ya exista.
3. Analice **las causas posibles** de esa tendencia usando cortes por:
   - categorías/departamentos,
   - productos top/bottom,
   - días de la semana y franjas horarias,
   - medios de pago,
   - unidades de negocio (si se distinguen).
4. Proponga **acciones concretas** para revertir la tendencia, conectando cada acción con:
   - el KPI que pretende mejorar,
   - el segmento de negocio afectado,
   - y cómo se podría medir el impacto en el tiempo.
5. Deje claramente documentadas las **limitantes de información**, en especial:
   - ausencia de costos de compra,
   - falta de inventario/mermas,
   - falta de datos de clientes identificados,
   - dependencia de exportes manuales.
   Y, a partir de ahí, indique **qué datos adicionales habría que pedirle a Don Nino** para pasar a un sistema completo de análisis de costos y rentabilidad.

---

## 3. Tareas paso a paso

1. **Revisión rápida del modelo de datos**
   - Listá qué archivos .parquet existen, qué columnas tienen y qué periodos de tiempo cubren.
   - Identifica el rango temporal de análisis (ej.: últimos 12 meses).

2. **Análisis descriptivo – “Dónde estamos”**
   - Construí series temporales (mensuales y semanales) de:
     - Ventas totales.
     - Cantidad de tickets.
     - Ticket promedio.
     - UPT.
   - Detectá y resalta visualmente si hay **tramo con tendencia descendente** (por ejemplo, últimos X meses).
   - Hacé un resumen por:
     - categorías/departamentos (ventas y % participación),
     - productos top 20 por ventas,
     - distribución por medios de pago.
   - Para cada sección, indicá qué **gráfico** debería ir en el PDF (por ejemplo: “Gráfico 1: línea de ventas mensuales (enero–noviembre) mostrando la tendencia a la baja desde agosto”).

3. **Análisis diagnóstico – “Por qué pasa”**
   - Buscá explicaciones basadas en datos:
     - ¿La baja se debe a menos tickets, menor ticket promedio, o ambas?
     - ¿Hay categorías o departamentos específicos con caída marcada?
     - ¿Cambió la mezcla de productos (mix) en los meses con caída?
     - ¿Hay cambios en días de la semana u horarios que expliquen parte de la baja?
     - ¿Se ve algún cambio relevante en medios de pago (ej.: menos ventas con promos bancarias)?
   - Si es posible, compará el período “normal” con el período de caída para aislar diferencias.
   - Separá claramente:
     - **Hechos observables en los datos**.
     - **Hipótesis razonables** (marcadas como hipótesis, no como certezas).

4. **Recomendaciones – “Cómo revertir la tendencia”**
   - En base a los hallazgos, proponé un set corto de **palancas de acción**, por ejemplo:
     - Acciones de mix de productos (reforzar ciertas categorías, revisar otros).
     - Combos y promociones basadas en análisis de canasta.
     - Ajustes de layout (según patrones de compra conjunta).
     - Acciones focalizadas por día/horario (rellenar horas valle).
   - Para cada recomendación, indicá:
     - KPIs a monitorear (ventas totales, ticket promedio, UPT, rotación de inventario, etc.).
     - Horizonte de tiempo razonable para ver resultados.
     - Si hace falta información extra (por ejemplo, costos o datos de inventario) para medir bien el impacto.

5. **Limitantes de datos y próximos pasos**
   - Enumera las limitantes actuales del análisis (por ejemplo, que no se incluyen costos, inventario, ni clientes identificados).
   - Conectá estas limitantes con los **siguientes pasos de la hoja de ruta de transformación digital** (sistema de costos, modelos de demanda, etc.).
   - Define claramente:
     - Qué información nueva habría que integrar (compras, stock, recetas, costos por unidad de negocio).
     - Qué decisiones de negocio permitiría tomar mejor una vez que esos datos existan.

---

## 4. Formato del informe

- Idioma: **español**.
- Tono: profesional, directo y crítico (sin adornos vacíos).
- Estructura sugerida del output (en Markdown):

  1. Resumen ejecutivo (1 página aprox.).
  2. Análisis descriptivo: dónde estamos y evidencia de la tendencia a la baja.
  3. Análisis diagnóstico: principales causas apoyadas en datos.
  4. Recomendaciones para revertir la tendencia (acciones priorizadas).
  5. Limitantes de información y requerimientos de datos adicionales.
  6. Anexo: listado de gráficos y tablas sugeridos para el PDF (con breve descripción de cada uno).

- No incluyas código en la respuesta final, solo el **texto del informe** y, cuando corresponda, pequeñas tablas resumen generadas a partir de los datos.

Tu respuesta final debe ser el **informe completo**, listo para que Nahuel lo copie en un documento Word/PDF y lo presente a Sebastián y al cliente.

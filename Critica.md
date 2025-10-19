# Informe crítico de validación de datos y storytelling

## 1. Alcance de la revisión
- Datasets verificados: `data/app_dataset/*.parquet` (alcance, KPIs, kpi_periodo, kpi_semana, kpi_dia, kpi_medio_pago, pareto_cat_global, pareto_prod_global, rentabilidad_ticket, tickets).
- Scripts revisados: lectura de `pipeline_estrategias.py` (se intentó reejecutar; ver conclusiones), código de `dashboard_cientifico.py` (sección Pareto, análisis temporal) y documento `Estrategias_Analitica.md`.
- Herramientas utilizadas: Python 3.10 (via `python -c`), cálculos directos sobre los Parquet entregados. Se dejaron rastros reproducibles en el historial del repositorio.

## 2. Métricas numéricas verificadas
Valores obtenidos directamente desde los Parquet comparados con los expuestos en el dashboard:

| Métrica                                | Valor recalculado | Observaciones |
|----------------------------------------|-------------------|---------------|
| Tickets totales (`n_tickets`)          | 306 011           | Coincide con dashboard y README. |
| Ventas totales (`ventas_total`)        | $8 216 314 170,99 | Coincide. |
| Margen total (`margen_total`)          | $2 285 459 564,25 | Coincide. |
| Ticket promedio                        | $26 849,73        | Coincide. |
| Rentabilidad global                    | 27,82 %           | Coincide. |
| Items promedio por ticket              | 10,07             | Coincide. |
| Rentabilidad promedio por ticket       | $7 468,55         | Coincide. |
| Ventas por medio de pago (participación) | Crédito 49,6 %; Efectivo 31,3 %; “BILLETERA VITUAL” 19,2 % | Nombres sin normalizar. |
| Ventas por día de semana               | Sábado lidera (1,73 B / 56 745 tickets) | Apoya conclusiones sobre fin de semana. |
| Cuantiles de rentabilidad por ticket   | Q1 26,23 %; mediana 28,56 %; Q3 30,04 % | Texto analítico menciona valores menores (20 %, 35 %). |

## 3. Hallazgos críticos y discrepancias
1. **Cuantiles de rentabilidad**: el dashboard y el informe mencionan Q1≈20 %, Q3≈35 %, pero los datos entregan Q1=26,2 %, Q3=30,0 %. Esto cambia la lectura sobre “tickets de bajo margen”, porque el tramo inferior no es tan delgado como se describe.
2. **Pareto de productos**: para alcanzar el 80 % de las ventas se requieren **1 544 SKU**. El top 10 presentado cubre apenas 12,4 % de las ventas, por lo que el nuevo gráfico “Top 10 que explican el 80 %” no cumple con la premisa. Se sugiere mostrar el número real de productos necesarios o replantear el título.
3. **Granularidad horaria inexistente**: todos los tickets traen `hora = 0`. La distribución “cada 30 minutos” y el insight asociado al horario pico carecen de fundamento. Debe eliminarse o documentar la ausencia de datos de horario real.
4. **Medios de pago sin limpieza**: `BILLETERA VITUAL` (con typo) y duplicados por mayúsculas implican que las participaciones por medio no están consolidadas correctamente. Esto invalida parte de la narrativa sobre “bolsillo digital” si no se corrige.
5. **Cobertura temporal**: la serie comienza en octubre 2024 y termina el 10 de octubre 2025; sin un año calendario completo. Algunas conclusiones (“promedios anuales”, “últimos 30 días”) deberían especificar este recorte.
6. **Pipeline de generación**: intentar ejecutar `pipeline_estrategias.py` vuelve a procesar los 2,94 M de registros, pero la corrida actual se detiene en el bloque de market basket (error de memoria al manipular arrays de ~38 MiB). El pipeline no es idempotente ni modular, dificultando la auditoría.
7. **Nombres de categorías**: aparecen mayúsculas con acentos perdidos (`CARNICERIA AL 10,5 %`) y uso mixto de comas/puntos. Esto sugiere pérdida de encoding en la normalización y puede afectar visualizaciones o integraciones posteriores.

## 4. Evaluación del storytelling e investigación
- **Fortalezas**: narrativa conectada con estrategias comerciales (combos, layout, fidelización) y referencias a competidores locales (Carrefour Express, Vea, Átomo). El resumen ejecutivo ordena “oleadas” de trabajo que ayudan a contextualizar la evolución.
- **Debilidades**:
  - No se incluyen fuentes ni fecha de la investigación de mercado: difícil validar las cifras externas (ej. “30 % de las ventas en oferta”).
  - Falta trazabilidad entre insights y tests estadísticos. No se muestran intervalos, hipótesis ni validaciones sobre variaciones (p.ej. diferencia significativa entre días de semana).
  - Las estrategias se basan en heurísticos (Pareto, combos) pero no se documentan experimentos A/B ni simulaciones de impacto.
  - No se discuten riesgos: estacionalidad corta, sesgos por no incluir e-commerce, ausencia de horarios reales, etc.

## 5. Recomendaciones de mejora
1. **Calidad de datos**: limpiar nombres de medios de pago, normalizar categorías y decodificar caracteres especiales. Incorporar validaciones en el pipeline (por ejemplo, `assert tickets['hora'].nunique() > 1`).
2. **Granularidad temporal real**: si el raw original tiene timestamp, preservar hora/minuto en `tickets.parquet`. Si no existe, eliminar gráficos de media hora y documentar la limitación.
3. **Pareto de productos**: mostrar claramente cuántos SKU representan el 80 % y ofrecer un top N configurable. Alternativa: agrupar por familias o subcategorías para lograr concentraciones útiles.
4. **Cuantiles y segmentación**: recalcular y actualizar las cifras en el dashboard e insights; de lo contrario, ajustar copy para no citar valores incorrectos.
5. **Pipeline reproducible**: modularizar `pipeline_estrategias.py` para permitir reejecutar etapas (KPIs, Pareto, Market Basket) por separado y evitar volver a cargar datasets intermedios. Registrar consumo de memoria y añadir banderas `--skip-*`.
6. **Investigación documental**: incluir en el repo un apéndice con las fuentes y fecha de consulta, y diferenciar claramente datos primarios vs. benchmarking externo.
7. **Análisis adicional**: agregar métricas de recurrencia de clientes (si existe identificador), elasticidad por categoría/precio y un control de merma si ese dato está en el raw. Explorar series de ventas vs. inflación para contextualizar márgenes.

## 6. Elementos que aportarían poco valor
- Gráfico de “tickets cada 30 minutos” (sin granularidad real), y cualquier insight derivado.
- Texto que asume cuartiles <20 % de rentabilidad. Debe reescribirse o eliminarse.
- Narrativas que presuponen 80/20 para productos sin mostrar que el patrón se cumple (con 1 544 SKU dentro del 80 %, el fenómeno es más cercano a 50/50).

## 7. Ejecución de scripts y reproducibilidad
- **Intento de `pipeline_estrategias.py`**: el proceso avanza hasta el bloque de market basket y luego arroja `numpy.core._exceptions._ArrayMemoryError`. Requiere optimización o ejecución en entorno con más memoria. Se recomienda habilitar argumentos CLI para procesar en etapas y reutilizar resultados previos.
- **Verificaciones ejecutadas**: múltiples comandos `python -c` sobre los Parquet, calculando sumas, percentiles y conteos (ver historial de consola). Estos resultados sustentan la tabla de la sección 2.

## 8. Próximos pasos sugeridos
1. Corregir y re-publicar los indicadores afectados (cuartiles de rentabilidad, horario pico, top de productos).
2. Refactorizar el pipeline para poder reejecutarlo sin fallas y con validaciones automáticas de calidad.
3. Documentar explícitamente el periodo cubierto, las exclusiones (p.ej. e-commerce) y los supuestos de margen.
4. Incorporar un cuaderno (Jupyter o Markdown) donde se muestren las verificaciones numéricas paso a paso para futuras auditorías.
5. Revisar la investigación de competencia con citas verificables y, si es posible, integrar métricas comparativas (tickets por m², share de promos) que permitan contrastar con los datos de NINO.

---
**Conclusión:** los indicadores principales coinciden con los cálculos entregados, pero existen incongruencias en los cuantiles de rentabilidad, el Pareto de productos y la granularidad temporal. Antes de avanzar con nuevas recomendaciones comerciales, es imprescindible depurar los campos clave, alinear el storytelling con los números reales y robustecer el pipeline para garantizar reproducibilidad y trazabilidad analítica.

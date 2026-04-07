# Informe de Auditoria de Datos para Claude Code

Fecha de ejecucion: 2026-03-27
Periodo auditado: 2024-10-01 a 2025-12-31
Dataset: Supermercado Nino / BOSIN S.A.

## Objetivo

Compartir con Claude Code un resumen ejecutivo y tecnico de la auditoria de calidad de datos sobre los parquets productivos del supermercado, con foco en integridad, consistencia de margenes, paretos de elaboracion propia, cross-checks entre datasets, anomalias y calidad textual.

## Archivos auditados

- `data/app_dataset/detalle_lineas.parquet`
- `data/app_dataset/tickets.parquet`
- `data/app_dataset/pareto_prod_global.parquet`
- `data/app_dataset/kpi_categoria.parquet`
- `data/app_dataset/kpi_dia.parquet`
- `data/app_dataset/kpi_hora.parquet`
- `data/app_dataset/kpi_medio_pago.parquet`
- `data/app_dataset/alcance_dataset.parquet`
- `data/raw/RENTABILIDAD.csv`

## Artefactos generados

- Script reproducible: `scripts/auditoria_dataset_supermercado_nino.py`
- Reporte tecnico completo: `outputs/auditoria_dataset_supermercado_nino_2026-03-27.md`
- Salida estructurada: `outputs/auditoria_dataset_supermercado_nino_2026-03-27.json`

## Scorecard

- Puntaje global de calidad: `81.1 / 100`
- Resultado agregado: `31 OK`, `11 REVISAR`, `3 ERROR`

## Resumen ejecutivo

El dataset base es consistente en sus metricas principales. Las ventas totales, la cantidad de tickets, el ticket promedio, la rentabilidad global y los paretos de Pasteleria y Rotiseria coinciden en general con los valores esperados.

Los principales problemas no estan en los totales, sino en campos derivados o auxiliares del modelo:

- El campo `hora` de `detalle_lineas.parquet` esta completamente degradado.
- `kpi_hora.parquet` no representa datos reales; contiene valores placeholder.
- La columna `rentabilidad_pct` en `detalle_lineas.parquet` esta corrupta y no debe usarse.
- La columna confiable para margenes es `rentabilidad_factor`.
- El universo de SKU operativo esta mezclado entre `producto_id` y `descripcion`, lo que explica la diferencia entre `10.772` codigos y `9.058` SKUs consolidados.

## Resultados clave validados

- Ventas totales encontradas: `$9.550.165.077,18`
- Tickets unicos encontrados: `345.130`
- Ticket promedio calculado: `$27.671,21`
- Items por ticket calculados desde `cantidad`: `10,10`
- Rentabilidad global calculada: `28,23%`
- Categorias unicas: `48`
- SKUs consolidados por `descripcion`: `9.058`

## Hallazgos criticos

### 1. Campo `hora` inutilizable

Estado: `ERROR`

Hallazgo:

- En `detalle_lineas.parquet`, todas las filas tienen `hora = 0`.
- Esto invalida cualquier analisis por franja horaria construido desde el detalle.

Impacto:

- Todos los analisis horarios del dashboard o de datasets derivados quedan comprometidos.

Hipotesis de causa raiz:

- El ETL perdio la hora original durante una transformacion y relleno con cero.

### 2. `kpi_hora.parquet` contiene placeholders

Estado: `ERROR`

Hallazgo:

- `kpi_hora.parquet` suma solo `$700.000`, contra `$9.550.165.077,18` del detalle.
- Tiene 14 filas con estructura artificial de `100 tickets` y `$50.000` por hora.

Impacto:

- El parquet horario no es util para reporting ni para decisiones.

Hipotesis de causa raiz:

- Se publico un dataset mock o de prueba en lugar del derivado real.

### 3. `rentabilidad_pct` esta corrupta

Estado: `ERROR`

Hallazgo:

- La verificacion `margen_linea = importe_total * rentabilidad_pct / 100` falla en `3.306.662` lineas.
- En `99,85%` de las filas, `rentabilidad_pct` coincide con `margen_linea`, no con un porcentaje.
- En cambio, `margen_linea = importe_total * rentabilidad_factor` da `0` errores.

Impacto:

- Cualquier proceso que use `rentabilidad_pct` como porcentaje real produce resultados incorrectos.

Hipotesis de causa raiz:

- Durante el ETL se sobrescribio `rentabilidad_pct` con el valor absoluto del margen.

## Hallazgos relevantes para revisar

### Integridad operativa

- `88` tickets negativos.
- `449` tickets en cero.
- `309` tickets mayores a `$500.000`.
- `20.328` lineas con `cantidad < 0`.
- `5.321` lineas con `precio_unitario = 0`.

Interpretacion probable:

- Los negativos y ceros parecen asociados a notas de credito, reversos o documentos internos.
- Los tickets muy altos parecen corresponder a operaciones mayoristas o movimientos especiales.

### Margenes

- `rentabilidad_factor` matchea correctamente contra `RENTABILIDAD.csv` en `46` categorias.
- Las 2 categorias sin referencia son `SIN CATEGORIA` y `VENTAS DE UVA`.
- Las categorias de `Elaboracion Propia` auditadas estan correctamente al `30%`.
- Los unicos productos con margen no positivo pertenecen a `IVA RED IB GRAL`, consistente con ajustes/impuestos.

### Pareto Pasteleria

- Ventas totales: `$93.793.761,46`
- Productos: `49`
- Producto lider: `TORTA BIZCOCHUELO NINO` con `30,86%`
- Top 3: `42,36%`
- Segmento C: `25 productos`, `5,24%`

Desvio a revisar:

- Para superar el `80%` de ventas se necesitan `14` productos, no `13`.
- Con 13 productos el acumulado queda en `78,15%`.
- El producto 14 lleva el acumulado a `80,69%`.

### Pareto Rotiseria

- Ventas totales: `$129.873.557,80`
- `64` SKUs y `38` familias
- `EMPANADA CARNE`: `$34.678.609,90`
- `EMPANADA J&Q`: `$9.414.500,00`
- `MIGA TRIPLE`: `$7.280.830,00`
- `EMPANADA CEBOLLA/QUESO`: `$2.544.700,00`
- Total empanadas: `49,85%`
- `MATAMBRE NINO`: `#2` con `$18.084.116,50`

Desvio a revisar:

- Para superar el `80%` se necesitan `14` familias, no `13`.
- Con 13 familias el acumulado queda en `78,36%`.
- La familia 14 lleva el acumulado a `80,51%`.

### Anomalias y outliers

- `7` dias con ventas fuera de `±3` desvio estandar.
- Los mas altos se concentran en `2024-12-23`, `2024-12-30`, `2025-07-24`, `2025-07-28`, `2025-12-22`, `2025-12-23` y `2025-12-30`.
- `8` productos aparecen en una sola transaccion con venta acumulada mayor a `$100.000`.
- `3` categorias tienen menos de `10` transacciones: `ART. VARIOS`, `ELECTRONICA`, `VENTAS DE UVA`.

### Calidad textual

- `1.924` descripciones aparecen asociadas a multiples `producto_id`.
- Hay `446.665` filas con el typo `BILLETERA VITUAL`.
- No se encontraron descripciones vacias ni literales `NAN` o `NULL`.

## Conclusiones para Claude Code

Si Claude Code va a trabajar sobre este dataset, deberia asumir lo siguiente:

1. Los campos confiables para ventas y margen son:
   - `importe_total`
   - `margen_linea`
   - `rentabilidad_factor`
   - `ticket_id`
   - `fecha`

2. Los campos que no deberian usarse sin remediacion previa son:
   - `hora`
   - `rentabilidad_pct`
   - `kpi_hora.parquet`

3. La unidad de SKU depende del caso:
   - Para operativa interna: `producto_id`
   - Para paretos y reporting consolidado: `descripcion`

4. Los totales globales del modelo son confiables:
   - Ventas
   - Tickets
   - Pareto global
   - KPI por categoria
   - Alcance del dataset

## Recomendaciones

1. Regenerar `detalle_lineas.parquet` preservando la hora original del comprobante.
2. Regenerar `kpi_hora.parquet` desde el detalle corregido.
3. Corregir el ETL que pisa `rentabilidad_pct` y recalcular el campo como porcentaje real.
4. Mantener `rentabilidad_factor` como fuente de verdad del margen hasta corregir el punto anterior.
5. Definir formalmente si el SKU analitico es `producto_id` o `descripcion`.
6. Normalizar `tipo_medio_pago`, corrigiendo `BILLETERA VITUAL` a `BILLETERA VIRTUAL`.
7. Revisar manualmente tickets negativos, tickets en cero, tickets > `$500.000` y categorias de muy baja frecuencia.

## Comando de reproduccion

```bash
python scripts/auditoria_dataset_supermercado_nino.py
```

## Nota final

La auditoria muestra que el dataset es usable para analisis de ventas, rentabilidad global y paretos, pero no para analisis horario ni para cualquier proceso que dependa de `rentabilidad_pct` como porcentaje real.

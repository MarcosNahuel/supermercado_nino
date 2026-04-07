# Auditoría Independiente de Métricas

Fecha de auditoría: 2026-04-06

## Alcance

Se auditó un análisis comparativo de tickets de Supermercado NINO generado por otro modelo de IA. La auditoría se rehízo desde datos crudos, reproduciendo las métricas indicadas en el prompt y comparándolas contra los valores afirmados en el análisis.

Períodos auditados:

- P1: 2026-03-30 a 2026-04-05
- P2: 2025-04-14 a 2025-04-20
- Baseline contrafáctico: 2025-01-05 a 2025-11-30

Evento de negocio:

- Implementación de fila única: 2026-03-28

## Fuentes usadas

1. [comprobantes_ventas_horario.csv](D:/OneDrive/GitHub/supermercado_nino definitivo claude/data/raw/comprobantes_ventas_horario.csv)
2. `H:\Mi unidad\PYMEINSIDE\nino\extraccion datos\2026\marzo\ReporteComprobantesVenta6-4.xlsx`
3. [detalle_lineas.parquet](D:/OneDrive/GitHub/supermercado_nino definitivo claude/data/processed/detalle_lineas.parquet)

## Metodología reproducida

- CSV histórico:
  - Separador `;`
  - Filtro: `Comprobante` empieza con `"Factura"`
  - Fecha: `Fecha.str[:10]`
  - Hora: `str[11:13]` sobre la columna `Hora`
- Excel 2026:
  - `header=4`
  - Excluir filas donde `Fecha` contenga `TOTAL` o `nan`
  - Fecha: `pd.to_datetime(..., dayfirst=True)`
  - Filtro: `Comprobante` empieza con `"Factura"`
  - Hora: `str[:2]` sobre la columna `Hora`
- Parquet:
  - Fecha normalizada a día
  - Productos totales = cantidad de líneas
  - Productos por ticket = `len(periodo) / ticket_id.nunique()`
- Cajas:
  - PV extraído con regex `(\d{4})-\d+`
  - Mapeo aplicado:

```python
PV_MAP = {"0014":1,"0015":1,"0016":2,"0017":2,"0018":3,"0019":3,
          "0020":4,"0021":4,"0022":5,"0023":5,"0024":6,"0025":6,
          "0026":7,"0027":7,"0028":8,"0029":8}
```

## Check 1. KPIs de período

### Resultados

| Métrica | Calculado P1 | Afirmado P1 | Dif. abs. P1 | Dif. % P1 | Veredicto P1 | Calculado P2 | Afirmado P2 | Dif. abs. P2 | Dif. % P2 | Veredicto P2 |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---|
| Tickets totales | 6,056 | 6,056 | 0 | 0.00% | OK | 5,930 | 5,930 | 0 | 0.00% | OK |
| Productos totales | 48,360 | 48,360 | 0 | 0.00% | OK | 55,728 | 55,728 | 0 | 0.00% | OK |
| Tickets / día | 865.14 | 865.10 | 0.04 | 0.00% | OK | 847.14 | 847.10 | 0.04 | 0.00% | OK |
| Productos / ticket | 7.9802 | 7.98 | 0.0002 | 0.00% | OK | 9.3598 | 9.36 | 0.0002 | 0.00% | OK |

### Observaciones

- Los tickets de comprobantes y los tickets únicos del parquet no coinciden exactamente:
  - P1: comprobantes `6,056` vs parquet `6,060`
  - P2: comprobantes `5,930` vs parquet `5,954`
- Esto no invalida la métrica auditada porque el prompt define `prod/ticket` usando `ticket_id.nunique()` del parquet.

## Check 2. Distribución por caja

### P1

| Caja | Tickets |
|---|---:|
| 1 | 945 |
| 2 | 1,146 |
| 3 | 984 |
| 4 | 838 |
| 5 | 856 |
| 6 | 891 |
| 7 | 370 |
| 8 | 26 |
| Total mapeado | 6,056 |
| Total tickets período | 6,056 |
| Sin mapear | 0 |

### P2

| Caja | Tickets |
|---|---:|
| 1 | 1,091 |
| 2 | 803 |
| 3 | 809 |
| 4 | 957 |
| 5 | 867 |
| 6 | 979 |
| 7 | 342 |
| 8 | 82 |
| Total mapeado | 5,930 |
| Total tickets período | 5,930 |
| Sin mapear | 0 |

### Veredicto

- La suma de cajas coincide exactamente con el total de tickets en ambos períodos.
- Veredicto: OK

## Check 3. Estadísticas por hora

Metodología aplicada:

- Conteo de `Comprobante` único por `fecha` y `hora`
- `pivot(fecha × hora)`
- Para cada hora `7–22`: media, mediana, P25, P75, P90

### Verificación de consistencia

| Período | Suma de tickets por hora | Tickets totales período | Veredicto |
|---|---:|---:|---|
| P1 | 6,056 | 6,056 | OK |
| P2 | 5,930 | 5,930 | OK |

### Hora pico real

| Período | Hora pico por media diaria | Media tickets/día |
|---|---:|---:|
| P1 | 12h | 153.43 |
| P2 | 12h | 145.71 |

### Tabla horaria P1

| Hora | Media | Mediana | P25 | P75 | P90 |
|---|---:|---:|---:|---:|---:|
| 7 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 8 | 11.29 | 11.00 | 0.00 | 22.00 | 22.80 |
| 9 | 80.86 | 94.00 | 66.00 | 95.50 | 98.20 |
| 10 | 125.14 | 117.00 | 109.50 | 138.50 | 154.60 |
| 11 | 146.57 | 136.00 | 133.00 | 158.50 | 180.80 |
| 12 | 153.43 | 149.00 | 117.50 | 190.50 | 208.40 |
| 13 | 18.14 | 14.00 | 11.00 | 25.50 | 28.80 |
| 14 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 16 | 16.57 | 22.00 | 9.50 | 24.00 | 25.20 |
| 17 | 59.00 | 64.00 | 26.00 | 91.50 | 111.00 |
| 18 | 77.86 | 103.00 | 39.00 | 114.00 | 128.20 |
| 19 | 92.00 | 122.00 | 53.50 | 133.50 | 140.20 |
| 20 | 82.86 | 107.00 | 45.00 | 126.00 | 129.20 |
| 21 | 1.43 | 0.00 | 0.00 | 1.50 | 4.00 |
| 22 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |

### Tabla horaria P2

| Hora | Media | Mediana | P25 | P75 | P90 |
|---|---:|---:|---:|---:|---:|
| 7 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 8 | 11.71 | 13.00 | 6.50 | 16.00 | 21.00 |
| 9 | 70.14 | 74.00 | 71.00 | 76.50 | 79.00 |
| 10 | 117.14 | 121.00 | 110.00 | 126.00 | 136.80 |
| 11 | 142.00 | 140.00 | 129.00 | 150.50 | 167.20 |
| 12 | 145.71 | 132.00 | 130.00 | 166.00 | 188.40 |
| 13 | 22.86 | 17.00 | 14.50 | 28.00 | 41.20 |
| 14 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 16 | 26.86 | 35.00 | 14.50 | 37.50 | 43.00 |
| 17 | 67.43 | 87.00 | 42.50 | 89.50 | 102.40 |
| 18 | 85.29 | 116.00 | 45.00 | 122.50 | 132.80 |
| 19 | 102.14 | 123.00 | 60.00 | 150.50 | 160.20 |
| 20 | 55.86 | 76.00 | 34.00 | 79.00 | 83.60 |
| 21 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 22 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |

### Comparación contra la afirmación del análisis

- Afirmación auditada: la hora pico sería aproximadamente `18–19h`
- Resultado reproducido: la hora pico total del día es `12h` en ambos períodos

### Veredicto

- Consistencia total de tickets/hora: OK
- Afirmación de hora pico `18–19h`: FALLO

### Causa probable

- El análisis parece haber interpretado un subpico vespertino dentro del bloque `17–20h`, pero no la hora pico global del día completo.
- Con la metodología pedida en el prompt, el máximo real está al mediodía.

## Check 4. Tendencia histórica

Metodología aplicada:

- Agregación semanal ISO iniciando en lunes
- `tickets = ticket_id.nunique()` por semana
- `prod_tk = líneas / tickets`
- Exclusión de semanas con menos de 5 días
- Regresión lineal con `scipy.stats.linregress`

### Resultado reproducido

La coincidencia con el análisis se obtiene corriendo la regresión sobre semanas completas pre `28/03/2026`.

| Métrica | Calculado | Afirmado | Dif. abs. | Dif. % | Veredicto |
|---|---:|---:|---:|---:|---|
| Slope tickets/día | -1.0030 | -1.00 | 0.0030 | 0.30% | OK |
| p-value tickets | 0.000645 | `< 0.001` | n/a | n/a | OK |
| r² tickets | 0.1522 | `≈ 0.15` | 0.0022 | 1.46% | OK |
| Slope prod_tk/día | -0.000374 | -0.0004 | 0.000026 | 6.48% | OK por redondeo |
| p-value prod_tk | 0.1672 | 0.167 | 0.0002 | 0.13% | OK |
| Media pre fila única prod_tk | 9.5899 | 9.59 | 0.0001 | 0.00% | OK |
| Semana 30/03 prod_tk | 7.9802 | 7.98 | 0.0002 | 0.00% | OK |
| Drop vs pre | -1.6097 | -1.61 | 0.0003 | 0.02% | OK |

### Observaciones

- El valor afirmado como `r ≈ 0.15` coincide en realidad con `r² ≈ 0.152`, no con `r`.
- Si se corre la regresión sobre todo el histórico, cambian los números:
  - tickets slope `-0.9007`
  - tickets p `0.00189`
  - prod_tk slope `-0.000592`
  - prod_tk p `0.0438`

### Causa probable de confusión

- El texto del análisis no explicita con suficiente claridad si la regresión se hace sobre todo el histórico o solo el tramo pre implementación.
- Los valores afirmados corresponden al tramo pre fila única, no al histórico completo.

## Check 5. Análisis contrafáctico

Baseline aplicado:

- Datos diarios entre `2025-01-05` y `2025-11-30`
- Mediana por día de semana para:
  - tickets
  - productos por ticket

### Baseline por día de semana

| DOW | tk_med | pt_med |
|---:|---:|---:|
| 0 | 815.0 | 9.0359 |
| 1 | 843.0 | 9.2974 |
| 2 | 808.0 | 8.9623 |
| 3 | 813.5 | 9.1430 |
| 4 | 895.0 | 9.9417 |
| 5 | 1,047.0 | 10.9557 |
| 6 | 467.0 | 9.5734 |

### Comparación diaria

| Fecha | DOW | Tickets real | Δ% tickets calculado | Δ% tickets afirmado | Dif. abs. | Dif. % | Prod/tk real | Δ% prod_tk calculado | Δ% prod_tk afirmado | Dif. abs. | Dif. % | Veredicto |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 2026-03-28 | 5 | 1,076 | +2.77% | +2.8% | 0.03 pp | 1.08% | 8.8875 | -18.88% | -18.9% | 0.02 pp | 0.12% | OK |
| 2026-03-29 | 6 | 480 | +2.78% | +2.8% | 0.02 pp | 0.58% | 8.6396 | -9.75% | -9.8% | 0.05 pp | 0.47% | OK |
| 2026-03-30 | 0 | 851 | +4.42% | +4.4% | 0.02 pp | 0.39% | 8.0176 | -11.27% | -11.3% | 0.03 pp | 0.27% | OK |
| 2026-03-31 | 1 | 940 | +11.51% | +11.5% | 0.01 pp | 0.06% | 8.5596 | -7.94% | -7.9% | 0.04 pp | 0.45% | OK |
| 2026-04-01 | 2 | 1,020 | +26.24% | +26.2% | 0.04 pp | 0.14% | 7.8725 | -12.16% | -12.2% | 0.04 pp | 0.34% | OK |
| 2026-04-02 | 3 | 1,050 | +29.07% | +29.1% | 0.03 pp | 0.10% | 8.3210 | -8.99% | -9.0% | 0.01 pp | 0.10% | OK |
| 2026-04-03 | 4 | 470 | -47.49% | -47.5% | 0.01 pp | 0.03% | 7.3319 | -26.25% | -26.3% | 0.05 pp | 0.19% | OK |
| 2026-04-04 | 5 | 1,260 | +20.34% | +20.3% | 0.04 pp | 0.22% | 7.9444 | -27.49% | -27.5% | 0.01 pp | 0.05% | OK |
| 2026-04-05 | 6 | 469 | +0.43% | +0.4% | 0.03 pp | 7.07% | 6.9680 | -27.21% | -27.2% | 0.01 pp | 0.05% | OK |

### Resumen días normales

Definición auditada:

- Días normales = `2026-03-28` a `2026-04-02`
- Se excluyen `2026-04-03`, `2026-04-04`, `2026-04-05`

| Métrica | Calculado | Afirmado | Dif. abs. | Dif. % | Veredicto |
|---|---:|---:|---:|---:|---|
| Δ% tickets promedio | +12.80% | +13.0% | 0.20 pp | 1.56% | OK |
| Δ% prod_tk promedio | -11.50% | -10.0% | 1.50 pp | 13.03% | OK por tolerancia absoluta del pedido |
| Efecto neto en volumen | -0.17% | +2.0% | 2.17 pp | 1267.00% | FALLO |

### Causa probable del fallo en efecto neto

- El `+2%` afirmado sale de recombinar valores redondeados (`+13%` y `-10%`).
- Con los valores calculados sin redondeo:

```text
(1 + 0.1279779699) * (1 - 0.1149775809) - 1 = -0.0017142084
```

- El efecto neto reproducido es `-0.17%`, levemente negativo, no `+2%`.

## Resumen ejecutivo

### Checks OK

1. Check 1. KPIs de período
2. Check 2. Distribución por caja
3. Check 4. Tendencia histórica

### Checks con fallo

1. Check 3. Estadísticas por hora
   - Falla la afirmación de que la hora pico sería `18–19h`
   - La hora pico real es `12h`
2. Check 5. Análisis contrafáctico
   - Fallan solo los agregados finales del efecto neto
   - Los 9 días individuales coinciden
   - El `+2%` neto no se reproduce; el valor calculado es `-0.17%`

## Resultado final

- Checks OK: `3`
- Checks FALLO: `2`

Conclusión:

- La mayor parte de los números auditables del análisis son correctos.
- Las discrepancias relevantes son dos:
  - la interpretación de la hora pico diaria
  - el efecto neto agregado en días normales, que no resiste el recálculo con valores exactos

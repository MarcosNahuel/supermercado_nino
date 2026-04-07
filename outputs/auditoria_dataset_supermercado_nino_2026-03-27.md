# Auditoria de Datos - Supermercado Nino (2026-03-27)

## Scorecard

- Puntaje global: **81.1/100**
- Estados: **{'OK': 31, 'REVISAR': 11, 'ERROR': 3}**

## Codigo Python utilizado

- Script reproducible: [D:\OneDrive\GitHub\supermercado_nino definitivo claude\scripts\auditoria_dataset_supermercado_nino.py](D:\OneDrive\GitHub\supermercado_nino definitivo claude\scripts\auditoria_dataset_supermercado_nino.py)
- Carga base con pandas: `pd.read_parquet(...)` y `pd.read_csv(...)`
- Las verificaciones estan encapsuladas en las funciones `audit_integrity`, `audit_margins`, `audit_pasteleria`, `audit_rotiseria`, `audit_cross_checks`, `audit_anomalies` y `audit_text_quality`.

## 1. INTEGRIDAD DE DATOS

- Check Ventas totales del detalle: [~ $9,550,000,000.00] vs [$9,550,165,077.18] -> **OK**
- Check Tickets distintos en detalle_lineas: [345,130] vs [345,130] -> **OK**
- Check Cruce tickets.parquet vs sum(detalle_lineas) por ticket: [0 tickets con diferencias materiales] vs [0 tickets con diff > $0.05 o faltantes] -> **OK**
  Detalle: Max diff ventas: $0.00
- Check Tickets negativos, cero o > $500K: [0 / 0 / 0] vs [88 negativos, 449 en cero, 309 > $500K] -> **REVISAR**
- Check Cantidades negativas o precio_unitario = 0: [0 / 0] vs [20328 lineas con cantidad negativa, 5321 con precio 0] -> **REVISAR**
- Check Rango de fechas del detalle: [2024-10-01 a 2025-12-31] vs [2024-10-01 a 2025-12-31 | 0 fuera de rango] -> **OK**
- Check Meses marcados como incompletos: [Solo 2025-10 y 2025-11 con flag] vs [Meses con flag: 2025-10, 2025-11] -> **OK**
  Detalle: Faltantes: ninguno | Inesperados: ninguno
- Check Integridad del campo hora en detalle_lineas: [Valores horarios reales distribuidos en 0-23] vs [hora unica = [0]] -> **ERROR**
  Causa raiz: El ETL cargo el campo hora en cero para todas las lineas; cualquier analisis horario derivado queda invalidado.
- Check Snapshot alcance_dataset vs conteos base: [n_tickets=345,130 y n_registros=3,334,045] vs [n_tickets=345,130, n_registros=3,334,045] -> **OK**

## 2. CONSISTENCIA DE MARGENES

- Check Formula margen_linea = importe_total * rentabilidad_pct / 100: [0 lineas fuera de tolerancia de $0.01] vs [3306662 lineas fuera de tolerancia] -> **ERROR**
  Detalle: Max diff: $169,981,184,087.50
  Causa raiz: La columna `rentabilidad_pct` esta sobrescrita con el valor absoluto de `margen_linea` en la mayoria de las filas; por eso la formula falla aunque el margen real este bien calculado.
- Check Formula margen_linea = importe_total * rentabilidad_factor: [0 lineas fuera de tolerancia de $0.01] vs [0 lineas fuera de tolerancia] -> **OK**
- Check rentabilidad_factor por categoria vs RENTABILIDAD.csv: [Todas las categorias operativas matchean contra la referencia] vs [46 categorias consistentes, 0 inconsistentes, 2 sin match en referencia] -> **REVISAR**
  Detalle: Categorias solo en referencia: 0
  Causa raiz: Las categorias sin referencia son `SIN CATEGORIA` y `VENTAS DE UVA`; el resto matchea contra la fuente de verdad.
- Check Categorias de "Elaboracion Propia" al 30%: [Todas al 30%] vs [9 OK, 0 fuera de 30%] -> **OK**
- Check Productos con margen_pct agregado <= 0: [0, salvo ajustes/impuestos reales] vs [4 productos] -> **OK**
  Causa raiz: Los productos no positivos corresponden al departamento fiscal IVA RED IB GRAL, con rentabilidad 0% en la fuente de verdad; parece ser dato operativo, no error de margen.
- Check Rentabilidad global desde detalle_lineas: [28.23%] vs [28.23%] -> **OK**

## 3. PARETO PASTELERIA

- Check Ventas totales de Reposteria y Pasteleria: [~ $93.8M] vs [$93,793,761.46] -> **OK**
- Check Cantidad de productos en la categoria: [49] vs [49] -> **OK**
- Check Productos necesarios para cubrir el 80% de ventas: [13] vs [14] -> **REVISAR**
  Causa raiz: Con 13 productos el acumulado queda en 78.15%; el producto 14 eleva la cobertura a 80.69%.
- Check Producto #1 y participacion: [TORTA BIZCOCHUELO NINO con ~31%] vs [TORTA BIZCOCHUELO NINO con 30.86%] -> **OK**
- Check Participacion Top 3 (Bizcochuelo + Cheesecake + Tarta Mix): [42% a 43%] vs [42.36%] -> **OK**
- Check Segmento C: cantidad de productos y aporte de ventas: [25 productos y ~5%] vs [25 productos y 5.24%] -> **OK**
- Check participacion_acumulada monotona creciente: [True] vs [True] -> **OK**

## 4. PARETO ROTISERIA

- Check Ventas totales de Rotiseria: [~ $129.9M] vs [$129,873,557.80] -> **OK**
- Check SKUs y familias: [64 SKUs y 38 familias] vs [64 SKUs y 38 familias] -> **OK**
- Check Ventas familia EMPANADA CARNE: [~ $34,700,000.00] vs [$34,678,609.90] -> **OK**
- Check Ventas familia EMPANADA J&Q: [~ $9,400,000.00] vs [$9,414,500.00] -> **OK**
- Check Ventas familia MIGA TRIPLE: [~ $7,300,000.00] vs [$7,280,830.00] -> **OK**
- Check Ventas familia EMPANADA CEBOLLA/QUESO: [~ $2,500,000.00] vs [$2,544,700.00] -> **OK**
- Check Empanadas como share del departamento: [~50%] vs [49.85%] -> **OK**
- Check Ranking individual de MATAMBRE NINO: [#2 con ~ $18M] vs [#2 con $18,084,116.50] -> **OK**
- Check Familias necesarias para cubrir 80%: [13] vs [14] -> **REVISAR**
  Causa raiz: Con 13 familias el acumulado queda en 78.36%; la familia 14 lleva el acumulado a 80.51%.

## 5. CROSS-CHECKS ENTRE DATASETS

- Check kpi_categoria mensual vs detalle_lineas mensual: [0 meses con diff > $0.05] vs [0 meses con diff > $0.05] -> **OK**
- Check Sum(ventas) pareto_prod_global vs detalle_lineas: [$9,550,165,077.18] vs [$9,550,165,077.18] -> **OK**
- Check Top 10 productos en pareto vs calculo directo desde detalle: [Misma lista y mismo orden] vs [Coinciden] -> **OK**
- Check alcance_dataset.ventas_total vs sum(tickets.ventas_totales): [$9,550,165,077.18] vs [$9,550,165,077.18] -> **OK**
- Check kpi_hora vs detalle_lineas: [$9,550,165,077.18] vs [$700,000.00 y 14 filas horarias] -> **ERROR**
  Causa raiz: kpi_hora contiene valores placeholder (100 tickets y $50,000 por hora) y no refleja el dataset real.

## 6. ANOMALIAS Y OUTLIERS

- Check Dias con ventas fuera de +/-3 desvios estandar: [Idealmente 0 o pocos dias explicables] vs [7 dias] -> **REVISAR**
- Check Productos con una sola transaccion y venta >= $100K: [0] vs [8] -> **REVISAR**
- Check Concentracion de medios de pago: [Sin un medio dominante > 60%] vs [Top share: EFECTIVO con 43.87%] -> **OK**
- Check Tickets duplicados (mismo ticket_id, fecha y monto): [0] vs [0] -> **OK**
- Check Categorias con menos de 10 transacciones: [0 o muy pocas justificadas] vs [3] -> **REVISAR**

## 7. CALIDAD DE DATOS TEXTUALES

- Check Descripciones repetidas con distinto producto_id: [0] vs [1924 descripciones] -> **REVISAR**
  Causa raiz: La diferencia entre 10,772 product_id unicos y 9,058 descripciones unicas surge de este colapso semantico: el pareto consolida por descripcion, no por codigo.
- Check Categorias con nombres similares potencialmente consolidables: [Revision manual de candidatos] vs [6] -> **REVISAR**
- Check Descripciones vacias o literales "NAN"/"NULL": [0] vs [0] -> **OK**
- Check Valores textuales con typo en tipo_medio_pago ("VITUAL"): [0] vs [446,665] -> **REVISAR**

## Hallazgos criticos

- [1. INTEGRIDAD DE DATOS] Integridad del campo hora en detalle_lineas -> **ERROR**. El ETL cargo el campo hora en cero para todas las lineas; cualquier analisis horario derivado queda invalidado.
- [2. CONSISTENCIA DE MARGENES] Formula margen_linea = importe_total * rentabilidad_pct / 100 -> **ERROR**. La columna `rentabilidad_pct` esta sobrescrita con el valor absoluto de `margen_linea` en la mayoria de las filas; por eso la formula falla aunque el margen real este bien calculado.
- [2. CONSISTENCIA DE MARGENES] rentabilidad_factor por categoria vs RENTABILIDAD.csv -> **REVISAR**. Las categorias sin referencia son `SIN CATEGORIA` y `VENTAS DE UVA`; el resto matchea contra la fuente de verdad.
- [3. PARETO PASTELERIA] Productos necesarios para cubrir el 80% de ventas -> **REVISAR**. Con 13 productos el acumulado queda en 78.15%; el producto 14 eleva la cobertura a 80.69%.
- [4. PARETO ROTISERIA] Familias necesarias para cubrir 80% -> **REVISAR**. Con 13 familias el acumulado queda en 78.36%; la familia 14 lleva el acumulado a 80.51%.
- [5. CROSS-CHECKS ENTRE DATASETS] kpi_hora vs detalle_lineas -> **ERROR**. kpi_hora contiene valores placeholder (100 tickets y $50,000 por hora) y no refleja el dataset real.
- [7. CALIDAD DE DATOS TEXTUALES] Descripciones repetidas con distinto producto_id -> **REVISAR**. La diferencia entre 10,772 product_id unicos y 9,058 descripciones unicas surge de este colapso semantico: el pareto consolida por descripcion, no por codigo.

## Evidencia principal

### Top tickets > $500K

| ticket_id          | fecha               |   ventas_totales |   margen_total |   unidades_totales |   productos_unicos |
|:-------------------|:--------------------|-----------------:|---------------:|-------------------:|-------------------:|
| PR  0028-00003247  | 2025-07-28 00:00:00 |      3.29467e+07 |    9.93237e+06 |               5706 |                 18 |
| PR  0028-00003245  | 2025-07-24 00:00:00 |      2.90137e+07 |    8.83113e+06 |               5556 |                 18 |
| PR  0028-00003406  | 2025-12-10 00:00:00 |      7.74594e+06 |    2.17335e+06 |               2270 |                 14 |
| PR  0028-00002970  | 2025-02-24 00:00:00 |      7.66123e+06 |    2.14514e+06 |               3660 |                  1 |
| PR  0028-00003317  | 2025-10-02 00:00:00 |      5.9359e+06  |    1.66205e+06 |                989 |                 10 |
| FC A 0028-00000059 | 2025-10-02 00:00:00 |      5.8416e+06  |    1.63565e+06 |                989 |                 10 |
| FC A 0028-00000060 | 2025-10-02 00:00:00 |      5.8416e+06  |    1.63565e+06 |                989 |                 10 |
| PR  0028-00003320  | 2025-10-07 00:00:00 |      5.1351e+06  |    1.43783e+06 |               1250 |                 11 |
| PR  0028-00003124  | 2025-04-28 00:00:00 |      4.96871e+06 |    1.41364e+06 |               1560 |                 13 |
| FC A 0028-00000058 | 2025-05-20 00:00:00 |      4.96871e+06 |    1.41364e+06 |               1560 |                 13 |

### Meses con ratio de mes_incompleto

| periodo   |   mes_incompleto |   mes_incompleto_pct |
|:----------|-----------------:|---------------------:|
| 2024-10   |                0 |                    0 |
| 2024-11   |                0 |                    0 |
| 2024-12   |                0 |                    0 |
| 2025-01   |                0 |                    0 |
| 2025-02   |                0 |                    0 |
| 2025-03   |                0 |                    0 |
| 2025-04   |                0 |                    0 |
| 2025-05   |                0 |                    0 |
| 2025-06   |                0 |                    0 |
| 2025-07   |                0 |                    0 |

### Margenes no positivos

| categoria       | descripcion                 |           ventas |   margen |   unidades |   tickets |   n_product_ids |   margen_pct_calc |
|:----------------|:----------------------------|-----------------:|---------:|-----------:|----------:|----------------:|------------------:|
| IVA RED IB GRAL | PHILIPS LAMPARA LED 12 W LF |      2.29274e+06 |        0 |       1323 |       908 |               1 |                 0 |
| IVA RED IB GRAL | PHILIPS LAMPARA LED 12 W LC |      1.0591e+06  |        0 |        610 |       436 |               1 |                 0 |
| IVA RED IB GRAL | PHILIPS LED LUZ FRIA 10.5 W | 140800           |        0 |         96 |        59 |               1 |                 0 |
| IVA RED IB GRAL | LAMPARA PHILIPS LED 13 W LC |   6609           |        0 |          6 |         2 |               1 |                 0 |

### Pasteleria top 20

| descripcion              |      ventas |           margen |   unidades | categoria               |   margen_pct |   participacion |   participacion_acumulada | segmento_pareto   |   participacion_categoria_pct |   participacion_categoria_acum_pct |
|:-------------------------|------------:|-----------------:|-----------:|:------------------------|-------------:|----------------:|--------------------------:|:------------------|------------------------------:|-----------------------------------:|
| TORTA BIZCOCHUELO NINO   | 2.89453e+07 |      8.68359e+06 |   1540.56  | REPOSTERIA Y PASTELERIA |           30 |     0.00303087  |                  0.28924  | A                 |                      30.8606  |                            30.8606 |
| CHEESECAKE NINO          | 5.56797e+06 |      1.67039e+06 |    229.6   | REPOSTERIA Y PASTELERIA |           30 |     0.000583024 |                  0.539687 | A                 |                       5.9364  |                            36.797  |
| TARTA MIX NINO           | 5.21517e+06 |      1.56455e+06 |    358.245 | REPOSTERIA Y PASTELERIA |           30 |     0.000546082 |                  0.554352 | A                 |                       5.56026 |                            42.3572 |
| BUDIN NINO X 200 GRS     | 5.0241e+06  |      1.50723e+06 |   1863     | REPOSTERIA Y PASTELERIA |           30 |     0.000526075 |                  0.562406 | A                 |                       5.35654 |                            47.7138 |
| CHOCOTORTA NINO          | 3.88566e+06 |      1.1657e+06  |    193.595 | REPOSTERIA Y PASTELERIA |           30 |     0.000406868 |                  0.604902 | A                 |                       4.14277 |                            51.8565 |
| TARTA CABSHA NINO        | 3.71465e+06 |      1.11439e+06 |    256.305 | REPOSTERIA Y PASTELERIA |           30 |     0.000388961 |                  0.610892 | A                 |                       3.96044 |                            55.817  |
| MASAS SECAS NINO         | 3.49166e+06 |      1.0475e+06  |     29.91  | REPOSTERIA Y PASTELERIA |           30 |     0.000365612 |                  0.622219 | A                 |                       3.72269 |                            59.5397 |
| TORTA SELVA NEGRA NINO   | 3.38467e+06 |      1.0154e+06  |    178.125 | REPOSTERIA Y PASTELERIA |           30 |     0.000354409 |                  0.62725  | A                 |                       3.60863 |                            63.1483 |
| ALFAJORCITO MAIZENA NINO | 3.29108e+06 | 987325           |     21.715 | REPOSTERIA Y PASTELERIA |           30 |     0.00034461  |                  0.632484 | A                 |                       3.50885 |                            66.6572 |
| PANETTONE NINO           | 2.95799e+06 | 887398           |     84.99  | REPOSTERIA Y PASTELERIA |           30 |     0.000309732 |                  0.6515   | A                 |                       3.15372 |                            69.8109 |

### Rotiseria top familias

| familia                       |      ventas |           margen |   unidades |   variantes |   participacion_pct |   participacion_acum_pct |
|:------------------------------|------------:|-----------------:|-----------:|------------:|--------------------:|-------------------------:|
| EMPANADA CARNE                | 3.46786e+07 |      1.04036e+07 |   6041     |           4 |            26.7018  |                  26.7018 |
| MATAMBRE NINO                 | 1.80841e+07 |      5.42523e+06 |    168.77  |           1 |            13.9244  |                  40.6262 |
| EMPANADA J&Q                  | 9.4145e+06  |      2.82435e+06 |   1970     |           4 |             7.24897 |                  47.8752 |
| MIGA TRIPLE                   | 7.28083e+06 |      2.18425e+06 |   1003     |           4 |             5.60609 |                  53.4813 |
| EMPANADA POLLO                | 6.29285e+06 |      1.88786e+06 |   1494     |           4 |             4.84537 |                  58.3267 |
| LENGUA A LA VINAGRETA NINO    | 3.77896e+06 |      1.13369e+06 |     21.45  |           1 |             2.90972 |                  61.2364 |
| EMPANADA HUMITA               | 3.65535e+06 |      1.0966e+06  |    862     |           3 |             2.81455 |                  64.0509 |
| EMPANADA VERDURA              | 3.51805e+06 |      1.05542e+06 |    848     |           3 |             2.70883 |                  66.7597 |
| EMPANADA CAPRESE              | 3.128e+06   | 938400           |    757     |           3 |             2.4085  |                  69.1682 |
| PERNIL DE CERDO HORNEADO NINO | 3.10824e+06 | 932473           |     38.785 |           1 |             2.39328 |                  71.5615 |

### Top 10 directo

| descripcion             |      ventas |
|:------------------------|------------:|
| MOLIDA ESPECIAL         | 1.88009e+08 |
| COSTILLA ARQUEADA       | 1.56007e+08 |
| MOLIDA INTERMEDIA       | 1.40415e+08 |
| MUSLO DE POLLO          | 1.26049e+08 |
| FILET / LOMO            | 1.15319e+08 |
| POLLO AVICOLA LUJAN     | 1.06437e+08 |
| SUPREMA DE POLLO        | 9.68318e+07 |
| MILANESAS DE POLLO NINO | 9.45034e+07 |
| VACIO                   | 8.96262e+07 |
| TORTAS X 6U.            | 7.21374e+07 |

### Top 10 pareto

| descripcion             |      ventas |
|:------------------------|------------:|
| MOLIDA ESPECIAL         | 1.88009e+08 |
| COSTILLA ARQUEADA       | 1.56007e+08 |
| MOLIDA INTERMEDIA       | 1.40415e+08 |
| MUSLO DE POLLO          | 1.26049e+08 |
| FILET / LOMO            | 1.15319e+08 |
| POLLO AVICOLA LUJAN     | 1.06437e+08 |
| SUPREMA DE POLLO        | 9.68318e+07 |
| MILANESAS DE POLLO NINO | 9.45034e+07 |
| VACIO                   | 8.96262e+07 |
| TORTAS X 6U.            | 7.21374e+07 |

### Dias outliers

| fecha               |      ventas |   zscore |
|:--------------------|------------:|---------:|
| 2025-12-23 00:00:00 | 7.08587e+07 |  5.70787 |
| 2025-12-30 00:00:00 | 6.82199e+07 |  5.39487 |
| 2025-12-22 00:00:00 | 5.66576e+07 |  4.02338 |
| 2024-12-23 00:00:00 | 5.64203e+07 |  3.99523 |
| 2025-07-28 00:00:00 | 5.5166e+07  |  3.84645 |
| 2025-07-24 00:00:00 | 5.44468e+07 |  3.76115 |
| 2024-12-30 00:00:00 | 5.15131e+07 |  3.41315 |

### Distribucion medios de pago

| tipo_medio_pago    |   importe_total |   share_pct |
|:-------------------|----------------:|------------:|
| EFECTIVO           |     4.1898e+09  |     43.8715 |
| TARJETA DE DÉBITO  |     2.24877e+09 |     23.5469 |
| TARJETA DE CRÉDITO |     1.88002e+09 |     19.6857 |
| BILLETERA VITUAL   |     1.23158e+09 |     12.8959 |

### Descripciones duplicadas

| descripcion_norm                         |   n_product_ids |
|:-----------------------------------------|----------------:|
| DOS HERMANOS SNACKS S/T X80G             |              10 |
| PORTOFINO CORTINA DE BAÑO TELA ESTAMPADA |              10 |
| CHOCOARROZ 2 X 22 GR S/T                 |               9 |
| TOALLA ROSTRO FANTASIA 41X70             |               8 |
| CEREAL MIX 28 GR X 3 UNIDADES            |               7 |
| VARITAS DE INCIENSO PREMIUM X 20 U       |               7 |
| CUADERNO TRIUNFANTE ESCOLAR 50H          |               7 |
| BARRA DE CEREAL FELFORT X3U              |               7 |
| GRANIX BOCADITOS X 180 GRS               |               6 |
| SET/TOALLA Y TOALLON ARCO IRIS 500GR     |               6 |

### Categorias similares

| categoria_1         | categoria_2              |   similaridad |
|:--------------------|:-------------------------|--------------:|
| CONGELADOS AL 10.5% | CONGELADOS AL 21%        |         0.857 |
| CARNICERIA          | CARNICERIA AL 10,5 %     |         0.8   |
| CARNICERIA          | ELABORADOS DE CARNICERIA |         0.645 |
| PAN                 | PAN PARA REVENTA         |         0.429 |
| PAN                 | PANAD.ELAB.PROPIA        |         0.3   |
| PAN                 | PANIFIC.Y MASAS FRESCAS  |         0.25  |

## Recomendaciones

- Corregir el ETL del campo `hora` y regenerar `kpi_hora.parquet`; hoy el analisis horario no es confiable.
- Alinear la definicion de SKU entre datasets: `producto_id` (10,772) vs descripcion consolidada (9,058).
- Revisar la politica de `mes_incompleto`; si la regla esperada es Oct/Nov 2025, validar que no se este aplicando de forma parcial o heredada.
- Documentar explicitamente que `pareto_prod_global.participacion` y `participacion_acumulada` son globales, no por categoria.
- Corregir typos textuales como `BILLETERA VITUAL` para evitar segmentaciones duplicadas en reporting.
- Revisar manualmente tickets > $500K, productos con una sola transaccion >= $100K y descripciones repetidas con multiples codigos.

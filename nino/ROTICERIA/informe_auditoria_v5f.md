INFORME DE AUDITORIA - ESTRUCTURA DE COSTOS ROTISERIA NINO v5f

Fecha: 2026-03-22
Auditor: Codex (asistido por IA)
Alcance: Verificacion integral del Excel de 8 hojas, del script `generar_excel_costos.py`, del parquet `detalle_lineas.parquet` y de la ventana POS externa referida por el script.

## 1. OPINION

**FAVORABLE CON SALVEDADES**

La estructura central del modelo es consistente: las ventas mensuales desestacionalizadas, el CMV al 70%, el margen bruto al 30%, el mix de medios de pago, IIBB, ICH, costo financiero, costos fijos y el resultado final concilian entre el script, el parquet POS y las formulas del Excel. Las principales salvedades no invalidan el resultado base, pero si afectan la calidad formal y la trazabilidad del archivo: (i) la hoja mensual de medios de pago subexpone billeteras en enero-marzo 2026, (ii) la memoria cita incorrectamente el articulo del Codigo Fiscal de Mendoza para excluir IVA de la base de IIBB, (iii) el script depende de 4 Excels externos en `H:` para la ventana de 31 dias, y (iv) la liquidacion de presentismo adopta una base mas restrictiva que la indicada por la circular de escalas FAECYS diciembre 2025-abril 2026.

## 2. HALLAZGOS CRITICOS

| # | Hallazgo | Hoja | Celda | Valor actual | Valor correcto | Impacto ($) |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | El presentismo se calcula solo sobre el remunerativo. La circular FAECYS de escalas diciembre 2025-abril 2026 indica que el Art. 40 incrementa cifras remunerativas y no remunerativas. | Estructura Costos | B39 | -350.388 | -375.387 min. | -24.999/mes min. sobre resultado |

Nota: el impacto informado es minimo, asumiendo que el adicional sobre suma no remunerativa conserva caracter no remunerativo. Si la empresa decide otro criterio para SAC u otros derivados, el impacto puede ser mayor.

## 3. HALLAZGOS MENORES

| # | Hallazgo | Severidad | Recomendacion |
| --- | --- | --- | --- |
| 1 | La exclusion del IVA de la base de IIBB esta bien calculada, pero la fuente citada como Art. 169 del Codigo Fiscal Mendoza 2026 es incorrecta; corresponde Art. 173 inc. 1. | Media | Corregir citas en `Estructura Costos`, `Simulador` y `Memoria de Calculo`. |
| 2 | La hoja `Ventas Mensuales` informa billetera en $0 para enero, febrero y marzo 2026 por coexistencia de etiquetas `BILLETERA VITUAL` y `BILLETERA VIRTUAL`. | Alta | Normalizar `tipo_medio_pago` antes de agrupar o sumar ambas variantes tambien en la hoja mensual. |
| 3 | La hoja `Sensibilizacion` no responde al set pedido de escenarios con margenes 25%, 30%, 35% y merma 3%, 5%, 8%; usa 25/28/30/33/35 y 8/6/5/3/2. | Media | Rehacer la hoja como matriz 3x3 o, como minimo, incluir esos 9 cruces. |
| 4 | La ventana de ventas de 31 dias es reproducible en esta maquina, pero depende de 4 Excels externos en `H:` y no de insumos versionados en el repo. | Alta | Versionar snapshot de esos archivos o derivar la ventana desde el parquet consolidado. |

## 4. VERIFICACION PUNTO POR PUNTO

### 4.1 Parametros Laborales

- Sueldo basico: **OK** - La circular de escalas FAECYS diciembre 2025-abril 2026, categoria Auxiliar Especializado A, fija para marzo 2026 un basico remunerativo de **$1.080.274**.
- Sueldo no remunerativo: **OK** - El acuerdo paritario del 05/12/2025 mantiene **$40.000 + $60.000 = $100.000** no remunerativos durante enero-marzo 2026, incorporandolos al basico en abril 2026.
- Contribuciones patronales 29,74%: **OK** - El Excel aplica la tasa solo sobre `B28` remunerativo, no sobre el no remunerativo.
- Presentismo 8,33%: **ERROR** - El modelo lo calcula sobre remunerativo y agrega CP, pero la circular de escalas indica que el Art. 40 incrementa cifras remunerativas y no remunerativas. Impacto minimo detectado: **$24.999/mes**.
- SAC base 1/12: **OK CON SALVEDAD** - La formula del modelo es consistente con el criterio adoptado: remunerativo + presentismo + cargas sobre ambos. Si se corrige la base de presentismo, debe revisarse la provision.
- Vacaciones: **OK** - Aplica 14 dias corridos, divisor 25 y contribuciones patronales. Formula del script y exposicion del Excel coinciden.

### 4.2 Ventas y Desestacionalizacion

- Ventana de datos: **OK** - La ventana es **16/02/2026 a 18/03/2026**, con **31 dias** y **$11.369.307** de ventas brutas.
- Indice estacional con meses completos 2025: **OK** - El script excluye `mes_incompleto=True`, por lo que no toma octubre ni noviembre 2025.
- Marzo 2026 incompleto fuera de promedios: **OK** - Marzo 2026 se excluye del calculo estacional y del promedio mensual historico.
- Formula de ventas mensuales `V`: **OK** - `V = (11.369.307 / 31) x 30,4167 / 1,0095 = 11.050.346`.
- V incluye IVA: **OK** - El parquet normalizado muestra **97,97%** de comprobantes `FB`; por lo tanto, tratar `V` como facturacion bruta con IVA es consistente.

### 4.3 CMV y Margen

- Margen bruto 30%: **OK** - Las **31.486** lineas de `ROTISERIA` del parquet tienen `rentabilidad_factor = 0.30`.
- CMV = V x 0,70: **OK** - `CMV = 11.050.346 x 0,70 = 7.735.242`.
- Formulas Excel: **OK** - En `Estructura Costos`, `B14` es `=-B6*0.70` y `B21` es `=B6+B14`.

### 4.4 Impuestos y Tasas

- IIBB Mendoza 3% sobre V sin IVA: **OK CON SALVEDAD** - La formula `=ROUND(-B6/1.21*0.03,0)` es correcta. La cita normativa a **Art. 169** es incorrecta; corresponde **Art. 173 inc. 1** del Codigo Fiscal Mendoza 2026.
- ICH 1,2% solo sobre bancarizado: **OK** - La hoja `Comisiones Financieras` calcula base imponible como `Ventas - Efectivo` y luego aplica `0,012`.
- Mix tarjetas vs POS real: **OK** - Meses completos dic/2025-feb/2026: Efectivo **47,07%**, Debito **32,71%**, Credito **9,64%**, Billetera **10,58%**.
- Costo financiero: **OK** - La formula por canal es correcta: `V x mix x TNA x dias / 365`.
- Exposicion mensual del mix: **ERROR DE EXPOSICION** - En `Ventas Mensuales`, `I19`, `I20` e `I21` muestran `0` y deberian mostrar **1.877.529**, **1.824.484** y **1.542.596** respectivamente. No afecta el calculo central porque el mix principal si suma ambas variantes ortograficas de billetera.

### 4.5 Servicios

- Gas: **OK (ESTIMADO)** - Se usa Ecogas Cuyana SGP P1-P2, factor 1,315 y consumo de 250 m3. El monto es razonable para una rotiseria chica/mediana. No hay factura ni cuadro tarifario adjunto en el repo para recalculo documental independiente.
- Electricidad: **OK (ESTIMADO)** - Se usa EDEMSA T1-G, factor 1,39 y consumo de 500 kWh. El supuesto es razonable para vitrina, heladera, campana e iluminacion.
- Consumos estimados: **OK** - 250 m3 de gas y 500 kWh resultan plausibles para la operacion descripta.

### 4.6 Formulas Excel

- Subtotales en `Estructura Costos`: **OK** - Los principales subtotales son sumas de componentes (`B30`, `B41`, `B50`, `B60`, `B62`, `B75`, `B86`, `B95`).
- `Comisiones Financieras` parametrica: **OK** - Comisiones y costo financiero referencian el Bloque 2 editable (`B16:B20`).
- Toggles SI/NO en `Simulador`: **OK** - Todas las filas auditadas cumplen `=IF(Bx="SI",Cx,0)`.
- Recalculo del simulador: **OK** - Las dependencias de formulas cubren ventas, margen, CP, servicios, impuestos y resultado.
- Resultado = MB - CF - CV: **OK** - `C63 = C60 - C61 - C62`.
- PE y Cobertura: **OK** - En simulador `C65 = IF(B11-D54/B10>0,D43/(B11-D54/B10),0)` y `C67 = C66/C65`. En la hoja principal el signo negativo esta resuelto por convencion de costos negativos.
- Referencias cruzadas Estructura -> Comisiones: **OK** - `B67:B70`, `B74` y `B81:B84` apuntan a la hoja `Comisiones Financieras`.
- Cache de formulas: **OK CON SALVEDAD** - El archivo no guarda valores cacheados legibles por `openpyxl`, pero esta configurado con `fullCalcOnLoad=True`, por lo que Excel recalcula al abrir.

### 4.7 Otros Fijos

- Alquiler: **OK** - No se detecta alquiler en el Excel ni en el script.
- Amortizacion de equipos: **OK** - No se detecta amortizacion de equipos.
- Mantenimiento $30.000: **OK** - Esta incluido en `B54`.
- Descartables, seguros, indumentaria, agua: **OK (ESTIMADOS)** - Los montos son razonables y estan explicitados como estimados/ajustables.
- Habilitaciones bromatologica y municipal: **OK** - Se exponen como mensualizaciones (`anual / 12` y `tasa comercio / 12`).

### 4.8 Sensibilizacion

- Escenarios 25%/30%/35% y merma 3%/5%/8%: **ERROR** - La hoja no contiene ese set; usa 5 escenarios propios (25/8, 28/6, 30/5, 33/3, 35/2).
- Consistencia de calculos: **OK** - Para los escenarios efectivamente cargados, los resultados son consistentes con la formula base del script.

### 4.9 Memoria de Calculo

- Formula demostrada vs script: **OK** - La memoria replica los mismos numeros y formulas del script.
- Fuentes normativas: **ERROR PARCIAL** - El caso mas claro es IIBB: se cita Art. 169 y corresponde Art. 173 inc. 1 del Codigo Fiscal Mendoza 2026. Tambien falta explicitar el alcance del Art. 40 sobre sumas no remunerativas.
- Conceptos relevantes: **OK CON SALVEDAD** - No faltan rubros centrales, pero deberia explicitarse que la venta de 31 dias proviene de Excels externos al repo y que existe dualidad `BILLETERA VITUAL`/`BILLETERA VIRTUAL`.

## 5. RESUMEN NUMERICO VERIFICADO

| Concepto | Valor script | Valor Excel | Match? |
| --- | ---: | ---: | --- |
| Ventas (V) | 11.050.346 | 11.050.346 | Si |
| CMV | -7.735.242 | -7.735.242 | Si |
| Margen Bruto | 3.315.104 | 3.315.104 | Si |
| Laboral | -5.432.333 | -5.432.333 | Si |
| Servicios | -306.446 | -306.446 | Si |
| Otros Fijos | -185.000 | -185.000 | Si |
| Total CF | -5.923.779 | -5.923.779 | Si |
| Comisiones | -92.880 | -92.880 | Si |
| IIBB | -273.976 | -273.976 | Si |
| ICH | -70.193 | -70.193 | Si |
| Merma | -552.517 | -552.517 | Si |
| Costo Fin | -35.466 | -35.466 | Si |
| Total CV | -1.025.032 | -1.025.032 | Si |
| RESULTADO | -3.633.707 | -3.633.707 | Si |
| PE | 28.584.173 | 28.584.173 | Si |

Nota metodologica: en celdas con formula, el match se verifico por inspeccion de formula y conciliacion de dependencias, ya que `openpyxl` no lee cache numerica del archivo para esas celdas.

## 6. RECOMENDACIONES

1. Corregir el criterio de presentismo o, como minimo, documentar expresamente por que se excluye la suma no remunerativa pese a la circular de escalas.
2. Corregir todas las referencias a `Art. 169` por `Art. 173 inc. 1` en IIBB Mendoza.
3. Normalizar `tipo_medio_pago` antes de agrupar (`BILLETERA VITUAL` vs `BILLETERA VIRTUAL`) para que la hoja `Ventas Mensuales` no subexponga billeteras.
4. Versionar o encapsular dentro del repo los 4 Excels usados para la ventana reciente, o reemplazarlos por una fuente consolidada interna.
5. Redisenar `Sensibilizacion` para incluir la matriz pedida de 25%/30%/35% x 3%/5%/8%.

## 7. CONCLUSION

El Excel auditado presenta una base tecnica solida y, en su nucleo, esta bien conciliado con el script y con los datos POS: la venta mensual, el margen, los costos fijos, los costos variables, el resultado y el punto de equilibrio estan correctamente calculados bajo los supuestos hoy cargados. La opinion favorable queda condicionada a las salvedades expuestas, en especial la definicion del presentismo frente a sumas no remunerativas, la correccion de la cita normativa de IIBB y la mejora de la trazabilidad del proceso para que el archivo quede plenamente reproducible y autosuficiente.

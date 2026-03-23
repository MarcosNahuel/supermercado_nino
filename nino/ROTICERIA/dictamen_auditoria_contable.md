# DICTAMEN DE AUDITORIA CONTABLE
## Estructura de Costos - Rotiseria NINO (BOSIN S.A.)
### Lujan de Cuyo, Mendoza | Marzo 2026

---

**Archivo auditado:** `Estructura_Costos_Rotiseria_NINO.xlsx` (5 hojas)
**Script generador:** `generar_excel_costos.py`
**Fuentes de datos:** `detalle_lineas.parquet` (Oct 2024 - Dic 2025), Excel POS 2026
**Alcance:** Revision integral de supuestos, calculos, parametros impositivos y coherencia

---

## I. OPINION

La estructura de costos presenta una base metodologica razonable pero contiene **tres hallazgos de materialidad significativa** y **cinco observaciones de alcance moderado** que deben considerarse antes de utilizar el informe para toma de decisiones. La conclusion de deficit operativo (-$3.46M/mes) es cualitativamente correcta, pero la magnitud exacta esta sujeta a las incertidumbres descriptas.

---

## II. HALLAZGOS CRITICOS

### C1. Factor de costo uniforme 0.70: incorrecto — debe diferenciarse por rubro

**Materialidad: ALTA. Afecta costeo por receta y validacion del margen.**

El script aplica un factor unico de 0.70 (retail → costo) a todos los insumos. Sin embargo, el propio sistema POS del supermercado registra un `rentabilidad_factor` distinto por categoria:

| Categoria insumo | Rent. Factor POS | Costo real (1-RF) | Script usa | Error |
|---|---|---|---|---|
| **Carniceria** | 0.20 | **0.80** | 0.70 | **Subestima costo 14%** |
| **Pollo** | 0.20 | **0.80** | 0.70 | **Subestima costo 14%** |
| **Fiambreria** | 0.45 | **0.55** | 0.70 | **Sobreestima costo 27%** |
| Embutidos | 0.45 | 0.55 | 0.70 | Sobreestima costo 27% |
| Almacen | 0.28 | 0.72 | 0.70 | ~OK |
| Harinas | 0.28 | 0.72 | 0.70 | ~OK |
| Lacteos | 0.30 | 0.70 | 0.70 | OK |
| Panificacion | 0.30 | 0.70 | 0.70 | OK |
| Huevos frescos | 0.28 | 0.72 | 0.70 | ~OK |

**Impacto en margen ponderado:**

| Metodo | Margen ponderado | Diferencia |
|---|---|---|
| Factor uniforme 0.70 (actual) | 41.5% | Referencia |
| Factores diferenciados por rubro | 37.6% | -3.9pp |
| Parametro del sistema POS | 30.0% | -11.5pp |

Con factores diferenciados, el gap con el 30% del sistema se reduce de 11.5pp a 7.6pp. El gap residual se explica por: (a) rendimiento de coccion no contemplado en las recetas, (b) mermas de produccion, y (c) productos fuera de la muestra (14.1% de ventas).

**Conclusion:** El margen bruto del 30% utilizado en la estructura principal ES el dato correcto (proviene del parametro del sistema POS). La hoja de costeo por receta es orientativa pero no reemplaza el dato del sistema.

---

### C2. Mix de medios de pago desactualizado — comisiones sobreestimadas

**Materialidad: MODERADA-ALTA (~$20K/mes).**

El script usa el mix de medios de pago del **periodo completo** Oct 2024 - Dic 2025. El mix cambio significativamente:

| Medio | Historico (script) | Dic 2025 real | Diferencia |
|---|---|---|---|
| Efectivo | 39.5% | 47.2% | +7.7pp |
| Debito | 25.8% | 32.8% | +7.0pp |
| Credito | 22.7% | 20.0% | -2.7pp |
| **Billetera Virtual** | **12.1%** | **0.0%** | **-12.1pp** |

La billetera virtual desaparecio completamente del mix. Impacto en comisiones:

| Concepto | Script actual | Con mix Dic 2025 | Diferencia |
|---|---|---|---|
| Com. credito (3%) | $75,088 | $66,362 | -$8,726 |
| Com. debito (1.2%) | $34,190 | $43,534 | +$9,344 |
| Com. billetera (1.5%) | $20,049 | $0 | -$20,049 |
| **Total comisiones** | **$129,327** | **$109,896** | **-$19,431** |

El deficit real seria ~$19K/mes menor (-$3.437M en vez de -$3.456M).

**Recomendacion:** Usar mix de los ultimos 3 meses (Oct-Dic 2025) o, idealmente, de la ventana Feb-Mar 2026.

---

### C3. Tratamiento del IVA: incertidumbre sobre si V incluye o excluye IVA

**Materialidad: POTENCIALMENTE ALTA (si V incluye IVA, los costos fijos como % de ventas netas suben de 50% a 60%).**

El script trata V ($11,050,346) como "ventas netas sin IVA" y calcula V × 1.21 como "ventas brutas". Sin embargo:

1. El 97.8% de las ventas son **Factura B** (consumidor final), donde el precio exhibido INCLUYE IVA (Ley 24.240)
2. Las categorias del sistema nombran el IVA explicitamente ("CARNICERIA AL 10,5 %"), sugiriendo que los precios son IVA-incluido
3. No existe columna separada de IVA en los datos
4. El `rentabilidad_factor = 0.30` se aplica sobre el precio registrado; si ese precio incluye IVA, el margen real sobre neto seria diferente

**Escenarios:**

| Escenario | V neto | TF/V neto | Resultado |
|---|---|---|---|
| V es sin IVA (asumido) | $11,050,346 | 49.9% | -$3,456,249 |
| V es con IVA 21% | $9,132,517 | 60.4% | Recalcular integramente |

**Nota atenuante:** Si V incluye IVA y CMV = V × 0.70 tambien incluye IVA, los margenes PORCENTUALES son identicos. La distorsion afecta solo a los ratios donde intervienen costos fijos absolutos (laboral, servicios). El deficit en pesos absolutos cambiaria porque el CMV real (sin IVA) seria menor, pero el margen bruto en pesos tambien.

**Recomendacion:** Verificar con el sistema POS o con el contador si `importe_total` es neto o bruto de IVA. Es el supuesto mas critico del modelo.

---

## III. OBSERVACIONES DE ALCANCE MODERADO

### M1. Productos vendidos por peso: PVP en receta no refleja ingreso real por lote de produccion

El matambre, la lengua, el pernil y el arrollado se venden **por kilogramo** en el POS (cantidad registrada en fracciones de kg). Sin embargo, las recetas usan el precio/kg como si fuera el PVP por unidad de produccion.

Ejemplo MATAMBRE NINO:
- PVP en receta: $42,051 (= precio por kg de producto terminado)
- Costo receta: 1.8 kg matambre crudo → ~1.3 kg cocido (merma coccion ~28%)
- Ingreso real por lote: 1.3 kg × $42,051/kg = **$54,666**
- Margen real: ($54,666 - $25,914) / $54,666 = **52.6%** (no 38.4%)

Afecta 21.6% de las ventas (matambre 13.9%, lengua 2.9%, pernil 2.4%, arrollado 2.4%).

**Impacto en margen ponderado:** Incrementa el margen, lo que paradojicamente AGRANDA el gap con el 30% del sistema. Refuerza la conclusion de C1: la hoja de costeo por receta es orientativa, no precisa.

---

### M2. Desestacionalizacion contaminada por inflacion

El indice estacional se calcula con ventas **nominales** de 2025. Con inflacion anual del ~25-30%, los meses tardios del anio tienen ventas nominales mas altas por efecto precio, no solo por estacionalidad.

- Dic 2025 diario: $517K (indice 1.6034)
- Ene 2025 diario: $261K (indice 0.8102)

La relacion 517/261 = 1.98x incluye tanto estacionalidad (diciembre es temporada alta real) como ~25% de inflacion acumulada. El indice de diciembre esta "inflado" por la inflacion.

**Efecto:** El indice ponderado de la ventana Feb-Mar 2026 (1.0095) se usa para DIVIDIR las ventas reales. Si los indices estan inflados, el divisor seria mayor, subestimando las ventas desestacionalizadas.

**Magnitud estimada:** Efecto modesto (~2-4% sobre V) porque Feb y Mar tienen indices cercanos a 1.0. El efecto seria mayor si la ventana incluyera Dic o Ene.

---

### M3. Impuesto Debitos/Creditos: simplificacion razonable pero imprecisa

El script aplica ICH = V × 1.2% sobre el total de ventas. El impuesto grava movimientos bancarios (0.6% debito + 0.6% credito), no ventas directamente.

- Las ventas en **efectivo** (~47%) no generan debito bancario directo
- Pero los pagos a proveedores, empleados e impuestos generan debitos adicionales
- La simplificacion V × 1.2% captura ambos efectos de manera aproximada

**Resultado:** La sobreestimacion por aplicar sobre efectivo se compensa parcialmente con los debitos de gastos no contemplados. Error neto estimado < $15K/mes. No es critico.

---

### M4. Gas y electricidad: tarifas solo con IVA, faltan otros tributos

Las facturas de gas y electricidad en Mendoza incluyen, ademas de IVA 21%:

**Gas (Ecogas):**
- Impuesto Ley 27.200 (ex fondo fiduciario)
- Tasa municipal sobre factura
- Otros cargos regulatorios

**Electricidad (EDEMSA):**
- Tasa municipal
- Fondo provincial de energia
- Cargos por capacidad

El script calcula: (CF + CV) × 1.21. La factura real puede ser 15-25% mayor.

| Servicio | Script | Estimado real | Diferencia |
|---|---|---|---|
| Gas | $122,297 | ~$140,000-150,000 | +$18-28K |
| Electricidad | $151,065 | ~$170,000-185,000 | +$19-34K |
| **Total** | **$273,362** | **~$310-335K** | **+$37-62K** |

**Impacto:** Aumenta el deficit en $37-62K/mes. Moderado.

**Recomendacion:** Reemplazar con montos de facturas reales de Ecogas y EDEMSA.

---

### M5. Costos laborales: provisiones faltantes

El modelo no provisiona:

| Concepto | Estimacion mensual | Base normativa |
|---|---|---|
| Vacaciones (14 dias/anio sin antiguedad) | ~$155K | Art. 150 LCT, CCT 130/75 Art. 74 |
| Indemnizacion por despido (provision) | ~$300K (estimado) | Art. 245 LCT |
| Presentismo: no se aclara si esta en basico | Verificar | Art. 40 CCT 130/75 |

**Nota:** El presentismo del CCT 130/75 es un adicional del 8.33% sobre el basico de convenio. Si los $1,080,274 NO incluyen presentismo, el sueldo real seria ~$1,170,307 y el laboral subiria ~$324K/mes.

**Recomendacion:** Confirmar con RRHH si el basico incluye presentismo. Agregar provision de vacaciones.

---

## IV. OBSERVACIONES MENORES

### K1. Costeo milanesa de miga: perdida real mayor a la reportada

Con factores diferenciados, la milanesa de miga tiene margen **-69.5%** (costo $14,074 vs PVP $8,304). Cada docena vendida genera $5,770 de perdida. Con 2.6% de ventas (~$287K/mes), la perdida mensual en milanesas es ~$110K.

**Recomendacion urgente:** Subir PVP a minimo $15,000/docena para alcanzar margen positivo, o discontinuar el producto.

### K2. Diciembre distorsiona promedios historicos

Dic 2025: ticket promedio $12,160 vs promedio anual $7,910 (+54%). El mix de productos de diciembre (matambre, miga triple × 100 unidades) es atipico. Los promedios historicos de tickets y medios de pago estan sesgados por este mes.

### K3. Alquiler/amortizacion inmueble probablemente subvaluado

$150,000/mes (~USD 120 al tipo de cambio actual) por el 15% de un local comercial en Lujan de Cuyo es extremadamente bajo para marzo 2026. Verificar con el contrato de alquiler o valuacion fiscal del inmueble.

### K4. Falta Tasa de Seguridad e Higiene municipal

La estructura incluye "Habilitacion municipal" ($8K) pero no la **Tasa de Seguridad e Higiene** de la Municipalidad de Lujan de Cuyo, que se calcula como porcentaje de los ingresos brutos (tipicamente 0.5-1.5%). Sobre V = $11M, esto podria ser $55-165K/mes.

### K5. No se incluye costo de overhead administrativo

La rotiseria opera dentro de un supermercado. No se asigna costo por: administracion, contabilidad, RRHH, limpieza general, seguridad, sistema POS. Si se prorrateara, podria sumar $100-300K/mes adicionales.

### K6. Costo financiero ausente

No se contempla costo de capital de trabajo (stock de insumos, desfasaje entre venta y cobro de tarjetas). A tasa activa ~50% TNA, sobre un capital de trabajo estimado de 15 dias de CMV (~$3.8M), el costo financiero seria ~$160K/mes.

---

## V. VERIFICACIONES CONFIRMADAS

Los siguientes items fueron auditados y son correctos:

- Aritmetica: V, CMV, MB, CP, SAC, LAB, SERV, OTROS_F, TF, CV, RES, PE → todos verificados OK
- Contribuciones patronales 29.74% (12.71% SIPA + 1.58% PAMI + 5.56% AF + 0.89% FNE + 6% OS + 3% ART): alicuotas correctas para empleador NO MiPyME, sector Servicios/Comercio
- CCT 130/75 Empleados de Comercio, Aux. Especializado A: categoria correcta para personal de rotiseria
- SAC = (base_rem + contribuciones) / 12: formula correcta para provisionar aguinaldo + cargas sobre aguinaldo
- Tarifa gas Ecogas Cuyana SGP: referencia ENARGAS Res 89/2026 verificable
- Tarifa electricidad EDEMSA T1-G: referencia EPRE Res 025/2026 verificable
- IIBB Mendoza 4%: alicuota plausible para comercio minorista de alimentos (Ley Impositiva Mendoza)
- Indice estacional: metodologia correcta (excluye meses incompletos Oct-Nov)
- Coherencia interna: las 5 hojas del Excel son mutuamente consistentes
- Sensibilizacion: 5 escenarios recalculados correctamente
- Ventas 2026: ventana de 31 dias reales, desestacionalizacion con indice ponderado

---

## VI. RESUMEN DE IMPACTO ESTIMADO

| # | Hallazgo | Efecto en resultado |
|---|---|---|
| C1 | Factor costo diferenciado | No afecta resultado principal (usa 30% del sistema) |
| C2 | Mix medios de pago | Mejora ~$19K/mes |
| C3 | IVA en V | Indeterminado sin dato del POS |
| M1 | Productos por peso | Solo afecta hoja recetas |
| M2 | Inflacion en estacionalidad | Posible subestimacion V en 2-4% (~$80-160K) |
| M3 | ICH simplificado | < $15K/mes |
| M4 | Tributos gas/elec | Empeora ~$37-62K/mes |
| M5 | Vacaciones + presentismo | Empeora ~$155-480K/mes |
| K4 | Tasa Seg. e Higiene | Empeora ~$55-165K/mes |
| K5 | Overhead administrativo | Empeora ~$100-300K/mes |
| K6 | Costo financiero | Empeora ~$160K/mes |

**Rango de deficit ajustado:** -$3.2M a -$4.4M/mes (vs -$3.46M del modelo base).

La conclusion de que la rotiseria es deficitaria con la estructura actual de 3 empleados es **robusta** y se mantiene en cualquier escenario razonable.

---

## VII. RECOMENDACIONES PARA PRESENTACION AL CONTADOR

1. **Verificar tratamiento IVA** con el proveedor del sistema POS antes de cualquier otra accion
2. **Solicitar ultimas facturas** de Ecogas y EDEMSA para reemplazar estimaciones
3. **Confirmar con RRHH** si el basico de $1,080,274 incluye presentismo CCT 130/75
4. **Actualizar mix de medios de pago** con datos de la ventana Feb-Mar 2026
5. **Agregar provision de vacaciones** al menos como nota al pie
6. **Considerar Tasa de Seg. e Higiene** y overhead administrativo como items separados
7. **La milanesa de miga se vende con perdida de -69.5%**: requiere decision comercial inmediata

---

*Dictamen emitido con caracter de revision limitada. No constituye una auditoria de estados contables bajo RT 37. Los montos estimados deben verificarse contra documentacion de respaldo.*

# DICTAMEN DE AUDITORÍA INDEPENDIENTE
## Estructura de Costos v4 - Rotisería NINO (BOSIN S.A.)
### Luján de Cuyo, Mendoza | 21 de Marzo de 2026

---

**Archivo auditado:** `Estructura_Costos_Rotiseria_NINO.xlsx` (5 hojas, generado por `generar_excel_costos.py`)
**Fuentes verificadas:** `detalle_lineas.parquet` (3.9M filas, Oct 2024 - Mar 2026), Excel POS 2026 (4 archivos)
**Alcance:** Revisión celda-por-celda de cálculos, cruce con datos fuente, coherencia entre hojas, razonabilidad de supuestos, normativa impositiva y laboral
**Versión auditada:** v4 (2026-03-21), que incorporó provisión vacaciones, mix de pagos reciente, y factores de costo diferenciados

---

## I. OPINIÓN PROFESIONAL

La estructura de costos v4 presenta mejoras significativas respecto a versiones anteriores (corrección de contribuciones, provisión de vacaciones, factores diferenciados). Sin embargo, la auditoría independiente detectó **un error crítico nuevo**, **dos errores moderados**, y confirma la vigencia de varias observaciones del dictamen anterior.

**La conclusión de déficit operativo (~$3.6M/mes) es cualitativamente correcta y robusta.** Sin embargo, la magnitud exacta del déficit está afectada por los errores detectados. El déficit corregido se estima entre **$3.2M y $3.9M/mes** dependiendo del tratamiento de items pendientes.

La estructura **es presentable a un contador** para toma de decisiones estratégicas (continuar/restructurar/cerrar la rotisería), con las salvedades que se detallan a continuación.

---

## II. ERRORES CRÍTICOS (>$50K/mes de impacto)

### C1. BILLETERA VIRTUAL: typo en datos captura solo 0.55% en vez de 11% — `generar_excel_costos.py:161`

**Materialidad: ALTA. Afecta mix de pagos, comisiones, y potencialmente IIBB/ICH.**

El parquet contiene **dos variantes** del medio de pago billetera:
- `BILLETERA VIRTUAL` → 10.45% de ventas rotisería (Oct 2025 - Mar 2026)
- `BILLETERA VITUAL` (typo, sin R) → 0.55% de ventas

El script en línea 161:
```python
pBI = mp_p.get("BILLETERA VITUAL", mp_p.get("BILLETERA VIRTUAL", 0))
```
Esta lógica toma `BILLETERA VITUAL` primero (porque existe con 0.55%). **Nunca llega al fallback** `BILLETERA VIRTUAL` (10.45%). Resultado: pBI = 0.55% en vez del 11% real.

**Impacto directo:**

| Concepto | Script actual (pBI=0.55%) | Correcto (pBI=11%) | Diferencia |
|---|---|---|---|
| Comisión billetera | $912/mes | $18,233/mes | +$17,321/mes |
| Mix total capturado | 89.54% | 100% | +10.46% desaparecía |

**Impacto secundario:** El mix del script no suma 100% (suma 89.54%). Falta capturar el 10.46% de ventas por billetera virtual. Esto no afecta IIBB ni ICH (que se calculan sobre V), pero sí las comisiones.

**Corrección propuesta (línea 161):**
```python
# Sumar ambas variantes
pBI = mp_p.get("BILLETERA VITUAL", 0) + mp_p.get("BILLETERA VIRTUAL", 0)
```

**Impacto en resultado: +$17,321/mes de costo adicional (empeora el déficit).**

---

### C2. ICH (Imp. Débitos y Créditos) aplicado sobre ventas totales incluyendo efectivo — `generar_excel_costos.py:224`

**Materialidad: ALTA. Sobrestima ICH en ~$62,500/mes.**

El script calcula:
```python
ich_m = round(V * ICH_PCT)  # ICH_PCT = 0.012
```

El impuesto al cheque (Ley 25.413) grava movimientos bancarios al 0.6% débito + 0.6% crédito = 1.2%. Las ventas en **efectivo (~47%)** no generan movimiento bancario directo.

| Cálculo | Base | ICH |
|---|---|---|
| Script actual | V = $11,050,346 (100%) | $132,604 |
| Correcto (solo bancarizado) | V × (1-pEF) = $5,841,618 (52.9%) | $70,099 |
| **Sobrestimación** | | **$62,505/mes** |

**Nota atenuante (del dictamen anterior):** Los pagos a proveedores, empleados e impuestos también generan débitos bancarios no contemplados. Sin embargo, esos débitos corresponden a **gastos**, no a **ingresos**, y no deberían cargarse como costo variable sobre ventas.

**Corrección propuesta (línea 224):**
```python
ich_m = round(V * (1 - pEF) * ICH_PCT)
```

**Impacto en resultado: -$62,505/mes de costo variable (mejora el déficit).**

---

### C3. Tratamiento IVA: V incluye IVA pero se presenta como "sin IVA" — `generar_excel_costos.py:246-250`

**Materialidad: ALTA en presentación. Moderada en cálculos.**

**Evidencia concluyente:**
1. El 97.1% de la facturación de rotisería es **Factura B** (consumidor final), donde el precio incluye IVA por Ley 24.240
2. El `precio_unitario` del POS coincide con el precio de góndola (con IVA). Ejemplo: Empanada carne x12 = $10,702 en Feb 2026 (POS) — este es el precio que paga el consumidor, IVA incluido
3. Los Excel 2026 (fuente de V) provienen del mismo sistema POS → `Importe` incluye IVA
4. La categoría `ROTISERIA` no tiene alícuota en el nombre (a diferencia de "CARNICERIA AL 10,5 %"), lo que indica IVA 21% (alimentos elaborados)

**El script presenta:**
```
VENTAS BRUTAS (con IVA) = V × 1.21 = $13,370,919    ← INCORRECTO (doble IVA)
(-) IVA Débito Fiscal   = -V × 0.21 = -$2,320,573   ← INCORRECTO
VENTAS NETAS (sin IVA)  = V = $11,050,346            ← En realidad YA incluye IVA
```

**Sin embargo, el impacto real en los cálculos es NULO si la estructura es internamente consistente:**
- Si V incluye IVA y CMV = V × 0.70, el margen bruto del 30% se aplica sobre precio con IVA → es el mismo parámetro del sistema POS
- IIBB se aplica sobre ingresos brutos devengados = V (que ya incluye IVA) → correcto
- Los costos fijos son absolutos (no dependen de V) → no cambian

**El error es de presentación, no de cálculo.** Las filas de "Ventas Brutas con IVA" y "(-) IVA DF" en la hoja 1 son ficticias y deben eliminarse.

**Corrección propuesta (líneas 246-250):**
- Eliminar las filas de "VENTAS BRUTAS" e "IVA Débito Fiscal"
- Renombrar a: `VENTAS (IVA incluido, Factura B 97%)` = V
- Agregar nota: "Los precios de Factura B (97% de la facturación) incluyen IVA. V es la facturación bruta real."

**Impacto en resultado: $0 (solo presentación). Pero confunde gravemente a quien lea el Excel.**

---

## III. ERRORES MODERADOS ($10-50K/mes)

### M1. Precios de insumos desactualizados: pan rallado y PVP empanada — `generar_excel_costos.py:584,668,706`

**Materialidad: MODERADA. Afecta solo hoja de Costeo Recetas, no el resultado principal.**

| Insumo/Producto | Script | POS Feb 2026 | Diferencia |
|---|---|---|---|
| Pan rallado NINO 1kg | $2,874 | $3,270 | +13.8% (subestima CMV) |
| Empanada carne x12 PVP | $10,104 | $10,702 | +5.9% (subestima ingreso) |
| Salsa bolognesa PVP | $7,560 | $7,886 | +4.3% |
| Matambre NINO PVP | $43,628 | $44,951 | +3.0% |

Los restantes 12 insumos y 6 PVPs están dentro del ±3% (aceptable).

**Impacto:** Solo en la hoja de Costeo Recetas. El resultado principal usa CMV = V × 0.70 (parámetro del sistema), no los costeos individuales.

---

### M2. Sensibilización: tabla de PE usa `vp_adj` con merma variable pero IIBB e ICH fijos sobre V — `generar_excel_costos.py:784-786`

**Materialidad: BAJA. Afecta solo la interpretación de escenarios.**

En la sensibilización (líneas 784-786):
```python
vp_adj = (comT + iibb_m + ich_m + round(V * mr)) / V
```

Las comisiones (`comT`), IIBB (`iibb_m`) e ICH (`ich_m`) están fijos en sus valores base mientras solo varía la merma. Esto es **conceptualmente correcto** (V no cambia entre escenarios, solo cambia el margen bruto y la merma), pero no refleja el error C2 del ICH. Una vez corregido ICH, la sensibilización también debe recalcularse.

---

## IV. OBSERVACIONES COSMÉTICAS

### K1. Desglose contribuciones patronales: redondeo individual difiere en $200 del total

Las alícuotas individuales (12.71% + 1.58% + 5.56% + 0.89% + 6% + 3%) redondeadas por separado suman $963,620. El total CP_m calculado como 29.74% × base = $963,820. **Diferencia de $200 por redondeo.** Esto confunde al lector pero no afecta el resultado (se usa el total correcto).

### K2. SAC: etiquetado conceptualmente impreciso — `generar_excel_costos.py:183`

La fórmula `SAC = (ST_rem + CP_m) / 12` es **algebraicamente equivalente** a la fórmula correcta `SAC_bruto + CP_sobre_SAC`, con diferencia de solo $6/mes por redondeo. Sin embargo, la etiqueta "SAC sobre remunerativo + cargas" sugiere que las cargas entran en la base del aguinaldo, lo cual es incorrecto conceptualmente. El SAC se calcula sobre la remuneración bruta, y las contribuciones se aplican sobre el SAC.

### K3. Provisión vacaciones: redondeo por empleado antes de multiplicar — `generar_excel_costos.py:187`

`VAC_bruto = round(SB_REM / 25 * VAC_DIAS / 12) * NE` redondea por empleado antes de multiplicar por 3. Diferencia: ~$2/mes. Insignificante.

### K4. Nota de PE en sensibilización — `generar_excel_costos.py:800`

Línea 800: "contribuciones bajan de **20.4%** a 18% SUSS". Debería decir **20.74%** (consistente con el desglose SUSS del script).

---

## V. HALLAZGOS PENDIENTES (vigentes del dictamen anterior v3)

Los siguientes hallazgos del dictamen anterior **siguen vigentes** en v4:

| # | Hallazgo | Estado v4 | Impacto estimado |
|---|---|---|---|
| ~~C1 v3~~ | Factor costo diferenciado | **RESUELTO** en v4 | - |
| ~~C2 v3~~ | Mix medios de pago desactualizado | **RESUELTO** en v4 (pero con bug C1 nuevo) | - |
| M1 v3 | Productos por peso (matambre, etc.) | **Vigente** — solo afecta hoja recetas | Distorsiona margen recetas |
| M2 v3 | Desestacionalización contaminada por inflación | **Vigente** — efecto modesto (~2-4% sobre V) | ~$80-160K/mes |
| M4 v3 | Gas/electricidad: faltan tributos provinciales | **Vigente** | +$37-62K/mes costo |
| M5 v3 | Presentismo CCT 130/75 no aclarado | **Vigente** | Potencialmente +$324K/mes |
| M5 v3 | No hay provisión indemnizaciones | **Vigente** | ~$300K/mes |
| ~~M5 v3~~ | Falta provisión vacaciones | **RESUELTO** en v4 ($196,217/mes) | - |
| K3 v3 | Alquiler $150K probablemente bajo | **Vigente** | Subestimación indefinida |
| K4 v3 | Falta Tasa Seg. e Higiene municipal | **Vigente** | +$55-165K/mes |
| K5 v3 | Falta overhead administrativo | **Vigente** | +$100-300K/mes |
| K6 v3 | Falta costo financiero | **Vigente** | ~$160K/mes |

---

## VI. VERIFICACIONES CONFIRMADAS (v4 OK)

Los siguientes cálculos fueron auditados celda por celda y son **correctos**:

- **CMV:** $7,735,242 = V × 0.70 ✓
- **Margen bruto:** $3,315,104 = V × 0.30 ✓
- **Sueldos:** $3,540,822 = $1,180,274 × 3 ✓
- **Base contribuciones:** $3,240,822 = $1,080,274 × 3 (solo remunerativo) ✓
- **Contribuciones:** $963,820 = $3,240,822 × 0.2974 ✓
- **Alícuotas CP:** 12.71% + 1.58% + 5.56% + 0.89% + 6% + 3% = 29.74% ✓
- **SAC:** $350,387 ≈ (ST_rem + CP_m) / 12 ✓ (algebraicamente equivalente)
- **Vacaciones:** $196,217 (14 días Art. 150 LCT, divisor 25 Art. 155 LCT, + CP) ✓ **Nuevo en v4**
- **Laboral total:** $5,052,746 = sueldos + CP + SAC + seguro + vacaciones ✓
- **Gas:** $122,297 = ($24,129 + 250 × $307.77) × 1.21 ✓
- **Electricidad:** $151,065 = ($16,114/2 + 500 × $233.58) × 1.21 ✓
- **Otros fijos:** $385,000 = suma de 9 items (150K+80K+50K+30K+25K+15K+15K+12K+8K) ✓
- **TF:** $5,711,108 = $5,052,746 + $273,362 + $385,000 ✓
- **IIBB:** $442,014 = V × 4% ✓ (base bruta correcta si V incluye IVA)
- **Merma:** $552,517 = V × 5% ✓
- **Resultado:** -$3,600,793 = $3,315,104 - $5,711,108 - $1,204,789 ✓
- **PE fórmula:** TF / (MG - CV/V) → conceptualmente correcta ✓
- **Factores rentabilidad_factor:** Carnicería 0.20, Fiambrería 0.45, Almacén 0.28, Panificación 0.30, Congelados 0.28 — todos verificados contra parquet ✓
- **Coherencia entre 5 hojas:** Totales de Estructura = datos de Ventas Mensuales = base Productos ✓
- **Índice estacional 2025:** 10 meses completos, Oct/Nov excluidos correctamente ✓

---

## VII. CUADRO RESUMEN DE IMPACTO

### Errores detectados en esta auditoría (v4)

| # | Hallazgo | Efecto en resultado | Tipo |
|---|---|---|---|
| **C1** | Billetera virtual: typo captura 0.55% vs 11% real | **Empeora $17K/mes** | Bug en datos/script |
| **C2** | ICH sobre ventas totales (incluye efectivo) | **Mejora $63K/mes** | Error conceptual |
| **C3** | IVA presentado incorrectamente (doble IVA ficticio) | $0 (presentación) | Error de presentación |
| M1 | Precios desactualizados en recetas | Solo hoja recetas | Desfase temporal |
| M2 | Sensibilización hereda error ICH | Recalcular | Derivado de C2 |

### Resultado corregido (solo errores C1 y C2)

| Concepto | v4 actual | v4 corregido | Diferencia |
|---|---|---|---|
| Comisión billetera | -$912 | -$18,233 | -$17,321 |
| ICH | -$132,604 | -$70,099 | +$62,505 |
| **CV total** | **-$1,204,789** | **-$1,160,105** | **+$44,684** |
| **Resultado** | **-$3,600,793** | **-$3,556,109** | **+$44,684** |
| PE | $29,905,358 | Recalcular | Mejora |

### Rango de déficit considerando items pendientes

| Escenario | Resultado mensual |
|---|---|
| v4 corregido (solo C1+C2) | -$3,556,109 |
| + tributos servicios (-$50K) | -$3,606,109 |
| + Tasa Seg. e Higiene (-$110K) | -$3,716,109 |
| + overhead administrativo (-$200K) | -$3,916,109 |
| + costo financiero (-$160K) | -$4,076,109 |
| + presentismo si no está incluido (-$324K) | -$4,400,109 |

**Rango de déficit real estimado: -$3.6M a -$4.4M/mes.**

---

## VIII. OBSERVACIONES ADICIONALES DEL ETL

Durante la auditoría se detectaron problemas en el pipeline de datos (`data/processed/detalle_lineas.parquet`) que si bien no afectan directamente esta estructura de costos, deben corregirse para análisis futuros:

1. **Typo `BILLETERA VITUAL`**: 446,665 registros globales no normalizados. El ETL no corrige este typo.
2. **Marzo 2026 no marcado como incompleto**: Solo tiene 18 días (hasta 18/03) pero `mes_incompleto=False`. La lógica del ETL está hardcodeada para Oct/Nov 2025 solamente.
3. **Trailing spaces en `tipo_factura`**: Existen "FB" y "FB " como valores distintos. No afecta esta auditoría pero puede causar errores en otros análisis.
4. **Categoría `CARNICERIA AL 10,5 %`**: Tiene espacio extra antes del `%`. Cosmético pero puede causar bugs si se busca por nombre exacto.

---

## IX. RECOMENDACIONES PARA PRESENTACIÓN AL CONTADOR

### Prioridad inmediata (antes de presentar)
1. **Corregir bug billetera virtual** (C1): unificar ambas variantes en el script
2. **Corregir ICH** (C2): aplicar solo sobre monto bancarizado
3. **Eliminar filas ficticias de IVA** (C3): presentar V como "facturación bruta (IVA incluido)"
4. **Regenerar el Excel** con las correcciones

### Prioridad alta (validar con documentación)
5. **Solicitar últimas facturas de Ecogas y EDEMSA** para reemplazar estimaciones de servicios
6. **Confirmar con RRHH** si el básico de $1,080,274 incluye presentismo CCT 130/75
7. **Obtener dato de Tasa de Seg. e Higiene** de la Municipalidad de Luján de Cuyo

### Prioridad media (mejoras del modelo)
8. **Agregar nota**: "Costos no incluidos: overhead administrativo, costo financiero, provisión indemnizaciones"
9. **Actualizar precios de insumos** en hoja recetas (pan rallado, empanada carne x12)
10. **Corregir ETL**: normalizar billetera virtual, detectar meses incompletos automáticamente

---

## X. DICTAMEN FINAL

La estructura de costos v4 de la Rotisería NINO constituye una herramienta **razonablemente confiable** para análisis de gestión, sujeta a las correcciones descriptas (C1, C2, C3). La conclusión de **déficit operativo significativo** (~$3.6M/mes, ~33% de facturación) es **cualitativamente robusta** y se mantiene o agrava en todos los escenarios de corrección.

Los errores detectados tienen un efecto neto de +$45K/mes (mejora marginal), confirmando que el déficit reportado no está artificialmente inflado.

**La estructura es presentable a un contador para toma de decisiones**, con la salvedad de que:
- Se corrijan los tres errores críticos antes de la presentación
- Se aclare explícitamente que V incluye IVA (Factura B)
- Los items pendientes (servicios, presentismo, tasas municipales, overhead) se listen como notas de salvedad

---

*Dictamen emitido con carácter de revisión independiente. Verificación celda-por-celda del script generador y cruce con base de datos fuente (3.9M registros). No constituye una auditoría de estados contables bajo RT 37 FACPCE. Los montos estimados deben verificarse contra documentación de respaldo.*

*Mendoza, 21 de marzo de 2026*

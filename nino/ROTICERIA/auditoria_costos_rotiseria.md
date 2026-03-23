========================================
INFORME DE AUDITORIA
Estructura de Costos - Rotiseria NINO (BOSIN S.A.)
Fecha: 2026-03-20
Auditor: Independiente (automatizado)
========================================

Archivo auditado: nino/ROTICERIA/Estructura_Costos_Rotiseria_NINO.xlsx
Fuentes de datos: data/processed/detalle_lineas.parquet, Excel 2026 (H:/Mi unidad/PYMEINSIDE/nino/)
Script generador: nino/ROTICERIA/generar_excel_costos.py

---

## CORRECCIONES APLICADAS (v3 - 2026-03-20, v4 - 2026-03-21)

### 1. Ventas: ultimos 31 dias desestacionalizados (sin cambios respecto v2)

**Metodologia:**
- Fuente: 4 Excel de 2026 (ReporteMovimientosItemEnComprobantes 1/2/22/3), filtro ROTISERIA
- Ventana: 31 dias, $11,369,307 brutos
- Indice estacional ponderado: 1.0095 (Feb 1.0903 x 13d + Mar 1.1280 x 18d, base 10 meses completos 2025)
- Formula: ($11,369,307 / 31) * 30.4167 / 1.0095 = $11,050,346

### 2. Contribuciones patronales: alicuota corregida de 29.4% a 29.74%

**Antes (v2):** CP_PCT = 0.294 (no coincidia con desglose individual de alicuotas)
**Ahora (v3):** CP_PCT = 0.2974 (= 12.71% + 1.58% + 5.56% + 0.89% + 6% + 3%)

| Concepto | v2 | v3 | Diferencia |
|---|---|---|---|
| Contribuciones | $952,802 (29.4%) | $963,820 (29.74%) | +$11,018 |
| SAC mensualizado | $349,469 | $350,387 | +$918 |
| **Subtotal Laboral** | **$4,844,593** | **$4,856,529** | **+$11,936** |

### 3. Resultado v2 omitia servicios y otros fijos (ERROR CRITICO)

**Error detectado:** La v2 calculaba Resultado = MB - LAB - CV = $3,315,104 - $4,844,593 - $1,256,462 = -$2,785,951.
Omitia SERV ($273,362) y OTROS_F ($385,000). El resultado correcto incluye TODOS los costos fijos.

**Formula correcta:** Resultado = MB - TF - CV = MB - (LAB + SERV + OTROS_F) - CV

### 4. Precios de insumos y PVPs actualizados a Dic 2025

**Antes:** Precios hardcodeados correspondientes a ~Sep-Oct 2025.
**Ahora:** Precios extraidos del parquet (promedio Dic 2025), PVPs de rotiseria Dic 2025.

Principales cambios:
- Nalga: $13,400 → $17,149/kg (+28%, mayor impacto en milanesas)
- Molida especial: $12,200 → $13,734/kg (+13%, impacto en empanadas)
- Empanada carne x12 PVP: $8,000 → $9,652 (+21%)
- Matambre NINO PVP: $38,200 → $42,051 (+10%)
- Milanesa miga margen: -30% → -53% (costo sube, PVP sin cambio)

### 5. Sensibilizacion corregida

**Error detectado:** La v2 de analisis_costos_rotiseria.md usaba TF sin OTROS_F en escenarios no-base (diferencia de $385,000 por escenario). Ahora todos los escenarios usan TF completo.

### 6. Ruta de salida del script corregida

**Antes:** `nino/Estructura_Costos_Rotiseria_NINO.xlsx` (ubicacion incorrecta)
**Ahora:** `nino/ROTICERIA/Estructura_Costos_Rotiseria_NINO.xlsx`

### 7. Provision vacaciones incorporada (v4 - 2026-03-21)

**Antes (v3):** No se provisionaban vacaciones. Advertencia pendiente.
**Ahora (v4):** Provision vacaciones $196,217/mes (14 dias Art.150 LCT + contribuciones patronales).

| Concepto | v3 | v4 | Diferencia |
|---|---|---|---|
| Laboral | $4,856,529 | $5,052,746 | +$196,217 |
| TF | $5,514,891 | $5,711,108 | +$196,217 |

### 8. Comisiones recalculadas con mix de pagos reciente (v4)

**Antes (v3):** Mix historico (EF 39.5%, DE 25.8%, CR 22.7%, BI 12.1%). Comisiones: $129,327.
**Ahora (v4):** Mix reciente Oct 2025-Mar 2026 (EF ~48%, DE ~31%, CR ~11%, BI ~1%). Comisiones: $77,654.

| Concepto | v3 | v4 | Diferencia |
|---|---|---|---|
| Credito | $75,088 | $35,380 | -$39,708 |
| Debito | $34,190 | $41,362 | +$7,172 |
| Billetera | $20,049 | $912 | -$19,137 |
| **Total comisiones** | **$129,327** | **$77,654** | **-$51,673** |
| **CV total** | **$1,256,462** | **$1,204,789** | **-$51,673** |

### 9. Precios insumos y recetas actualizados a Feb 2026 con factores diferenciados (v4)

**Antes (v3):** Precios Dic 2025 × factor unico 0.70.
**Ahora (v4):** Precios Feb 2026 × factor diferenciado por categoria (rentabilidad_factor POS).

Margen ponderado recetas: 41.5% → 38.7%.

---

## VALORES ACTUALES (v4)

| Concepto | Monto | % s/Ventas |
|---|---|---|
| Ventas netas | $11,050,346 | 100% |
| CMV (70%) | -$7,735,242 | 70% |
| Margen bruto | $3,315,104 | 30% |
| Costos fijos totales | -$5,711,108 | 51.7% |
|   - Laboral | -$5,052,746 | 45.7% |
|   - Servicios | -$273,362 | 2.5% |
|   - Otros fijos | -$385,000 | 3.5% |
| Costos variables | -$1,204,789 | 10.9% |
| **Resultado** | **-$3,600,793** | **-32.6%** |
| Pto. equilibrio | $29,905,358 | - |
| Cobertura | 37% | - |

---

## ADVERTENCIAS PENDIENTES

### 1. Vacaciones provisionadas (RESUELTO en v4)

Provision vacaciones incorporada: $196,217/mes (14 dias Art.150 LCT + contribuciones).

### 2. No se provisionan indemnizaciones

No incluye provision por posibles indemnizaciones.

### 3. Presentismo (Art. 40 CCT 130/75)

No se aclara si el basico de $1,080,274 ya incluye presentismo.

### 4. Gap margen ponderado recetas (38.7%) vs margen asumido (30%)

Las 10 recetas costeadas (85.9% de ventas) dan margen ponderado 38.7%, pero la estructura asume 30% de margen bruto global. Posibles causas:
- El 30% es un parametro conservador del sistema POS
- Los factores por categoria (0.55-0.80) pueden no capturar exactamente el costo real
- Los productos "Otros" (14.1% de ventas) pueden tener margenes menores
Recomendacion: validar con dato real de CMV del contador.

### 5. Precios de insumos actualizados a Feb 2026 (RESUELTO en v4)

Los precios de insumos ahora provienen del POS Feb 2026 con factores de costo diferenciados por categoria (rentabilidad_factor).

---

## VERIFICACIONES OK (v4)

- Ventas netas: $11,050,346 (31d desestac., idx=1.0095) OK
- CMV: $7,735,242 = V * 0.70 OK
- Margen bruto: $3,315,104 = V * 0.30 OK
- Sueldos: $3,540,822 = $1,180,274 * 3 OK
- Base contribuciones: $3,240,822 = $1,080,274 * 3 OK (solo remunerativo)
- Contribuciones: $963,820 = $3,240,822 * 0.2974 OK
- Desglose CP: 411,908 + 51,205 + 180,190 + 28,843 + 194,449 + 97,225 = 963,820 OK (coincide con total)
- SAC: $350,387 = ($3,240,822 + $963,820) / 12 OK
- Provision vacaciones: $196,217 (14 dias Art.150 LCT + contribuciones) OK
- Laboral total: $5,052,746 = $3,540,822 + $963,820 + $350,387 + $1,500 + $196,217 OK
- Servicios: $273,362 = gas $122,297 + elec $151,065 OK
  - Gas: ($24,129 + 250 * $307.77) * 1.21 = $122,297 OK
  - Elec: ($16,114/2 + 500 * $233.58) * 1.21 = $151,065 OK
- Otros fijos: $385,000 (9 items: 150K+80K+50K+30K+25K+15K+15K+12K+8K) OK
- TF: $5,711,108 = $5,052,746 + $273,362 + $385,000 OK
- Costos variables: $1,204,789 = $77,654 + $442,014 + $132,604 + $552,517 OK
  - Comisiones: $35,380 + $41,362 + $912 = $77,654 OK (mix reciente Oct 2025-Mar 2026)
  - IIBB: $442,014 = V * 4% OK
  - ICH: $132,604 = V * 1.2% OK
  - Merma: $552,517 = V * 5% OK
- Resultado: -$3,600,793 = $3,315,104 - $5,711,108 - $1,204,789 OK
- PE: $29,905,358 = TF / (MG - CV/V) OK
- Cobertura: 37% = V / PE OK
- Sensibilizacion: pendiente recalculo con nuevos TF y CV
- Costeo recetas: 10 productos, precios Feb 2026 con factores diferenciados por categoria OK
- Coherencia 5 hojas: totales de estructura = datos de ventas mensuales = base productos OK
- Supuestos: actualizados con provision vacaciones y mix pagos reciente OK

---

## CONCLUSION v4

La v4 incorporó las correcciones de la estructura de costos:

1. **Provision vacaciones incorporada** ($196,217/mes, 14 dias Art.150 LCT + contribuciones)
2. **Laboral actualizado** a $5,052,746 (antes $4,856,529)
3. **Comisiones recalculadas** con mix de pagos reciente Oct 2025-Mar 2026 ($77,654 vs $129,327 anterior)
4. **Precios de insumos actualizados** a Feb 2026 (POS) con factores diferenciados por categoria
5. **Margen ponderado recetas** ajustado a 38.7% (antes 41.5%)
6. **TF total** $5,711,108 (antes $5,514,891)
7. **CV total** $1,204,789 (antes $1,256,462)

---

## CORRECCIONES v5 (2026-03-21) — Auditoría independiente

### 10. Billetera virtual: typo corregido (v5)
**Antes (v4):** `pBI = mp_p.get("BILLETERA VITUAL", ...)` capturaba solo 0.55% (typo sin R)
**Ahora (v5):** Suma ambas variantes → pBI = 11%. Comisiones: $94,964 (antes $77,654)

### 11. ICH solo sobre monto bancarizado (v5)
**Antes (v4):** ICH = V × 1.2% = $132,604 (aplicaba sobre 100% incluyendo efectivo)
**Ahora (v5):** ICH = V × (1-pEF) × 1.2% = $70,118 (solo 53% bancarizado)

### 12. IVA en presentación corregido (v5)
**Antes (v4):** Mostraba "VENTAS BRUTAS = V×1.21" (doble IVA, V ya incluye IVA)
**Ahora (v5):** V presentado como facturación bruta real (IVA incluido, 97% Factura B)

### 13. IIBB corregido: alícuota 3% sobre base sin IVA (v5)
**Antes (v4):** IIBB = V × 4% = $442,014
**Ahora (v5):** IIBB = (V/1.21) × 3% = $273,976 (Ley 9680 Rubro 7, Art. 169 CF Mendoza excluye IVA DF)
**Diferencia: -$168,038/mes**

### 14. Presentismo CCT 130/75 incorporado (v5)
**Antes (v4):** No incluido. El básico $1,080,274 NO incluye presentismo (confirmado con escalas FAECYS)
**Ahora (v5):** Presentismo 8.33% s/básico = $270,066 bruto + $80,322 CP = $350,388/mes (Art. 40 CCT 130/75)

### 15. Tributos servicios incorporados (v5)
**Antes (v4):** Solo IVA 21%. Gas $122,297, Elec $151,065
**Ahora (v5):** Gas ×1.315 = $132,909, Elec ×1.39 = $173,537
- Gas: +Fdo Fiduciario 6.8% + IIBB distrib 3% + tasa muni ~5%
- Elec: +CCCE 7.5% + EPRE 1.5% + IIBB 3% + CAP ~3%

### 16. Nota MiPyME corregida (v5)
20.4% → 20.74% SUSS

---

## VALORES v5

| Concepto | v4 | v5 | Delta |
|---|---|---|---|
| Laboral | -$5,052,746 | -$5,403,134 | -$350,388 |
| Servicios | -$273,362 | -$306,446 | -$33,084 |
| TF total | -$5,711,108 | -$6,094,580 | -$383,472 |
| Comisiones | -$77,654 | -$94,964 | -$17,310 |
| IIBB | -$442,014 | -$273,976 | +$168,038 |
| ICH | -$132,604 | -$70,118 | +$62,486 |
| CV total | -$1,204,789 | -$991,575 | +$213,214 |
| **Resultado** | **-$3,600,793** | **-$3,771,051** | **-$170,258** |
| PE | $29,905,358 | $28,984,886 | -$920,472 |
| Cobertura | 37% | 38% | +1pp |

El resultado empeora $170K/mes (presentismo +$350K y tributos +$33K superan la mejora de IIBB -$168K e ICH -$62K).
El PE mejora porque la proporción de costos variables bajó significativamente.

---

## CONCLUSION v5

El resultado deficitario es **-$3.77M/mes (-34.1% s/ventas)**. PE: $29.0M/mes, cobertura 38%.
Pendientes: indemnizaciones (~$300K/mes), overhead administrativo, costo financiero.

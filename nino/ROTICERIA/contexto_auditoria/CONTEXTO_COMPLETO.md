# Contexto para Auditoría - Estructura de Costos Rotisería NINO

## Estado actual (v5b - 2026-03-21)

### Archivos principales
- `nino/ROTICERIA/Estructura_Costos_Rotiseria_NINO.xlsx` — Excel con 5 hojas generado por el script
- `nino/ROTICERIA/generar_excel_costos.py` — Script Python que genera el Excel
- `nino/ROTICERIA/analisis_costos_rotiseria.md` — Análisis narrativo completo
- `nino/ROTICERIA/auditoria_costos_rotiseria.md` — Registro de auditoría v3/v4/v5
- `nino/ROTICERIA/dictamen_auditoria_contable.md` — Dictamen contable profesional (v3, desactualizado)
- `nino/ROTICERIA/dictamen_auditoria_independiente_v4.md` — Auditoría independiente que detectó errores v4

### Base de datos
- `data/processed/detalle_lineas.parquet` — 3,906,199 filas, Oct 2024 - Mar 2026, 29 columnas
- `data/raw/SERIE_COMPROBANTES_COMPLETOS.csv` — CSV unificado (sep=";", decimal=",")
- Datos 2026 unificados via `scripts/unificar_datos_2026.py`

### Valores clave v5b
```
Ventas:          $11,050,346   (31d desestac., idx=1.0095, IVA incluido Factura B 97%)
CMV (70%):       -$7,735,242
MB (30%):         $3,315,104
Costos fijos:    -$6,123,779
  Laboral:       -$5,432,333
    Sueldos:     -$3,540,822  (3 × $1,180,274: $1,080,274 rem + $100,000 NR)
    CP 29.74%:     -$963,820  (solo sobre remunerativo)
    SAC:           -$379,586  (mensualizado, incluye presentismo en base)
    Seguro:          -$1,500  (Dto. 1567/74)
    Presentismo:   -$350,388  (Art. 40 CCT 130/75, 8.33% s/básico + CP)
    Vacaciones:    -$196,217  (14 días Art. 150 LCT + CP)
  Servicios:       -$306,446
    Gas:           -$132,909  (250 m3, Ecogas × 1.315 inc. IVA+tributos)
    Electricidad:  -$173,537  (500 kWh, EDEMSA × 1.39 inc. IVA+tributos)
  Otros fijos:     -$385,000  (9 items estimados)
Costos variables:-$1,028,836
  Comisiones:       -$94,964  (CR + DE + BI 11% real)
  IIBB:            -$273,976  (3% s/base sin IVA, Art. 169 CF Mendoza, Ley 9680)
  ICH:              -$70,118  (1.2% solo bancarizado 53%)
  Merma:           -$552,517  (5%)
  Costo financiero: -$37,261  (TNA 40%, CR 18d + DE 3d + BI 2d)
RESULTADO:       -$3,837,511  (-34.7%)
PE:              $29,598,403   (cobertura 37%)
```

### Correcciones aplicadas (v3→v4→v5)
1. CP_PCT 0.294 → 0.2974 [v3]
2. Precios insumos actualizados a Feb 2026 del POS [v4]
3. PVPs actualizados a Feb 2026 [v4]
4. Factores de costo diferenciados por categoría [v4]
5. Mix medios de pago actualizado a Oct 2025-Mar 2026 [v4]
6. Provisión vacaciones incorporada [v4]
7. Ruta de salida del script corregida [v3]
8. Billetera virtual: corregido typo (0.55% → 11% real) [v5]
9. ICH solo sobre monto bancarizado [v5]
10. V presentado como facturación bruta con IVA [v5]
11. IIBB: 3% sobre base sin IVA (Art. 169 CF Mendoza, Ley 9680) [v5]
12. Presentismo CCT 130/75 ($350,388/mes) [v5]
13. Tributos servicios: gas ×1.315, elec ×1.39 [v5]
14. Nota MiPyME: 20.74% [v5]
15. Costo financiero por demora acreditación tarjetas ($37,261/mes) [v5]
16. SAC incluye presentismo en base (remunerativo): $379,586 [v5b]
17. Recetas: precios más baratos Feb 2026, Ricota $3,840 (no $7,680) [v5b]
18. MIGA TRIP. x12 es sandwich de miga triple (no milanesa): margen 29% (antes -61%) [v5b]
19. Paleta Piamontesa $7,650/kg reemplaza Jamón Paladini $17,040/kg en J&Q y arrollado [v5b]
20. Tapas empanada Via Veneto $1,150/doc (más baratas del POS) [v5b]

### Hallazgos pendientes
- **Indemnizaciones**: Sin provisión (concepto discutible para análisis de gestión)
- **Matambre se vende por peso**: PVP en receta es por kg, no por pieza (solo afecta hoja recetas)
- **Desestacionalización con inflación**: Índice estacional contaminado por ~25% inflación anual (efecto modesto ~2-4%)
- **Precios recetas**: pan rallado, empanada carne x12 ligeramente desactualizados (no afecta resultado)
- **Alquiler $150K probablemente bajo** para Mar 2026

### Hallazgos resueltos en v5
- ~~IVA: V incluye IVA, presentación corregida~~
- ~~Gas/electricidad: tributos provinciales incorporados~~
- ~~Presentismo CCT 130/75: incorporado~~
- ~~IIBB: 3% s/base sin IVA~~
- ~~Billetera virtual: typo corregido~~
- ~~ICH: solo bancarizado~~
- ~~Tasa Seg. e Higiene Luján: por aforo/m2, $8K/mes ya cubre~~
- ~~Costo financiero: incorporado~~
- ~~Overhead/costo capital: no aplican a nivel departamental~~

### Parámetros laborales
- CCT 130/75 Empleados de Comercio, Aux. Especializado A
- Sueldo: $1,080,274 rem + $100,000 NR = $1,180,274/empleado (escala Dic 2025 - Mar 2026, confirmado FAECYS)
- 3 empleados, sin antigüedad
- CP 29.74% sobre remunerativo (12.71% SIPA + 1.58% PAMI + 5.56% AF + 0.89% FNE + 6% OS + 3% ART)
- Presentismo 8.33% s/básico (Art. 40 CCT 130/75), remunerativo, genera CP
- SAC = (base_rem + CP) / 12
- Vacaciones: 14 días Art. 150 LCT, divisor 25 Art. 155 LCT, mensualizado + CP

### Parámetros impositivos (verificados v5)
- IIBB Mendoza: 3% s/base sin IVA (Ley 9680 Rubro 7 comercio minorista, Art. 169 CF excluye IVA DF)
- ICH: 1.2% (0.6%+0.6%) solo sobre monto bancarizado (excluye efectivo 47%)
- Gas: tarifa × 1.315 (IVA 21% + Fdo Fiduciario 6.8% Res MEC 1253/2025 + IIBB distrib 3% + tasa muni ~5%)
- Elec: tarifa × 1.39 (IVA 21% + CCCE 7.5% Ley 6497 + EPRE 1.5% + IIBB 3% + CAP ~3%)
- Tasa municipal Luján de Cuyo: por aforo/m2 (no % ventas), cubierto en $8K habilitación

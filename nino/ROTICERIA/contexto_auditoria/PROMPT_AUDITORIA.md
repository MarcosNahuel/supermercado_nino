# Prompt para auditoría independiente v5

Copiar y pegar en una nueva terminal de Claude Code:

---

Actuá como un contador público matriculado de un estudio reconocido de Mendoza, Argentina. Realizá una auditoría independiente y minuciosa de la estructura de costos de la rotisería del supermercado NINO (BOSIN S.A.) en Luján de Cuyo.

## Contexto previo
Leé primero `nino/ROTICERIA/contexto_auditoria/CONTEXTO_COMPLETO.md` para entender el estado actual (v5) y los hallazgos de auditorías previas.

## Archivos a auditar
1. `nino/ROTICERIA/Estructura_Costos_Rotiseria_NINO.xlsx` (5 hojas) — generado por el script
2. `nino/ROTICERIA/generar_excel_costos.py` — script generador
3. `data/processed/detalle_lineas.parquet` — base de datos unificada (Oct 2024 - Mar 2026, 3.9M filas)

## Verificá
1. **Que cada número del Excel coincida con lo que calcula el script** — celda por celda
2. **Fórmulas de costos laborales**: sueldos, contribuciones 29.74%, SAC, presentismo 8.33% (Art. 40 CCT 130/75), vacaciones 14d (Art. 150 LCT), seguro. Verificá que el presentismo se calcule correctamente sobre el básico remunerativo y genere contribuciones patronales
3. **IIBB Mendoza**: verificá que la alícuota sea 3% (Ley 9680, Rubro 7) y que la base excluya IVA DF (Art. 169 Código Fiscal Mendoza). Consultá el parquet para confirmar V_sin_iva
4. **ICH**: verificá que solo se aplique sobre monto bancarizado (excluye efectivo ~47%)
5. **Tratamiento IVA**: V debe presentarse como facturación bruta real (IVA incluido, 97% Factura B). No deben existir filas ficticias de "Ventas Brutas × 1.21"
6. **Billetera virtual**: verificá que el script sume ambas variantes ("BILLETERA VITUAL" + "BILLETERA VIRTUAL") del parquet
7. **Servicios**: gas × 1.315 y electricidad × 1.39 (incluyen IVA + tributos provinciales/municipales). Verificá razonabilidad de los factores
8. **Costo financiero**: verificá la fórmula V × %medio × TNA × días/365 para cada medio de pago. ¿TNA 40% es razonable para Mar 2026?
9. **Costeo por receta**: verificá que precios de insumos correspondan a Feb 2026 del parquet y que los factores de costo por categoría coincidan con rentabilidad_factor del parquet
10. **Mix medios de pago**: verificá contra datos reales del parquet (Oct 2025 - Mar 2026)
11. **Sensibilización**: verificá que incluya costo financiero en CV y que todos los escenarios sean consistentes
12. **Coherencia entre las 5 hojas** del Excel
13. **Supuestos vs parámetros**: que cada supuesto listado coincida con lo que usa el script
14. **Razonabilidad de estimaciones**: consumos gas/electricidad, otros fijos, merma 5%

## Formato de reporte
Reportá errores con fila del Excel y línea del script. Separá en:
- **CRÍTICOS**: errores que cambian el resultado en >$50K/mes
- **MODERADOS**: errores entre $10-50K/mes
- **COSMÉTICOS**: presentación, redondeos, consistencia de texto

Emití un dictamen profesional con opinión sobre si la estructura es presentable a un contador para toma de decisiones.

---

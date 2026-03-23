# Prompt para auditoría completa — Codex / Claude Code

Copiar y pegar en Codex o nueva terminal de Claude Code.
El output debe ser un archivo `.md` guardado en `nino/ROTICERIA/dictamen_auditoria_v5b.md`.

---

Sos un contador público matriculado (CPCE Mendoza) con 20 años de experiencia en auditoría de PyMEs del sector alimentos. Te contrataron para una auditoría independiente de la estructura de costos de la rotisería del supermercado NINO (BOSIN S.A.), Luján de Cuyo, Mendoza.

## TU ENTREGABLE

Guardá tu dictamen completo en `nino/ROTICERIA/dictamen_auditoria_v5b.md` con el formato exacto que se describe al final.

## Archivos a leer (en este orden)

1. `nino/ROTICERIA/contexto_auditoria/CONTEXTO_COMPLETO.md` — estado actual v5b, correcciones previas, parámetros
2. `nino/ROTICERIA/generar_excel_costos.py` — script Python que genera el Excel (FUENTE DE VERDAD de los cálculos)
3. `data/processed/detalle_lineas.parquet` — base de datos POS (3.9M filas, Oct 2024 - Mar 2026)

NO leas auditorías previas (`dictamen_auditoria_contable.md`, `dictamen_auditoria_independiente_v4.md`, `auditoria_costos_rotiseria.md`) — queremos una opinión fresca sin sesgo.

## Alcance de la auditoría

### A. VERIFICACIÓN ARITMÉTICA (celda por celda)
Recalculá manualmente cada valor del script y verificá que los números cuadren:

1. **Ventas (V)**: ¿Cómo se calcula? ¿Qué fuente usa? ¿La desestacionalización es correcta?
2. **CMV y Margen Bruto**: V × 0.70 y V × 0.30. ¿El 30% es un dato o un supuesto?
3. **Laboral completo**:
   - Sueldos brutos = SB_TOTAL × NE
   - Base remunerativa vs no remunerativa (¿por qué se separan?)
   - Contribuciones patronales: recalculá 29.74% sobre base remunerativa. Verificá cada alícuota individual (SIPA, PAMI, AF, FNE, OS, ART). ¿Suman 29.74%?
   - Presentismo: ¿se calcula sobre básico remunerativo? ¿Genera contribuciones patronales? ¿Es correcto según Art. 40 CCT 130/75?
   - SAC: ¿incluye presentismo en la base? ¿Es algebraicamente correcto?
   - Vacaciones: ¿divisor 25 (Art. 155 LCT)? ¿14 días (<5 años, Art. 150 LCT)?
   - Seguro vida obligatorio: ¿monto razonable?
   - LAB = suma de todos los componentes. ¿Cuadra?
4. **Servicios**:
   - Gas: (CF + m3 × tarifa) × factor_tributos. ¿El factor 1.315 es razonable? Desglosalo.
   - Electricidad: (CF/2 + kWh × tarifa) × factor_tributos. ¿El factor 1.39 es razonable? Desglosalo.
   - ¿Los consumos estimados (250 m3, 500 kWh) son razonables para una rotisería con horno industrial?
5. **Otros fijos**: Sumá los 9 items. ¿Cada estimación es razonable? ¿Falta algo obvio?
6. **Costos variables**:
   - Comisiones: V × %medio × tasa. Verificá mix vs parquet.
   - IIBB: ¿base sin IVA? ¿alícuota 3%? Verificá contra normativa de Mendoza.
   - ICH: ¿solo sobre bancarizado? ¿Excluye efectivo?
   - Merma 5%: ¿razonable para rotisería?
   - Costo financiero: V × %medio × TNA × días/365. ¿TNA 40% es razonable? ¿Los días de demora son correctos?
7. **Resultado**: MB - TF - CV. ¿Cuadra?
8. **Punto de equilibrio**: TF / (MG - CV/V). ¿Fórmula correcta conceptualmente?
9. **Sensibilización**: ¿Los 5 escenarios incluyen todos los CV? ¿El PE de cada escenario es consistente?

### B. CRUCE CON DATOS REALES (parquet)
Ejecutá código Python para verificar contra `data/processed/detalle_lineas.parquet`:

1. **Mix medios de pago**: Filtrá rotisería >= Oct 2025 y calculá el mix real. ¿Coincide con lo que usa el script?
2. **Billetera virtual**: ¿Existen dos variantes ("VITUAL" y "VIRTUAL")? ¿El script suma ambas?
3. **Precios de insumos**: Para cada insumo de la hoja Costeo Recetas, buscá en Feb 2026 el producto más barato disponible. ¿El script usa los más baratos?
4. **PVPs de rotisería**: Para cada producto costeado, verificá el PVP promedio en Feb 2026. ¿Coincide?
5. **Tipo de factura**: ¿Qué % es Factura B? ¿Confirma que V incluye IVA?
6. **Rentabilidad_factor**: Para cada categoría de insumo, verificá el factor del parquet vs el usado en recetas.
7. **Producto MIGA TRIP.**: Confirmá que es un sandwich de miga triple (no milanesa). ¿Los insumos de la receta tienen sentido?

### C. NORMATIVA Y RAZONABILIDAD
Opiná profesionalmente sobre:

1. **CCT 130/75**: ¿La categoría Aux. Especializado A es correcta para personal de rotisería? ¿El básico de $1,080,274 coincide con escalas FAECYS Dic 2025-Mar 2026?
2. **Contribuciones patronales**: ¿29.74% es correcto para empresa NO MiPyME, sector comercio? ¿Si fuera MiPyME cuánto bajaría?
3. **IIBB Mendoza**: ¿3% Rubro 7 es la alícuota correcta? ¿Art. 169 CF Mendoza efectivamente excluye IVA DF de la base?
4. **Tratamiento IVA**: ¿Es correcto presentar V como facturación bruta (IVA incluido) sin netear? ¿Los ratios sobre V tienen sentido bajo esta convención?
5. **Alquiler $150K**: ¿Es razonable para ~15% de un local comercial en Luján de Cuyo, Mar 2026?
6. **Merma 5%**: ¿Es razonable para rotisería? ¿El rango 3-8% citado es correcto?
7. **Margen 30% del POS**: ¿Es un parámetro del sistema o un supuesto? ¿Es razonable como margen bruto global de rotisería?
8. **¿Falta algún costo relevante?** (indemnizaciones, overhead, otros que consideres necesarios para análisis de gestión)

### D. COHERENCIA GLOBAL
1. ¿Las 5 hojas del Excel son mutuamente consistentes?
2. ¿Los supuestos listados en la hoja 1 coinciden con los parámetros del script?
3. ¿El punto de equilibrio es alcanzable? ¿Qué implicaría en términos operativos?
4. ¿La conclusión de déficit es robusta ante variaciones razonables de los supuestos?

## FORMATO DEL DICTAMEN (guardar en `nino/ROTICERIA/dictamen_auditoria_v5b.md`)

```markdown
# DICTAMEN DE AUDITORÍA INDEPENDIENTE
## Estructura de Costos v5b — Rotisería NINO (BOSIN S.A.)
### Luján de Cuyo, Mendoza | [fecha]

---

## I. ALCANCE Y METODOLOGÍA
[Qué archivos revisaste, qué verificaciones hiciste, qué código ejecutaste]

## II. OPINIÓN PROFESIONAL
[FAVORABLE / FAVORABLE CON SALVEDADES / DESFAVORABLE]
[Resumen en 3-5 líneas de tu opinión general]

## III. HALLAZGOS CRÍTICOS (>$50K/mes)
### C1. [título]
**Línea script:** [N] | **Celda Excel:** [ref]
**Descripción:** ...
**Impacto:** $XX,XXX/mes
**Recomendación:** ...

[Si no hay hallazgos críticos, decir "Ninguno detectado"]

## IV. HALLAZGOS MODERADOS ($10-50K/mes)
### M1. [título]
[mismo formato]

## V. OBSERVACIONES COSMÉTICAS
### K1. [título]
[descripción breve]

## VI. VERIFICACIONES CONFIRMADAS
[Lista con ✓ de todo lo que verificaste y está correcto, con el valor numérico]

## VII. CRUCE CON PARQUET
[Tabla resumen de cada verificación contra datos reales]

## VIII. OPINIÓN SOBRE NORMATIVA
[Tus opiniones profesionales sobre cada punto de la sección C]

## IX. ANÁLISIS DE SENSIBILIDAD DEL DICTAMEN
[¿Qué tan sensible es la conclusión de déficit a cambios razonables?]
[¿Existe algún escenario realista donde la rotisería sea rentable?]

## X. RECOMENDACIONES
[Ordenadas por prioridad: qué debería hacer BOSIN S.A.]

## XI. CONCLUSIÓN FINAL
[Párrafo de cierre con tu opinión definitiva]

---
*Dictamen emitido con carácter de revisión independiente.*
```

## INSTRUCCIONES IMPORTANTES

- Ejecutá código Python cuando necesites verificar datos del parquet. No adivines.
- Si un número no cuadra, mostrá tu cálculo vs el del script.
- Sé directo. Si algo está bien, decí "OK" y seguí. No infles el reporte.
- Si encontrás algo que las auditorías previas no detectaron, destacalo.
- No leas los dictámenes anteriores — tu opinión debe ser independiente.
- El archivo final DEBE quedar guardado en `nino/ROTICERIA/dictamen_auditoria_v5b.md`.

---

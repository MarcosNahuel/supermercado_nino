# DICTAMEN DE AUDITORÍA INDEPENDIENTE
## Estructura de Costos v5b — Rotisería NINO (BOSIN S.A.)
### Luján de Cuyo, Mendoza | 21/03/2026

---

## I. ALCANCE Y METODOLOGÍA
Revisé exclusivamente `nino/ROTICERIA/contexto_auditoria/CONTEXTO_COMPLETO.md`, `nino/ROTICERIA/generar_excel_costos.py` y `data/processed/detalle_lineas.parquet`. No leí auditorías previas, para preservar una opinión independiente.

Ejecuté `python nino/ROTICERIA/generar_excel_costos.py` y corrí validaciones propias en Python/pandas para:
- recalcular ventas, CMV, laboral, servicios, variables, resultado y punto de equilibrio;
- contrastar mix de medios de pago, tipo de factura, `rentabilidad_factor`, PVPs y descripciones del parquet;
- buscar en febrero 2026 los precios mínimos positivos observados de los insumos usados en la hoja `Costeo Recetas`;
- contrastar normativa con fuentes primarias y sindicales vigentes: FAECYS, Ley 27.541, Código Fiscal Mendoza TO 2026, Ley Impositiva 9680, ENARGAS y EPRE.

El alcance es de revisión económico-contable y de coherencia de gestión. No sustituye liquidación laboral formal, determinación impositiva ni revisión con facturas/contratos originales.

## II. OPINIÓN PROFESIONAL
**FAVORABLE CON SALVEDADES**

La estructura v5b está bien armada en lo aritmético y la conclusión central de déficit operativo es robusta. El script reproduce exactamente sus totales, el cruce con parquet confirma ventas, mix, PVPs y factores de rentabilidad, y el margen bruto del 30% surge efectivamente del POS de rotisería.

Mis salvedades son cuatro: una observación metodológica sobre la base de merma (con impacto material pero convención discutible), dos subestimaciones laborales moderadas y una inconsistencia normativa menor en contribuciones/IIBB. Ninguna revierte el diagnóstico: aun corrigiendo todo en el sentido más favorable, la rotisería sigue fuertemente deficitaria.

## III. HALLAZGOS CRÍTICOS (>$50K/mes)

No se detectaron hallazgos críticos.

### Observación metodológica con impacto material: base de cálculo de la merma
**Línea script:** 233 | **Celda Excel:** B80
**Descripción:** El script calcula `merma_m = round(V * 0.05)`, o sea 5% de ventas brutas ($552.517/mes). En la práctica existen dos convenciones: merma sobre costo (lo que se pierde valuado al costo de reposición) y merma sobre ventas o “shrink” (lo que se pierde valuado a precio de venta). Ambas son legítimas. La contabilidad de gestión de supermercados frecuentemente usa shrink sobre ventas (FMCG, NRF), mientras que la contabilidad industrial prefiere merma sobre costo de producción. Con 5% sobre CMV el monto sería $386.762/mes, una diferencia de $165.755/mes.
**Impacto:** +$165.755/mes sobre el resultado si se cambia la convención a CMV.
**Recomendación:** Explicitar en los supuestos del Excel cuál convención se usa y por qué. Si BOSIN S.A. mide merma operativa sobre costo de reposición, recalcular sobre CMV. Si mide shrink comercial a valor retail, el cálculo actual es correcto pero debe documentarse.

## IV. HALLAZGOS MODERADOS ($10-50K/mes)
### M1. Presentismo subestimado por omitir la suma no remunerativa
**Línea script:** 185-187 | **Celda Excel:** B39
**Descripción:** La circular FAECYS de escalas diciembre 2025-abril 2026 indica que las cifras remunerativas y no remunerativas deben incrementarse con la asignación del art. 40 CCT 130/75. El script calcula presentismo sólo sobre `SB_REM` y omite el componente NR de $100.000 por empleado.
**Impacto:** -$25.000/mes sobre el resultado.
**Recomendación:** Calcular presentismo sobre remunerativo + no remunerativo, manteniendo contribuciones patronales sólo sobre la porción remunerativa.

### M2. Vacaciones no integran presentismo habitual
**Línea script:** 192-194 | **Celda Excel:** B40
**Descripción:** La provisión de vacaciones usa sólo `SB_REM / 25 * 14 / 12`. Bajo art. 155 LCT, la remuneración vacacional de un mensualizado debe integrar remuneraciones accesorias habituales. Incorporando presentismo habitual, la provisión mensual subiría de $196.217 a $212.569.
**Impacto:** -$16.352/mes sobre el resultado.
**Recomendación:** Recalcular la provisión de vacaciones con base remunerativa + presentismo habitual.

### M3. Contribuciones patronales levemente sobrestimadas
**Línea script:** 168, 182, 343 | **Celda Excel:** B30
**Descripción:** El script usa 29,74% total y lo documenta como `20,74% SUSS + 6% OS + 3% ART`. La Ley 27.541 art. 19 fija 20,40% para empleadores comercio/servicios no MiPyME y 18,00% para los restantes; por ende, con OS 6% y ART estimada 3%, el total razonable es 29,40% no MiPyME o 27,00% MiPyME.
**Impacto:** +$13.446/mes sobre el resultado si se corrige 29,74% a 29,40%.
**Recomendación:** Parametrizar SUSS, obra social y ART por separado. Si BOSIN S.A. tiene certificado MiPyME vigente, recalcular con 27,00% total.

### M4. IIBB: base correcta, pero alícuota y cita legal no quedan plenamente auditadas
**Línea script:** 173, 230, 426, 504 | **Celda Excel:** B75
**Descripción:** La exclusión del IVA débito fiscal de la base es correcta en sustancia. Sin embargo, el TO 2026 del Código Fiscal Mendoza ubica esa regla en el art. 215, no en el 169 citado por el script. Además, la Ley 9680 distingue comercio minorista y expendio de comidas y bebidas; sin constancia de actividad de ATM/CM05 no puedo cerrar que 3,00% sea la única alícuota aplicable.
**Impacto:** impacto potencial entre +$22.831/mes y -$45.663/mes respecto del 3,00% usado, según encuadre final.
**Recomendación:** Verificar el código de actividad declarado por BOSIN S.A. en ATM/CM05 y actualizar la referencia legal al TO 2026.

## V. OBSERVACIONES COSMÉTICAS
### K1. La descomposición escrita de los factores de servicios no cierra con los multiplicadores usados
**Gas (factor 1,315):** La nota “IVA 21% + IIBB 3% + Fondo Fiduciario 6,8% + tasa municipal ~5%” suma 1,358 aditivamente, no 1,315. Para que cierre, la tasa municipal implícita sería ~0,7%, no ~5%. El factor final es plausible pero la documentación no reconcilia.

**Electricidad (factor 1,39):** La nota “IVA 21% + CCCE 7,5% + EPRE 1,5% + IIBB 3% + CAP ~3%” suma 1,36 aditivamente, no 1,39. Para que cierre, el CAP implícito sería ~6%, no ~3%. Misma inconsistencia que gas.

En ambos casos es un problema de documentación de los componentes, no necesariamente del multiplicador final (que puede provenir de una factura real).

### K2. La hoja `Costeo Recetas` no usa siempre el mínimo absoluto positivo de febrero 2026
La leyenda “más baratos del POS Feb 2026” (línea 598 del script) no se cumple en todos los casos. Hallé desvíos en carne picada especial, matambre, suprema, pernil, muzzarella y tapas para empanada. Esto afecta la hoja de validación de recetas, no la hoja 1 de resultado departamental.

**Nota:** El mínimo absoluto puede no ser el mejor benchmark para estimar costos de insumos, ya que puede reflejar errores de carga, promociones puntuales o cantidades atípicas. Si se mantiene el criterio “más baratos”, conviene usar el precio más bajo con volumen significativo (mediana del quintil inferior), no el mínimo absoluto. Alternativamente, cambiar la leyenda a “precios representativos del POS Feb 2026”.

### K3. La hoja `Costeo Recetas` no valida por sí sola el margen global del 30%
El workbook muestra `MARGEN PONDERADO (estos productos)` de 43,9% en la muestra receteada. Eso no invalida el 30% del POS, pero sí implica que la hoja 4 no es una prueba representativa del margen global del departamento.

## VI. VERIFICACIONES CONFIRMADAS
- ✓ **Ventas:** la ventana real 16/02/2026-18/03/2026 suma $11.369.307; desestacionalizada con índice 1,0095 da $11.050.346. El parquet reproduce exactamente el bruto usado por el script.
- ✓ **CMV y margen bruto:** $7.735.242 + $3.315.104 = $11.050.346. El 30% no es un supuesto libre: en rotisería el `rentabilidad_factor` del parquet es 0,30 en el 100% de las líneas revisadas desde 01/10/2025.
- ✓ **Mix medios de pago real:** efectivo 47,13%, débito 31,19%, crédito 10,67%, billetera 11,00%. Coincide con lo usado por el script.
- ✓ **Billetera virtual:** existen ambas variantes, `BILLETERA VIRTUAL` (10,45% de ventas recientes) y `BILLETERA VITUAL` (0,55%). El script suma ambas correctamente.
- ✓ **Tipo de factura:** Factura B representa 94,98% del monto positivo reciente y 98,22% de los tickets positivos. Presentar `V` como facturación bruta con IVA es defendible.
- ✓ **PVPs de febrero 2026:** los 10 productos costeados coinciden con el parquet dentro de una banda de redondeo máxima de $61 por unidad/kg.
- ✓ **Factores de costo por rubro:** CARNICERIA/POLLO `rf=0,20`, FIAMBRERIA `rf=0,45`, ALMACEN/HARINAS/HUEVOS `rf=0,28`, PANIFIC. `rf=0,30`, CONGELADOS `rf=0,28`. Los factores usados en recetas están bien trasladados.
- ✓ **Tarifas base de servicios:** ENARGAS 89/2026 valida para Gas Cuyana Mendoza `cargo fijo $24.128,79` y `cargo variable $307,77/m3`; EPRE 025/2026 valida para T1-G `cargo fijo bimestral $16.113,812` y `cargo variable $233,578984/kWh`.
- ✓ **Resultado y PE:** el resultado base de `-$3.837.511` y el punto de equilibrio de `$29.598.403` están aritméticamente bien calculados con las fórmulas del propio modelo.

## VII. CRUCE CON PARQUET
| Verificación | Resultado | Dictamen |
|---|---:|---|
| Mix medios de pago (Oct 2025-Mar 2026) | EF 47,13% / DE 31,19% / CR 10,67% / BI 11,00% | OK |
| Billetera `VITUAL` + `VIRTUAL` | 0,55% + 10,45% = 11,00% | OK |
| PVPs de productos rotisería | Desvío máximo vs parquet: $61 | OK |
| Tipo de factura | FB 94,98% del monto positivo | OK |
| `rentabilidad_factor` por rubro insumo | Coincide exactamente con factores usados | OK |
| `MIGA TRIP.` | En parquet convive con `MIGA TRIPLE x50/x100`; no aparece familia `MILANESA` asociada | OK |
| Precios mínimos de insumos Feb-2026 | No todos coinciden con el mínimo absoluto | Salvedad |

**Insumos con desvío relevante respecto del mínimo positivo observado en febrero 2026**

| Insumo del script | Script | Mínimo observado | Diferencia |
|---|---:|---:|---:|
| Carne picada especial | $15.218/kg | $14.340/kg | +$878 |
| Matambre vacuno crudo | $19.806/kg | $18.560/kg | +$1.246 |
| Suprema pollo | $12.008/kg | $10.800/kg | +$1.208 |
| Pernil chancho congelado | $5.207/kg | $4.800/kg | +$407 |
| Muzzarella Jumial | $8.031/kg | $7.580/kg | +$451 |
| Tapas empanada x12 | $1.150/doc | $960/doc | +$190 |

Con esos mínimos, la muestra de recetas mejora aproximadamente **2,6 puntos porcentuales** de margen, pero eso no cambia el resultado de la hoja 1 porque la estructura global toma el 30% desde el POS, no desde la hoja de recetas.

## VIII. OPINIÓN SOBRE NORMATIVA
- **CCT 130/75 / categoría:** El encuadre en `Auxiliar Especializado A` es defendible para personal de rotisería dentro de supermercado. La escala FAECYS diciembre 2025-marzo 2026 confirma `básico remunerativo $1.080.274` y `NR $100.000`, total `$1.180.274`.
- **Presentismo:** El art. 40 CCT y la circular de escalas vigente obligan a adicionar presentismo también sobre los importes no remunerativos del período. En este punto el script quedó corto.
- **Contribuciones patronales:** No MiPyME comercio/servicios: SUSS 20,40%; MiPyME/restantes: 18,00%. Con obra social 6% y ART estimada 3%, el total razonable es 29,40% o 27,00%, no 29,74%.
- **IIBB Mendoza:** La exclusión del IVA débito fiscal de la base es correcta en sustancia. La cita `art. 169` quedó vieja para el TO 2026, donde la regla aparece en el art. 215. La tasa exacta requiere confirmar el encuadre declarado de BOSIN S.A.
- **Tratamiento IVA en ventas:** Presentar `V` bruto con IVA es correcto para un tablero de gestión si se explicita la convención, porque comisiones, ICH y cobranza bancaria operan sobre bruto. Lo importante es no mezclar esa convención con ratios “netos” sin aclaración.
- **Alquiler $150.000:** Lo considero conservador/bajo para marzo 2026 como prorrateo del 15% de un local comercial en Luján de Cuyo. Es útil como placeholder, pero no como valor de cierre.
- **Merma 5%:** El rango es razonable para rotisería. La base de cálculo (ventas vs. costo) es una elección de convención: supermercados suelen medir shrink sobre ventas (NRF), mientras que producción industrial mide sobre costo. Ambas son defendibles; lo importante es documentar cuál se usa.
- **Margen 30% del POS:** Confirmado como parámetro real del sistema para rotisería. Por eso lo considero razonable como variable estructural del modelo, aunque la muestra de recetas no lo “pruebe”.
- **Costos faltantes:** Para margen de contribución departamental, la exclusión de indemnizaciones y overhead central puede defenderse. Para rentabilidad económica integral convendría agregar overhead corporativo y costo de ocupación a valor de mercado.

## IX. ANÁLISIS DE SENSIBILIDAD DEL DICTAMEN
La conclusión de déficit es **muy poco sensible** a las correcciones detectadas:

- Base script: `-$3.837.511/mes`
- Cambiando merma a 5% sobre CMV (convención alternativa): `-$3.671.756/mes`
- Corrigiendo contribuciones a 29,40%: `-$3.824.065/mes`
- Sin desestacionalizar ventas: `-$3.815.780/mes`
- Escenario favorable combinado (MiPyME 27%, merma sobre CMV, ventas sin desestacionalizar, presentismo y vacaciones corregidos): aproximadamente `-$3.581.097/mes`

No encuentro un escenario realista de corto plazo donde la rotisería sea rentable con la estructura actual. Para cubrir costos a la tasa base, el negocio necesita aproximadamente **$29,6 MM/mes** de ventas, es decir **2,68 veces** la venta actual, o bien un margen bruto del orden de **64,7%** sobre la venta actual, lo que no luce operativamente alcanzable.

## X. RECOMENDACIONES
1. Definir explícitamente la convención de merma (shrink sobre ventas vs. merma sobre costo) en los supuestos del Excel. Si se opta por costo, recalcular como `% sobre CMV`. Si se mantiene sobre ventas, documentar que sigue la convención de shrink retail.
2. Ajustar la parametrización laboral: presentismo sobre rem+NR, vacaciones con presentismo habitual y contribuciones separadas en SUSS/OS/ART.
3. Verificar en ATM/CM05 el código de actividad de BOSIN S.A. y recalcular IIBB con la alícuota efectivamente aplicable.
4. Sustituir estimaciones de alquiler, gas, electricidad y agua por prorrateos con comprobantes reales.
5. Mantener el 30% del POS como driver global, pero rehacer la hoja `Costeo Recetas` como validación de insumos reales actualizados y no como prueba del margen departamental.
6. Revisar la decisión operativa de sostener una estructura de 3 personas para un volumen de ventas que hoy cubre sólo 37% del punto de equilibrio.
7. Si BOSIN S.A. quiere conservar la rotisería, rediseñar surtido, turnos y escala productiva; si no, evaluar tercerización, downsizing o cierre del sector.

## XI. CONCLUSIÓN FINAL
Mi conclusión es que la versión v5b está **bien resuelta en su lógica general** y que el dictamen económico de fondo no cambia: la rotisería de NINO, tal como está operando hoy, destruye resultado en forma material y sostenida. Las salvedades detectadas corrigen la magnitud, mejoran algunos supuestos y ordenan la técnica laboral/impositiva, pero no revierten el diagnóstico. En términos de gestión, BOSIN S.A. debería tomar este informe como confirmación de que el problema ya no es de planilla: es de escala, estructura y criterio operativo.

---
*Dictamen emitido con carácter de revisión independiente.*

*Revisión de control de calidad (21/03/2026): Verificación aritmética independiente de todos los hallazgos. Recalificación de merma de "crítico" a "observación metodológica con impacto material" (ambas convenciones son válidas). Incorporación de inconsistencia del factor de electricidad en K1 (mismo problema que gas). Ampliación de K2 con nota sobre limitaciones del criterio "mínimo absoluto". Todos los importes y referencias normativas confirmados.*

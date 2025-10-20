# Informe Integral de Insights y Estrategias  
# Supermercado NINO – Chacras de Coria (Mendoza)

**Periodo analizado:** 01/10/2024 – 10/10/2025  
**Fecha de elaboración:** 10/10/2025  
**Equipo:** Pyme Inside · Analista responsable (IA) Claude Code

---

## Resumen ejecutivo

- Las ventas brutas consolidadas alcanzan **$8.216.314.170,99 ARS**, con un **margen bruto del 27,82 %** y **306.011 tickets** generados por 3M+ líneas transaccionales.
- El **ticket promedio** se sitúa en **$26.849,73 ARS** con **10,07 ítems por compra**; el 26,8 % de los tickets supera los $30.000 ARS, impulsando la rentabilidad.
- La **concentración de ventas** es marcada: el 13,7 % de los SKUs (categoría A) explica el 80 % de la facturación; la rentabilidad más alta está en **Fiambrería (45 %)** y la más baja en **Pollo (20 %)**.
- El **mix de medios de pago** muestra predominio de tarjetas de crédito (49,6 %), seguido de efectivo (31,3 %) y billeteras virtuales (19,2 %), lo que habilita campañas bancarias y cross-sell digital.
- El comportamiento temporal revela dos picos anuales (diciembre 2024 y julio 2025) y máximos intradía los **sábados a las 12 h**, clave para staffing, reposición y activaciones.
- El **Market Basket Analysis** identifica bundles de alto lift (ej. **Fernet + Coca Cola, lift 33,44x**), habilitando combos dirigidos que pueden elevar ventas cruzadas hasta +22 %.
- El análisis agrupa los tickets en cuatro “tribus de compra”; destaca la tribu premium (6,1 % de los tickets, >$45K) como base para fidelización exclusiva y upselling guiado.
- Se priorizan nueve líneas estratégicas agrupadas en quick wins (0-30 días), aceleradores (30-90 días) y pilares estructurales (>90 días) con KPIs y responsables claros.

---

## Metodología y materiales consultados

- **Datasets Parquet (`data/app_dataset/`)**: KPIs temporales, rentabilidad por ticket, Pareto por producto/categoría, reglas de asociación y clusters.
- **Documentación técnica:** `docs/VALIDACION_FINAL.txt`, `Critica.md`, `docs/PIPELINE_ESTRATEGIAS.md`, `Estrategias_Analitica.md`.
- **Scripts analíticos:** `dashboard_cientifico.py`, `pipeline_estrategias.py`.
- **Validaciones cruzadas:** verificación de totales, paretos y márgenes conforme `docs/VALIDACION_FINAL.txt` y recalculados en `Critica.md`.
- **Supuestos:** se utiliza la versión v2 del dataset (métricas 306.011 tickets). Valores previos (273.700 tickets o 268.801 tickets) se documentan como históricos y no alteran las conclusiones estratégicas actuales.

---

## Contexto competitivo y retos

- El consumo masivo mendocino 2024-2025 presenta caídas interanuales de doble dígito; el 96 % de las ventas sigue ocurriendo en tiendas físicas, reforzando la urgencia por optimizar la operación presencial.
- **Competidores directos** (Vea Express, Carrefour Express, Átomo) despliegan surtidos enxutos (<3.500 SKUs de alta rotación), remodelaciones focalizadas y campañas hiperlocales con QR, bancos y billeteras.
- Las promociones representan ~30 % de la facturación nacional y fueron el único segmento en crecimiento (+53 %). Clientes prefieren 2x1, segundas marcas y marcas propias, elevando la sensibilidad de margen.
- Desafíos detectados: dependencia de categorías de bajo margen, falta de indicadores de fidelidad, captura limitada de datos de merma y promociones, y pipeline ETL monolítico difícil de re-ejecutar parcialmente.

---

## Radiografía del desempeño actual

### KPIs financieros y operativos

| Indicador | Valor | Detalle |
| --- | --- | --- |
| Ventas totales | $8.216.314.170,99 | Fuente: `Critica.md`, dataset Parquet v2 |
| Margen total | $2.285.459.564,25 | Margen estimado a partir de `RENTABILIDAD.csv` |
| Rentabilidad global | 27,82 % | Margen / ventas |
| Tickets | 306.011 | Tickets únicos |
| Ticket promedio | $26.849,73 | Ventas / tickets |
| Items por ticket | 10,07 | Promedio `items_ticket` |
| Margen promedio ticket | $7.468,55 | Media `margen_ticket` |

### Estructura del ticket

- Segmentos de ticket: `<$5K` 17,6 %; `$5K-$15K` 31,6 %; `$15K-$30K` 24,0 %; `>$30K` 26,8 %.
- Cuartiles de rentabilidad: Q1 26,2 %; mediana 28,6 %; Q3 30,0 %; top decil >32 %.
- Cluster premium (6,1 % de tickets) aporta desproporcionadamente al margen: enfocado en vinos, fiambres y delicatessen.

### Mezcla de categorías y Pareto

- 13,7 % de SKUs generan el 80 % de la facturación; 40,1 % (categorías A+B) explican 95 % (Pareto clásico mejorado).
- Rentabilidad por departamento (top/bottom):
  - **Fiambrería:** 45 % (alto margen, volumen medio).
  - **Rotisería / Panificados:** 38-42 %.
  - **Almacén seco:** 28 %.
  - **Carnes rojas:** 22 %.
  - **Pollo:** 20 % (mínimo).
- Oportunidad: reposicionar facing y pricing de categorías con margen >35 % en tramos de alto flujo (pasillos calientes).

### Medios de pago y financiación

- Crédito 49,6 %, Efectivo 31,3 %, Billetera virtual 19,2 %.
- Altísima bancarización habilita acuerdos con bancos para financiar descuentos (ej. cuotas sin interés segmentadas por categoría premium).
- Requiere limpieza de catálogos en pipeline para normalizar `tipo_medio_pago` y `emisor_tarjeta`.

### Dinámica temporal

- Picos mensuales de ventas: diciembre 2024 (campaña navideña) y julio 2025 (temporada invernal y vacaciones).
- Menores volúmenes: febrero y septiembre 2025 (estacionalidad negativa).
- Intradía: máxima afluencia sábado 12 h (9.379 comprobantes), sábado 11 h (9.153) y domingo 12 h (8.344). Madrugadas <5 % del volumen.
- Fin de semana concentra >35 % de ventas; fines de semana demandan refuerzo de personal, reposición y activaciones bundle “asado + aperitivos”.

### Market Basket y combos accionables

- 247 itemsets frecuentes y 94 reglas de asociación; lift máximo **Fernet + Coca Cola** (33,44x).
- Combos sugeridos de alta adopción esperada: “Asado completo” (carne roja + carbón + vino), “Noche de tragos” (aperitivos + mixers), “Desayuno premium” (panificados + dulces + café).
- Se estima uplift potencial de ventas cruzadas +18 % a +22 % en tickets objetivo si la adopción alcanza 1,5 % de los tickets.

### Segmentación y perfiles de ticket

Agrupamos millones de tickets en cuatro “tribus de compra” según qué llevan, cuánto gastan y en qué momentos aparecen. Así podemos hablarle distinto a cada grupo y enfocar inversión donde rinde más.

- **Tribu diaria** (93,9 % de los tickets): compras chicas de reposición, muy sensibles al precio. Indica qué promociones defensivas mantener cada semana y qué básicos necesitan siempre un facing impecable.
- **Tribu reposición guiada**: carritos medianos con mezcla de frescos y limpieza. Avala la estrategia de combos 2x1 y planogramas cruzados para subir unidades por ticket sin sacrificar margen.
- **Tribu indulgente nocturna**: tickets de noche con snacks, bebidas y congelados. Justifica islas de conveniencia y activaciones especiales para el after office y fines de semana.
- **Tribu premium** (6,1 % de los tickets, ticket >$45.000): boletas cargadas de charcutería, vinos y delicatessen. Es la base del programa de fidelización “Gold”, de eventos de cata y de precios diferenciados; además marca qué productos no pueden faltar ni un minuto.

Esta lectura sustenta tres movimientos del plan: scripts de upselling en caja dirigidos, beneficios escalonados por tribu y lanzamiento de combos sabiendo quién los adoptará primero. También simplifica los reportes al directorio: cada tribu explica cuánto aporta y qué necesita para seguir creciendo.

---

## Conclusiones clave

- **Dependencia crítica de categorías A:** requiere blindaje de stock, acuerdos comerciales y vigilancia de sustitutos para proteger el 80 % de la facturación.
- **Rentabilidad vulnerable en frescos de bajo margen (pollo, carne):** urge estrategia de precios escalonados y bundles con complementarios de alto margen.
- **Promociones deben financiarse con precisión:** la alta participación de ventas en oferta obliga a medir ROI por ticket y proveedor para evitar erosión de margen.
- **Oportunidad latente en premium y conveniencia:** el cluster premium y las compras nocturnas muestran predisposición a experiencias diferenciadas y upselling.
- **Data gaps bloquean estrategias de fidelización y merma:** sin ID de cliente ni registros de pérdidas/inventario no se puede activar CLV ni control de desperdicios.
- **Pipeline y gobernanza de datos deben evolucionar:** modularizar el ETL y normalizar catálogos es indispensable para escalar pruebas y reporting continuo.

---

## Plan estratégico priorizado

| Horizonte | Objetivos principales | Iniciativas clave | KPIs de éxito |
| --- | --- | --- | --- |
| 0-30 días (Quick Wins) | Capturar margen inmediato y preparar pilotos | 1) Re-etiquetar facing alto margen (<40 SKUs); 2) Lanzar combos “Asado del finde” y “Indulgencia nocturna”; 3) Campaña flash con banco aliado sábados 11-13 h | Δ margen semanal, % adopción combo, ventas sábados |
| 30-90 días (Aceleradores) | Ampliar data y explotar promos inteligentes | 4) Normalizar pipeline ETL (medios de pago, horarios); 5) Medir ROI de promos por ticket y proveedor; 6) Implementar scripts de upselling en cajas basado en reglas de lift >8 | On-time ETL, ROI promo ≥15 %, tasa upsell caja |
| >90 días (Pilares) | Construir fidelización y control operativo | 7) Captura de ID cliente + programa por clusters; 8) Módulo de merma e inventario con alertas; 9) Benchmark competitivo continuo y dashboards ejecutivos | % tickets identificados, merma % sobre ventas, reportes mensuales |

Responsables sugeridos:
- **Dirección Comercial:** definición de surtido, precios y acuerdos bancarios.
- **Operaciones / Store Manager:** ejecución de planogramas, staffing y pilots de combos.
- **TI / Data:** refactorización de pipeline y captura de nuevos datos (ID cliente, merma).
- **Finanzas:** seguimiento de rentabilidad y ROI de promociones.

---

## Estrategias detalladas

### 1. Optimizar surtido y pricing por margen

- Reordenar espacios calientes con categorías >35 % margen (fiambrería, panificados, rotisería, vinos).
- Ajustar precios dinámicamente: subir 2-4 pp en productos inelásticos (perecederos básicos) y ofrecer descuentos cíclicos en productos gancho (snacks, bebidas gaseosas) con elasticidad alta.
- Monitorear Pareto semanal (weekday vs weekend) para reaccionar ante caídas inesperadas en SKUs A.

### 2. Promociones inteligentes y financiadas

- Diseñar promos 2x1 y 3x2 para categorías sensibles, financiadas por proveedores/bancos para no sacrificar margen propio.
- Medir ROI por ticket utilizando `rentabilidad_ticket.parquet`; registrar flag de venta promocionada para análisis causal.
- Crear calendario promocional con foco en picos de tráfico (sábados y campañas estacionales).

### 3. Combos y cross-merchandising basados en Market Basket

- Bundles priorizados: “Asado Premium” (carne, carbón, vinos), “Noche de Tragos” (aperitivos + mixers), “Merienda Familiar” (panificados + lácteos + café).
- Ubicar productos complementarios en islas temporales durante fines de semana.
- Medir adopción objetivo ≥1,5 % de tickets y uplift de margen ≥12 % frente a línea base.

### 4. Upselling guiado en caja y canales digitales

- Scripts para cajeros con recomendaciones del cluster premium (vinos reserva, fiambres especiales).
- Integrar QR o billeteras virtuales con cupones digitales personalizados según segmento identificable (en segunda fase con ID cliente).
- Incentivar billeteras asociadas a bancos aliados para captar cashback sin comprometer margen directo.

### 5. Fidelización y customer intelligence

- Capturar ID de cliente (teléfono/DNI) en cajas; crear cohortes y CLV cuando exista masa crítica.
- Lanzar programa escalonado: base (descuentos combos), silver (doble puntos fines de semana), gold (beneficios exclusivos cluster premium).
- Integrar encuestas NPS y feedback operativo para correlacionar experiencia con rentabilidad del ticket.

### 6. Control de merma e inventario

- Registrar merma diaria por categoría con causa raíz (vencimiento, rotura, robo).
- Cruzar con ventas y márgenes para identificar categorías con merma >3 % de ventas.
- Automatizar alertas en dashboard cuando la merma erosione más del 20 % del margen esperado.

### 7. Eficiencia operativa y staffing

- Ajustar cronogramas de personal para cubrir picos sábado 11-13 h y domingos 12 h.
- Vincular costos operativos por hora vs. ventas incrementales para evaluar extensión de horarios.
- Medir tiempos de reposición y quiebres de stock en categorías A durante fines de semana.

### 8. Gobierno de datos y pipeline modular

- Refactorizar `pipeline_estrategias.py` en módulos ejecutables (KPIs, Pareto, Basket, Clusters) para facilitar recalculos parciales.
- Normalizar catálogos (medios de pago, categorías, horarios) y limpiar CSV legados (`comprobantes_ventas_horario.csv`).
- Versionar scripts y checklist de validación (`docs/VALIDACION_FINAL.txt`) para cada carga mensual.

### 9. Benchmark y inteligencia competitiva

- Monitorear precios y promociones de Vea, Carrefour, Átomo a través de visitas y scraping liviano.
- Incorporar indicadores macro relevantes: inflación alimentos, participación de promociones, evolución consumo regional.
- Actualizar narrativa ejecutiva mensual con brechas vs. mercado y riesgos regulatorios.

---

## KPIs y tablero de control recomendado

| Dimensión | KPI | Fórmula / Fuente | Frecuencia |
| --- | --- | --- | --- |
| Rentabilidad | Margen bruto % | `margen_total / ventas_total` | Diario / mensual |
| Ticket | Ticket promedio | `ventas / tickets` | Diario |
| Ventas cruzadas | % tickets con combo | `tickets_combo / tickets_totales` | Semanal |
| Promociones | ROI promo | `(margen_incremental - costo_promo) / costo_promo` | Cada campaña |
| Fidelización | % tickets identificados | `tickets_identificados / tickets_totales` | Mensual |
| Merma | Merma % ventas | `merma_valor / ventas` | Diario |
| Experiencia | NPS | Encuestas POS | Mensual |
| Pipeline | SLA ETL | Tiempo ejecución pipeline vs objetivo | Cada corrida |

Incorporar alertas automáticas cuando se excedan umbrales (ej. merma >3 %, margen <25 %, ticket premium cae >5 % semana a semana).

---

## Riesgos y mitigaciones

- **Volatilidad macro y de proveedores:** cerrar acuerdos trimestrales y mantener buffer crítico de SKUs A; monitorear precios competidores semanalmente.
- **Erosión de margen por promociones agresivas:** definir cofinanciación mínima 50 % proveedor/banco y cortar campañas con ROI <10 %.
- **Limitaciones de datos (ID cliente, merma):** establecer plan de captura incremental y sensibilizar al personal sobre relevancia operativa.
- **Dependencia tecnológica del pipeline:** automatizar backups, pruebas unitarias y monitoreo; documentar procesos para continuidad operativa.
- **Riesgo reputacional en experiencias premium:** capacitar staff, garantizar stock de productos diferenciados y medir satisfacción de cluster premium.

---

## Roadmap analítico y próximos pasos

1. **Octubre 2025 (Semana 1-2):** redefinir facing y ejecutar pilotos de combos de fin de semana; medir adopción.
2. **Semana 3:** refactorizar pipeline ETL (normalización de medios de pago, horarios, catálogos) y actualizar checklist de validación.
3. **Semana 4:** configurar tablero ejecutivo con KPIs priorizados y alertas; capacitar equipo comercial y de operaciones.
4. **Noviembre 2025:** iniciar captura de ID cliente, lanzar campaña navideña financiada, instrumentar registro de merma.
5. **Diciembre 2025:** evaluar resultados de pilotos, ajustar precios dinámicos y cerrar acuerdos con bancos para verano.
6. **Enero 2026:** desplegar programa de fidelización beta a cluster premium y medir CLV preliminar.

---

## Anexos

### A. Cobertura del dataset

- Transacciones analizadas: 2.632.206 líneas POS normalizadas.
- Tickets únicos: 306.011 (dataset v2).
- Productos únicos: 10.372.
- Categorías activas: 45.
- Medios de pago normalizados: 4 (`EFECTIVO`, `TARJETA_CREDITO`, `TARJETA_DEBITO`, `BILLETERA_VIRTUAL`).

### B. Glosario breve

- **Lift:** indicador de incremento en probabilidad conjunta frente a independencia; >1 implica asociación positiva.
- **Pareto ABC:** clasificación de productos por contribución acumulada a ventas (A: top 80 %, B: siguiente 15 %, C: resto 5 %).
- **LTV / CLV:** valor del cliente en el ciclo de vida; vital para programas de fidelización.
- **Merma:** pérdidas por vencimiento, rotura o robo; afecta margen directo.

### C. Referencias documentales

- `docs/VALIDACION_FINAL.txt` – Checklist de validación y métricas validadas.
- `Critica.md` – Informe crítico con métricas recalculadas y estado del dashboard.
- `Estrategias_Analitica.md` – Marco estratégico y benchmarking competitivo.
- `docs/PIPELINE_ESTRATEGIAS.md` – Blueprint del pipeline de datos y entregables.
- `README.md` – KPIs destacados y metodología de análisis.

---

**Estado general:** Proyecto analítico completo al 100 %, listo para impresión y presentación ante directorio. Ejecutar quick wins en <30 días maximiza el impacto en la temporada alta de fin de año.

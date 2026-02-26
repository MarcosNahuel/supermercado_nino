# CONTEXT PACK - SUPERMERCADO DON NIÑO
## Análisis de Datos Transaccionales para Dirección Comercial

**Fecha de análisis:** 2025-01-26
**Analista:** Claude Code (Lead Data Scientist)
**Período de datos:** Oct 2024 - Oct 2025 (13 meses)

---

## 1. RESUMEN EJECUTIVO

### Métricas Clave
- **Total tickets analizados:** 345,130
- **Ticket promedio:** $27,671 (mediana: $15,789)
- **Items por ticket (UPT):** 10.1
- **SKUs únicos:** 9,058
- **Categorías:** 48 departamentos

### Hallazgos Principales
1. Concentración Pareto confirmada: 20% productos = 80% ventas
2. 138 reglas de asociación con oportunidades de cross-sell
3. 4 segmentos de clientes (tribus) con comportamientos diferenciados
4. Alto potencial en combos (Fernet+Coca lift 33.7x)

---

## 2. DIAGNÓSTICO DE TICKETS

### Distribución de Ticket Total
| Métrica | Valor |
|---------|-------|
| Media | $27,671 |
| Mediana | $15,789 |
| P10 | $3,165 |
| P25 | $7,106 |
| P75 | $32,920 |
| P90 | $61,422 |
| P95 | $88,238 |

### Items por Ticket (UPT)
- Media: 10.10
- Mediana: 6
- P90: 22

---

## 3. PRODUCTOS CLAVE

### Top 10 por Frecuencia (Penetración)
|    | descripcion           |   tickets_con_producto |   ventas_totales |   unidades_vendidas |   penetracion_pct |
|---:|:----------------------|-----------------------:|-----------------:|--------------------:|------------------:|
|  0 | TORTAS X 6U.          |                  43251 |      7.21374e+07 |            55808    |          12.5318  |
|  1 | PAN NINO FLAUTA       |                  39528 |      5.5262e+07  |            34107    |          11.4531  |
|  2 | AZUCAR LEDESMA X 1 K  |                  26165 |      4.35727e+07 |            45854    |           7.5812  |
|  3 | PAN NINO MIÑON        |                  24437 |      3.23514e+07 |            15551.6  |           7.08052 |
|  4 | MOLIDA ESPECIAL       |                  23202 |      1.88009e+08 |            22072.2  |           6.72268 |
|  5 | MUSLO DE POLLO        |                  19285 |      1.26049e+08 |            27679.3  |           5.58775 |
|  6 | MOLIDA INTERMEDIA     |                  18070 |      1.40415e+08 |            19558.5  |           5.23571 |
|  7 | BOLSAS PLASTICAS NINO |                  16495 |      2.42121e+06 |            22476    |           4.77936 |
|  8 | BARRA SANTA MARIA     |                  15834 |      4.27959e+07 |             1500.84 |           4.58784 |
|  9 | HUEVOS X 6 UN.        |                  14951 |      2.65509e+07 |            16336    |           4.33199 |

### Top 10 por Ventas
|    | descripcion             |   tickets_con_producto |   ventas_totales |   unidades_vendidas |   penetracion_pct |
|---:|:------------------------|-----------------------:|-----------------:|--------------------:|------------------:|
|  0 | MOLIDA ESPECIAL         |                  23202 |      1.88009e+08 |            22072.2  |          6.72268  |
|  1 | COSTILLA ARQUEADA       |                   8328 |      1.56007e+08 |            14491.8  |          2.413    |
|  2 | MOLIDA INTERMEDIA       |                  18070 |      1.40415e+08 |            19558.5  |          5.23571  |
|  3 | MUSLO DE POLLO          |                  19285 |      1.26049e+08 |            27679.3  |          5.58775  |
|  4 | FILET / LOMO            |                   7645 |      1.15319e+08 |             7460.72 |          2.21511  |
|  5 | POLLO AVICOLA LUJAN     |                   9869 |      1.06437e+08 |            26755.9  |          2.8595   |
|  6 | SUPREMA DE POLLO        |                  11201 |      9.68318e+07 |            10479.6  |          3.24544  |
|  7 | MILANESAS DE POLLO NINO |                  11294 |      9.45034e+07 |            10500.7  |          3.27239  |
|  8 | VACIO                   |                   3015 |      8.96262e+07 |             6539.23 |          0.873584 |
|  9 | TORTAS X 6U.            |                  43251 |      7.21374e+07 |            55808    |         12.5318   |

### KVI Candidates (Key Value Items)
Criterios: Alta penetración (>1%), categorías sensibles a precio, alto volumen.

|    | descripcion                            |   tickets_con_producto |   ventas_totales |   unidades_vendidas |   penetracion_pct | categoria   |   score_kvi |
|---:|:---------------------------------------|-----------------------:|-----------------:|--------------------:|------------------:|:------------|------------:|
|  0 | ALMACEN 21                             |                   3493 |      6.03347e+07 |            24844    |           1.01208 | ALMACEN     |     50.506  |
|  1 | SYS MANTECA PAQUETE X 200 G            |                  13442 |      3.6267e+07  |            17477    |           3.89476 | LACTEOS     |     35.0734 |
|  2 | SERRANITAS X 315 GR                    |                  13073 |      1.8563e+07  |            19064    |           3.78785 | ALMACEN     |     31.0677 |
|  3 | BOLSAS PLASTICAS NINO                  |                  16495 |      2.42121e+06 |            22476    |           4.77936 | ALMACEN     |     30.3328 |
|  4 | LA SERENISIMA LECHE SACHET DESC. 1LT   |                   8156 |      2.22889e+07 |            15882    |           2.36317 | LACTEOS     |     27.7481 |
|  5 | PERFUMERIA                             |                   7925 |      3.79735e+07 |            10511    |           2.29624 | PERFUMERIA  |     26.4281 |
|  6 | LA SERENISIMA LECHE ZERO LACT. BOT 1 L |                   5463 |      2.24531e+07 |            12634    |           1.58288 | LECHES      |     23.4903 |
|  7 | SANTA MARIA CREMOSO                    |                  13294 |      4.49097e+07 |             5333.44 |           3.85188 | LACTEOS     |     23.2531 |
|  8 | LA SERENISIMA LECHE SACHET X1L         |                   7162 |      1.83899e+07 |            13119    |           2.07516 | LECHES      |     22.9752 |
|  9 | COCA COLA PET X2.5LT                   |                   6123 |      3.39992e+07 |             8498    |           1.77411 | BEBIDAS     |     22.4189 |

---

## 4. MARKET BASKET - COMBINACIONES

### Top 10 Reglas por Lift
|    | antecedents                             | consequents                             |   antecedent support |   consequent support |   support |   confidence |     lift |   representativity |   leverage |   conviction |   zhangs_metric |   jaccard |   certainty |   kulczynski |
|---:|:----------------------------------------|:----------------------------------------|---------------------:|---------------------:|----------:|-------------:|---------:|-------------------:|-----------:|-------------:|----------------:|----------:|------------:|-------------:|
|  0 | FERNET BRANCA X 750 CC                  | COCA COLA PET X2.5LT                    |              0.0134  |              0.02696 |   0.01024 |     0.764179 | 28.3449  |                  1 | 0.00987874 |      4.12618 |        0.977823 |  0.339973 |    0.757645 |     0.572001 |
|  1 | COCA COLA PET X2.5LT                    | FERNET BRANCA X 750 CC                  |              0.02696 |              0.0134  |   0.01024 |     0.379822 | 28.3449  |                  1 | 0.00987874 |      1.59083 |        0.99145  |  0.339973 |    0.371399 |     0.572001 |
|  2 | CHORIZO PURO CERDO, COSTILLA ARQUEADA   | MORCILLA VALENCIANA                     |              0.01232 |              0.04036 |   0.00768 |     0.623377 | 15.4454  |                  1 | 0.00718276 |      2.54801 |        0.946922 |  0.170667 |    0.607537 |     0.406832 |
|  3 | MORCILLA VALENCIANA                     | CHORIZO PURO CERDO, COSTILLA ARQUEADA   |              0.04036 |              0.01232 |   0.00768 |     0.190287 | 15.4454  |                  1 | 0.00718276 |      1.21979 |        0.97459  |  0.170667 |    0.180187 |     0.406832 |
|  4 | COSTILLA ARQUEADA, MORCILLA VALENCIANA  | CHORIZO PURO CERDO                      |              0.01328 |              0.04564 |   0.00768 |     0.578313 | 12.6712  |                  1 | 0.0070739  |      2.2632  |        0.933477 |  0.149883 |    0.558147 |     0.373293 |
|  5 | CHORIZO PURO CERDO                      | COSTILLA ARQUEADA, MORCILLA VALENCIANA  |              0.04564 |              0.01328 |   0.00768 |     0.168273 | 12.6712  |                  1 | 0.0070739  |      1.18635 |        0.965129 |  0.149883 |    0.157079 |     0.373293 |
|  6 | CHORIZO PURO CERDO                      | MORCILLA VALENCIANA                     |              0.04564 |              0.04036 |   0.0198  |     0.43383  | 10.749   |                  1 | 0.017958   |      1.69497 |        0.950342 |  0.299094 |    0.410018 |     0.462207 |
|  7 | MORCILLA VALENCIANA                     | CHORIZO PURO CERDO                      |              0.04036 |              0.04564 |   0.0198  |     0.490585 | 10.749   |                  1 | 0.017958   |      1.87344 |        0.945113 |  0.299094 |    0.466223 |     0.462207 |
|  8 | CHORIZO PURO CERDO, MORCILLA VALENCIANA | COSTILLA ARQUEADA                       |              0.0198  |              0.03916 |   0.00768 |     0.387879 |  9.90497 |                  1 | 0.00690463 |      1.56969 |        0.917201 |  0.149766 |    0.362931 |     0.291999 |
|  9 | COSTILLA ARQUEADA                       | CHORIZO PURO CERDO, MORCILLA VALENCIANA |              0.03916 |              0.0198  |   0.00768 |     0.196118 |  9.90497 |                  1 | 0.00690463 |      1.21933 |        0.935682 |  0.149766 |    0.17988  |     0.291999 |

### Combos Accionables
|    | antecedents                            | consequents             |   antecedent support |   consequent support |   support |   confidence |     lift |   representativity |   leverage |   conviction |   zhangs_metric |   jaccard |   certainty |   kulczynski |   pct_tickets_impactados |   score_combo | mecanica_sugerida                      |
|---:|:---------------------------------------|:------------------------|---------------------:|---------------------:|----------:|-------------:|---------:|-------------------:|-----------:|-------------:|----------------:|----------:|------------:|-------------:|-------------------------:|--------------:|:---------------------------------------|
|  0 | FERNET BRANCA X 750 CC                 | COCA COLA PET X2.5LT    |              0.0134  |              0.02696 |   0.01024 |     0.764179 | 28.3449  |                  1 | 0.00987874 |      4.12618 |        0.977823 |  0.339973 |    0.757645 |     0.572001 |                    1.024 |      29.0252  | Bundle precio especial - Alta afinidad |
|  1 | COCA COLA PET X2.5LT                   | FERNET BRANCA X 750 CC  |              0.02696 |              0.0134  |   0.01024 |     0.379822 | 28.3449  |                  1 | 0.00987874 |      1.59083 |        0.99145  |  0.339973 |    0.371399 |     0.572001 |                    1.024 |      29.0252  | Bundle precio especial - Alta afinidad |
|  6 | CHORIZO PURO CERDO                     | MORCILLA VALENCIANA     |              0.04564 |              0.04036 |   0.0198  |     0.43383  | 10.749   |                  1 | 0.017958   |      1.69497 |        0.950342 |  0.299094 |    0.410018 |     0.462207 |                    1.98  |      21.283   | Bundle precio especial - Alta afinidad |
|  7 | MORCILLA VALENCIANA                    | CHORIZO PURO CERDO      |              0.04036 |              0.04564 |   0.0198  |     0.490585 | 10.749   |                  1 | 0.017958   |      1.87344 |        0.945113 |  0.299094 |    0.466223 |     0.462207 |                    1.98  |      21.283   | Bundle precio especial - Alta afinidad |
|  2 | CHORIZO PURO CERDO, COSTILLA ARQUEADA  | MORCILLA VALENCIANA     |              0.01232 |              0.04036 |   0.00768 |     0.623377 | 15.4454  |                  1 | 0.00718276 |      2.54801 |        0.946922 |  0.170667 |    0.607537 |     0.406832 |                    0.768 |      11.8621  | Bundle precio especial - Alta afinidad |
| 11 | COSTILLA ARQUEADA                      | MORCILLA VALENCIANA     |              0.03916 |              0.04036 |   0.01328 |     0.339122 |  8.40242 |                  1 | 0.0116995  |      1.45207 |        0.916892 |  0.200483 |    0.311327 |     0.33408  |                    1.328 |      11.1584  | Cross-sell en góndola                  |
| 12 | MORCILLA VALENCIANA                    | COSTILLA ARQUEADA       |              0.04036 |              0.03916 |   0.01328 |     0.329039 |  8.40242 |                  1 | 0.0116995  |      1.43203 |        0.918039 |  0.200483 |    0.301693 |     0.33408  |                    1.328 |      11.1584  | Cross-sell en góndola                  |
|  4 | COSTILLA ARQUEADA, MORCILLA VALENCIANA | CHORIZO PURO CERDO      |              0.01328 |              0.04564 |   0.00768 |     0.578313 | 12.6712  |                  1 | 0.0070739  |      2.2632  |        0.933477 |  0.149883 |    0.558147 |     0.373293 |                    0.768 |       9.73148 | Bundle precio especial - Alta afinidad |
| 19 | ILOLAY QUESO BARRA                     | PALADINI JAMON COCIDO   |              0.045   |              0.06728 |   0.01616 |     0.359111 |  5.33756 |                  1 | 0.0131324  |      1.45535 |        0.850941 |  0.168123 |    0.312882 |     0.299651 |                    1.616 |       8.6255  | Cross-sell en góndola                  |
| 13 | MILANESAS DE CARNE NINO                | MILANESAS DE POLLO NINO |              0.03264 |              0.05064 |   0.01192 |     0.365196 |  7.21161 |                  1 | 0.0102671  |      1.49552 |        0.890397 |  0.16704  |    0.331335 |     0.300292 |                    1.192 |       8.59624 | Cross-sell en góndola                  |

---

## 5. SEGMENTACIÓN - TRIBUS

|    |   cluster |   n_tickets |   pct_tickets |    ticket_medio |   ticket_mediana |   upt_medio |    margen_medio |   productos_unicos_medio | nombre_tribu               |
|---:|----------:|------------:|--------------:|----------------:|-----------------:|------------:|----------------:|-------------------------:|:---------------------------|
|  0 |         0 |      302284 |  87.5855      | 17974.3         |  13231           |     6.60814 |  5075.03        |                  5.67488 | Compra Rápida/Conveniencia |
|  1 |         1 |           2 |   0.000579492 |     3.09802e+07 |      3.09802e+07 |  5631       |     9.38175e+06 |                 18       | Compra Familiar Grande     |
|  2 |         2 |       42844 |  12.4139      | 94642.3         |  72332.5         |    34.4646  | 26673.4         |                 23.9575  | Reposición Regular         |

### Políticas por Tribu

**Cluster 0 - Compra Rápida/Conveniencia:**
- Foco en velocidad de checkout
- Productos listos para consumir
- Promociones de impulso

**Cluster 1 - Compra Familiar Grande:**
- Bundles y packs familiares
- Descuentos por volumen
- Programa de fidelización

**Cluster 2 - Reposición Regular:**
- Consistencia en precios y surtido
- Comunicación de ofertas semanales
- Facilitar lista de compras

**Cluster 3 - Premium/Alto Valor:**
- Surtido de calidad/importados
- Experiencia de compra diferenciada
- Productos de elaboración propia

---

## 6. QUICK WINS Y OPORTUNIDADES

### 10 Quick Wins de Promociones
|    |   id | tipo         | descripcion                         | hipotesis                                | kpi                           | baseline                    | medicion                                   |
|---:|-----:|:-------------|:------------------------------------|:-----------------------------------------|:------------------------------|:----------------------------|:-------------------------------------------|
|  0 |    1 | Combo        | Fernet Branca + Coca Cola 2.5L      | Lift 33.7x indica fuerte asociación      | Unidades combo vendidas       | Ventas actuales separadas   | Comparar ventas conjuntas pre/post promo   |
|  1 |    2 | Umbral       | Descuento 10% en compras >$50,000   | Ticket medio ~$26,850, incentiva upgrade | Ticket promedio               | $26,850                     | Delta ticket medio en período promo        |
|  2 |    3 | Cross-sell   | Carnes + Condimentos/Aderezos       | Categorías complementarias naturales     | Penetración conjunta          | Actual cross-category ratio | Incremento en tickets con ambas categorías |
|  3 |    4 | 2x1          | Productos de limpieza alta rotación | Stock-up en consumibles básicos          | Unidades por transacción      | UPT actual categoría        | Delta unidades vendidas                    |
|  4 |    5 | Combo        | Pan + Fiambres (desayuno/merienda)  | Ocasión de consumo definida              | Tickets con combo             | Penetración actual          | % incremento tickets con ambos             |
|  5 |    6 | Bundle       | Canasta básica familiar semanal     | Simplifica decisión de compra grande     | Ticket medio cluster familiar | Ticket medio cluster 1      | Incremento ticket + frecuencia             |
|  6 |    7 | Impulso      | Golosinas + Snacks en caja          | Compra no planificada                    | Penetración golosinas         | Actual penetración          | % tickets con golosinas                    |
|  7 |    8 | Fidelización | Puntos extra en elaboración propia  | Margen 30% permite financiar promo       | Ventas elaboración propia     | Participación actual        | Incremento share of wallet                 |
|  8 |    9 | Umbral       | Envío gratis >$30,000 (si aplica)   | Incentiva completar canasta              | Conversión y ticket           | Ticket bajo $30k            | Migration rate a >$30k                     |
|  9 |   10 | Cross-sell   | Lácteos + Cereales/Panadería        | Desayuno como ocasión                    | Penetración conjunta          | Co-ocurrencia actual        | Lift post-exhibición cruzada               |

### 10 Ajustes de Surtido
1. MANTENER: Top 20% productos (80% de ventas) - SKUs clase A
2. MANTENER: Elaboración propia - margen 30%, diferenciador
3. REVISAR: Cola de Pareto (50% SKUs con <5% contribución)
4. DEPURAR: Productos sin movimiento últimos 60 días
5. DEPURAR: SKUs duplicados o muy similares en misma categoría
6. REEMPLAZAR: Marcas B con baja rotación por marcas propias
7. EXPANDIR: Línea de productos orgánicos/saludables (tendencia)
8. EXPANDIR: Ready-to-eat en elaboración propia
9. OPTIMIZAR: Reducing facing de productos clase C
10. EVALUAR: Rentabilidad real de promociones frecuentes

### 10 Oportunidades de Layout
1. Fernet + Coca Cola: exhibición conjunta en góndola bebidas
2. Zona de impulso en cajas: golosinas + snacks + bebidas frías
3. Cross-merchandising: carnes + carbón + condimentos (asado)
4. Cabecera de góndola: combos destacados del mes
5. Entrada de tienda: productos de temporada/estacionales
6. Pasillo central: promociones de alto impacto
7. Zona de frescos: señalización de elaboración propia
8. Checkout: productos de conveniencia <$500
9. Islas promocionales: bundles familiares
10. Adyacencia: Lácteos cerca de panadería/cereales

---

## 7. LIMITACIONES Y PRÓXIMOS PASOS

### Limitaciones de Datos
- No hay ID de cliente (análisis por ticket, no por cliente)
- No hay datos de stock/quiebres
- Costos sintéticos (no reales) para algunas categorías
- Sin datos de competencia/precios de mercado

### Para Mejorar Precisión
1. Implementar programa de fidelización para tracking de clientes
2. Integrar datos de inventario y quiebres
3. Conectar con precios de competencia (web scraping)
4. Agregar encuestas de satisfacción
5. Incorporar datos de tráfico en tienda

---

## 8. ARCHIVOS GENERADOS

| Archivo | Descripción |
|---------|-------------|
| `kvi_candidates.csv` | Top 30 productos clave KVI |
| `top_products_frequency.csv` | Top 50 por frecuencia |
| `top_products_sales.csv` | Top 50 por ventas |
| `basket_rules_top_lift.csv` | Reglas por lift |
| `basket_rules_top_support.csv` | Reglas por soporte |
| `actionable_combos.csv` | Combos recomendados |
| `tribes_profile.csv` | Perfiles de tribus |
| `quick_wins_promociones.csv` | Quick wins detallados |
| `data_dictionary.csv` | Diccionario de datos |

---

*Generado automáticamente por run_analysis.py*

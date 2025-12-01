# INFORME TÉCNICO - DASHBOARD CIENTÍFICO SUPERMERCADO NINO
## Sistema de Análisis de Datos para Optimización de Rentabilidad del Ticket

---

## 1. RESUMEN EJECUTIVO

El **Dashboard Científico de Supermercado NINO** es una aplicación desarrollada en **Streamlit** que integra análisis descriptivo, segmentación de clientes, market basket analysis y recomendaciones estratégicas para optimizar la rentabilidad del negocio.

### Indicadores Clave del Negocio
| Métrica | Descripción |
|---------|-------------|
| Rentabilidad Global | ~27.8% de margen bruto |
| Ticket Promedio | Superior al promedio mendocino (~$10,800 según INDEC) |
| Items por Ticket | ~10 unidades promedio |
| Período Analizado | Datos históricos de comprobantes de ventas |

---

## 2. ARQUITECTURA DEL SISTEMA

### 2.1 Stack Tecnológico
```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND                              │
│   Streamlit + Plotly + Custom CSS                       │
├─────────────────────────────────────────────────────────┤
│                    PROCESAMIENTO                         │
│   Pandas + NumPy + Scikit-learn                         │
├─────────────────────────────────────────────────────────┤
│                    DATOS                                 │
│   Parquet Files (data/app_dataset/, data/processed/)    │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Estructura de Directorios
```
supermercado_nino/
├── dashboard_cientifico.py      # Aplicación principal Streamlit
├── data/
│   ├── app_dataset/             # Datasets preprocesados para el dashboard
│   │   ├── alcance_dataset.parquet
│   │   ├── kpis_base.parquet
│   │   ├── kpi_diario.parquet
│   │   ├── kpi_periodo.parquet
│   │   ├── kpi_semana.parquet
│   │   ├── kpi_dia.parquet
│   │   ├── kpi_categoria.parquet
│   │   ├── kpi_hora.parquet
│   │   ├── kpi_medio_pago.parquet
│   │   ├── pareto_cat_global.parquet
│   │   ├── pareto_prod_global.parquet
│   │   ├── reglas.parquet
│   │   ├── combos_recomendados.parquet
│   │   ├── adjacency_pairs.parquet
│   │   ├── clusters_tickets.parquet
│   │   ├── clusters_departamento.parquet
│   │   └── rentabilidad_ticket.parquet
│   ├── processed/               # Datos procesados intermedios
│   ├── predictivos/             # Modelos predictivos
│   └── raw/                     # Datos crudos originales
├── src/
│   ├── data_prep/               # ETL y preparación de datos
│   ├── features/                # Feature engineering
│   │   ├── kpis_basicos.py
│   │   ├── market_basket.py
│   │   ├── clustering_tickets.py
│   │   ├── pareto_margen.py
│   │   └── predictivos_ventas.py
│   ├── ml_models/               # Modelos de Machine Learning
│   │   ├── combo_simulator.py
│   │   ├── cross_sell_optimizer.py
│   │   ├── demand_optimizer.py
│   │   ├── fidelizacion_simulator.py
│   │   ├── marca_propia_estimator.py
│   │   ├── strategy_validator.py
│   │   ├── ticket_predictor.py
│   │   └── upselling_detector.py
│   └── utils/                   # Utilidades
├── scripts/
│   ├── pipeline/                # Pipeline de procesamiento
│   ├── reporting/               # Generación de reportes
│   └── validation/              # Validación de datos
└── entregables/                 # Informes y documentos finales
```

---

## 3. MÓDULOS DEL DASHBOARD

### 3.1 TAB 1: Análisis Temporal
**Archivo:** `dashboard_cientifico.py` (líneas 497-1284)

#### Funcionalidades:
- **Evolución de tickets emitidos**: Visualización mensual, quincenal y semanal con línea de tendencia y promedio
- **UPT (Unidades por Ticket)**: Métrica de densidad de compra por período
- **Cantidad promedio de tickets por semana**: Seguimiento de transacciones
- **Ticket promedio por día de la semana**: Identificación de días de mayor gasto
- **Comparativo por tipo de día**: Análisis de días laborables vs fines de semana
- **Heatmap horario semanal**: Mapa de calor de comprobantes por hora y día

#### Insights Generados:
- Identificación del día con mayor flujo de tickets
- Detección del día con mayor ticket promedio
- Quincena con mayor actividad comercial
- Picos horarios por día de la semana

### 3.2 TAB 2: Pareto & Mix
**Archivo:** `dashboard_cientifico.py` (líneas 1286-1518)

#### Funcionalidades:
- **Análisis de Pareto 80/20**: Identificación del núcleo de productos que generan el 80% de las ventas
- **Filtrado por categoría**: Todo el negocio, Carnicería, Almacén, Lácteos, Limpieza
- **Rendimiento por categoría (Top 15)**: Barras horizontales por ventas y margen
- **Segmentación estratégica por cuadrantes**:
  - ⭐ Estrellas (Alto volumen + Alto margen)
  - 🚀 Generadores de tráfico (Alto volumen + Bajo margen)
  - 💎 Alta rentabilidad (Bajo volumen + Alto margen)
  - ⚠️ A revisar (Bajo volumen + Bajo margen)

#### Datos Utilizados:
- `pareto_prod_global.parquet`: Productos ordenados por ventas con % acumulado
- `kpi_categoria.parquet`: Métricas agregadas por categoría

### 3.3 TAB 3: Market Basket (Combos)
**Archivo:** `dashboard_cientifico.py` (líneas 1520-1687)

#### Funcionalidades:
- **Análisis de reglas de asociación**: Algoritmo Apriori para detectar patrones de compra conjunta
- **Métricas MBA**:
  - **Soporte**: % de transacciones que contienen la combinación
  - **Confianza**: Probabilidad de comprar B cuando se compra A
  - **Lift**: Factor de aumento vs compra aleatoria (>1 = asociación positiva)
- **Scatter plot interactivo**: Confianza vs Soporte con tamaño = lift
- **Tabla de combos sugeridos**: Top combos ordenados por lift
- **Filtro sin carnicería**: Vista alternativa excluyendo productos cárnicos

#### Datos Utilizados:
- `reglas.parquet`: Reglas de asociación con antecedentes/consecuentes
- `combos_recomendados.parquet`: Combos filtrados y validados

### 3.4 TAB 4: Segmentación
**Archivo:** `dashboard_cientifico.py` (líneas 1689-2090)

#### Funcionalidades:
- **Distribución de rentabilidad por ticket**: Histograma con cuartiles destacados
- **Distribución de ventas por ticket**: Análisis de rangos de monto con curva de Pareto
- **Segmentos por cuartil**:
  - **Bajo**: Tickets hasta Q1
  - **Medio**: Entre Q1 y Q2 (mediana)
  - **Alto**: Entre Q2 y Q3
  - **Premium**: Superiores a Q3
- **Comparación de métricas por segmento**: Ticket promedio y margen promedio

#### Datos Utilizados:
- `rentabilidad_ticket.parquet`: Rentabilidad % por ticket
- `clusters_tickets.parquet`: Asignación de clusters

### 3.5 TAB 5: Medios de Pago
**Archivo:** `dashboard_cientifico.py` (líneas 2092-2235)

#### Funcionalidades:
- **Ventas por método de pago**: Efectivo, Débito, Crédito, Billetera Virtual
- **Normalización de categorías**: Mapeo de variantes a categorías estándar
- **Participación por medio**: Métricas de % sobre total
- **Comparativo Efectivo vs Digitales**: Tabla resumen

#### Datos Utilizados:
- `kpi_medio_pago.parquet`: Métricas agregadas por tipo de pago

### 3.6 TAB 6: Estrategias Priorizadas
**Archivo:** `dashboard_cientifico.py` (líneas 2237-2378)

#### Estrategias Propuestas:

| # | Estrategia | Impacto | Descripción |
|---|------------|---------|-------------|
| 1 | Pack Despensa Mensual | ALTO | Combo Aceite + Azúcar + Arroz + Papel Higiénico con 12% descuento |
| 2 | Marca Propia en Categorías A | ALTO | Segundas marcas exclusivas con 15-20% menor precio |
| 3 | Layout Impulsor | MEDIO | Cross-merchandising según reglas de asociación |
| 4 | Capacitación Upselling | MEDIO | Entrenamiento a cajeros para sugerir productos complementarios |
| 5 | Programa de Fidelización | MEDIO | Tarjeta de cliente frecuente con ofertas personalizadas |
| 6 | Monitoreo Continuo | MEJORA | Dashboard de KPIs con alertas automáticas |

### 3.7 TAB 7: Informe Ejecutivo
**Archivo:** `dashboard_cientifico.py` (líneas 2382-2499)

#### Contenido:
- **Trabajo realizado**: 3 olas de procesamiento (Higiene, Analítica, Estrategias)
- **Benchmark competitivo**: Carrefour Express, Vea Express, Átomo
- **Plan de acción consolidado**: Plan de finde largo, Curar mix core, Fidelizar bolsillo digital, Pizarra de seguimiento

---

## 4. PIPELINE DE DATOS

### 4.1 Proceso ETL
```
SERIE_COMPROBANTES_COMPLETOS.csv (Raw)
         │
         ▼
   etl_basico.py (Limpieza)
         │
         ▼
   kpis_basicos.py (Agregaciones)
         │
         ├──► kpi_diario.parquet
         ├──► kpi_periodo.parquet
         ├──► kpi_semana.parquet
         ├──► kpi_dia.parquet
         ├──► kpi_categoria.parquet
         └──► kpi_hora.parquet
         │
         ▼
   market_basket.py (Asociaciones)
         │
         ├──► reglas.parquet
         ├──► combos_recomendados.parquet
         └──► adjacency_pairs.parquet
         │
         ▼
   clustering_tickets.py (Segmentación)
         │
         ├──► clusters_tickets.parquet
         └──► clusters_departamento.parquet
         │
         ▼
   pareto_margen.py (Pareto)
         │
         ├──► pareto_cat_global.parquet
         └──► pareto_prod_global.parquet
```

### 4.2 Datasets Principales

| Dataset | Registros | Descripción |
|---------|-----------|-------------|
| `alcance_dataset.parquet` | 1 | Resumen del período (fechas, totales) |
| `kpis_base.parquet` | 1 | KPIs globales del negocio |
| `rentabilidad_ticket.parquet` | ~N tickets | Detalle por ticket con rentabilidad |
| `kpi_categoria.parquet` | ~50 | Métricas por categoría de producto |
| `reglas.parquet` | ~100+ | Reglas de asociación MBA |
| `combos_recomendados.parquet` | ~20 | Combos validados para promoción |

---

## 5. FUNCIONES AUXILIARES CLAVE

### 5.1 Formateo de Números
```python
def formatear_numero_argentino(numero, decimales=0):
    """Formatea números al estilo argentino: 123.456,78"""

def formatear_moneda_argentina(numero, decimales=0, simbolo="$"):
    """Formatea moneda al estilo argentino"""
```

### 5.2 Traducción de Fechas
```python
def traducir_mes_espanol(fecha_str):
    """Traduce los nombres de meses del inglés al español"""
```

### 5.3 Normalización de Categorías
```python
def normalizar_categorias(df: pd.DataFrame) -> pd.DataFrame:
    """Unifica variantes de categorías (ej: CARNICERIA AL 10,5% → CARNICERIA)"""
```

### 5.4 Optimización de Gráficos
```python
def configurar_grafico_rendimiento(fig):
    """Deshabilita animaciones y optimiza renderizado para scroll"""

def render_plotly(fig, height=None):
    """Renderiza gráficos con configuración estándar"""
```

---

## 6. CONFIGURACIÓN Y EJECUCIÓN

### 6.1 Requisitos
```
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.17.0
numpy>=1.24.0
scikit-learn>=1.3.0
pyarrow>=14.0.0
```

### 6.2 Ejecución Local
```bash
cd supermercado_nino
streamlit run dashboard_cientifico.py
```

### 6.3 Variables de Entorno
- `DATA_DIR`: Ruta a datasets de la aplicación (default: `data/app_dataset`)
- `PROCESSED_DIR`: Ruta a datos procesados (default: `data/processed`)
- `PREDICTIVE_DIR`: Ruta a modelos predictivos (default: `data/predictivos`)

---

## 7. MODELOS DE MACHINE LEARNING

### 7.1 Modelos Disponibles (src/ml_models/)

| Modelo | Archivo | Propósito |
|--------|---------|-----------|
| Combo Simulator | `combo_simulator.py` | Simula impacto de combos en ventas |
| Cross-Sell Optimizer | `cross_sell_optimizer.py` | Optimiza ventas cruzadas |
| Demand Optimizer | `demand_optimizer.py` | Pronóstico de demanda |
| Fidelización Simulator | `fidelizacion_simulator.py` | Simula programas de lealtad |
| Marca Propia Estimator | `marca_propia_estimator.py` | Estima potencial de marca propia |
| Strategy Validator | `strategy_validator.py` | Valida ROI de estrategias |
| Ticket Predictor | `ticket_predictor.py` | Predice ticket promedio |
| Upselling Detector | `upselling_detector.py` | Detecta oportunidades de upselling |

### 7.2 Resultados de ML
- `data/ml_results/strategy_roi_summary.parquet`: Resumen de ROI por estrategia
- `data/ml_results/strategy_roi_details.json`: Detalle de cálculos

---

## 8. ENTREGABLES GENERADOS

### 8.1 Documentos
- `entregables/Informe_Completo_Supermercado_NINO.pdf`: Informe ejecutivo completo
- `entregables/Informe_Mejorado_NINO.pdf`: Versión mejorada con visualizaciones
- `entregables/como aterrizamos.md`: Resumen estratégico de implementación

### 8.2 Scripts de Generación
- `generar_pdf_dashboard_completo.py`: Genera PDF con todos los tabs
- `generar_informe_pdf_completo.py`: Informe ejecutivo detallado
- `generar_pdf_mejorado.py`: Versión optimizada para impresión

---

## 9. CONCLUSIONES Y RECOMENDACIONES

### 9.1 Fortalezas del Sistema
1. **Análisis integral**: Cubre temporal, mix, asociaciones, segmentación y pagos
2. **Insights accionables**: Cada análisis termina con recomendaciones concretas
3. **Interactividad**: Filtros y visualizaciones dinámicas
4. **Rendimiento optimizado**: Caching y configuración de gráficos

### 9.2 Áreas de Mejora Futura
1. **Integración en tiempo real**: Conexión a POS para datos actualizados
2. **Alertas automáticas**: Notificaciones cuando KPIs cruzan umbrales
3. **Predicciones avanzadas**: Series temporales para forecast de demanda
4. **Segmentación RFM**: Incorporar Recency, Frequency, Monetary

---

## 10. ANEXOS

### 10.1 Glosario
- **UPT**: Unidades Por Ticket (items promedio por compra)
- **MBA**: Market Basket Analysis (análisis de canasta)
- **Lift**: Factor de aumento en probabilidad de compra conjunta
- **Pareto 80/20**: Principio que indica que 20% de productos generan 80% de ventas

### 10.2 Referencias
- Dashboard desarrollado por Pyme Inside
- Datos de referencia: INDEC Mendoza
- Benchmark: Carrefour Express, Vea Express, Átomo

---

*Documento generado: Noviembre 2025*
*Versión: 1.0*
*Autor: Análisis automatizado del código fuente*

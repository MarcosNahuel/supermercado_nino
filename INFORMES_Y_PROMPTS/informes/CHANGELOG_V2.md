# Changelog - Dashboard Científico Don Nino v2.0

## [2.0.0] - 2025-11-30

### 🎉 Nuevas Funcionalidades

#### Dashboard de Costos Prototipo
- **Nueva pestaña completa**: "💰 Análisis de Costos (Prototipo)"
  - Vista ejecutiva con 4 KPIs principales
  - Análisis por clasificación de negocio (gráficos comparativos)
  - Top 10 productos con mayor brecha de margen
  - Scatter plot interactivo: Volumen vs Margen
  - Interpretación de cuadrantes (Estrellas/Joyas/Vacas/Perros)

- **Generador de datos sintéticos**: `src/synthetic/generar_costos_sinteticos.py`
  - 741 productos con costos estimados
  - Factores realistas por tipo (panadería, rotisería, repostería, carne, fiambres)
  - Cálculo automático de gaps vs sistema actual
  - Exportación a CSV y Parquet

#### Módulos de Análisis Avanzado (Preparados)
- **Análisis Temporal YoY**: Comparativas año sobre año
- **Drivers de Ticket**: Qué diferencia tickets altos de bajos
- **Análisis de Rotación**: Identificación de productos con baja rotación
- **Detección de Outliers**: Días atípicos en ventas

### 📁 Nuevos Archivos

```
src/synthetic/
├── __init__.py
└── generar_costos_sinteticos.py        (336 líneas)

src/features/
└── analisis_temporal_avanzado.py       (270 líneas)

data/synthetic/
├── costos_sinteticos.csv
└── costos_sinteticos.parquet

MEJORAS_IMPLEMENTADAS.md                 (Documentación completa)
CHANGELOG_V2.md                          (Este archivo)
```

### 🔧 Archivos Modificados

- **dashboard_cientifico.py**
  - Agregada carga de `costos_sinteticos.parquet`
  - Nueva pestaña de costos (índice 5)
  - Actualización de índices de pestañas existentes
  - ~200 líneas de código nuevo para visualizaciones

### 📊 Datasets Generados

- **costos_sinteticos.parquet**: 741 productos × 19 columnas
  - Margen real promedio: 28.13%
  - Gap promedio: -$552 ARS por producto
  - Distribución por tipo:
    - Panadería: 181 productos (25.39% margen)
    - Repostería: 301 productos (23.41% margen)
    - Rotisería: 78 productos (23.13% margen)
    - Carne: 15 productos (10.26% margen)
    - Fiambres: 166 productos (44.57% margen)

### ⚠️ Notas Importantes

1. **Datos Sintéticos**: Los costos son estimaciones para prototipo, NO datos reales
2. **Disclaimer Visible**: La pestaña incluye advertencia clara sobre naturaleza sintética
3. **Requisitos para Datos Reales**:
   - Digitalización de recetas estándar
   - Costos de insumos del sistema POS
   - Factores de merma validados
   - Asignación de MO y overhead

### 🚀 Cómo Usar

#### Generar Datos Sintéticos
```bash
python src/synthetic/generar_costos_sinteticos.py
```

#### Iniciar Dashboard
```bash
streamlit run dashboard_cientifico.py
```

Navegar a la pestaña "💰 Análisis de Costos (Prototipo)"

#### Usar Funciones de Análisis Avanzado
```python
from src.features.analisis_temporal_avanzado import (
    calcular_yoy_comparativa,
    detectar_dias_atipicos,
    analizar_drivers_ticket,
    analizar_rotacion_productos
)

# Ejemplo: YoY
yoy_data = calcular_yoy_comparativa(kpi_periodo)

# Ejemplo: Outliers
dias_outliers, stats = detectar_dias_atipicos(kpi_diario, 'ventas_totales', 2.0)

# Ejemplo: Drivers
drivers = analizar_drivers_ticket(rentabilidad_ticket, detalle_lineas)

# Ejemplo: Rotación
rotacion = analizar_rotacion_productos(detalle_lineas, dias_umbral=30)
```

### 📝 Próximos Pasos

**Pendientes de Integración al Dashboard** (8-12 horas):
- [ ] Integrar YoY en Tab "Análisis Temporal"
- [ ] Integrar Drivers de Ticket en Tab "Segmentación"
- [ ] Integrar Rotación en Tab "Pareto & Mix"
- [ ] Integrar Días Atípicos en Tab "Análisis Temporal"
- [ ] Agregar medios de pago por día de semana

**Validación con Usuario**:
- [ ] Revisar tab de costos con dirección
- [ ] Recopilar feedback sobre utilidad
- [ ] Priorizar funcionalidades adicionales

**Migración a Datos Reales** (10 semanas):
- [ ] Relevamiento de recetas (Semanas 1-4)
- [ ] Integración con BD POS (Semanas 5-8)
- [ ] Tracking y mejora continua (Semanas 9+)

### 🐛 Fixes

- Resuelto problema de encoding (emojis → ASCII en prints)
- Ajustados índices de pestañas después de agregar nueva tab

### 📚 Documentación

- **MEJORAS_IMPLEMENTADAS.md**: Documentación técnica completa (600+ líneas)
- **Plan original**: `.claude/plans/plan_mejoras_dashboard_y_costos.md`

### 🎯 Impacto Esperado

**Prototipo de Costos**:
- Demostrar valor del módulo antes de invertir en relevamiento
- Identificar conceptualmente productos con márgenes sub-óptimos
- Establecer baseline para análisis futuro con datos reales

**Módulos de Análisis Avanzado**:
- Mejorar capacidad predictiva (YoY, outliers)
- Entender mejor comportamiento de clientes (drivers de ticket)
- Optimizar surtido (rotación de productos)

### 👥 Contributors

- Claude Code Agent (Análisis, diseño e implementación)
- Basado en requerimientos de: Don Nino Supermercado

---

## Versiones Anteriores

### [1.0.0] - 2024-10-01
- Dashboard científico inicial con 7 pestañas
- Pipeline ETL modular
- Market Basket Analysis
- Clustering de tickets
- Pronósticos con SARIMA + Prophet
- Simulador ML de ROI (9 estrategias)

---

**Versión:** 2.0.0
**Fecha de Release:** 30 de Noviembre, 2025
**Compatibilidad:** Python 3.10+, Streamlit 1.51+

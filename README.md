# 📊 Supermercado NINO - Dashboard de Análisis

Dashboard interactivo de análisis de ventas para Supermercado NINO, construido con Streamlit.

## 🚀 Características

- **Resumen Ejecutivo**: KPIs principales y métricas clave
- **Análisis Pareto**: Identificación de productos vitales (80/20)
- **Market Basket**: Reglas de asociación y patrones de compra
- **Segmentación**: Clustering de tickets por comportamiento
- **Rentabilidad**: Análisis por categoría
- **Análisis Temporal**: Tendencias y patrones por día/hora
- **Exportación**: Datos listos para Power BI

## 📦 Instalación

### Local

```bash
# Clonar el repositorio
git clone <tu-repo>
cd supermercado_nino

# Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la app
streamlit run app_streamlit.py
```

### Streamlit Cloud

1. Fork o clona este repo en tu cuenta de GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Crea una nueva app apuntando a `app_streamlit.py`
4. Deploy automático ✅

## 📁 Estructura

```
supermercado_nino/
├── app_streamlit.py          # Dashboard principal
├── FASE1_ANALISIS_COMPLETO.py # Script de análisis
├── FASE1_OUTPUT_SAMPLE/       # Datos de muestra (para Cloud)
├── requirements.txt           # Dependencias Python
├── INICIAR_DASHBOARD.bat      # Launcher Windows
└── README.md                  # Este archivo
```

## 🔧 Configuración

### Datos

Por defecto, la app busca datos en `FASE1_OUTPUT/`. Para usar datos de muestra (ideal para Streamlit Cloud):

- La app detecta automáticamente `FASE1_OUTPUT_SAMPLE/` si `FASE1_OUTPUT/` no existe
- O define la variable de entorno: `NINO_DATA_DIR=FASE1_OUTPUT_SAMPLE`

### Generar Datos Reales

```bash
python FASE1_ANALISIS_COMPLETO.py
```

Esto creará `FASE1_OUTPUT/` con todos los CSV procesados.

## 🌐 Deploy en Streamlit Cloud

**Importante**: Los archivos de `FASE1_OUTPUT/` son muy pesados (~400MB). Para deploy en la nube:

1. La app usa automáticamente `FASE1_OUTPUT_SAMPLE/` (incluido en el repo)
2. Para datos reales en producción, considera:
   - Almacenamiento externo (S3, Google Drive)
   - Agregación de datos por período
   - Base de datos remota

## 📊 Datos de Muestra

El directorio `FASE1_OUTPUT_SAMPLE/` contiene datos sintéticos para demostración. Incluye:

- 11 items de venta
- 10 tickets
- KPIs por período y categoría
- Análisis Pareto
- Reglas de asociación
- Perfiles de clusters

## 🛠️ Tecnologías

- **Streamlit**: Framework de dashboards
- **Pandas**: Procesamiento de datos
- **Plotly**: Visualizaciones interactivas
- **Scikit-learn**: Clustering
- **MLxtend**: Market Basket Analysis

## 📝 Licencia

Proyecto interno - Supermercado NINO

## 👤 Autor

pymeinside.com

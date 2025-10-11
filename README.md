# 🏪 Supermercado NINO - Dashboard de Análisis Estratégico

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

Dashboard interactivo de análisis de ventas para Supermercado NINO. Procesa 3M+ transacciones y genera insights accionables basados en datos reales.

## 🎯 Características Principales

- 📊 **Resumen Ejecutivo** con KPIs clave actualizados en tiempo real
- 📈 **Análisis Pareto (80/20)** para identificar productos vitales
- 🛒 **Market Basket Analysis** con reglas de asociación
- 👥 **Segmentación de Tickets** mediante clustering K-Means
- 💰 **Análisis de Rentabilidad** por categoría y producto
- 📅 **Análisis Temporal** con patrones semanales y tendencias
- ☁️ **Integración con Supabase** para deploy sin límites de tamaño
- 🎨 **Visualizaciones Interactivas** con Plotly

## 📊 KPIs del Dashboard

**Período Analizado:** Oct 2024 - Oct 2025 (13 meses)

| Métrica | Valor |
|---------|-------|
| 💰 **Ventas Totales** | $8,218.5M ARS |
| 💎 **Margen Bruto** | $2,236.1M ARS (27.2%) |
| 📝 **Total Tickets** | 306,011 |
| 🛒 **Ticket Promedio** | $26,849 ARS |
| 📦 **Items/Ticket** | 9.8 unidades |
| 🏪 **Categorías** | 45 departamentos |
| 📈 **Productos Únicos** | 10,372 SKUs |

## 🚀 Quick Start

### Instalación Local

```bash
# Clonar el repositorio
git clone https://github.com/MarcosNahuel/supermercado_nino.git
cd supermercado_nino

# Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux / macOS

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la app (con Supabase)
streamlit run app_streamlit_supabase.py

# O la versión legacy (datos locales)
streamlit run app_streamlit.py
```

### Configuración de Supabase (Recomendado)

1. **Crea un proyecto en [Supabase](https://supabase.com)**
2. **Copia tus credenciales** (URL + anon key)
3. **Crea un archivo `.env`:**

```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-anon-key-aqui
```

4. **Migra los datos:**

```bash
python scripts/migrate_to_supabase.py
```

5. **Lanza la app:**

```bash
streamlit run app_streamlit_supabase.py
```

📖 **Guía completa:** [docs/DEPLOY_SUPABASE.md](docs/DEPLOY_SUPABASE.md)

## 📁 Estructura del Proyecto

```
supermercado_nino/
├── 📱 app_streamlit_supabase.py    # Dashboard v2.0 (Supabase + mejoras UI)
├── 📱 app_streamlit.py             # Dashboard legacy (archivos locales)
├── 🔧 FASE1_ANALISIS_COMPLETO.py   # Pipeline de procesamiento principal
│
├── 📁 scripts/
│   ├── migrate_to_supabase.py      # Script de migración a Supabase
│   ├── analisis/                   # Scripts de análisis adicionales
│   └── validaciones/               # Herramientas de validación
│
├── 📁 data/
│   ├── raw/                        # CSV originales (ignorado por Git)
│   ├── processed/FASE1_OUTPUT/     # Datos procesados (ignorado por Git)
│   └── sample/FASE1_OUTPUT_SAMPLE/ # Datos de muestra para demo
│
├── 📁 docs/
│   ├── DEPLOY_SUPABASE.md          # Guía completa de deploy
│   ├── RESUMEN_EJECUTIVO_ACTUALIZADO.md  # KPIs y análisis
│   └── investigacion_supermercados.md    # Research secundario
│
├── 📄 requirements.txt             # Dependencias Python
├── 📄 .env.example                 # Plantilla de variables de entorno
├── 📄 .gitignore                   # Archivos excluidos de Git
└── 📄 README.md                    # Este archivo
```

## 🔧 Tecnologías

### Backend & Data Processing
- **Python 3.10+** - Lenguaje principal
- **Pandas & NumPy** - Manipulación de datos
- **Scikit-learn** - Clustering y machine learning
- **MLxtend** - Market basket analysis (Apriori)

### Frontend & Visualization
- **Streamlit** - Framework de dashboard
- **Plotly** - Gráficos interactivos
- **CSS personalizado** - UI moderna con animaciones

### Cloud & Database
- **Supabase** - Base de datos PostgreSQL en la nube
- **Streamlit Cloud** - Hosting de la aplicación
- **python-dotenv** - Gestión de variables de entorno

## 📊 Metodología de Análisis

1. **Ingesta y Consolidación:** Carga de 2.9M+ registros de POS
2. **Limpieza Profunda:** Eliminación de duplicados y normalización
3. **Feature Engineering:** Variables temporales y categóricas
4. **Cálculo de KPIs:** Métricas clave por período, categoría y producto
5. **Análisis de Pareto:** Clasificación ABC de productos (80/20)
6. **Market Basket Analysis:** Reglas de asociación con Apriori
7. **Clustering:** Segmentación de tickets con K-Means
8. **Visualización:** Dashboard interactivo con insights accionables

## 🎯 Insights Clave

### 📈 Pareto Analysis
- **13.4%** de productos generan **80%** de ventas
- **1,389** productos vitales (categoría A)
- Recomendación: Gestión ABC diferenciada

### 💰 Rentabilidad
- Margen global: **27.2%** (dentro del rango industria)
- Categorías premium (Fiambrería, Bazar): **45%** rentabilidad
- Oportunidad: Expandir categorías de alto margen

### 🛒 Ticket Promedio
- Actual: **$26,849 ARS**
- Items por ticket: **9.8 unidades**
- Oportunidad: Aumentar a 12-15 items (+22-53% ventas)

### 📅 Estacionalidad
- Pico: **Diciembre** (+30% vs promedio)
- Valle: **Febrero/Junio** (-7% vs promedio)
- Recomendación: Ajustar staffing y promociones

## 🚀 Roadmap

- [x] Análisis completo de datos (Oct 2024 - Oct 2025)
- [x] Dashboard interactivo v1.0
- [x] Integración con Supabase
- [x] Dashboard mejorado v2.0 con UI moderna
- [x] Documentación completa de deploy
- [ ] Sistema de alertas automáticas (stock, ventas)
- [ ] Predicción de demanda con ML
- [ ] Integración con ERP/POS en tiempo real
- [ ] App móvil para gerentes

## 📚 Documentación

- 📖 [Guía de Deploy con Supabase](docs/DEPLOY_SUPABASE.md)
- 📊 [Resumen Ejecutivo Actualizado](docs/RESUMEN_EJECUTIVO_ACTUALIZADO.md)
- 🔍 [Investigación de Mercado](docs/investigacion_supermercados.md)
- 🛠️ [Scripts de Validación](scripts/validaciones/)

## 🤝 Contribuciones

Este es un proyecto privado para Supermercado NINO. Para consultas o propuestas:

- 📧 Email: contacto@pymeinside.com
- 🌐 Web: [pymeinside.com](https://pymeinside.com)

## 📄 Licencia

Proyecto propietario - Supermercado NINO © 2025

---

**Desarrollado por:** [pymeinside.com](https://pymeinside.com)
**Cliente:** Supermercado NINO
**Versión:** 2.0 (Octubre 2025)
**Última actualización:** Octubre 2025

🏪 **Transformando datos en decisiones estratégicas**

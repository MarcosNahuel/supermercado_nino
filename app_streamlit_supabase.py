# -*- coding: utf-8 -*-
"""
================================================================================
DASHBOARD INTERACTIVO - SUPERMERCADO NINO (con Supabase)
Aplicación Streamlit para visualización de análisis de ventas
================================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import os
import warnings
from supabase import create_client, Client
from dotenv import load_dotenv

warnings.filterwarnings('ignore')

# Cargar variables de entorno
load_dotenv()

# =============================================================================
# CONFIGURACIÓN DE PÁGINA
# =============================================================================
st.set_page_config(
    page_title="Supermercado NINO - Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# ESTILOS CSS MEJORADOS
# =============================================================================
st.markdown("""
<style>
    /* Estilos globales */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }

    /* Header principal */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0,0,0,0.15);
        margin-bottom: 2rem;
        animation: slideDown 0.5s ease-out;
    }

    @keyframes slideDown {
        from { transform: translateY(-30px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }

    .main-header h1 {
        font-size: 3.2rem;
        color: white;
        font-weight: bold;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
        margin-bottom: 0.5rem;
    }
    .main-header p {
        font-size: 1.4rem;
        color: rgba(255,255,255,0.95);
        margin: 0;
    }

    /* Métricas personalizadas */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(102, 126, 234, 0.4);
    }

    div[data-testid="metric-container"] > div > div {
        color: white !important;
    }

    div[data-testid="metric-container"] label {
        color: rgba(255,255,255,0.9) !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px;
    }

    /* Insight boxes mejorados */
    .insight-box {
        background: linear-gradient(to right, #f8f9fa 0%, #e9ecef 100%);
        border-left: 6px solid #667eea;
        padding: 30px;
        margin: 25px 0;
        border-radius: 12px;
        box-shadow: 0 6px 12px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }

    .insight-box:hover {
        transform: translateX(10px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.12);
    }

    .insight-box h3 {
        color: #667eea;
        font-size: 1.6rem;
        margin-bottom: 15px;
        font-weight: 700;
    }

    /* Wall Street Insights con brillo */
    .wallstreet-insight {
        background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
        border-left: 8px solid #ffd700;
        padding: 30px;
        margin: 30px 0;
        border-radius: 15px;
        color: white;
        box-shadow: 0 10px 25px rgba(26, 35, 126, 0.4);
        position: relative;
        overflow: hidden;
    }

    .wallstreet-insight::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
        transform: rotate(45deg);
        animation: shine 3s infinite;
    }

    @keyframes shine {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }

    .wallstreet-insight h3 {
        color: #ffd700;
        font-size: 1.7rem;
        margin-bottom: 20px;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 800;
        position: relative;
        z-index: 1;
    }

    /* Recomendaciones con iconos */
    .recommendation-box {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        border-left: 8px solid #4caf50;
        padding: 30px;
        margin: 25px 0;
        border-radius: 15px;
        box-shadow: 0 6px 12px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }

    .recommendation-box:hover {
        box-shadow: 0 10px 20px rgba(76, 175, 80, 0.25);
    }

    .recommendation-box h3 {
        color: #2e7d32;
        font-size: 1.6rem;
        margin-bottom: 15px;
        font-weight: 700;
    }

    /* Tablas mejoradas */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* Tabs personalizados */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 60px;
        background-color: #f8f9fa;
        border-radius: 10px 10px 0 0;
        padding: 0 30px;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
    }

    /* Botones mejorados */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 15px 30px;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# CONFIGURACIÓN DE DATOS (Supabase o Local)
# =============================================================================
@st.cache_resource
def init_supabase():
    """Inicializa conexión con Supabase si las credenciales están disponibles"""
    supabase_url = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")

    if supabase_url and supabase_key:
        try:
            client = create_client(supabase_url, supabase_key)
            return client
        except Exception as e:
            st.sidebar.warning(f"Error al conectar con Supabase: {e}")
            return None
    return None

@st.cache_data(ttl=3600)  # Cache por 1 hora
def load_data_from_supabase(_supabase_client):
    """Carga datos desde Supabase"""
    try:
        data = {}

        # Cargar tablas
        data['kpi_periodo'] = pd.DataFrame(_supabase_client.table('kpi_periodo').select('*').execute().data)
        data['kpi_categoria'] = pd.DataFrame(_supabase_client.table('kpi_categoria').select('*').execute().data)
        data['kpi_dia'] = pd.DataFrame(_supabase_client.table('kpi_dia_semana').select('*').execute().data)
        data['pareto'] = pd.DataFrame(_supabase_client.table('pareto_productos').select('*').execute().data)
        data['clusters'] = pd.DataFrame(_supabase_client.table('perfiles_clusters').select('*').execute().data)

        # Intentar cargar reglas (puede no existir)
        try:
            data['reglas'] = pd.DataFrame(_supabase_client.table('reglas_asociacion').select('*').execute().data)
        except:
            data['reglas'] = pd.DataFrame()

        # Cargar muestra de tickets e items para análisis temporal
        data['tickets'] = pd.DataFrame(_supabase_client.table('tickets').select('*').limit(10000).execute().data)

        # Convertir fechas
        if 'fecha' in data['tickets'].columns:
            data['tickets']['fecha'] = pd.to_datetime(data['tickets']['fecha'])

        return data
    except Exception as e:
        st.error(f"Error cargando datos desde Supabase: {e}")
        return None

@st.cache_data
def load_data_from_local():
    """Carga datos desde archivos CSV locales (fallback)"""
    DEFAULT_PROCESSED_DIR = Path("data/processed/FASE1_OUTPUT")
    DEFAULT_SAMPLE_DIR = Path("data/sample/FASE1_OUTPUT_SAMPLE")

    for base_path in [DEFAULT_PROCESSED_DIR, DEFAULT_SAMPLE_DIR]:
        if base_path.exists():
            try:
                data = {}
                data['kpi_periodo'] = pd.read_csv(base_path / '03_KPI_PERIODO.csv', sep=';', encoding='utf-8-sig')
                data['kpi_categoria'] = pd.read_csv(base_path / '04_KPI_CATEGORIA.csv', sep=';', encoding='utf-8-sig')
                data['pareto'] = pd.read_csv(base_path / '05_PARETO_PRODUCTOS.csv', sep=';', encoding='utf-8-sig')
                data['clusters'] = pd.read_csv(base_path / '07_PERFILES_CLUSTERS.csv', sep=';', encoding='utf-8-sig')
                data['kpi_dia'] = pd.read_csv(base_path / '08_KPI_DIA_SEMANA.csv', sep=';', encoding='utf-8-sig')

                try:
                    data['reglas'] = pd.read_csv(base_path / '06_REGLAS_ASOCIACION.csv', sep=';', encoding='utf-8-sig')
                except:
                    data['reglas'] = pd.DataFrame()

                try:
                    data['tickets'] = pd.read_csv(base_path / '02_TICKETS.csv', sep=';', encoding='utf-8-sig')
                    data['tickets']['fecha'] = pd.to_datetime(data['tickets']['fecha'])
                except:
                    data['tickets'] = pd.DataFrame()

                return data, base_path
            except Exception as e:
                continue

    return None, None

# =============================================================================
# CARGAR DATOS
# =============================================================================
supabase = init_supabase()
data = None
data_source = "local"

with st.spinner('🔄 Cargando datos...'):
    if supabase:
        st.sidebar.success("✅ Conectado a Supabase")
        data = load_data_from_supabase(supabase)
        if data:
            data_source = "supabase"

    if not data:
        data, local_path = load_data_from_local()
        if data:
            st.sidebar.info(f"📁 Datos locales: {local_path.name}")
        else:
            st.error("❌ No se pudieron cargar los datos. Verifica la configuración.")
            st.stop()

# =============================================================================
# HEADER
# =============================================================================
st.markdown("""
<div class="main-header">
    <h1>📊 Supermercado NINO</h1>
    <p>Dashboard de Análisis Estratégico de Ventas | pymeinside.com</p>
</div>
""", unsafe_allow_html=True)

# Indicador de fuente de datos
if data_source == "supabase":
    st.sidebar.markdown("🌐 **Fuente:** Supabase Cloud")
else:
    st.sidebar.markdown("💾 **Fuente:** Archivos Locales")

# =============================================================================
# MENÚ DE NAVEGACIÓN
# =============================================================================
st.sidebar.markdown("---")
pagina = st.sidebar.radio(
    "📍 Navegación",
    [
        "🏠 Resumen Ejecutivo",
        "📈 Análisis Pareto",
        "🛒 Market Basket",
        "👥 Segmentación",
        "💰 Rentabilidad",
        "📅 Análisis Temporal"
    ]
)

# =============================================================================
# PÁGINA: RESUMEN EJECUTIVO
# =============================================================================
if pagina == "🏠 Resumen Ejecutivo":
    st.header("📊 Resumen Ejecutivo")

    # Calcular KPIs globales
    total_ventas = data['kpi_periodo']['ventas'].sum()
    total_margen = data['kpi_periodo']['margen'].sum()
    total_tickets = data['kpi_periodo']['tickets'].sum()
    margen_pct = (total_margen / total_ventas * 100) if total_ventas > 0 else 0
    ticket_promedio = total_ventas / total_tickets if total_tickets > 0 else 0

    # KPIs en tarjetas
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("💰 Total Ventas", f"${total_ventas/1e6:.1f}M", f"+{margen_pct:.1f}% margen")

    with col2:
        st.metric("📝 Total Tickets", f"{total_tickets:,.0f}", f"${ticket_promedio:,.0f} promedio")

    with col3:
        st.metric("💎 Margen Total", f"${total_margen/1e6:.1f}M", f"{margen_pct:.1f}%")

    with col4:
        categorias_activas = len(data['kpi_categoria'])
        st.metric("🏪 Categorías", f"{categorias_activas}", "departamentos")

    st.markdown("---")

    # Gráfico de evolución de ventas
    st.subheader("📈 Evolución de Ventas Mensuales")

    fig_periodo = px.bar(
        data['kpi_periodo'],
        x='periodo',
        y='ventas',
        title='Ventas por Período (Oct 2024 - Oct 2025)',
        labels={'periodo': 'Período', 'ventas': 'Ventas ($)'},
        color='ventas',
        color_continuous_scale='Viridis',
        text='ventas'
    )

    fig_periodo.update_traces(texttemplate='$%{text:.2s}', textposition='outside')
    fig_periodo.update_layout(
        height=500,
        showlegend=False,
        hovermode='x unified',
        title_font_size=20
    )
    st.plotly_chart(fig_periodo, use_container_width=True)

    # Dos columnas para gráficos
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏆 Top 10 Categorías")
        top_cat = data['kpi_categoria'].nlargest(10, 'ventas')

        fig_cat = px.bar(
            top_cat,
            y='categoria',
            x='ventas',
            orientation='h',
            color='rentabilidad_pct',
            color_continuous_scale='RdYlGn',
            labels={'ventas': 'Ventas ($)', 'categoria': ''},
            title='Por Ventas y Rentabilidad'
        )
        fig_cat.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_cat, use_container_width=True)

    with col2:
        st.subheader("📅 Ventas por Día de Semana")

        dias_esp = {
            'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
            'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
        }

        kpi_dia_esp = data['kpi_dia'].copy()
        kpi_dia_esp['dia_esp'] = kpi_dia_esp['dia_semana'].map(dias_esp)

        fig_dia = px.bar(
            kpi_dia_esp,
            x='dia_esp',
            y='ventas',
            color='ventas',
            color_continuous_scale='Blues',
            labels={'dia_esp': '', 'ventas': 'Ventas ($)'},
            title='Distribución Semanal'
        )
        fig_dia.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_dia, use_container_width=True)

    # INSIGHT
    st.markdown("---")
    st.markdown("""
    <div class="wallstreet-insight">
        <h3>💼 INSIGHT</h3>
        <p style="font-size: 1.1rem; line-height: 1.8;">
        <strong>📊 CONCENTRACIÓN DE VALOR:</strong> El 13.4% de los productos (1,389 items) generan el 80% de las ventas.
        <br><strong>💰 OPORTUNIDAD DE MARGEN:</strong> Las categorías de Fiambrería y Bazar tienen 45% de rentabilidad vs 27% promedio.
        <br><strong>🎯 TICKET PROMEDIO:</strong> $26,849 con 9.8 items por compra - Oportunidad de aumentar UPT (units per transaction).
        <br><strong>📈 ROI POTENCIAL:</strong> Implementando las recomendaciones se proyecta un aumento de 10-15% en ventas y 15-25% en margen.
        </p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# PÁGINA: ANÁLISIS PARETO
# =============================================================================
elif pagina == "📈 Análisis Pareto":
    st.header("📈 Análisis de Pareto (Ley 80/20)")

    st.info("💡 **Principio de Pareto:** El 80% de los resultados provienen del 20% de las causas. En retail, esto significa que un pequeño porcentaje de productos genera la mayoría de las ventas.")

    # Estadísticas ABC
    productos_A = len(data['pareto'][data['pareto']['clasificacion_abc'] == 'A'])
    productos_B = len(data['pareto'][data['pareto']['clasificacion_abc'] == 'B'])
    productos_C = len(data['pareto'][data['pareto']['clasificacion_abc'] == 'C'])
    total_productos = len(data['pareto'])

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🏆 Productos A (80% ventas)", f"{productos_A:,}", f"{productos_A/total_productos*100:.1f}% del catálogo")

    with col2:
        st.metric("📊 Productos B (15% ventas)", f"{productos_B:,}", f"{productos_B/total_productos*100:.1f}% del catálogo")

    with col3:
        st.metric("📉 Productos C (5% ventas)", f"{productos_C:,}", f"{productos_C/total_productos*100:.1f}% del catálogo")

    # Gráfico de Pareto
    st.subheader("📊 Curva de Pareto - Top 100 Productos")

    top_100 = data['pareto'].head(100)

    fig_pareto = go.Figure()

    fig_pareto.add_trace(go.Bar(
        x=list(range(1, len(top_100)+1)),
        y=top_100['ventas'],
        name='Ventas',
        marker_color='#667eea',
        hovertemplate='<b>Producto #%{x}</b><br>Ventas: $%{y:,.0f}<extra></extra>'
    ))

    fig_pareto.add_trace(go.Scatter(
        x=list(range(1, len(top_100)+1)),
        y=top_100['pct_acumulado'],
        name='% Acumulado',
        yaxis='y2',
        line=dict(color='#f18f01', width=4),
        mode='lines+markers',
        marker=dict(size=8),
        hovertemplate='<b>Producto #%{x}</b><br>% Acum: %{y:.2f}%<extra></extra>'
    ))

    fig_pareto.add_hline(y=80, line_dash="dash", line_color="red", yref='y2',
                         annotation_text="Línea 80%", annotation_position="right")

    fig_pareto.update_layout(
        title='Curva de Pareto - Análisis de Concentración',
        xaxis_title='Ranking de Productos',
        yaxis_title='Ventas ($)',
        yaxis2=dict(
            title='% Acumulado',
            overlaying='y',
            side='right',
            range=[0, 100]
        ),
        height=600,
        hovermode='x unified',
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99)
    )

    st.plotly_chart(fig_pareto, use_container_width=True)

    # Top 20 productos con detalles
    st.subheader("🏆 Top 20 Productos Vitales (Categoría A)")

    top_20 = data['pareto'].head(20)[['producto_id', 'descripcion', 'categoria', 'ventas', 'pct_acumulado']]
    top_20 = top_20.copy()
    top_20['ventas'] = top_20['ventas'].apply(lambda x: f"${x:,.0f}")
    top_20['pct_acumulado'] = top_20['pct_acumulado'].apply(lambda x: f"{x:.2f}%")

    st.dataframe(top_20, use_container_width=True, hide_index=True)

    # Recomendaciones
    st.markdown("""
    <div class="recommendation-box">
        <h3>🎯 Recomendaciones de Acción</h3>
        <ul style="font-size: 1.05rem; line-height: 2;">
            <li><strong>Productos A:</strong> Stock de seguridad 15-30 días, monitoreo diario, ubicación premium en góndola</li>
            <li><strong>Productos B:</strong> Stock 7-15 días, revisión semanal, ubicación estándar</li>
            <li><strong>Productos C:</strong> Stock 3-7 días, considerar reducción de surtido o eliminación</li>
            <li><strong>Inversión:</strong> Concentrar recursos de marketing y promociones en productos A y B</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# PÁGINA: MARKET BASKET
# =============================================================================
elif pagina == "🛒 Market Basket":
    st.header("🛒 Análisis de Cesta de Compra")

    if len(data['reglas']) > 0:
        st.info("💡 **Market Basket Analysis:** Identifica productos que se compran juntos frecuentemente. El 'Lift' indica la fuerza de la asociación (>1 = asociación positiva).")

        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            min_lift = st.slider("🎯 Lift Mínimo", 1.0, float(data['reglas']['lift'].max()), 5.0, 0.5)
        with col2:
            min_confidence = st.slider("📊 Confianza Mínima", 0.1, 1.0, 0.2, 0.05)

        # Filtrar reglas
        reglas_filtradas = data['reglas'][
            (data['reglas']['lift'] >= min_lift) &
            (data['reglas']['confidence'] >= min_confidence)
        ].sort_values('lift', ascending=False)

        st.metric("🔍 Reglas Encontradas", len(reglas_filtradas), f"de {len(data['reglas'])} totales")

        if len(reglas_filtradas) > 0:
            # Top 20 reglas
            st.subheader(f"🏆 Top 20 Reglas de Asociación")

            top_reglas = reglas_filtradas.head(20)[['antecedents', 'consequents', 'support', 'confidence', 'lift']].copy()
            top_reglas['support'] = top_reglas['support'].apply(lambda x: f"{x:.3f}")
            top_reglas['confidence'] = top_reglas['confidence'].apply(lambda x: f"{x:.2%}")
            top_reglas['lift'] = top_reglas['lift'].apply(lambda x: f"{x:.2f}x")

            st.dataframe(top_reglas, use_container_width=True, hide_index=True)

            # Gráfico de scatter
            st.subheader("📊 Mapa de Reglas (Confidence vs Support)")

            fig_scatter = px.scatter(
                reglas_filtradas.head(50),
                x='support',
                y='confidence',
                size='lift',
                color='lift',
                hover_data=['antecedents', 'consequents'],
                title='Top 50 Reglas por Lift (tamaño de burbuja = Lift)',
                color_continuous_scale='Viridis',
                labels={'support': 'Soporte', 'confidence': 'Confianza', 'lift': 'Lift'}
            )
            fig_scatter.update_layout(height=600)
            st.plotly_chart(fig_scatter, use_container_width=True)

            # Recomendaciones
            st.markdown("""
            <div class="recommendation-box">
                <h3>💡 Cómo Usar Estas Reglas</h3>
                <ul style="font-size: 1.05rem; line-height: 2;">
                    <li><strong>Cross-Selling:</strong> Colocar productos asociados cerca en góndola</li>
                    <li><strong>Bundles:</strong> Crear combos promocionales con productos de alto Lift</li>
                    <li><strong>Recomendaciones:</strong> Sistema de sugerencias en caja "Los clientes también compraron..."</li>
                    <li><strong>Layout:</strong> Reorganizar el local basándose en patrones de compra</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ No se encontraron reglas con los filtros actuales. Intenta reducir los umbrales.")
    else:
        st.warning("⚠️ No hay datos de Market Basket disponibles. Ejecuta el análisis completo para generarlos.")

# =============================================================================
# PÁGINA: SEGMENTACIÓN
# =============================================================================
elif pagina == "👥 Segmentación":
    st.header("👥 Segmentación de Tickets (Clustering)")

    st.info("💡 **Clustering:** Agrupa tickets similares por monto y cantidad de items para identificar patrones de comportamiento de compra.")

    # Mostrar perfiles
    st.subheader("📊 Perfiles de Clusters Identificados")

    clusters_display = data['clusters'].copy()
    clusters_display['cantidad_tickets'] = clusters_display['cantidad_tickets'].apply(lambda x: f"{int(x):,}")
    clusters_display['ticket_promedio'] = clusters_display['ticket_promedio'].apply(lambda x: f"${float(x):,.2f}")
    clusters_display['items_promedio'] = clusters_display['items_promedio'].apply(lambda x: f"{float(x):.1f}")
    clusters_display['pct_tickets'] = clusters_display['pct_tickets'].apply(lambda x: f"{float(x):.1f}%")

    if 'pct_fin_semana' in clusters_display.columns:
        clusters_display['pct_fin_semana'] = clusters_display['pct_fin_semana'].apply(lambda x: f"{float(x):.1f}%")

    st.dataframe(clusters_display, use_container_width=True, hide_index=True)

    # Gráfico de distribución
    st.subheader("📈 Distribución de Tickets por Cluster")

    fig_clusters = px.bar(
        data['clusters'],
        x='etiqueta',
        y='cantidad_tickets',
        color='ticket_promedio',
        title='Cantidad y Valor Promedio por Segmento',
        labels={'etiqueta': 'Segmento', 'cantidad_tickets': 'Cantidad de Tickets', 'ticket_promedio': 'Ticket Promedio ($)'},
        color_continuous_scale='Bluered',
        text='cantidad_tickets'
    )
    fig_clusters.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
    fig_clusters.update_layout(height=500)
    st.plotly_chart(fig_clusters, use_container_width=True)

    # Recomendaciones por segmento
    st.markdown("""
    <div class="wallstreet-insight">
        <h3>🎯 Estrategias por Segmento</h3>
        <p style="font-size: 1.1rem; line-height: 1.8;">
        <strong>🛒 Compra de Conveniencia:</strong> Optimizar velocidad de caja, productos de compra impulsiva en checkout.
        <br><strong>📦 Compra Mediana:</strong> Programas de fidelización, cupones de descuento para próxima visita.
        <br><strong>🏪 Compra Grande Semanal:</strong> Ofertas por volumen, servicio de delivery, programa VIP.
        <br><strong>💰 Alto Valor:</strong> Atención personalizada, acceso anticipado a promociones, beneficios exclusivos.
        </p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# PÁGINA: RENTABILIDAD
# =============================================================================
elif pagina == "💰 Rentabilidad":
    st.header("💰 Análisis de Rentabilidad por Categoría")

    # KPIs de rentabilidad
    total_ventas_cat = data['kpi_categoria']['ventas'].sum()
    total_margen_cat = data['kpi_categoria']['margen'].sum()
    margen_pct_global = (total_margen_cat / total_ventas_cat * 100) if total_ventas_cat > 0 else 0

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("💎 Margen Global", f"{margen_pct_global:.2f}%", "promedio ponderado")

    with col2:
        categoria_mas_rentable = data['kpi_categoria'].nlargest(1, 'rentabilidad_pct').iloc[0]
        st.metric(
            "🏆 Categoría Más Rentable",
            categoria_mas_rentable['categoria'],
            f"{float(categoria_mas_rentable['rentabilidad_pct']):.0f}%"
        )

    with col3:
        categoria_mayor_ventas = data['kpi_categoria'].nlargest(1, 'ventas').iloc[0]
        st.metric(
            "📊 Mayor Volumen",
            categoria_mayor_ventas['categoria'],
            f"${float(categoria_mayor_ventas['ventas'])/1e6:.1f}M"
        )

    # Gráfico de ventas vs rentabilidad
    st.subheader("📊 Matriz Ventas vs Rentabilidad")

    top_20_cat = data['kpi_categoria'].nlargest(20, 'ventas')

    fig_scatter_rent = px.scatter(
        top_20_cat,
        x='ventas',
        y='rentabilidad_pct',
        size='margen',
        color='rentabilidad_pct',
        hover_name='categoria',
        title='Top 20 Categorías: Ventas vs Rentabilidad (tamaño = Margen Total)',
        labels={'ventas': 'Ventas Totales ($)', 'rentabilidad_pct': 'Rentabilidad (%)'},
        color_continuous_scale='RdYlGn',
        size_max=60
    )

    # Línea de referencia en 27% (margen promedio)
    fig_scatter_rent.add_hline(y=margen_pct_global, line_dash="dash", line_color="gray",
                               annotation_text="Margen Promedio", annotation_position="right")

    fig_scatter_rent.update_layout(height=600)
    st.plotly_chart(fig_scatter_rent, use_container_width=True)

    # Gráfico dual de barras
    st.subheader("📈 Top 15 Categorías: Volumen y Rentabilidad")

    top_15_cat = data['kpi_categoria'].nlargest(15, 'ventas')

    fig_rent = go.Figure()

    fig_rent.add_trace(go.Bar(
        x=top_15_cat['categoria'],
        y=top_15_cat['ventas'],
        name='Ventas',
        marker_color='#667eea',
        yaxis='y',
        hovertemplate='%{x}<br>Ventas: $%{y:,.0f}<extra></extra>'
    ))

    fig_rent.add_trace(go.Scatter(
        x=top_15_cat['categoria'],
        y=top_15_cat['rentabilidad_pct'],
        name='Rentabilidad %',
        mode='lines+markers',
        line=dict(color='#f18f01', width=4),
        marker=dict(size=12),
        yaxis='y2',
        hovertemplate='%{x}<br>Rentabilidad: %{y:.1f}%<extra></extra>'
    ))

    fig_rent.update_layout(
        title='Ventas vs Rentabilidad por Categoría',
        xaxis_title='',
        yaxis_title='Ventas ($)',
        yaxis2=dict(
            title='Rentabilidad %',
            overlaying='y',
            side='right',
            range=[0, max(top_15_cat['rentabilidad_pct']) * 1.2]
        ),
        height=600,
        hovermode='x unified',
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99)
    )

    st.plotly_chart(fig_rent, use_container_width=True)

    # Tabla detallada
    st.subheader("📋 Detalle Completo de Rentabilidad")

    tabla_rent = data['kpi_categoria'][['categoria', 'ventas', 'margen', 'rentabilidad_pct', 'pct_ventas']].copy()
    tabla_rent = tabla_rent.sort_values('ventas', ascending=False)
    tabla_rent['ventas'] = tabla_rent['ventas'].apply(lambda x: f"${float(x):,.0f}")
    tabla_rent['margen'] = tabla_rent['margen'].apply(lambda x: f"${float(x):,.0f}")
    tabla_rent['rentabilidad_pct'] = tabla_rent['rentabilidad_pct'].apply(lambda x: f"{float(x):.0f}%")
    tabla_rent['pct_ventas'] = tabla_rent['pct_ventas'].apply(lambda x: f"{float(x):.2f}%")

    st.dataframe(tabla_rent, use_container_width=True, hide_index=True)

    # Recomendaciones
    st.markdown("""
    <div class="recommendation-box">
        <h3>💰 Oportunidades de Optimización de Margen</h3>
        <ul style="font-size: 1.05rem; line-height: 2;">
            <li><strong>Expansión de Categorías Premium:</strong> Aumentar espacio para Fiambrería, Bazar, Perfumería (45%+ rentabilidad)</li>
            <li><strong>Mix Optimization:</strong> Reducir productos de baja rentabilidad en categorías de alto volumen</li>
            <li><strong>Private Label:</strong> Desarrollar marca propia en categorías de alta rotación para mejorar márgenes</li>
            <li><strong>Dynamic Pricing:</strong> Ajustar precios basados en elasticidad y margen objetivo por categoría</li>
            <li><strong>Cross-Selling Estratégico:</strong> Combinar productos de alta rotación con productos de alta rentabilidad</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# PÁGINA: ANÁLISIS TEMPORAL
# =============================================================================
elif pagina == "📅 Análisis Temporal":
    st.header("📅 Análisis Temporal de Ventas")

    if len(data['tickets']) > 0 and 'fecha' in data['tickets'].columns:
        # Serie temporal agregada
        st.subheader("📈 Evolución Temporal de Ventas")

        ventas_diarias = data['tickets'].groupby(data['tickets']['fecha'].dt.date).agg({
            'monto_total_ticket': 'sum',
            'ticket_id': 'count'
        }).reset_index()

        ventas_diarias.columns = ['fecha', 'ventas', 'tickets']
        ventas_diarias = ventas_diarias.sort_values('fecha')

        # Media móvil 7 días
        ventas_diarias['ma7'] = ventas_diarias['ventas'].rolling(window=7, min_periods=1).mean()

        fig_temporal = go.Figure()

        fig_temporal.add_trace(go.Scatter(
            x=ventas_diarias['fecha'],
            y=ventas_diarias['ventas'],
            mode='lines',
            name='Ventas Diarias',
            line=dict(color='#667eea', width=1),
            opacity=0.6,
            hovertemplate='%{x}<br>Ventas: $%{y:,.0f}<extra></extra>'
        ))

        fig_temporal.add_trace(go.Scatter(
            x=ventas_diarias['fecha'],
            y=ventas_diarias['ma7'],
            mode='lines',
            name='Media Móvil 7 días',
            line=dict(color='#f18f01', width=3),
            hovertemplate='%{x}<br>MA7: $%{y:,.0f}<extra></extra>'
        ))

        fig_temporal.update_layout(
            title='Ventas Diarias con Tendencia (Media Móvil 7 días)',
            xaxis_title='Fecha',
            yaxis_title='Ventas ($)',
            height=500,
            hovermode='x unified',
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
        )

        st.plotly_chart(fig_temporal, use_container_width=True)

        # Distribución por día de semana (más detallado)
        st.subheader("📊 Patrón Semanal de Ventas")

        data['tickets']['dia_semana'] = data['tickets']['fecha'].dt.day_name()

        ventas_por_dia = data['tickets'].groupby('dia_semana').agg({
            'monto_total_ticket': ['sum', 'mean', 'count']
        }).reset_index()

        ventas_por_dia.columns = ['dia_semana', 'ventas_total', 'ticket_promedio', 'cantidad_tickets']

        # Ordenar días
        dias_orden = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        ventas_por_dia['dia_semana'] = pd.Categorical(ventas_por_dia['dia_semana'], categories=dias_orden, ordered=True)
        ventas_por_dia = ventas_por_dia.sort_values('dia_semana')

        # Mapear a español
        dias_esp = {
            'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
            'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
        }
        ventas_por_dia['dia_esp'] = ventas_por_dia['dia_semana'].map(dias_esp)

        fig_dia = go.Figure()

        fig_dia.add_trace(go.Bar(
            x=ventas_por_dia['dia_esp'],
            y=ventas_por_dia['ventas_total'],
            name='Ventas Totales',
            marker_color='#667eea',
            hovertemplate='%{x}<br>Ventas: $%{y:,.0f}<extra></extra>'
        ))

        fig_dia.update_layout(
            title='Ventas Totales por Día de Semana',
            xaxis_title='',
            yaxis_title='Ventas ($)',
            height=400,
            showlegend=False
        )

        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(fig_dia, use_container_width=True)

        with col2:
            # Tickets por día
            fig_tickets = px.bar(
                ventas_por_dia,
                x='dia_esp',
                y='cantidad_tickets',
                title='Cantidad de Tickets por Día',
                labels={'dia_esp': '', 'cantidad_tickets': 'Tickets'},
                color='cantidad_tickets',
                color_continuous_scale='Purples'
            )
            fig_tickets.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_tickets, use_container_width=True)

        # Insights
        dia_max_ventas = ventas_por_dia.nlargest(1, 'ventas_total').iloc[0]
        dia_max_tickets = ventas_por_dia.nlargest(1, 'cantidad_tickets').iloc[0]

        st.markdown(f"""
        <div class="insight-box">
            <h3>🎯 Insights Temporales</h3>
            <ul style="font-size: 1.05rem; line-height: 1.8;">
                <li><strong>Día con mayores ventas:</strong> {dia_max_ventas['dia_esp']} (${dia_max_ventas['ventas_total']:,.0f})</li>
                <li><strong>Día con más tickets:</strong> {dia_max_tickets['dia_esp']} ({int(dia_max_tickets['cantidad_tickets']):,} tickets)</li>
                <li><strong>Ticket promedio más alto:</strong> {ventas_por_dia.nlargest(1, 'ticket_promedio').iloc[0]['dia_esp']}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ No hay datos de tickets disponibles para análisis temporal detallado.")

        # Mostrar al menos el análisis por período
        st.subheader("📊 Análisis por Período (Mensual)")

        fig_periodo_temp = px.line(
            data['kpi_periodo'],
            x='periodo',
            y='ventas',
            title='Evolución de Ventas Mensuales',
            labels={'periodo': 'Período', 'ventas': 'Ventas ($)'},
            markers=True,
            line_shape='spline'
        )
        fig_periodo_temp.update_traces(line=dict(width=3, color='#667eea'), marker=dict(size=10))
        fig_periodo_temp.update_layout(height=500)
        st.plotly_chart(fig_periodo_temp, use_container_width=True)

# =============================================================================
# FOOTER
# =============================================================================
st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div style="text-align: center; font-size: 0.85rem; color: #666; padding: 15px;">
<strong>🏪 Supermercado NINO</strong><br>
Analytics Dashboard v2.0<br>
📊 Datos: {'Supabase Cloud ☁️' if data_source == 'supabase' else 'Local 💾'}<br>
🚀 pymeinside.com<br>
Powered by Streamlit + Supabase
</div>
""", unsafe_allow_html=True)

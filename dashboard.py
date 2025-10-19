# -*- coding: utf-8 -*-
"""
Dashboard Simplificado - Supermercado NINO
Muestra todos los análisis del pipeline estratégico
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="Supermercado NINO - Dashboard Estratégico",
    page_icon="📊",
    layout="wide"
)

# Cargar datos
DATA_DIR = Path("data/app_dataset")

@st.cache_data
def load_data():
    data = {}
    try:
        # Datos principales
        data['alcance'] = pd.read_parquet(DATA_DIR / 'alcance_dataset.parquet')
        data['kpis_base'] = pd.read_parquet(DATA_DIR / 'kpis_base.parquet')
        data['kpi_diario'] = pd.read_parquet(DATA_DIR / 'kpi_diario.parquet')
        data['kpi_semana'] = pd.read_parquet(DATA_DIR / 'kpi_semana.parquet')
        data['kpi_periodo'] = pd.read_parquet(DATA_DIR / 'kpi_periodo.parquet')
        data['kpi_categoria'] = pd.read_parquet(DATA_DIR / 'kpi_categoria.parquet')
        data['kpi_dia'] = pd.read_parquet(DATA_DIR / 'kpi_dia.parquet')
        data['pareto_cat'] = pd.read_parquet(DATA_DIR / 'pareto_cat_global.parquet')
        data['pareto_prod'] = pd.read_parquet(DATA_DIR / 'pareto_prod_global.parquet')
        data['reglas'] = pd.read_parquet(DATA_DIR / 'reglas.parquet')
        data['combos'] = pd.read_parquet(DATA_DIR / 'combos_recomendados.parquet')
        data['clusters_tickets'] = pd.read_parquet(DATA_DIR / 'clusters_tickets.parquet')
        data['clusters_depto'] = pd.read_parquet(DATA_DIR / 'clusters_departamento.parquet')
        data['kpi_pago'] = pd.read_parquet(DATA_DIR / 'kpi_medio_pago.parquet')
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return None
    return data

data = load_data()

if not data:
    st.stop()

# ==============================================================================
# PORTADA
# ==============================================================================
st.markdown("""
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem; border-radius: 15px; text-align: center;
            box-shadow: 0 8px 16px rgba(0,0,0,0.15); margin-bottom: 2rem;'>
    <h1 style='color: white; margin: 0; font-size: 3rem;'>📊 Supermercado NINO</h1>
    <p style='color: rgba(255,255,255,0.95); margin: 0.5rem 0 0 0; font-size: 1.3rem;'>
        Dashboard Analítico Estratégico
    </p>
</div>
""", unsafe_allow_html=True)

# Alcance del dataset
alcance = data['alcance'].iloc[0]
st.markdown("### 📋 Alcance del Dataset")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Período", f"{alcance['min_fecha'].strftime('%d/%m/%Y')} - {alcance['max_fecha'].strftime('%d/%m/%Y')}")
with col2:
    st.metric("Tickets", f"{alcance['n_tickets']:,}")
with col3:
    st.metric("Ítems", f"{alcance['n_items']:,}")
with col4:
    st.metric("Ventas", f"${alcance['ventas_total']:,.0f}")

# KPIs Base
st.markdown("### 📈 KPIs Principales")
kpis = data['kpis_base'].iloc[0]

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Rentabilidad Global", f"{kpis['rentabilidad_global']*100:.2f}%")
with col2:
    st.metric("Ticket Promedio", f"${kpis['ticket_promedio']:,.0f}")
with col3:
    st.metric("Items/Ticket", f"{kpis['items_promedio_ticket']:.2f}")
with col4:
    st.metric("Margen/Ticket", f"${kpis['rentabilidad_promedio_ticket']:,.0f}")

# ==============================================================================
# PESTAÑAS
# ==============================================================================
tabs = st.tabs([
    "📊 Análisis Temporal",
    "🎯 Pareto",
    "🛒 Market Basket",
    "👥 Segmentación",
    "💳 Medios de Pago"
])

# ------------------------------------------------------------------------------
# TAB 1: ANÁLISIS TEMPORAL
# ------------------------------------------------------------------------------
with tabs[0]:
    st.markdown("## 📊 Análisis Temporal")

    # Evolución diaria
    st.markdown("### Evolución Diaria de Ventas")
    fig_diario = px.line(
        data['kpi_diario'],
        x='fecha',
        y='ventas',
        title="Ventas Diarias",
        labels={'fecha': 'Fecha', 'ventas': 'Ventas ($)'}
    )
    fig_diario.update_traces(line_color='#667eea', line_width=2)
    st.plotly_chart(fig_diario, use_container_width=True)

    # Semanal y Mensual
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Ventas Semanales")
        fig_semana = px.bar(
            data['kpi_semana'].tail(12),
            x='semana_iso',
            y='ventas',
            title="Últimas 12 Semanas"
        )
        fig_semana.update_traces(marker_color='#667eea')
        st.plotly_chart(fig_semana, use_container_width=True)

    with col2:
        st.markdown("### Ventas Mensuales")
        fig_periodo = px.bar(
            data['kpi_periodo'],
            x='periodo',
            y='ventas',
            title="Por Mes"
        )
        fig_periodo.update_traces(marker_color='#764ba2')
        st.plotly_chart(fig_periodo, use_container_width=True)

    # Por día de semana
    st.markdown("### Ventas por Día de Semana")
    fig_dow = px.bar(
        data['kpi_dia'],
        x='dia_semana',
        y='ventas',
        title="Distribución por Día de Semana"
    )
    fig_dow.update_traces(marker_color='#667eea')
    st.plotly_chart(fig_dow, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 2: PARETO
# ------------------------------------------------------------------------------
with tabs[1]:
    st.markdown("## 🎯 Análisis de Pareto")

    # Categorías
    st.markdown("### Pareto por Categorías")
    pareto_cat = data['pareto_cat'].head(20)

    fig_pareto_cat = go.Figure()
    fig_pareto_cat.add_trace(go.Bar(
        x=pareto_cat['categoria'],
        y=pareto_cat['ventas'],
        name='Ventas',
        marker_color='#667eea'
    ))
    fig_pareto_cat.add_trace(go.Scatter(
        x=pareto_cat['categoria'],
        y=pareto_cat['pct_acumulado_ventas'],
        name='% Acumulado',
        yaxis='y2',
        line=dict(color='#ff6b6b', width=3)
    ))
    fig_pareto_cat.update_layout(
        title="Top 20 Categorías - Curva de Pareto",
        yaxis=dict(title='Ventas'),
        yaxis2=dict(title='% Acumulado', overlaying='y', side='right'),
        height=500
    )
    st.plotly_chart(fig_pareto_cat, use_container_width=True)

    # Productos Top
    st.markdown("### Top 30 Productos")
    pareto_prod = data['pareto_prod'].head(30)
    st.dataframe(
        pareto_prod[['descripcion', 'categoria', 'ventas', 'margen', 'abc_ventas']],
        hide_index=True,
        use_container_width=True
    )

# ------------------------------------------------------------------------------
# TAB 3: MARKET BASKET
# ------------------------------------------------------------------------------
with tabs[2]:
    st.markdown("## 🛒 Market Basket Analysis")

    # Reglas principales
    st.markdown("### Top 20 Reglas de Asociación")
    reglas_top = data['reglas'].nlargest(20, 'lift')
    st.dataframe(
        reglas_top[['antecedents', 'consequents', 'support', 'confidence', 'lift']],
        hide_index=True,
        use_container_width=True
    )

    # Scatter plot
    st.markdown("### Visualización: Confidence vs Support")
    fig_scatter = px.scatter(
        data['reglas'],
        x='support',
        y='confidence',
        size='lift',
        color='lift',
        hover_data=['antecedents', 'consequents'],
        title="Reglas de Asociación",
        labels={'support': 'Soporte', 'confidence': 'Confianza', 'lift': 'Lift'}
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # Combos recomendados
    st.markdown("### 💡 Combos Recomendados")
    combos_display = data['combos'][['antecedent', 'consequent', 'lift', 'precio_combo_sugerido', 'margen_combo_estimado']]
    combos_display['precio_combo_sugerido'] = combos_display['precio_combo_sugerido'].apply(lambda x: f"${x:,.0f}")
    combos_display['margen_combo_estimado'] = combos_display['margen_combo_estimado'].apply(lambda x: f"{x:.1f}%")
    st.dataframe(combos_display, hide_index=True, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 4: SEGMENTACIÓN
# ------------------------------------------------------------------------------
with tabs[3]:
    st.markdown("## 👥 Segmentación de Clientes")

    # Clusters de tickets
    st.markdown("### Segmentos de Tickets")
    clusters = data['clusters_tickets']

    fig_clusters = go.Figure()
    fig_clusters.add_trace(go.Bar(
        x=clusters['etiqueta'],
        y=clusters['cantidad_tickets'],
        name='Tickets',
        marker_color='#667eea'
    ))
    fig_clusters.update_layout(
        title="Distribución de Segmentos",
        xaxis_title="Segmento",
        yaxis_title="Cantidad de Tickets"
    )
    st.plotly_chart(fig_clusters, use_container_width=True)

    # Tabla detallada
    st.dataframe(
        clusters[['etiqueta', 'cantidad_tickets', 'ticket_promedio', 'items_promedio', 'margen_promedio', 'pct_tickets']],
        hide_index=True,
        use_container_width=True
    )

    # Clusters por departamento
    st.markdown("### Análisis por Departamento")
    depto_top = data['clusters_depto'].nlargest(15, 'ventas')

    fig_depto = px.bar(
        depto_top,
        x='departamento',
        y=['ventas', 'margen'],
        title="Top 15 Departamentos",
        barmode='group'
    )
    st.plotly_chart(fig_depto, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 5: MEDIOS DE PAGO
# ------------------------------------------------------------------------------
with tabs[4]:
    st.markdown("## 💳 Análisis de Medios de Pago")

    # KPIs por medio de pago
    pago_summary = data['kpi_pago'].groupby('tipo_medio_pago').agg({
        'tickets': 'sum',
        'ventas': 'sum',
        'margen': 'sum',
        'ticket_promedio': 'mean'
    }).reset_index()

    # Treemap
    fig_tree = px.treemap(
        pago_summary,
        path=['tipo_medio_pago'],
        values='ventas',
        title="Participación de Ventas por Medio de Pago"
    )
    st.plotly_chart(fig_tree, use_container_width=True)

    # Tabla detallada
    st.markdown("### Detalle por Medio de Pago y Emisor")
    pago_display = data['kpi_pago'][['tipo_medio_pago', 'emisor_tarjeta', 'tickets', 'ventas', 'ticket_promedio', 'participacion_ventas']]
    pago_display['ventas'] = pago_display['ventas'].apply(lambda x: f"${x:,.0f}")
    pago_display['ticket_promedio'] = pago_display['ticket_promedio'].apply(lambda x: f"${x:,.0f}")
    pago_display['participacion_ventas'] = pago_display['participacion_ventas'].apply(lambda x: f"{x:.2f}%")
    st.dataframe(pago_display, hide_index=True, use_container_width=True)

# ==============================================================================
# FOOTER
# ==============================================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    Dashboard generado por pipeline_estrategias.py | Supermercado NINO | pymeinside.com
</div>
""", unsafe_allow_html=True)

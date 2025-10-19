# -*- coding: utf-8 -*-
"""
================================================================================
DASHBOARD CIENTÍFICO - SUPERMERCADO NINO
Análisis de datos para validar estrategias de rentabilidad del ticket
Enfoque: Storytelling + Insights accionables vinculados a 9 estrategias
================================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import numpy as np

st.set_page_config(
    page_title="NINO - Dashboard Analítico",
    page_icon="📊",
    layout="wide"
)

# Función para formatear números al estilo argentino (puntos para miles, comas para decimales)
def formatear_numero_argentino(numero, decimales=0):
    """Formatea números al estilo argentino: 123.456,78"""
    if pd.isna(numero):
        return "N/A"

    # Redondear al número de decimales especificado
    numero_redondeado = round(numero, decimales)

    # Separar parte entera y decimal
    if decimales > 0:
        parte_entera = int(numero_redondeado)
        parte_decimal = int((numero_redondeado - parte_entera) * (10 ** decimales))
        parte_decimal_str = f"{parte_decimal:0{decimales}d}"
    else:
        parte_entera = int(numero_redondeado)
        parte_decimal_str = ""

    # Formatear parte entera con puntos como separadores de miles
    parte_entera_formateada = f"{parte_entera:,}".replace(",", ".")

    # Combinar parte entera y decimal
    if decimales > 0:
        return f"{parte_entera_formateada},{parte_decimal_str}"
    else:
        return parte_entera_formateada

def formatear_moneda_argentina(numero, decimales=0, simbolo="$"):
    """Formatea moneda al estilo argentino"""
    return f"{simbolo}{formatear_numero_argentino(numero, decimales)}"
st.markdown("""
<style>
    /* Estilos para las pestañas más grandes */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        padding: 10px 20px;
        background-color: #f8f9fa;
        border-radius: 10px 10px 0 0;
        border-bottom: 3px solid #1a237e;
    }

    .stTabs [data-baseweb="tab"] {
        height: 60px;
        padding: 15px 30px;
        background-color: #e3f2fd;
        border-radius: 8px 8px 0 0;
        border: 2px solid #1a237e;
        font-size: 16px;
        font-weight: 600;
        color: #1a237e;
        transition: all 0.3s ease;
        min-width: 200px;
        text-align: center;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: #bbdefb;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    .stTabs [aria-selected="true"] {
        background-color: #1a237e !important;
        color: #ffd700 !important;
        border: 2px solid #ffd700 !important;
        transform: translateY(-3px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }

    /* Hacer el texto de las pestañas más grande */
    .stTabs [data-baseweb="tab"] div {
        font-size: 18px !important;
        font-weight: 700 !important;
    }

    /* Espaciado para el contenido de las pestañas */
    .stTabs [data-baseweb="tab-panel"] {
        padding: 20px 10px;
        background-color: white;
        border-radius: 0 0 15px 15px;
        border: 2px solid #e0e0e0;
        border-top: none;
        margin-top: -2px;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# CARGAR DATOS
# =============================================================================
DATA_DIR = Path("data/app_dataset")

@st.cache_data
def load_all_data():
    data = {}
    try:
        data['alcance'] = pd.read_parquet(DATA_DIR / 'alcance_dataset.parquet')
        data['kpis_base'] = pd.read_parquet(DATA_DIR / 'kpis_base.parquet')
        data['kpi_diario'] = pd.read_parquet(DATA_DIR / 'kpi_diario.parquet')
        data['kpi_periodo'] = pd.read_parquet(DATA_DIR / 'kpi_periodo.parquet')
        data['kpi_semana'] = pd.read_parquet(DATA_DIR / 'kpi_semana.parquet')
        data['kpi_dia'] = pd.read_parquet(DATA_DIR / 'kpi_dia.parquet')
        data['kpi_categoria'] = pd.read_parquet(DATA_DIR / 'kpi_categoria.parquet')
        data['pareto_cat'] = pd.read_parquet(DATA_DIR / 'pareto_cat_global.parquet')
        data['pareto_prod'] = pd.read_parquet(DATA_DIR / 'pareto_prod_global.parquet')
        data['reglas'] = pd.read_parquet(DATA_DIR / 'reglas.parquet')
        data['combos'] = pd.read_parquet(DATA_DIR / 'combos_recomendados.parquet')
        data['adjacency'] = pd.read_parquet(DATA_DIR / 'adjacency_pairs.parquet')
        data['clusters_tickets'] = pd.read_parquet(DATA_DIR / 'clusters_tickets.parquet')
        data['clusters_depto'] = pd.read_parquet(DATA_DIR / 'clusters_departamento.parquet')
        data['kpi_pago'] = pd.read_parquet(DATA_DIR / 'kpi_medio_pago.parquet')
        data['rentabilidad_ticket'] = pd.read_parquet(DATA_DIR / 'rentabilidad_ticket.parquet')
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return None
    return data

data = load_all_data()
if not data:
    st.stop()

# =============================================================================
# HEADER
# =============================================================================
st.markdown("""
<div style='background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
            padding: 2.5rem; border-radius: 15px; text-align: center;
            box-shadow: 0 10px 30px rgba(26, 35, 126, 0.4); margin-bottom: 2rem;'>
    <h1 style='color: #ffd700; margin: 0; font-size: 2.8rem; font-weight: 800;'>
        📊 SUPERMERCADO NINO - DASHBOARD ANALÍTICO
    </h1>
    <p style='color: rgba(255,255,255,0.95); margin: 0.8rem 0 0 0; font-size: 1.2rem;'>
        Insights de Datos para Aumentar Rentabilidad del Ticket
    </p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# RESUMEN EJECUTIVO
# =============================================================================
st.markdown("## 📊 Resumen Ejecutivo del Dataset")

alcance = data['alcance'].iloc[0]
kpis = data['kpis_base'].iloc[0]

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📅 Período", f"{alcance['min_fecha'].strftime('%d/%m/%Y')}\n{alcance['max_fecha'].strftime('%d/%m/%Y')}")
with col2:
    st.metric("🧾 Tickets", formatear_numero_argentino(alcance['n_tickets']))
with col3:
    st.metric("📦 SKUs Únicos", formatear_numero_argentino(alcance['n_skus_unicos']))
with col4:
    st.metric("💰 Ventas Totales", f"{formatear_moneda_argentina(alcance['ventas_total']/1e6, 1)}M")

st.markdown("### KPIs Principales")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Rentabilidad Global", f"{formatear_numero_argentino(kpis['rentabilidad_global']*100, 2)}%")
with col2:
    st.metric("Ticket Promedio", formatear_moneda_argentina(kpis['ticket_promedio']))
with col3:
    st.metric("Items/Ticket", formatear_numero_argentino(kpis['items_promedio_ticket'], 2))
with col4:
    st.metric("Margen/Ticket", f"{formatear_numero_argentino((kpis['rentabilidad_promedio_ticket']/kpis['ticket_promedio'])*100, 1)}%")

# Calcular los valores formateados ANTES de usarlos en el texto
rentabilidad_global_pct = formatear_numero_argentino(kpis['rentabilidad_global']*100, 2)
ticket_promedio = formatear_moneda_argentina(kpis['ticket_promedio'])
margen_ticket_pct = formatear_numero_argentino((kpis['rentabilidad_promedio_ticket']/kpis['ticket_promedio'])*100, 1)
mendocino_promedio = formatear_numero_argentino(10800)

st.markdown(f"""
<div style='background: #e8f5e9; border-left: 6px solid #4caf50; padding: 20px; margin: 20px 0; border-radius: 10px;'>
    <h4 style='color: #2e7d32; margin: 0;'>💡 Insight Clave</h4>
    <p style='margin: 10px 0 0 0;'>
        Con <b>rentabilidad global del {rentabilidad_global_pct}%</b> y <b>ticket promedio de {ticket_promedio}</b>,
        NINO está <b>por encima del promedio</b> mendocino (${mendocino_promedio} según INDEC).
        Sin embargo, el <b>margen por ticket ({margen_ticket_pct}%)</b> indica oportunidad de optimizar
        el <b>mix de productos</b> hacia categorías de mayor rentabilidad.
    </p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# TABS PRINCIPALES
# =============================================================================
tabs = st.tabs([
    "📈 Análisis Temporal",
    "🎯 Pareto & Mix",
    "🛒 Market Basket (Combos)",
    "👥 Segmentación",
    "💳 Medios de Pago",
    "🚀 Estrategias Priorizadas",
    "📋 Informe Ejecutivo"
])

# =============================================================================
# TAB 1: ANÁLISIS TEMPORAL
# =============================================================================
with tabs[0]:
    st.markdown("## 📈 Análisis Temporal - Detectar Patrones de Compra")

    # Ventas diarias con cortes de mes
    st.markdown("### Ventas Diarias (con cortes de mes)")

    kpi_diario = data['kpi_diario'].copy()
    kpi_diario['fecha'] = pd.to_datetime(kpi_diario['fecha'])
    kpi_diario['mes'] = kpi_diario['fecha'].dt.to_period('M')

    fig_diario = go.Figure()
    fig_diario.add_trace(go.Scatter(
        x=kpi_diario['fecha'],
        y=kpi_diario['ventas'],
        mode='lines',
        name='Ventas Diarias',
        line=dict(color='#1a237e', width=2),
        fill='tozeroy',
        fillcolor='rgba(26, 35, 126, 0.1)'
    ))

    fig_diario.update_layout(
        title="Evolución Diaria de Ventas (Período Completo)",
        xaxis_title="Fecha",
        yaxis_title="Ventas ($)",
        height=500,
        hovermode='x unified'
    )
    st.plotly_chart(fig_diario, use_container_width=True)

    st.markdown("""
    <div style='background: #fff3e0; border-left: 6px solid #ff9800; padding: 20px; margin: 20px 0; border-radius: 10px;'>
        <h4 style='color: #e65100; margin: 0;'>🔍 Insight: Estacionalidad Mensual</h4>
        <p style='margin: 10px 0 0 0;'>
            Se observan <b>picos de ventas al inicio/medio de mes</b> (cobro de salarios) y
            <b>caídas hacia fin de mes</b>. <b>Estrategia sugerida:</b> Aplicar
            <b>promociones umbral</b> ("$500 off en compras >$5000") en <b>días 1-15 de cada mes</b>
            para capitalizar el mayor poder adquisitivo. En días 20-30, activar
            <b>descuentos por combo</b> para mantener volumen.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Ventas por día del MES (último mes)
    st.markdown("### Ventas por Día del Mes (Último Mes Completo)")

    ultimo_periodo = kpi_diario['mes'].max()
    mes_anterior = ultimo_periodo - 1
    kpi_ultimo_mes = kpi_diario[kpi_diario['mes'] == mes_anterior].copy()
    kpi_ultimo_mes['dia_mes'] = kpi_ultimo_mes['fecha'].dt.day

    fig_dia_mes = px.bar(
        kpi_ultimo_mes,
        x='dia_mes',
        y='ventas',
        title=f"Ventas por Día del Mes ({mes_anterior})",
        labels={'dia_mes': 'Día del Mes', 'ventas': 'Ventas ($)'}
    )
    fig_dia_mes.update_traces(marker_color='#283593')
    st.plotly_chart(fig_dia_mes, use_container_width=True)

    st.markdown("""
    <div style='background: #e8f5e9; border-left: 6px solid #4caf50; padding: 20px; margin: 20px 0; border-radius: 10px;'>
        <h4 style='color: #2e7d32; margin: 0;'>💡 Acción: Promociones por Ciclo de Pago</h4>
        <p style='margin: 10px 0 0 0;'>
            <b>Días 1-10:</b> Mayor poder de compra → Promociones umbral ($X off en compras >$Y)<br>
            <b>Días 15-20:</b> Refuerzo de quincena → Combos de alto margen<br>
            <b>Días 25-30:</b> Fin de mes crítico → Descuentos focalizados en básicos
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Por día de semana (promedio)
    st.markdown("### Ventas Promedio por Día de Semana")

    kpi_dow = data['kpi_dia'].copy()
    # Traducir días al español y ordenar
    dias_map = {
        'Monday': 'Lunes',
        'Tuesday': 'Martes',
        'Wednesday': 'Miércoles',
        'Thursday': 'Jueves',
        'Friday': 'Viernes',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }
    kpi_dow['dia_esp'] = kpi_dow['dia_semana'].map(dias_map)
    orden_dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    kpi_dow['dia_esp'] = pd.Categorical(kpi_dow['dia_esp'], categories=orden_dias, ordered=True)
    kpi_dow = kpi_dow.sort_values('dia_esp')

    # Calcular promedio por día
    kpi_dow['ticket_promedio'] = kpi_dow['ventas'] / kpi_dow['tickets']

    fig_dow = go.Figure()
    fig_dow.add_trace(go.Bar(
        x=kpi_dow['dia_esp'],
        y=kpi_dow['ventas'],
        name='Ventas Promedio',
        marker_color='#1a237e',
        yaxis='y',
        text=kpi_dow['ventas'].apply(lambda x: f'${x/1e6:.1f}M'),
        textposition='outside'
    ))
    fig_dow.add_trace(go.Scatter(
        x=kpi_dow['dia_esp'],
        y=kpi_dow['ticket_promedio'],
        name='Ticket Promedio',
        line=dict(color='#ff9800', width=3),
        yaxis='y2'
    ))
    fig_dow.update_layout(
        title="Ventas y Ticket Promedio por Día de Semana (Promedio del Período)",
        xaxis_title="Día de Semana",
        yaxis=dict(title="Ventas ($)"),
        yaxis2=dict(title="Ticket Promedio ($)", overlaying='y', side='right'),
        height=500,
        hovermode='x unified'
    )
    st.plotly_chart(fig_dow, use_container_width=True)

    st.markdown("""
    <div style='background: #fff3e0; border-left: 6px solid #ff9800; padding: 20px; margin: 20px 0; border-radius: 10px;'>
        <h4 style='color: #e65100; margin: 0;'>🔍 Insight: Fin de Semana = Tickets Grandes</h4>
        <p style='margin: 10px 0 0 0;'>
            Los <b>sábados muestran ticket promedio más alto</b> (compras de abastecimiento familiar).
            <b>Estrategia sugerida:</b> Implementar <b>upselling en cajas</b> los sábados
            (sugerencia de vinos, snacks premium) puede aumentar ticket +2-3%.
            <b>Lunes-miércoles:</b> Tickets más bajos → Ideal para <b>promociones de segundo producto</b>
            para aumentar UPT (unidades por ticket).
        </p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# TAB 2: PARETO & MIX
# =============================================================================
with tabs[1]:
    st.markdown("## 🎯 Análisis de Pareto - Optimizar Mix de Productos")

    st.markdown("### Curva de Pareto por Categorías")

    pareto_cat = data['pareto_cat'].head(20)

    fig_pareto = go.Figure()
    fig_pareto.add_trace(go.Bar(
        x=pareto_cat['categoria'],
        y=pareto_cat['ventas'],
        name='Ventas',
        marker_color='#1a237e',
        yaxis='y'
    ))
    fig_pareto.add_trace(go.Scatter(
        x=pareto_cat['categoria'],
        y=pareto_cat['pct_acumulado_ventas'],
        name='% Acumulado',
        line=dict(color='#ff6b6b', width=4),
        yaxis='y2'
    ))
    # Línea 80/20 - usando add_shape para especificar yaxis
    fig_pareto.add_shape(
        type="line",
        x0=0,
        x1=1,
        y0=80,
        y1=80,
        xref="paper",
        yref="y2",
        line=dict(color="green", width=2, dash="dash")
    )
    fig_pareto.add_annotation(
        x=0.95,
        y=80,
        xref="paper",
        yref="y2",
        text="80% (Regla Pareto)",
        showarrow=False,
        font=dict(color="green")
    )
    fig_pareto.update_layout(
        title="Top 20 Categorías - Curva de Pareto 80/20",
        xaxis_title="Categoría",
        yaxis=dict(title="Ventas ($)"),
        yaxis2=dict(title="% Acumulado", overlaying='y', side='right', range=[0, 100]),
        height=500,
        hovermode='x unified'
    )
    st.plotly_chart(fig_pareto, use_container_width=True)

    # Calcular cuántas categorías hacen el 80%
    cats_80 = pareto_cat[pareto_cat['pct_acumulado_ventas'] <= 80]
    n_cats_80 = len(cats_80)
    total_cats = len(data['pareto_cat'])

    st.markdown(f"""
    <div style='background: #e8f5e9; border-left: 6px solid #4caf50; padding: 20px; margin: 20px 0; border-radius: 10px;'>
        <h4 style='color: #2e7d32; margin: 0;'>💡 Insight: Concentración de Ventas</h4>
        <p style='margin: 10px 0 0 0;'>
            <b>{n_cats_80} categorías</b> (de {total_cats}) generan el <b>80% de las ventas</b>.
            Estas son las <b>categorías tipo A</b> que requieren:<br>
            • <b>Stock prioritario</b> (evitar quiebres)<br>
            • <b>Ubicación premium en góndola</b><br>
            • <b>Cross-merchandising</b> con productos complementarios<br><br>
            <b>Estrategia #1:</b> Introducir <b>marca propia</b> en estas categorías tipo A
            puede aumentar margen +2-5 pp (según benchmark de sector).
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Margen por categoría
    st.markdown("### Rentabilidad por Categoría (Top 15)")

    kpi_cat = data['kpi_categoria'].head(15)

    fig_margen = go.Figure()
    fig_margen.add_trace(go.Bar(
        x=kpi_cat['categoria'],
        y=kpi_cat['ventas'],
        name='Ventas',
        marker_color='#1a237e',
        yaxis='y'
    ))
    fig_margen.add_trace(go.Scatter(
        x=kpi_cat['categoria'],
        y=kpi_cat['margen_pct'],
        name='Margen %',
        line=dict(color='#4caf50', width=4),
        mode='lines+markers',
        yaxis='y2'
    ))
    fig_margen.update_layout(
        title="Ventas vs Margen % por Categoría",
        xaxis_title="Categoría",
        yaxis=dict(title="Ventas ($)"),
        yaxis2=dict(title="Margen %", overlaying='y', side='right'),
        height=500,
        hovermode='x unified'
    )
    st.plotly_chart(fig_margen, use_container_width=True)

    # Identificar categorías de alto margen vs bajo margen
    cat_alto_margen = kpi_cat.nlargest(3, 'margen_pct')['categoria'].tolist()
    cat_bajo_margen = kpi_cat.nsmallest(3, 'margen_pct')['categoria'].tolist()

    st.markdown(f"""
    <div style='background: #fff3e0; border-left: 6px solid #ff9800; padding: 20px; margin: 20px 0; border-radius: 10px;'>
        <h4 style='color: #e65100; margin: 0;'>🔍 Insight: Oportunidad de Mix</h4>
        <p style='margin: 10px 0 0 0;'>
            <b>Categorías de ALTO margen:</b> {', '.join(cat_alto_margen)}<br>
            <b>Categorías de BAJO margen:</b> {', '.join(cat_bajo_margen)}<br><br>
            <b>Estrategia #4:</b> <b>Layout impulsor</b> - Colocar productos de alto margen
            en <b>zonas de alto tráfico</b> (fin de góndola, cajas) puede aumentar su
            participación en el ticket. Átomo logró <b>subir ventas 30%</b> tras remodelar layout.
        </p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# TAB 3: MARKET BASKET (COMBOS)
# =============================================================================
with tabs[2]:
    st.markdown("## 🛒 Market Basket Analysis - Combos Estratégicos")

    st.markdown("### 🌟 COMBO ESTRELLA: FERNET + COCA COLA")

    # Buscar la regla específica
    reglas = data['reglas']
    regla_fernet_coca = reglas[
        (reglas['antecedents'].str.contains('FERNET', na=False)) &
        (reglas['consequents'].str.contains('COCA', na=False))
    ]

    if len(regla_fernet_coca) > 0:
        regla = regla_fernet_coca.iloc[0]
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Confianza", f"{regla['confidence']*100:.1f}%",
                     help="78% de quienes compran Fernet también compran Coca")
        with col2:
            st.metric("Lift", f"{regla['lift']:.1f}x",
                     help="Compran juntos 13x más de lo esperado por azar")
        with col3:
            st.metric("Soporte", f"{regla['support']*100:.2f}%",
                     help="Aparecen juntos en 2.7% de todos los tickets")

    st.markdown("""
    <div style='background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
                border-left: 8px solid #ffd700; padding: 25px; margin: 20px 0;
                border-radius: 15px; color: white;'>
        <h4 style='color: #ffd700; margin: 0;'>💰 ESTRATEGIA #2: COMBO FERNET + COCA</h4>
        <p style='margin: 15px 0 0 0; font-size: 1.1rem;'>
            <b>Dato clave:</b> 78% de tickets con Fernet incluyen Coca (Lift 13.1x)<br>
            <b>Acción inmediata:</b><br>
            1. <b>Ubicar juntos en góndola</b> (adyacencia física)<br>
            2. <b>Combo promocional:</b> "Fernet 750cc + Coca 2.5L = $X" (10-15% descuento)<br>
            3. <b>Cartelería:</b> "El combo perfecto para tu finde"<br><br>
            <b>Impacto esperado:</b> +10-15% en ticket promedio de fines de semana
            (cuando se concentran estas compras). ROI estimado: <b>+$150K/mes</b>
            en ventas incrementales.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Top 20 reglas
    st.markdown("### Top 20 Reglas de Asociación (por Lift)")

    reglas_top = reglas.nlargest(20, 'lift')
    st.dataframe(
        reglas_top[['antecedents', 'consequents', 'support', 'confidence', 'lift']],
        hide_index=True,
        use_container_width=True
    )

    # Scatter plot
    st.markdown("### Visualización: Confidence vs Support")

    fig_scatter = px.scatter(
        reglas,
        x='support',
        y='confidence',
        size='lift',
        color='lift',
        hover_data=['antecedents', 'consequents'],
        title="Reglas de Asociación (tamaño = Lift)",
        labels={'support': 'Soporte', 'confidence': 'Confianza', 'lift': 'Lift'},
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("""
    <div style='background: #e8f5e9; border-left: 6px solid #4caf50; padding: 20px; margin: 20px 0; border-radius: 10px;'>
        <h4 style='color: #2e7d32; margin: 0;'>💡 Cómo Implementar Combos</h4>
        <p style='margin: 10px 0 0 0;'>
            <b>Prioridad 1:</b> Reglas con <b>Lift >5</b> y <b>Confianza >50%</b>
            → Combos con alta probabilidad de éxito<br>
            <b>Prioridad 2:</b> Negociar con proveedores <b>financiamiento de descuentos</b><br>
            <b>Prioridad 3:</b> Medir ROI: Ventas incrementales vs costo de descuento<br><br>
            <b>Benchmark:</b> Combos bien diseñados aumentan ventas cruzadas <b>+22%</b>
            (fuente: estudios retail internacionales citados en Estrategias_Analitica.md).
        </p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# TAB 4: SEGMENTACIÓN
# =============================================================================
with tabs[3]:
    st.markdown("## 👥 Segmentación de Tickets - Personalizar Estrategias")

    # Análisis de rentabilidad por ticket
    st.markdown("### Distribución de Rentabilidad por Ticket")

    rentabilidad = data['rentabilidad_ticket'].copy()
    rentabilidad['rentabilidad_pct'] = rentabilidad['rentabilidad_pct_ticket'] * 100
    # Filtrar valores válidos
    rentabilidad = rentabilidad[rentabilidad['rentabilidad_pct'].notna() & (rentabilidad['rentabilidad_pct'] > 0)]

    fig_hist = px.histogram(
        rentabilidad,
        x='rentabilidad_pct',
        nbins=50,
        title="Distribución de Rentabilidad por Ticket",
        labels={'rentabilidad_pct': 'Rentabilidad (%)', 'count': 'Cantidad de Tickets'},
        color_discrete_sequence=['#1a237e']
    )
    fig_hist.update_layout(
        height=400,
        showlegend=False,
        xaxis_title="Rentabilidad (%)",
        yaxis_title="Cantidad de Tickets"
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    # Calcular cuartiles
    q1 = rentabilidad['rentabilidad_pct'].quantile(0.25)
    mediana = rentabilidad['rentabilidad_pct'].quantile(0.5)
    q3 = rentabilidad['rentabilidad_pct'].quantile(0.75)

    st.markdown(f"""
    <div style='background: #fff3e0; border-left: 6px solid #ff9800; padding: 20px; margin: 20px 0; border-radius: 10px;'>
        <h4 style='color: #e65100; margin: 0;'>🔍 Insight: Variabilidad de Rentabilidad</h4>
        <p style='margin: 10px 0 0 0;'>
            <b>Q1 (25%):</b> {q1:.1f}% | <b>Mediana:</b> {mediana:.1f}% | <b>Q3 (75%):</b> {q3:.1f}%<br><br>
            Existe <b>alta variabilidad</b> en la rentabilidad por ticket.
            Tickets en el <b>cuartil inferior (<{q1:.0f}%)</b> tienen bajo margen →
            Revisar si incluyen muchos productos en promoción o categorías de bajo margen.<br><br>
            <b>Estrategia #6:</b> Implementar <b>programa de fidelización</b> para identificar
            clientes de alto valor (tickets con rentabilidad >{q3:.0f}%) y ofrecerles
            <b>ofertas personalizadas</b> que mantengan su gasto sin erosionar margen.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Segmentación simple por monto
    st.markdown("### Segmentos de Tickets por Monto")

    # Crear segmentos manualmente
    tickets_raw = data['rentabilidad_ticket'].copy()
    tickets_raw['segmento'] = pd.cut(
        tickets_raw['monto_total_ticket'],
        bins=[0, 5000, 15000, 30000, float('inf')],
        labels=['Conveniencia\n(<$5K)', 'Compra Chica\n($5K-$15K)', 'Compra Mediana\n($15K-$30K)', 'Compra Grande\n(>$30K)']
    )

    segmentos = tickets_raw.groupby('segmento').agg({
        'ticket_id': 'count',
        'monto_total_ticket': 'mean',
        'items_ticket': 'mean',
        'margen_ticket': 'mean'
    }).reset_index()
    segmentos.columns = ['segmento', 'cantidad_tickets', 'ticket_promedio', 'items_promedio', 'margen_promedio']
    segmentos['pct_tickets'] = (segmentos['cantidad_tickets'] / segmentos['cantidad_tickets'].sum() * 100).round(1)

    fig_seg = go.Figure()
    fig_seg.add_trace(go.Bar(
        x=segmentos['segmento'],
        y=segmentos['cantidad_tickets'],
        text=segmentos['pct_tickets'].apply(lambda x: f'{x}%'),
        textposition='outside',
        marker_color=['#1a237e', '#283593', '#3949ab', '#5c6bc0'],
        name='Cantidad'
    ))
    fig_seg.update_layout(
        title="Distribución de Tickets por Segmento de Monto",
        xaxis_title="Segmento",
        yaxis_title="Cantidad de Tickets",
        height=450,
        showlegend=False
    )
    st.plotly_chart(fig_seg, use_container_width=True)

    # Tabla detallada
    st.dataframe(
        segmentos[['segmento', 'cantidad_tickets', 'ticket_promedio', 'items_promedio', 'margen_promedio', 'pct_tickets']],
        hide_index=True,
        use_container_width=True
    )

    st.markdown("""
    <div style='background: #e8f5e9; border-left: 6px solid #4caf50; padding: 20px; margin: 20px 0; border-radius: 10px;'>
        <h4 style='color: #2e7d32; margin: 0;'>💡 Estrategias por Segmento</h4>
        <p style='margin: 10px 0 0 0;'>
            <b>Compra Grande (Ticket >$20K):</b> Upselling de productos premium en caja<br>
            <b>Compra Mediana ($5K-$20K):</b> Promociones umbral para subir a siguiente nivel<br>
            <b>Compra de Conveniencia (<$5K):</b> Combos y descuentos en segunda unidad<br><br>
            <b>Estrategia #5:</b> Capacitar cajeros en <b>upselling</b> según segmento detectado
            puede aumentar UPT +0.2 ítems (+2-3% en ticket).
        </p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# TAB 5: MEDIOS DE PAGO
# =============================================================================
with tabs[4]:
    st.markdown("## 💳 Análisis de Medios de Pago")

    # Gráfico de torta
    st.markdown("### Participación de Ventas por Medio de Pago")

    pago_summary = data['kpi_pago'].groupby('tipo_medio_pago').agg({
        'tickets': 'sum',
        'ventas': 'sum',
        'margen': 'sum'
    }).reset_index()
    pago_summary['participacion'] = (pago_summary['ventas'] / pago_summary['ventas'].sum() * 100).round(1)

    fig_pie = px.pie(
        pago_summary,
        values='ventas',
        names='tipo_medio_pago',
        title="Distribución de Ventas por Medio de Pago",
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Blues_r
    )
    fig_pie.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Ventas: $%{value:,.0f}<br>Participación: %{percent}'
    )
    fig_pie.update_layout(height=500)
    st.plotly_chart(fig_pie, use_container_width=True)

    # Métricas clave
    col1, col2, col3 = st.columns(3)
    efectivo_pct = pago_summary[pago_summary['tipo_medio_pago'] == 'EFECTIVO']['participacion'].values[0] if len(pago_summary[pago_summary['tipo_medio_pago'] == 'EFECTIVO']) > 0 else 0
    tarjeta_pct = 100 - efectivo_pct

    with col1:
        st.metric("% Efectivo", f"{formatear_numero_argentino(efectivo_pct, 1)}%")
    with col2:
        st.metric("% Tarjeta", f"{formatear_numero_argentino(tarjeta_pct, 1)}%")
    with col3:
        ticket_efectivo = pago_summary[pago_summary['tipo_medio_pago'] == 'EFECTIVO']['ventas'].sum() / pago_summary[pago_summary['tipo_medio_pago'] == 'EFECTIVO']['tickets'].sum() if len(pago_summary[pago_summary['tipo_medio_pago'] == 'EFECTIVO']) > 0 else 0
        st.metric("Ticket Efectivo", formatear_moneda_argentina(ticket_efectivo))

    st.markdown("""
    <div style='background: #fff3e0; border-left: 6px solid #ff9800; padding: 20px; margin: 20px 0; border-radius: 10px;'>
        <h4 style='color: #e65100; margin: 0;'>🔍 Insight: Oportunidad en Medios de Pago</h4>
        <p style='margin: 10px 0 0 0;'>
            <b>Estrategia #2 (variante):</b> Negociar con bancos <b>descuentos co-financiados</b>
            en días específicos (ej: "Martes de descuento con Banco X").<br><br>
            En 2024-2025, <b>alianzas súper-banco-billetera</b> fueron clave para mantener volumen
            sin sacrificar margen. Benchmark: descuentos bancarios pueden <b>aumentar ventas +15%</b>
            en días promocionales sin impactar margen del negocio.
        </p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# TAB 6: ESTRATEGIAS PRIORIZADAS
# =============================================================================
with tabs[5]:
    st.markdown("## 🚀 Estrategias Priorizadas - Plan de Acción")

    st.markdown("""
    <div style='background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
                padding: 30px; margin: 20px 0; border-radius: 15px; color: white;'>
        <h3 style='color: #ffd700; margin: 0 0 20px 0;'>🎯 PLAN DE ACCIÓN - PRÓXIMOS 90 DÍAS</h3>
        <p style='font-size: 1.1rem;'>
            Basado en el análisis de datos, se recomienda implementar las siguientes estrategias
            en orden de <b>prioridad por impacto esperado</b>:
        </p>
    </div>
    """, unsafe_allow_html=True)

    estrategias_html = """
    <style>
    .estrategia {
        background: white;
        border-left: 8px solid;
        padding: 25px;
        margin: 20px 0;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .impacto-alto { border-color: #4caf50; }
    .impacto-medio { border-color: #ff9800; }
    .impacto-bajo { border-color: #9e9e9e; }
    .estrategia h4 { margin: 0 0 10px 0; }
    .estrategia .tag {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: bold;
        margin-right: 10px;
    }
    .tag-alto { background: #4caf50; color: white; }
    .tag-medio { background: #ff9800; color: white; }
    .tag-bajo { background: #9e9e9e; color: white; }
    </style>

    <div class="estrategia impacto-alto">
        <span class="tag tag-alto">IMPACTO ALTO</span>
        <h4>📦 Estrategia #1: Promos Inteligentes - Combos Focalizados</h4>
        <p><b>Dato que respalda:</b> Combo Fernet + Coca tiene Lift 13.1x (78% de confianza)</p>
        <p><b>Acción:</b></p>
        <ul>
            <li>Crear combo físico en góndola: Fernet + Coca juntos con cartel</li>
            <li>Precio combo: 10% descuento vs suma individual</li>
            <li>Implementar en fin de semana (sábados = tickets grandes)</li>
        </ul>
        <p><b>Meta:</b> Aumentar ticket promedio +10% en fines de semana</p>
        <p><b>Inversión:</b> $0 (descuento absorbido por margen actual)</p>
        <p><b>ROI esperado:</b> +${formatear_numero_argentino(150000)}/mes en ventas incrementales</p>
    </div>

    <div class="estrategia impacto-alto">
        <span class="tag tag-alto">IMPACTO ALTO</span>
        <h4>🏷️ Estrategia #2: Optimizar Surtido - Marca Propia en Categorías A</h4>
        <p><b>Dato que respalda:</b> 8 categorías generan 80% de ventas (Pareto)</p>
        <p><b>Acción:</b></p>
        <ul>
            <li>Identificar productos de alta rotación en categorías A sin marca propia</li>
            <li>Negociar con proveedores regionales marca NINO o segunda marca exclusiva</li>
            <li>Posicionar al lado de marcas líderes con 15-20% menor precio</li>
        </ul>
        <p><b>Meta:</b> Marca propia alcance 10% de ventas en categorías A</p>
        <p><b>Mejora margen:</b> +2-5 pp en margen bruto global</p>
    </div>

    <div class="estrategia impacto-medio">
        <span class="tag tag-medio">IMPACTO MEDIO</span>
        <h4>🏪 Estrategia #3: Layout Impulsor - Cross-Merchandising</h4>
        <p><b>Dato que respalda:</b> Átomo aumentó ventas 30% tras remodelar layout</p>
        <p><b>Acción:</b></p>
        <ul>
            <li>Piloto: Reubicar 3 categorías de alto margen a zonas de alto tráfico</li>
            <li>Crear exhibiciones conjuntas según reglas de asociación</li>
            <li>Productos impulso (snacks, bebidas) en puntos de espera</li>
        </ul>
        <p><b>Meta:</b> UPT +0.5 ítems (de 10.07 a 10.57)</p>
        <p><b>Inversión:</b> ${formatear_numero_argentino(50000)} (reposicionamiento, cartelería)</p>
        <p><b>Ticket esperado:</b> +3-5%</p>
    </div>

    <div class="estrategia impacto-medio">
        <span class="tag tag-medio">IMPACTO MEDIO</span>
        <h4>🎓 Estrategia #4: Capacitación en Upselling</h4>
        <p><b>Dato que respalda:</b> Tickets grandes los sábados (mayor receptividad)</p>
        <p><b>Acción:</b></p>
        <ul>
            <li>Entrenar cajeros: sugerir 1 producto complementario al finalizar compra</li>
            <li>Focus en fines de semana cuando ticket es mayor</li>
            <li>Productos sugeridos: vinos, snacks premium, panadería</li>
        </ul>
        <p><b>Meta:</b> 10% de clientes agregan 1 ítem sugerido</p>
        <p><b>Ticket esperado:</b> +2-3%</p>
    </div>

    <div class="estrategia impacto-medio">
        <span class="tag tag-medio">IMPACTO MEDIO</span>
        <h4>💎 Estrategia #5: Programa de Fidelización</h4>
        <p><b>Dato que respalda:</b> Alta variabilidad en rentabilidad por ticket (Q1=20%, Q3=35%)</p>
        <p><b>Acción:</b></p>
        <ul>
            <li>Tarjeta de cliente frecuente (física o digital)</li>
            <li>Identificar clientes de alto valor (tickets >Q3)</li>
            <li>Ofertas personalizadas según historial de compra</li>
        </ul>
        <p><b>Meta:</b> 30% de clientes registrados en 6 meses</p>
        <p><b>Retención esperada:</b> +20 pp (de 50% a 70%)</p>
        <p><b>Ticket clientes fieles:</b> +10% vs no registrados</p>
    </div>

    <div class="estrategia impacto-bajo">
        <span class="tag tag-bajo">MEJORA CONTINUA</span>
        <h4>📊 Estrategia #6: Monitoreo Continuo - Dashboard de KPIs</h4>
        <p><b>Dato que respalda:</b> "Lo que no se mide no se mejora"</p>
        <p><b>Acción:</b></p>
        <ul>
            <li>Revisar este dashboard semanalmente</li>
            <li>Configurar alertas: ticket promedio cae >10%, quiebres de stock, merma >2%</li>
            <li>Reunión mensual: revisar KPIs y ajustar estrategias</li>
        </ul>
        <p><b>Objetivo:</b> Toma de decisiones <b>data-driven</b> (basada en datos)</p>
    </div>
    """

    st.markdown(estrategias_html, unsafe_allow_html=True)

    # Resumen de impacto acumulado
    st.markdown("""
    <div style='background: linear-gradient(135deg, #4caf50 0%, #8bc34a 100%);
                padding: 30px; margin: 30px 0; border-radius: 15px; color: white;'>
        <h3 style='margin: 0 0 15px 0;'>📈 IMPACTO ACUMULADO ESTIMADO (6 MESES)</h3>
        <div style='display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-top: 20px;'>
            <div style='background: rgba(255,255,255,0.2); padding: 20px; border-radius: 10px; text-align: center;'>
                <h4 style='margin: 0; font-size: 2rem;'>+12-18%</h4>
                <p style='margin: 5px 0 0 0;'>Ticket Promedio</p>
            </div>
            <div style='background: rgba(255,255,255,0.2); padding: 20px; border-radius: 10px; text-align: center;'>
                <h4 style='margin: 0; font-size: 2rem;'>+3-5pp</h4>
                <p style='margin: 5px 0 0 0;'>Margen Bruto</p>
            </div>
            <div style='background: rgba(255,255,255,0.2); padding: 20px; border-radius: 10px; text-align: center;'>
                <h4 style='margin: 0; font-size: 2rem;'>+$2-3M</h4>
                <p style='margin: 5px 0 0 0;'>Ventas Incrementales/Año</p>
            </div>
        </div>
        <p style='margin: 20px 0 0 0; text-align: center; font-size: 1.1rem;'>
            <b>Fuente:</b> Estimaciones basadas en benchmarks de sector (Estrategias_Analitica.md)
            y datos propios de NINO
        </p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1.5rem; background: #f5f5f5; border-radius: 10px;'>
    <p style='margin: 0; font-size: 1.1rem;'><b>Dashboard Supermercado NINO</b></p>
    <p style='margin: 5px 0 0 0; font-size: 0.9rem; color: #999;'>
        Pyme Inside
    </p>
</div>
""", unsafe_allow_html=True)

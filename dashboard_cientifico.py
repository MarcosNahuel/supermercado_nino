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
from calendar import monthrange
import numpy as np
import unicodedata

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
        # Cargar archivos básicos con manejo de errores específico
        required_files = {
            'alcance': 'alcance_dataset.parquet',
            'kpis_base': 'kpis_base.parquet',
            'kpi_diario': 'kpi_diario.parquet',
            'kpi_periodo': 'kpi_periodo.parquet',
            'kpi_semana': 'kpi_semana.parquet',
            'kpi_dia': 'kpi_dia.parquet',
            'kpi_categoria': 'kpi_categoria.parquet',
            'kpi_hora': 'kpi_hora.parquet',
            'pareto_cat': 'pareto_cat_global.parquet',
            'pareto_prod': 'pareto_prod_global.parquet',
            'reglas': 'reglas.parquet',
            'combos': 'combos_recomendados.parquet',
            'adjacency': 'adjacency_pairs.parquet',
            'clusters_tickets': 'clusters_tickets.parquet',
            'clusters_depto': 'clusters_departamento.parquet',
            'kpi_pago': 'kpi_medio_pago.parquet',
            'rentabilidad_ticket': 'rentabilidad_ticket.parquet'
        }

        for key, filename in required_files.items():
            try:
                data[key] = pd.read_parquet(DATA_DIR / filename)
                print(f"✓ Loaded {filename}")
            except Exception as e:
                print(f"✗ Error loading {filename}: {e}")
                data[key] = pd.DataFrame()  # Crear DataFrame vacío para evitar errores posteriores

        # Cargar datos horarios del CSV
        horario_path = Path('data/raw/comprobantes_ventas_horario.csv')
        if horario_path.exists():
            try:
                print("Loading horario CSV...")
                horario_df = pd.read_csv(
                    horario_path,
                    sep=';',
                    dtype=str,
                    engine='python'
                )
                print(f"✓ Loaded CSV with {len(horario_df)} rows")

                # Verificar columnas requeridas
                required_columns = ['Fecha', 'Hora', 'Comprobante']
                missing_columns = [col for col in required_columns if col not in horario_df.columns]
                if missing_columns:
                    print(f"✗ Missing columns in CSV: {missing_columns}")
                    data['horario_semana'] = pd.DataFrame()
                    data['horario_semana_matrix'] = pd.DataFrame()
                else:
                    # Procesar fechas
                    horario_df['Fecha'] = pd.to_datetime(
                        horario_df['Fecha'].str.replace(',000', '', regex=False),
                        format='%Y-%m-%d %H:%M:%S',
                        errors='coerce'
                    )
                    horario_df['Hora'] = pd.to_datetime(
                        horario_df['Hora'].str.replace(',000', '', regex=False),
                        format='%Y-%m-%d %H:%M:%S',
                        errors='coerce'
                    )

                    # Verificar si hay fechas válidas
                    valid_dates = horario_df['Fecha'].notna() & horario_df['Hora'].notna()
                    if valid_dates.sum() == 0:
                        print("✗ No valid dates found in CSV")
                        data['horario_semana'] = pd.DataFrame()
                        data['horario_semana_matrix'] = pd.DataFrame()
                    else:
                        horario_df = horario_df.dropna(subset=['Fecha', 'Hora'])
                        horario_df['hora'] = horario_df['Hora'].dt.hour.astype(int)

                        dias_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                        dias_map = {
                            'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
                            'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
                        }

                        horario_df['dia_eng'] = horario_df['Fecha'].dt.day_name()
                        horario_df = horario_df[horario_df['dia_eng'].isin(dias_order)]
                        horario_df['dia'] = horario_df['dia_eng'].map(dias_map)
                        horario_df['dia_idx'] = horario_df['dia_eng'].apply(dias_order.index)

                        horario_semana = (
                            horario_df.groupby(['dia_idx', 'dia', 'hora'], as_index=False)
                            .agg(comprobantes=('Comprobante', 'count'))
                            .sort_values(['dia_idx', 'hora'])
                        )

                        horario_pivot = (
                            horario_semana.pivot(index='dia', columns='hora', values='comprobantes')
                            .reindex(['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'])
                            .fillna(0)
                        )

                        data['horario_semana'] = horario_semana
                        data['horario_semana_matrix'] = horario_pivot
                        print(f"✓ Processed horario data: {horario_semana.shape}")

            except Exception as e:
                print(f"✗ Error processing horario CSV: {e}")
                data['horario_semana'] = pd.DataFrame()
                data['horario_semana_matrix'] = pd.DataFrame()
        else:
            print("✗ Horario CSV file not found")
            data['horario_semana'] = pd.DataFrame()
            data['horario_semana_matrix'] = pd.DataFrame()

    except Exception as e:
        st.error(f"Error general cargando datos: {e}")
        print(f"✗ General error: {e}")
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
# TAB 1: ANALISIS TEMPORAL
# =============================================================================
with tabs[0]:
    st.markdown("## Ritmo de comprobantes")

    detalle_tickets = data.get('rentabilidad_ticket')

    if detalle_tickets is None or detalle_tickets.empty:
        st.warning("No se encontraron tickets para esta vista temporal.")
    else:
        detalle_tickets = detalle_tickets.copy()
        detalle_tickets['fecha'] = pd.to_datetime(detalle_tickets['fecha'])
        detalle_tickets['ticket_id'] = detalle_tickets['ticket_id'].astype(str)
        max_fecha = detalle_tickets['fecha'].max()
        ultimo_mes_incompleto = None
        if pd.notna(max_fecha):
            dias_mes = monthrange(max_fecha.year, max_fecha.month)[1]
            if max_fecha.day < dias_mes:
                ultimo_mes_incompleto = max_fecha.to_period('M')
        if ultimo_mes_incompleto is not None:
            detalle_tickets = detalle_tickets[
                detalle_tickets['fecha'].dt.to_period('M') != ultimo_mes_incompleto
            ]
        if detalle_tickets.empty:
            st.warning("Al filtrar el mes parcial mas reciente no quedaron datos suficientes para esta vista.")
            st.stop()

        # -------------------------
        # Mensual (tickets por mes)
        # -------------------------
        kpi_periodo = data.get('kpi_periodo')
        if kpi_periodo is not None and not kpi_periodo.empty:
            kpi_periodo_plot = kpi_periodo.copy()
            kpi_periodo_plot['periodo_dt'] = pd.to_datetime(kpi_periodo_plot['periodo'].astype(str) + '-01')
            kpi_periodo_plot = kpi_periodo_plot.sort_values('periodo_dt')
            if ultimo_mes_incompleto is not None:
                # Drop trailing partial month (ej. octubre 2025 incompleto)
                kpi_periodo_plot = kpi_periodo_plot[
                    kpi_periodo_plot['periodo_dt'].dt.to_period('M') != ultimo_mes_incompleto
                ]
            kpi_periodo_plot['periodo_label'] = kpi_periodo_plot['periodo_dt'].dt.strftime('%Y-%m')
        else:
            kpi_periodo_plot = pd.DataFrame(columns=['periodo_label', 'tickets'])

        # -------------------------
        # Semanal (tickets por semana)
        # -------------------------
        kpi_semana = data.get('kpi_semana')
        if kpi_semana is not None and not kpi_semana.empty:
            try:
                # Verificar si existe la columna semana_iso
                if 'semana_iso' not in kpi_semana.columns:
                    print("✗ semana_iso column missing from kpi_semana")
                    kpi_semana_plot = pd.DataFrame(columns=['semana_inicio', 'tickets', 'semana_label', 'mes_periodo'])
                else:
                    kpi_semana_plot = kpi_semana.copy()
                    kpi_semana_plot['semana_inicio'] = kpi_semana_plot['semana_iso'].apply(
                        lambda s: pd.to_datetime(s + '-1', format='%G-W%V-%u')
                    )
                    kpi_semana_plot = kpi_semana_plot.sort_values('semana_inicio')
                    if ultimo_mes_incompleto is not None:
                        kpi_semana_plot = kpi_semana_plot[
                            kpi_semana_plot['semana_inicio'].dt.to_period('M') != ultimo_mes_incompleto
                        ]
                    if kpi_semana_plot.empty:
                        kpi_semana_plot = pd.DataFrame(columns=['semana_inicio', 'tickets', 'semana_label', 'mes_periodo'])
                    else:
                        kpi_semana_plot['semana_label'] = kpi_semana_plot['semana_inicio'].dt.strftime('%Y-%m-%d')
                        kpi_semana_plot['mes_periodo'] = kpi_semana_plot['semana_inicio'].dt.to_period('M')
            except Exception as e:
                print(f"✗ Error processing kpi_semana: {e}")
                kpi_semana_plot = pd.DataFrame(columns=['semana_inicio', 'tickets', 'semana_label', 'mes_periodo'])
        else:
            kpi_semana_plot = pd.DataFrame(columns=['semana_inicio', 'tickets', 'semana_label', 'mes_periodo'])

        # -------------------------
        # Diario (tickets cada 30 minutos)
        # -------------------------
        kpi_dia = data.get('kpi_dia')
        tickets_dia = None
        if kpi_dia is not None and not kpi_dia.empty:
            try:
                mapa_dias = {
                    'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
                    'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
                }

                # Verificar si existe la columna dia_semana
                if 'dia_semana' not in kpi_dia.columns:
                    print("✗ dia_semana column missing from kpi_dia")
                    tickets_dia = None
                else:
                    kpi_dia = kpi_dia.copy()
                    kpi_dia['dia'] = kpi_dia['dia_semana'].map(mapa_dias)
                    kpi_dia = kpi_dia.dropna(subset=['dia'])
                    tickets_dia = (
                        kpi_dia.groupby('dia', as_index=False)
                        .agg(
                            tickets_totales=('tickets', 'sum'),
                            ventas_totales=('ventas', 'sum')
                        )
                    )
                    tickets_dia['ticket_promedio'] = tickets_dia['ventas_totales'] / tickets_dia['tickets_totales']
                    orden = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
                    tickets_dia['dia'] = pd.Categorical(tickets_dia['dia'], categories=orden, ordered=True)
                    tickets_dia = tickets_dia.sort_values('dia')
            except Exception as e:
                print(f"✗ Error processing kpi_dia: {e}")
                tickets_dia = None
        else:
            tickets_dia = None

        # -------------------------
        # Quincenal (tickets por quincena)
        # -------------------------
        detalle_tickets['mes_periodo'] = detalle_tickets['fecha'].dt.to_period('M')
        detalle_tickets['quincena'] = np.where(
            detalle_tickets['fecha'].dt.day <= 15,
            'Quincena 1',
            'Quincena 2'
        )
        detalle_tickets['quincena_label'] = (
            detalle_tickets['mes_periodo'].astype(str) + ' ' + detalle_tickets['quincena']
        )
        detalle_tickets['quincena_order'] = detalle_tickets['mes_periodo'].dt.to_timestamp()
        detalle_tickets['quincena_idx'] = detalle_tickets['quincena'].map({'Quincena 1': 1, 'Quincena 2': 2})

        tickets_quincena = (
            detalle_tickets.groupby(['quincena_order', 'quincena_idx', 'quincena_label'], as_index=False)
            .agg(tickets=('ticket_id', 'nunique'))
            .sort_values(['quincena_order', 'quincena_idx'])
        )

        col_mensual, col_semanal = st.columns(2)
        with col_mensual:
            st.markdown("### Mensual - Tickets por mes")
            if not kpi_periodo_plot.empty:
                fig_mensual = px.bar(
                    kpi_periodo_plot,
                    x='periodo_label',
                    y='tickets',
                    labels={'periodo_label': 'Mes', 'tickets': 'Tickets unicos'},
                    color_discrete_sequence=['#1a237e']
                )
                fig_mensual.update_layout(
                    height=420,
                    xaxis_tickangle=-35
                )
                st.plotly_chart(fig_mensual, use_container_width=True)
            else:
                st.info("No hay datos suficientes para el análisis mensual.")

        with col_semanal:
            st.markdown("### Semanal - Tickets por semana")
            if not kpi_semana_plot.empty:
                fig_semanal = px.bar(
                    kpi_semana_plot,
                    x='semana_inicio',
                    y='tickets',
                    labels={'semana_inicio': 'Semana (inicio)', 'tickets': 'Tickets unicos'},
                    color_discrete_sequence=['#3949ab']
                )
                if 'semana_label' in kpi_semana_plot:
                    customdata = np.column_stack([kpi_semana_plot['semana_label']])
                    fig_semanal.update_traces(
                        customdata=customdata,
                        hovertemplate="Semana: %{customdata[0]}<br>Tickets: %{y:,}<extra></extra>"
                    )
                axis_kwargs = {
                    'tickangle': -35,
                    'tickformat': '%b %Y',
                    'dtick': 'M1'
                }
                if 'mes_periodo' in kpi_semana_plot:
                    meses_series = (
                        kpi_semana_plot['mes_periodo']
                        .dropna()
                        .drop_duplicates()
                        .sort_values()
                    )
                    meses = list(meses_series)
                    if meses:
                        x_min = meses[0].to_timestamp()
                        ultimo_periodo = meses[-1]
                        ultimo_dia_mes = ultimo_periodo.to_timestamp('M')
                        x_max = ultimo_dia_mes + pd.Timedelta(hours=23, minutes=59, seconds=59)
                        for idx, periodo in enumerate(meses):
                            inicio_mes = periodo.to_timestamp()
                            if idx + 1 < len(meses):
                                fin_mes = meses[idx + 1].to_timestamp()
                            else:
                                fin_mes = x_max
                            fillcolor = '#e8eaf6' if idx % 2 == 0 else '#f5f5f5'
                            fig_semanal.add_vrect(
                                x0=inicio_mes,
                                x1=fin_mes,
                                fillcolor=fillcolor,
                                opacity=0.18,
                                layer='below',
                                line_width=0
                            )
                            if idx + 1 < len(meses):
                                boundary = meses[idx + 1].to_timestamp()
                                fig_semanal.add_vline(
                                    x=boundary,
                                    line_width=1,
                                    line_dash='dot',
                                    line_color='#9e9e9e'
                                )
                        axis_kwargs['range'] = [x_min, x_max]
                fig_semanal.update_layout(height=420)
                fig_semanal.update_xaxes(**axis_kwargs)
                st.plotly_chart(fig_semanal, use_container_width=True)
            else:
                st.info("No hay datos suficientes para el análisis semanal.")

        col_diario, col_anual = st.columns(2)
        with col_diario:
            st.markdown("### Diario - Ticket promedio por día de semana")
            if tickets_dia is not None and not tickets_dia.empty:
                fig_media_dia = px.bar(
                    tickets_dia,
                    x='dia',
                    y='ticket_promedio',
                    labels={'dia': 'Día de la semana', 'ticket_promedio': 'Ticket promedio ($)'},
                    color_discrete_sequence=['#ff9800']
                )
                fig_media_dia.update_layout(
                    height=420,
                    yaxis_tickprefix='$',
                    yaxis_tickformat=',.0f'
                )
                st.plotly_chart(fig_media_dia, use_container_width=True)
            else:
                st.info("No fue posible calcular el promedio diario con los datos disponibles.")

        with col_anual:
            st.markdown("### Anual - Tickets por quincena")
            if not tickets_quincena.empty:
                fig_quincena = px.bar(
                    tickets_quincena,
                    x='quincena_label',
                    y='tickets',
                    labels={'quincena_label': 'Periodo', 'tickets': 'Tickets unicos'},
                    color_discrete_sequence=['#3949ab']
                )
                fig_quincena.update_layout(
                    height=420,
                    xaxis_tickangle=-35
                )
                st.plotly_chart(fig_quincena, use_container_width=True)
            else:
                st.info("No hay datos suficientes para el análisis por quincena.")

        # Resumen para narrativa
        detalle_tickets['dia_semana_idx'] = detalle_tickets['fecha'].dt.weekday
        dias_map = {
            0: 'Lunes', 1: 'Martes', 2: 'Miercoles', 3: 'Jueves',
            4: 'Viernes', 5: 'Sabado', 6: 'Domingo'
        }
        dow_summary = (
            detalle_tickets
            .groupby('dia_semana_idx', as_index=False)
            .agg(tickets=('ticket_id', 'nunique'))
            .sort_values('dia_semana_idx')
        )

        if (
            not dow_summary.empty
            and tickets_dia is not None
            and not tickets_dia.empty
            and not tickets_quincena.empty
        ):
            dow_summary['label'] = dow_summary['dia_semana_idx'].map(dias_map)
            dia_fuerte = dow_summary.loc[dow_summary['tickets'].idxmax(), 'label']
            dia_top_row = tickets_dia.loc[tickets_dia['ticket_promedio'].idxmax()]
            dia_top = dia_top_row['dia']
            ticket_promedio_top = formatear_moneda_argentina(dia_top_row['ticket_promedio'], 0)
            quincena_top = tickets_quincena.loc[tickets_quincena['tickets'].idxmax(), 'quincena_label']
            st.markdown(
                f"""
                <div style='background: #ede7f6; border-left: 6px solid #5e35b1; padding: 20px; margin: 20px 0; border-radius: 10px;'>
                    <h4 style='color: #4527a0; margin: 0;'>Ritmo clave para las campanas</h4>
                    <p style='margin: 10px 0 0 0;'>
                        &bull; <b>{dia_fuerte}</b> concentra el mayor flujo semanal de tickets.<br>
                        &bull; El día con mayor ticket promedio es <b>{dia_top}</b> ({ticket_promedio_top}).<br>
                        &bull; La <b>{quincena_top}</b> marca el tramo mas intenso del calendario, util para planificar abastecimiento y promociones.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

        horario_matrix = data.get('horario_semana_matrix')
        horario_semana = data.get('horario_semana')
        st.markdown("### Horario semanal - Comprobantes por hora")
        if (
            horario_matrix is not None and hasattr(horario_matrix, 'empty') and not horario_matrix.empty
            and horario_semana is not None and not horario_semana.empty
        ):
            try:
                fig_horario = go.Figure(
                    data=go.Heatmap(
                        z=horario_matrix.values,
                        x=[f"{int(h):02d}h" for h in horario_matrix.columns],
                        y=horario_matrix.index.tolist(),
                        colorscale='Blues',
                        colorbar=dict(title='Comprobantes')
                    )
                )
                fig_horario.update_layout(
                    height=420,
                    xaxis_title="Hora del día",
                    yaxis_title="Día de la semana",
                    margin=dict(l=0, r=0, t=30, b=0)
                )
                st.plotly_chart(fig_horario, use_container_width=True)

                top_horas = horario_semana.loc[
                    horario_semana.groupby('dia_idx')['comprobantes'].idxmax()
                ].sort_values('dia_idx')
                global_top = horario_semana.sort_values('comprobantes', ascending=False).head(3)

                resumen_lines = [
                    f"<li><b>{row['dia']}</b>: pico a las <b>{int(row['hora']):02d}:00</b> con {formatear_numero_argentino(row['comprobantes'])} comprobantes.</li>"
                    for _, row in top_horas.iterrows()
                ]
                global_lines = [
                    f"<li>{row['dia']} - {int(row['hora']):02d}:00 ({formatear_numero_argentino(row['comprobantes'])} comprobantes)</li>"
                    for _, row in global_top.iterrows()
                ]
                st.markdown(
                    f"""
                    <div style='background: #e1f5fe; border-left: 6px solid #039be5;
                               padding: 18px; margin: 16px 0; border-radius: 10px;'>
                        <h4 style='color: #0277bd; margin: 0;'>Claves de la semana por hora</h4>
                        <p style='margin: 8px 0 0 0;'>Picos por día:</p>
                        <ul style='margin: 6px 0 0 16px;'>
                            {''.join(resumen_lines)}
                        </ul>
                        <p style='margin: 14px 0 0 0;'>Top 3 horarios generales:</p>
                        <ul style='margin: 6px 0 0 16px;'>
                            {''.join(global_lines)}
                        </ul>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            except Exception as e:
                print(f"✗ Error creating horario chart: {e}")
                st.info("Error generando gráfico horario. Verificar datos de comprobantes_ventas_horario.csv.")
        else:
            st.info("No se pudo construir la vista horaria; verificar la fuente `comprobantes_ventas_horario.csv`.")
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

    st.markdown("### Pareto de productos (Top 10 y participación acumulada)")

    pareto_prod = data['pareto_prod'].copy()
    top_prod_80 = pareto_prod[pareto_prod['pct_acumulado_ventas'] <= 80].head(10).copy()
    if top_prod_80.empty:
        top_prod_80 = pareto_prod.head(10).copy()

    productos_ordenados = top_prod_80.sort_values('ventas')

    fig_pareto_prod = go.Figure()
    fig_pareto_prod.add_trace(go.Bar(
        y=productos_ordenados['descripcion'],
        x=productos_ordenados['ventas'],
        orientation='h',
        name='Ventas',
        marker_color='#5b5bd6',
        hovertemplate='<b>%{y}</b><br>Ventas: $%{x:,.0f}<extra></extra>'
    ))
    fig_pareto_prod.add_trace(go.Scatter(
        y=productos_ordenados['descripcion'],
        x=productos_ordenados['pct_acumulado_ventas'],
        mode='lines+markers+text',
        name='% acumulado',
        line=dict(color='#ff6b6b', width=3),
        marker=dict(size=8),
        text=productos_ordenados['pct_acumulado_ventas'].round(1).astype(str) + '%',
        textposition='top left',
        xaxis='x2',
        hovertemplate='<b>%{y}</b><br>% acumulado: %{x:.1f}%<extra></extra>'
    ))
    fig_pareto_prod.update_layout(
        height=520,
        margin=dict(t=60, r=20, l=140, b=40),
        xaxis=dict(title='Ventas ($)', showgrid=False),
        xaxis2=dict(
            title='% acumulado',
            overlaying='x',
            side='top',
            range=[0, max(20, productos_ordenados['pct_acumulado_ventas'].max() + 2)],
            ticksuffix='%'
        ),
        yaxis=dict(title='Producto', showgrid=False),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hovermode='y unified',
        title="Top 10 productos y su aporte acumulado"
    )
    st.plotly_chart(fig_pareto_prod, use_container_width=True)

    tabla_prod = top_prod_80[['descripcion', 'categoria', 'ventas', 'pct_acumulado_ventas', 'margen']].copy()
    tabla_prod['ventas'] = tabla_prod['ventas'].apply(lambda x: formatear_moneda_argentina(x, 0))
    tabla_prod['margen'] = tabla_prod['margen'].apply(lambda x: formatear_moneda_argentina(x, 0))
    tabla_prod['pct_acumulado_ventas'] = tabla_prod['pct_acumulado_ventas'].round(1).astype(str) + '%'
    tabla_prod.columns = ['Producto', 'Categoría', 'Ventas', '% acumulado', 'Margen']

    st.dataframe(tabla_prod, use_container_width=True, hide_index=True)

    cobertura = float(top_prod_80['pct_acumulado_ventas'].max())
    categoria_dominante = top_prod_80['categoria'].value_counts().idxmax()

    st.markdown(f"""
    <div style='background: #ede7f6; border-left: 6px solid #5e35b1; padding: 20px; margin: 20px 0; border-radius: 10px;'>
        <h4 style='color: #4527a0; margin: 0;'>🎯 Insight: Productos clave</h4>
        <p style='margin: 10px 0 0 0;'>
            Los <b>{len(top_prod_80)} productos</b> concentran el <b>{cobertura:.1f}%</b> de las ventas acumuladas. 
            <b>{categoria_dominante}</b> reúne la mayor cantidad de ítems en este grupo, por lo que las
            campañas de abastecimiento, señalética en góndola y programas de fidelización deberían priorizarlos.
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
    q1 = rentabilidad['rentabilidad_pct'].quantile(0.25)
    mediana = rentabilidad['rentabilidad_pct'].quantile(0.5)
    q3 = rentabilidad['rentabilidad_pct'].quantile(0.75)
    min_pct = float(rentabilidad['rentabilidad_pct'].min()) if not rentabilidad.empty else 0.0
    max_pct = float(rentabilidad['rentabilidad_pct'].max()) if not rentabilidad.empty else 0.0

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
    if not rentabilidad.empty:
        quartile_ranges = [
            ("Q1", min_pct, q1, "#e8f5e9"),
            ("Q2", q1, mediana, "#fff8e1"),
            ("Q3", mediana, q3, "#e3f2fd"),
            ("Q4", q3, max_pct, "#fce4ec"),
        ]
        epsilon = max(1e-6, (max_pct - min_pct) * 0.001)
        for label, start, end, color in quartile_ranges:
            if end - start < epsilon:
                continue
            fig_hist.add_vrect(
                x0=float(start),
                x1=float(end),
                fillcolor=color,
                opacity=0.18,
                layer='below',
                line_width=0
            )
            midpoint = float(start + (end - start) / 2)
            fig_hist.add_annotation(
                x=midpoint,
                y=1.02,
                xref='x',
                yref='paper',
                text=label,
                showarrow=False,
                font=dict(color='#424242', size=12)
            )
        for boundary, color in [
            (float(q1), '#ffb300'),
            (float(mediana), '#fb8c00'),
            (float(q3), '#1976d2')
        ]:
            if np.isnan(boundary):
                continue
            fig_hist.add_vline(
                x=boundary,
                line_width=1.5,
                line_dash='dash',
                line_color=color,
                opacity=0.85
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
            <b>Compra Grande (Ticket >$30K):</b> Upselling de productos premium en caja y beneficios exclusivos.<br>
            <b>Compra Mediana ($15K-$30K):</b> Promociones umbral que incentiven sumar un ítem adicional.<br>
            <b>Compra Chica ($5K-$15K):</b> Combos de reposición y segunda unidad con descuento.<br>
            <b>Conveniencia (<$5K):</b> Productos impulso en cajas y exhibiciones tácticas.<br><br>
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

    kpi_pago = data.get('kpi_pago')
    if kpi_pago is None or kpi_pago.empty:
        st.info("No hay datos de medios de pago disponibles.")
    else:
        pago_raw = kpi_pago.copy()

        def normalizar_medio(valor: str) -> str:
            texto = str(valor).strip()
            texto = unicodedata.normalize('NFKD', texto)
            texto = ''.join(ch for ch in texto if not unicodedata.combining(ch))
            return texto.upper()

        pago_raw['medio_clave'] = pago_raw['tipo_medio_pago'].apply(normalizar_medio)
        medio_map = {
            'EFECTIVO': 'Efectivo',
            'SIN_DATO': 'Efectivo',
            'TARJETA DE CREDITO': 'Tarjeta de crédito',
            'TARJETA DE DEBITO': 'Tarjeta de débito',
            'BILLETERA VIRTUAL': 'Billetera virtual',
            'BILLETERA VITUAL': 'Billetera virtual',
        }
        pago_raw['medio_normalizado'] = pago_raw['medio_clave'].map(medio_map)
        pago_raw.loc[pago_raw['medio_normalizado'].isna(), 'medio_normalizado'] = pago_raw['tipo_medio_pago'].str.title()

        pago_summary = (
            pago_raw.groupby('medio_normalizado', as_index=False)
            .agg(
                tickets=('tickets', 'sum'),
                ventas=('ventas', 'sum'),
                margen=('margen', 'sum')
            )
        )
        pago_summary['participacion'] = (pago_summary['ventas'] / pago_summary['ventas'].sum() * 100).round(1)
        pago_summary['ticket_promedio'] = pago_summary['ventas'] / pago_summary['tickets']

        fig_pie = px.pie(
            pago_summary,
            values='ventas',
            names='medio_normalizado',
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

        col1, col2, col3 = st.columns(3)

        def obtener_participacion(nombre: str) -> float:
            fila = pago_summary[pago_summary['medio_normalizado'] == nombre]
            return float(fila['participacion'].iloc[0]) if not fila.empty else 0.0

        efectivo_pct = obtener_participacion('Efectivo')
        credito_pct = obtener_participacion('Tarjeta de crédito')
        billetera_pct = obtener_participacion('Billetera virtual')

        with col1:
            st.metric("% Efectivo", f"{formatear_numero_argentino(efectivo_pct, 1)}%")
        with col2:
            st.metric("% Tarjeta de crédito", f"{formatear_numero_argentino(credito_pct, 1)}%")
        with col3:
            st.metric("% Billetera virtual", f"{formatear_numero_argentino(billetera_pct, 1)}%")

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

    estrategias_html = estrategias_html.replace(
        "(Q1=20%, Q3=35%)",
        f"(Q1={q1:.1f}%, Q3={q3:.1f}%)"
    )

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
# TAB 7: INFORME EJECUTIVO
# =============================================================================
with tabs[6]:
    st.markdown("## Y Informe Ejecutivo")

    alcance = data['alcance'].iloc[0]
    kpis_resumen = data['kpis_base'].iloc[0]

    min_fecha = pd.to_datetime(alcance['min_fecha']).strftime('%d/%m/%Y')
    max_fecha = pd.to_datetime(alcance['max_fecha']).strftime('%d/%m/%Y')
    total_tickets = formatear_numero_argentino(int(alcance['n_tickets']))
    total_items = formatear_numero_argentino(int(alcance['n_registros']))
    ventas_totales = formatear_moneda_argentina(alcance['ventas_total'], 0)
    margen_total = formatear_moneda_argentina(alcance['margen_total'], 0)
    ticket_promedio = formatear_moneda_argentina(kpis_resumen['ticket_promedio'], 0)
    items_promedio = round(float(kpis_resumen['items_promedio_ticket']), 1)
    rentabilidad_global_pct = round(float(kpis_resumen['rentabilidad_global']) * 100, 1)
    margen_ticket = formatear_moneda_argentina(kpis_resumen['rentabilidad_promedio_ticket'], 0)

    top_categorias = data['kpi_categoria'].head(3)
    categorias_texto = ", ".join(
        f"{str(row['categoria']).title()} ({round(row['pct_ventas'], 1)}% de las ventas)"
        for _, row in top_categorias.iterrows()
    )

    pago_mix = (
        data['kpi_pago']
        .groupby('tipo_medio_pago', as_index=False)['ventas']
        .sum()
        .sort_values('ventas', ascending=False)
    )
    total_pagos = pago_mix['ventas'].sum()
    pago_map = {
        'TARJETA DE CR�DITO': 'tarjetas de credito',
        'TARJETA DE CREDITO': 'tarjetas de credito',
        'TARJETA DE D�BITO': 'tarjetas de debito',
        'TARJETA DE DEBITO': 'tarjetas de debito',
        'BILLETERA VITUAL': 'billeteras virtuales',
        'BILLETERA VIRTUAL': 'billeteras virtuales',
        'SIN_DATO': 'pagos en efectivo',
        'EFECTIVO': 'pagos en efectivo',
    }
    principales_medios = []
    for _, fila in pago_mix.head(3).iterrows():
        clave = str(fila['tipo_medio_pago']).strip().upper()
        descripcion = pago_map.get(clave, clave.title())
        participacion = round(fila['ventas'] / total_pagos * 100, 1)
        principales_medios.append(f"{descripcion} ({participacion}% del monto)")
    medios_texto = ", ".join(principales_medios)

    kpi_dia = data['kpi_dia'].copy()
    dia_map = {
        'Monday': 'los lunes',
        'Tuesday': 'los martes',
        'Wednesday': 'los miercoles',
        'Thursday': 'los jueves',
        'Friday': 'los viernes',
        'Saturday': 'los sabados',
        'Sunday': 'los domingos',
    }
    dia_pico = kpi_dia.loc[kpi_dia['ventas'].idxmax()]
    dia_pico_nombre = dia_map.get(str(dia_pico['dia_semana']), str(dia_pico['dia_semana']).lower())
    ventas_dia_pico = formatear_moneda_argentina(dia_pico['ventas'], 0)

    informe_html = f"""
    <div style='background: #fff8e1; border-left: 6px solid #f9a825; padding: 26px; border-radius: 12px; margin-bottom: 20px;'>
        <h3 style='margin: 0 0 14px 0; color: #bf360c;'>Trabajo realizado y aprendizajes internos</h3>
        <p style='margin: 0 0 12px 0;'>
            La historia de este dashboard arranca con una operacion concreta: normalizamos la base de tickets, armamos indicadores accionables
            y los conectamos con la hoja de ruta de rentabilidad. Tres oleadas de trabajo, documentadas en <i>Estrategias_Analitica.md</i>, dejaron huella.
        </p>
        <ul style='margin: 0; padding-left: 22px; line-height: 1.5;'>
            <li><b>Ola 1 - Higiene y consistencia:</b> depuramos {total_tickets} comprobantes entre {min_fecha} y {max_fecha}, garantizando ticket unico por comprobante y completando campos como items_ticket y margen_ticket.</li>
            <li><b>Ola 2 - Analitica descriptiva:</b> transformamos la materia prima en lecturas accionables: ticket promedio de {ticket_promedio}, {items_promedio} items por compra y margen acumulado de {margen_total} que marcan el punto de partida.</li>
            <li><b>Ola 3 - Historias y estrategias:</b> cruzamos los hallazgos con benchmarks para construir narrativas claras (clientes cargan la alacena los {dia_pico_nombre}, los medios de pago dominantes son {medios_texto}) que sostienen decisiones comerciales.</li>
        </ul>
    </div>
    <div style='background: #f1f8e9; border-left: 6px solid #7cb342; padding: 26px; border-radius: 12px; margin-bottom: 20px;'>
        <h3 style='margin: 0 0 14px 0; color: #33691e;'>Lo que aprendimos mirando a la competencia</h3>
        <p style='margin: 0 0 12px 0;'>
            El repaso de jugadores mendocinos deja claro que nadie se queda quieto. Las referencias del informe analitico muestran tres jugadas que hoy marcan el paso.
        </p>
        <ul style='margin: 0; padding-left: 22px; line-height: 1.5;'>
            <li><b>Carrefour Express:</b> expandio el formato de cercania tras adquirir 16 tiendas locales, privilegiando surtido curado y compras rapidas con promo bancaria semanal.</li>
            <li><b>Vea Express:</b> replica la logica de proximidad con 3000 referencias de alta rotacion y fuerte activacion de codigo QR/bases barriales para fidelizar a pie de tienda.</li>
            <li><b>Atomo:</b> apalanca precios bajos todos los dias y remodelaciones de layout; una sucursal escalo del puesto 90 al 8 solo por rediseniar salon y sumar categorias ancla.</li>
        </ul>
        <p style='margin: 14px 0 0 0;'>
            Tres lecturas clave: foco en surtidos rentables, promociones financiadas y experiencia en tienda como anzuelo diario.
        </p>
    </div>
    <div style='background: #e3f2fd; border-left: 6px solid #1976d2; padding: 26px; border-radius: 12px;'>
        <h3 style='margin: 0 0 14px 0; color: #0d47a1;'>Como aterrizamos esas jugadas con los datos de NINO</h3>
        <p style='margin: 0 0 12px 0;'>
            Con el termometro propio en mano podemos adaptar lo que funciona afuera. Cada insight del dataset activa una palanca concreta.
        </p>
        <ul style='margin: 0; padding-left: 22px; line-height: 1.5;'>
            <li><b>Plan de finde largo:</b> los {dia_pico_nombre} concentran el gasto (ventas de {ventas_dia_pico}); ideal para combos financiados que copien la cadencia Carrefour pero con surtido local.</li>
            <li><b>Curar el mix core:</b> las categorias lideres ({categorias_texto}) son nuestra version del surtido express; hay que defender margen subiendo segunda marca y cross merchandising a la manera de Atomo.</li>
            <li><b>Fidelizar bolsillo digital:</b> {medios_texto} confirman que el cliente ya usa medios bancarizados; se puede replicar la bateria de promociones ancla de Vea con acuerdos puntuales segun medio de pago.</li>
            <li><b>Pizarra de seguimiento:</b> la rentabilidad global del {rentabilidad_global_pct}% y el margen de {margen_ticket} por ticket nos dan umbrales; cualquier estrategia nueva debe sostener o ampliar esos numeros.</li>
        </ul>
        <p style='margin: 14px 0 0 0;'>
            Asi, el insight deja de ser un PDF y se convierte en agenda semanal: decidir, ejecutar y medir contra los mismos indicadores que hoy relatamos.
        </p>
    </div>
    """

    st.markdown(informe_html, unsafe_allow_html=True)

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

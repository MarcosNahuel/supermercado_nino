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
import json
import locale
import plotly.io as pio
from sklearn.linear_model import LinearRegression

# Configuración global de Plotly para mejor rendimiento
pio.templates.default = "plotly_white"
plotly_config = {
    'displayModeBar': False,  # Ocultar barra de herramientas
    'staticPlot': False,
    'responsive': True,
    'displaylogo': False,
    'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d']
}

# Función helper para renderizar gráficos optimizados
def render_plotly(fig, height=None):
    """Renderiza un gráfico de Plotly con configuración optimizada"""
    if height:
        fig.update_layout(height=height)
    st.plotly_chart(fig, use_container_width=True, config=plotly_config)

# Configurar pandas para mejor rendimiento
pd.options.mode.chained_assignment = None  # Desactivar warnings de copia
pd.options.display.max_rows = 100  # Limitar filas mostradas

# Configurar locale a español
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES')
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'Spanish_Spain.1252')
        except:
            pass  # Si no se puede configurar, continuamos sin locale

st.set_page_config(
    page_title="NINO - Dashboard Analítico",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado moderno con mejores prácticas
st.markdown("""
<style>
    /* ===== VARIABLES CSS (Design Tokens) ===== */
    :root {
        --primary-gradient: linear-gradient(135deg, #1a237e 0%, #283593 100%);
        --success-gradient: linear-gradient(135deg, #2e7d32 0%, #388e3c 100%);
        --info-gradient: linear-gradient(135deg, #1976d2 0%, #2196f3 100%);
        --warning-gradient: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);

        --shadow-sm: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.08);
        --shadow-md: 0 4px 6px rgba(0,0,0,0.1), 0 2px 4px rgba(0,0,0,0.06);
        --shadow-lg: 0 10px 30px rgba(26, 35, 126, 0.15);
        --shadow-xl: 0 20px 50px rgba(26, 35, 126, 0.25);

        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 20px;

        --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
        --transition-base: 300ms cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* ===== MEJORAS GLOBALES ===== */
    html, body, [data-testid="stAppViewContainer"] {
        overflow: auto !important;
        scroll-behavior: smooth;
        font-feature-settings: 'liga' 1, 'calt' 1; /* Ligaduras tipográficas */
    }

    /* ===== OPTIMIZACIÓN DE PERFORMANCE ===== */
    * {
        animation-duration: 0.15s !important;
        transition-duration: var(--transition-fast) !important;
    }

    /* Optimizar gráficos con GPU acceleration */
    .js-plotly-plot,
    [data-testid="stPlotlyChart"] {
        will-change: transform;
        transform: translateZ(0);
        backface-visibility: hidden;
    }

    /* ===== TABS MODERNOS ===== */
    [data-baseweb="tab-list"] {
        gap: 8px;
        background: linear-gradient(to bottom, #f8f9fa, #ffffff);
        padding: 12px 16px;
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-sm);
    }

    [data-baseweb="tab"] {
        border-radius: var(--radius-sm) !important;
        font-weight: 500 !important;
        padding: 10px 20px !important;
        transition: all var(--transition-base) !important;
        border: 1px solid transparent !important;
    }

    [data-baseweb="tab"]:hover {
        background: rgba(26, 35, 126, 0.05) !important;
        transform: translateY(-1px);
    }

    [data-baseweb="tab"][aria-selected="true"] {
        background: var(--primary-gradient) !important;
        color: white !important;
        box-shadow: var(--shadow-md);
        border: none !important;
    }

    [data-baseweb="tab-panel"] {
        overflow: visible !important;
        padding-top: 24px;
        animation: fadeIn 0.3s ease-in;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* ===== MÉTRICAS (st.metric) MEJORADAS ===== */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 20px;
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-md);
        border: 1px solid rgba(0,0,0,0.05);
        transition: all var(--transition-base);
    }

    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        color: #64748b !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* ===== BOTONES MEJORADOS ===== */
    .stButton > button {
        border-radius: var(--radius-sm);
        font-weight: 600;
        padding: 0.5rem 1.5rem;
        transition: all var(--transition-base);
        box-shadow: var(--shadow-sm);
        border: 1px solid rgba(26, 35, 126, 0.1);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
        border-color: rgba(26, 35, 126, 0.3);
    }

    /* ===== DATAFRAMES ESTILIZADOS ===== */
    [data-testid="stDataFrame"] {
        border-radius: var(--radius-md);
        overflow: hidden;
        box-shadow: var(--shadow-md);
        border: 1px solid rgba(0,0,0,0.05);
    }

    /* ===== EXPANDABLES MEJORADOS ===== */
    [data-testid="stExpander"] {
        border-radius: var(--radius-md);
        border: 1px solid rgba(0,0,0,0.08);
        box-shadow: var(--shadow-sm);
        transition: all var(--transition-base);
    }

    [data-testid="stExpander"]:hover {
        box-shadow: var(--shadow-md);
    }

    /* ===== INPUTS Y CONTROLES ===== */
    .stRadio > div {
        gap: 12px;
    }

    .stRadio > div > label {
        background: #f8f9fa;
        padding: 8px 16px;
        border-radius: var(--radius-sm);
        transition: all var(--transition-base);
        border: 2px solid transparent;
        font-weight: 500;
    }

    .stRadio > div > label:hover {
        background: #e3f2fd;
        transform: translateY(-1px);
    }

    .stRadio > div > label[data-checked="true"] {
        background: var(--primary-gradient);
        color: white !important;
        box-shadow: var(--shadow-sm);
    }

    /* ===== MARKDOWN HEADINGS MEJORADOS ===== */
    h1, h2, h3, h4, h5, h6 {
        letter-spacing: -0.02em;
        font-weight: 700;
    }

    h2 {
        border-bottom: 3px solid;
        border-image: var(--primary-gradient) 1;
        padding-bottom: 12px;
        margin-bottom: 24px;
    }

    /* ===== TOOLTIPS Y HELPS ===== */
    [data-testid="stTooltipHoverTarget"] {
        transition: transform var(--transition-fast);
    }

    [data-testid="stTooltipHoverTarget"]:hover {
        transform: scale(1.1);
    }

    /* ===== INFO/WARNING/SUCCESS BOXES ===== */
    [data-testid="stAlert"] {
        border-radius: var(--radius-md);
        border-left-width: 4px;
        box-shadow: var(--shadow-sm);
    }

    /* ===== SCROLLBAR PERSONALIZADO ===== */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #1a237e, #283593);
        border-radius: 10px;
        transition: background var(--transition-base);
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #0d47a1, #1565c0);
    }

    /* ===== ANIMACIONES SUAVES ===== */
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* ===== RESPONSIVE ADJUSTMENTS ===== */
    @media (max-width: 768px) {
        [data-testid="stMetricValue"] {
            font-size: 1.5rem !important;
        }

        [data-baseweb="tab"] {
            padding: 8px 12px !important;
            font-size: 0.875rem !important;
        }
    }

    /* ===== LOADING INDICATOR MEJORADO ===== */
    [data-testid="stSpinner"] > div {
        border-color: rgba(26, 35, 126, 0.1);
        border-top-color: #1a237e;
    }
</style>
""", unsafe_allow_html=True)

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

def traducir_mes_espanol(fecha_str):
    """Traduce los nombres de meses y días del inglés al español"""
    meses_en = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    meses_es = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

    meses_completos_en = ['January', 'February', 'March', 'April', 'May', 'June',
                          'July', 'August', 'September', 'October', 'November', 'December']
    meses_completos_es = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                          'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

    resultado = fecha_str
    # Traducir meses abreviados
    for en, es in zip(meses_en, meses_es):
        resultado = resultado.replace(en, es)

    # Traducir meses completos
    for en, es in zip(meses_completos_en, meses_completos_es):
        resultado = resultado.replace(en, es)

    return resultado

def configurar_grafico_rendimiento(fig):
    """Configura un gráfico Plotly para mejor rendimiento"""
    fig.update_layout(
        # Deshabilitar animaciones para mejor rendimiento
        transition_duration=0,
        # Optimizar renderizado - mantener estado durante scroll
        uirevision='constant',
        # Optimizar para scroll - deshabilitar zoom/pan por defecto
        dragmode=False
    )
    return fig

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
PROCESSED_DIR = Path("data/processed")
PREDICTIVE_DIR = Path("data/predictivos")

def normalizar_categorias(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza los nombres de las categorías en un DataFrame.
    - Guarda la categoría original en 'categoria_original'
    - Reemplaza 'categoria' con la versión normalizada
    """
    if 'categoria' not in df.columns:
        return df

    df = df.copy()
    # Guardar categoría original
    df['categoria_original'] = df['categoria'].astype(str)

    # Normalizar categorías
    df['categoria'] = df['categoria'].astype(str).str.upper().str.strip()

    # Mapeo de normalizaciones
    categoria_map = {
        'CARNICERIA AL 10,5 %': 'CARNICERIA',
        'CARNICERIA AL 10.5 %': 'CARNICERIA',
        'CARNICERIA AL 10,5%': 'CARNICERIA',
        'CARNICERIA AL 10.5%': 'CARNICERIA',
        'CARNES': 'CARNICERIA'
    }

    df['categoria'] = df['categoria'].replace(categoria_map)

    return df

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
                print(f"[OK] Loaded {filename}")
            except Exception as e:
                print(f"[ERROR] Error loading {filename}: {e}")
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
                print(f"[OK] Loaded CSV with {len(horario_df)} rows")

                # Verificar columnas requeridas
                required_columns = ['Fecha', 'Hora', 'Comprobante']
                missing_columns = [col for col in required_columns if col not in horario_df.columns]
                if missing_columns:
                    print(f"[ERROR] Missing columns in CSV: {missing_columns}")
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
                        print("[ERROR] No valid dates found in CSV")
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
                        print(f"[OK] Processed horario data: {horario_semana.shape}")

            except Exception as e:
                print(f"[ERROR] Error processing horario CSV: {e}")
                data['horario_semana'] = pd.DataFrame()
                data['horario_semana_matrix'] = pd.DataFrame()
        else:
            print("[ERROR] Horario CSV file not found")
            data['horario_semana'] = pd.DataFrame()
            data['horario_semana_matrix'] = pd.DataFrame()

    except Exception as e:
        st.error(f"Error general cargando datos: {e}")
        print(f"[ERROR] General error: {e}")
        return None

    # Normalizar categorías en todos los datasets que las tengan
    datasets_con_categorias = ['kpi_categoria', 'pareto_cat', 'pareto_prod', 'clusters_depto']
    for key in datasets_con_categorias:
        if key in data and not data[key].empty:
            data[key] = normalizar_categorias(data[key])
            print(f"[OK] Normalized categories in {key}")

    return data


@st.cache_data
def load_processed_data():
    processed = {}

    def _load(directory: Path, filename: str) -> pd.DataFrame:
        path = directory / filename
        if path.exists():
            try:
                return pd.read_parquet(path)
            except Exception as exc:
                print(f"⚠- Error loading {path}: {exc}")
        else:
            print(f"⚠- Missing expected file: {path}")
        return pd.DataFrame()

    processed["kpi_dia_modular"] = _load(PROCESSED_DIR, "kpi_dia.parquet")
    processed["kpi_tipo_dia_modular"] = _load(PROCESSED_DIR, "kpi_tipo_dia.parquet")
    processed["kpi_categoria_modular"] = _load(PROCESSED_DIR, "kpi_categoria.parquet")
    processed["kpi_medio_pago_modular"] = _load(PROCESSED_DIR, "kpi_medio_pago.parquet")
    processed["tickets_modular"] = _load(PROCESSED_DIR, "tickets.parquet")
    processed["ventas_semanales_categoria"] = _load(
        PROCESSED_DIR, "ventas_semanales_categoria.parquet"
    )
    processed["forecast_semana"] = _load(
        PREDICTIVE_DIR, "prediccion_ventas_semanal.parquet"
    )
    processed["forecast_modelos"] = _load(
        PREDICTIVE_DIR, "prediccion_ventas_semanal_modelos.parquet"
    )

    # Normalizar categorías en datasets procesados
    datasets_con_categorias = ['kpi_categoria_modular', 'ventas_semanales_categoria']
    for key in datasets_con_categorias:
        if key in processed and not processed[key].empty:
            processed[key] = normalizar_categorias(processed[key])
            print(f"[OK] Normalized categories in {key}")

    return processed

data = load_all_data()
processed_data = load_processed_data()
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
    st.metric("Codigos de producto unicos", formatear_numero_argentino(alcance['n_skus_unicos']))
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
    "💰 Márgenes - Costos",
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

            # Calcular margen % promedio por mes desde rentabilidad_ticket
            if 'rentabilidad_ticket' in data and data['rentabilidad_ticket'] is not None:
                detalle_rent = data['rentabilidad_ticket'].copy()
                detalle_rent['fecha'] = pd.to_datetime(detalle_rent['fecha'])
                detalle_rent['periodo'] = detalle_rent['fecha'].dt.to_period('M')

                # Calcular margen % correctamente: suma(margen) / suma(ventas) * 100
                margen_mensual = detalle_rent.groupby('periodo').agg({
                    'margen_ticket': 'sum',
                    'monto_total_ticket': 'sum'
                }).reset_index()
                margen_mensual['periodo'] = margen_mensual['periodo'].astype(str)
                margen_mensual['margen_pct'] = (margen_mensual['margen_ticket'] / margen_mensual['monto_total_ticket']) * 100

                # Merge con kpi_periodo_plot
                kpi_periodo_plot = kpi_periodo_plot.merge(
                    margen_mensual[['periodo', 'margen_pct']],
                    left_on=kpi_periodo_plot['periodo_dt'].dt.to_period('M').astype(str),
                    right_on='periodo',
                    how='left'
                )
        else:
            kpi_periodo_plot = pd.DataFrame(columns=['periodo_label', 'tickets', 'margen_pct'])

        # -------------------------
        # Semanal (tickets por semana)
        # -------------------------
        kpi_semana = data.get('kpi_semana')
        if kpi_semana is not None and not kpi_semana.empty:
            try:
                # Verificar si existe la columna semana_iso
                if 'semana_iso' not in kpi_semana.columns:
                    print("[ERROR] semana_iso column missing from kpi_semana")
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
                print(f"[ERROR] Error processing kpi_semana: {e}")
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
                    print("[ERROR] dia_semana column missing from kpi_dia")
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
                print(f"[ERROR] Error processing kpi_dia: {e}")
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
        detalle_tickets['quincena_inicio'] = (
            detalle_tickets['quincena_order'] +
            pd.to_timedelta(np.where(detalle_tickets['quincena_idx'] == 1, 0, 15), unit='D')
        )

        tickets_quincena = (
            detalle_tickets.groupby(['quincena_order', 'quincena_idx', 'quincena_label', 'quincena_inicio'], as_index=False)
            .agg(tickets=('ticket_id', 'nunique'))
            .sort_values(['quincena_order', 'quincena_idx'])
        )

        def construir_figura_tendencia(df, x_col, y_col, titulo, unidad_texto):
            df = df.dropna(subset=[x_col, y_col])
            if df.empty:
                return None, None

            df = df.sort_values(x_col)
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=df[x_col],
                    y=df[y_col],
                    mode='lines+markers',
                    name='Tickets',
                    line=dict(color='#1a237e', width=3),
                    marker=dict(size=8, color='#3949ab')
                )
            )

            # Agregar línea de promedio
            promedio = df[y_col].mean()
            fig.add_trace(
                go.Scatter(
                    x=df[x_col],
                    y=[promedio] * len(df),
                    mode='lines',
                    name='Promedio',
                    line=dict(color='#9c27b0', width=2, dash='dot')
                )
            )

            pendiente = None
            if len(df) >= 2:
                x_numeric = np.arange(len(df))
                y_values = df[y_col].to_numpy(dtype=float)
                pendiente, intercepto = np.polyfit(x_numeric, y_values, 1)
                tendencia = intercepto + pendiente * x_numeric
                fig.add_trace(
                    go.Scatter(
                        x=df[x_col],
                        y=tendencia,
                        mode='lines',
                        name='Tendencia',
                        line=dict(color='#ff7043', width=2, dash='dash')
                    )
                )

                pendiente_redondeada = round(float(pendiente), 1)
                signo = '+' if pendiente_redondeada >= 0 else '-'
                pendiente_texto = formatear_numero_argentino(abs(pendiente_redondeada), 1)
                fig.add_annotation(
                    x=df[x_col].iloc[-1],
                    y=tendencia[-1],
                    text=f"Pendiente: {signo}{pendiente_texto} tickets/{unidad_texto}",
                    showarrow=True,
                    arrowhead=2,
                    ax=0,
                    ay=-40,
                    bgcolor='rgba(255,255,255,0.85)'
                )
            fig.update_layout(
                title=titulo,
                height=420,
                margin=dict(t=70, r=20, l=60, b=40),
                xaxis_title=None,
                yaxis_title='Tickets',
                hovermode='x unified'
            )
            # Aplicar optimizaciones de rendimiento
            fig = configurar_grafico_rendimiento(fig)
            return fig, pendiente

        st.markdown('### Evolucion de tickets emitidos')
        vista_temporal = st.radio(
            'Selecciona la granularidad',
            options=('Mensual', 'Quincenal', 'Semanal'),
            horizontal=True
        )

        fig_temporal = None
        pendiente_temporal = None

        if vista_temporal == 'Mensual':
            if not kpi_periodo_plot.empty:
                df_mensual = kpi_periodo_plot[['periodo_dt', 'tickets']].rename(columns={'periodo_dt': 'periodo'})

                # Usar el mismo formato que semanal/quincenal con promedio y tendencia
                fig_temporal, pendiente_temporal = construir_figura_tendencia(
                    df_mensual,
                    'periodo',
                    'tickets',
                    'Mensual - Tickets emitidos',
                    'tickets'
                )

            else:
                st.info('No hay datos suficientes para el analisis mensual.')
        elif vista_temporal == 'Semanal':
            if not kpi_semana_plot.empty:
                df_semanal = kpi_semana_plot[['semana_inicio', 'tickets']].rename(columns={'semana_inicio': 'periodo'})
                fig_temporal, pendiente_temporal = construir_figura_tendencia(
                    df_semanal,
                    'periodo',
                    'tickets',
                    'Semanal - Tickets emitidos',
                    'semana'
                )
                if fig_temporal is not None:
                    # Generar etiquetas en español para semanas
                    fechas = df_semanal['periodo']
                    etiquetas_es = [traducir_mes_espanol(f.strftime('%d-%b')) for f in fechas]
                    fig_temporal.update_xaxes(
                        type='category',
                        ticktext=etiquetas_es,
                        tickvals=fechas
                    )
            else:
                st.info('No hay datos suficientes para el analisis semanal.')
        else:  # Quincenal
            if not tickets_quincena.empty:
                df_quincenal = tickets_quincena[['quincena_inicio', 'tickets']].rename(columns={'quincena_inicio': 'periodo'})
                fig_temporal, pendiente_temporal = construir_figura_tendencia(
                    df_quincenal,
                    'periodo',
                    'tickets',
                    'Quincenal - Tickets emitidos',
                    'quincena'
                )
                if fig_temporal is not None:
                    # Generar etiquetas en español para quincenas
                    fechas = df_quincenal['periodo']
                    etiquetas_es = [traducir_mes_espanol(f.strftime('%d-%b')) for f in fechas]
                    fig_temporal.update_xaxes(
                        type='category',
                        ticktext=etiquetas_es,
                        tickvals=fechas
                    )
            else:
                st.info('No hay datos suficientes para el analisis quincenal.')

        if fig_temporal is not None:
            render_plotly(fig_temporal)
            if pendiente_temporal is not None:
                pendiente_redondeada = round(float(pendiente_temporal), 1)
                signo = '+' if pendiente_redondeada >= 0 else '-'
                pendiente_texto = formatear_numero_argentino(abs(pendiente_redondeada), 1)
                unidad_ref = {'Mensual': 'mes', 'Semanal': 'semana', 'Quincenal': 'quincena'}[vista_temporal]
                st.caption(f'Pendiente (slope): {signo}{pendiente_texto} tickets por {unidad_ref}.')

                # Insight menos técnico
                if pendiente_redondeada < 0:
                    st.info(f"📉 **Tendencia a la baja:** En promedio, se emiten {formatear_numero_argentino(abs(pendiente_redondeada), 1)} tickets menos cada {unidad_ref}. Esto indica una reducción en la frecuencia de compras.")
                elif pendiente_redondeada > 0:
                    st.success(f"📈 **Tendencia al alza:** En promedio, se emiten {formatear_numero_argentino(abs(pendiente_redondeada), 1)} tickets más cada {unidad_ref}. Esto refleja un aumento en la frecuencia de compras.")
                else:
                    st.info(f"➡️ **Tendencia estable:** El número de tickets se mantiene relativamente constante en el período analizado.")

        st.markdown('### UPT (unidades por ticket)')

        # Selector de granularidad para UPT
        st.markdown('Selecciona la granularidad')
        vista_upt = st.radio(
            '',
            ['Mensual', 'Quincenal', 'Semanal'],
            horizontal=True,
            index=2,  # Por defecto Semanal
            key='vista_upt',
            label_visibility='collapsed'
        )

        # Calcular UPT según granularidad
        df_upt = None
        periodo_col = None
        titulo_upt = None

        if vista_upt == 'Mensual':
            detalle_tickets['mes_upt'] = detalle_tickets['fecha'].dt.to_period('M').dt.to_timestamp()
            df_upt = (
                detalle_tickets.groupby('mes_upt', as_index=False)
                .agg(
                    tickets=('ticket_id', 'nunique'),
                    unidades=('items_ticket', 'sum')
                )
                .sort_values('mes_upt')
            )
            periodo_col = 'mes_upt'
            titulo_upt = 'Mensual - UPT'
        elif vista_upt == 'Quincenal':
            detalle_tickets['quincena_upt'] = detalle_tickets['fecha'].apply(
                lambda x: pd.Timestamp(year=x.year, month=x.month, day=1 if x.day <= 15 else 15)
            )
            df_upt = (
                detalle_tickets.groupby('quincena_upt', as_index=False)
                .agg(
                    tickets=('ticket_id', 'nunique'),
                    unidades=('items_ticket', 'sum')
                )
                .sort_values('quincena_upt')
            )
            periodo_col = 'quincena_upt'
            titulo_upt = 'Quincenal - UPT'
        else:  # Semanal
            detalle_tickets['semana_inicio_upt'] = detalle_tickets['fecha'] - pd.to_timedelta(
                detalle_tickets['fecha'].dt.weekday, unit='D'
            )
            df_upt = (
                detalle_tickets.groupby('semana_inicio_upt', as_index=False)
                .agg(
                    tickets=('ticket_id', 'nunique'),
                    unidades=('items_ticket', 'sum')
                )
                .sort_values('semana_inicio_upt')
            )
            periodo_col = 'semana_inicio_upt'
            titulo_upt = 'Semanal - UPT'

        if df_upt is not None and not df_upt.empty:
            df_upt['upt'] = np.where(
                df_upt['tickets'] > 0,
                df_upt['unidades'] / df_upt['tickets'],
                np.nan
            )

            if df_upt['upt'].notna().any():
                fig_upt = go.Figure()

                # Línea principal de UPT
                fig_upt.add_trace(
                    go.Scatter(
                        x=df_upt[periodo_col],
                        y=df_upt['upt'],
                        mode='lines+markers',
                        name='UPT',
                        line=dict(color='#00897b', width=3),
                        marker=dict(size=7, color='#26a69a')
                    )
                )

                # Calcular y agregar línea de tendencia
                df_upt_valido = df_upt[df_upt['upt'].notna()].copy()
                if len(df_upt_valido) >= 2:
                    df_upt_valido['periodo_num'] = range(len(df_upt_valido))
                    z = np.polyfit(df_upt_valido['periodo_num'], df_upt_valido['upt'], 1)
                    p = np.poly1d(z)
                    df_upt_valido['tendencia'] = p(df_upt_valido['periodo_num'])
                    pendiente_upt = z[0]

                    fig_upt.add_trace(
                        go.Scatter(
                            x=df_upt_valido[periodo_col],
                            y=df_upt_valido['tendencia'],
                            mode='lines',
                            name='Tendencia',
                            line=dict(color='#ff7043', width=2, dash='dash')
                        )
                    )
                else:
                    pendiente_upt = None

                # Agregar línea de promedio
                upt_promedio = df_upt['upt'].dropna().mean()
                fig_upt.add_trace(
                    go.Scatter(
                        x=df_upt[periodo_col],
                        y=[upt_promedio] * len(df_upt),
                        mode='lines',
                        name='Promedio',
                        line=dict(color='#9c27b0', width=2, dash='dot')
                    )
                )

                fig_upt.update_layout(
                    title=f'<b><b>{titulo_upt}</b></b>',
                    height=360,
                    margin=dict(t=60, r=20, l=60, b=40),
                    yaxis_title='Unidades por ticket',
                    hovermode='x unified'
                )

                # Generar etiquetas en español para UPT
                fechas_upt = df_upt[periodo_col]
                if vista_upt == 'Mensual':
                    etiquetas_upt_es = [traducir_mes_espanol(f.strftime('%b %Y')) for f in fechas_upt]
                else:
                    etiquetas_upt_es = [traducir_mes_espanol(f.strftime('%d-%b')) for f in fechas_upt]

                fig_upt.update_xaxes(
                    type='category',
                    ticktext=etiquetas_upt_es,
                    tickvals=fechas_upt
                )
                fig_upt = configurar_grafico_rendimiento(fig_upt)
                render_plotly(fig_upt)

                st.caption(
                    f'UPT promedio del periodo: {formatear_numero_argentino(round(float(upt_promedio), 2), 2)} unidades.'
                )

                # Insight menos técnico
                if pendiente_upt is not None:
                    pendiente_upt_redondeada = round(float(pendiente_upt), 3)
                    unidad_ref_upt = {'Mensual': 'mes', 'Semanal': 'semana', 'Quincenal': 'quincena'}[vista_upt]

                    if pendiente_upt_redondeada < -0.01:
                        st.info(f"📉 **Tendencia a la baja:** El UPT está disminuyendo aproximadamente {formatear_numero_argentino(abs(pendiente_upt_redondeada), 3)} unidades por {unidad_ref_upt}. Los clientes están comprando menos artículos por visita.")
                    elif pendiente_upt_redondeada > 0.01:
                        st.success(f"📈 **Tendencia al alza:** El UPT está aumentando aproximadamente {formatear_numero_argentino(abs(pendiente_upt_redondeada), 3)} unidades por {unidad_ref_upt}. Los clientes están comprando más artículos por visita.")
                    else:
                        st.info(f"➡️ **Tendencia estable:** El UPT se mantiene relativamente constante alrededor de {formatear_numero_argentino(round(float(upt_promedio), 2), 2)} unidades por ticket.")
            else:
                st.info('No hay datos suficientes para calcular UPT.')
        else:
            st.info('No hay datos suficientes para calcular UPT.')

        # -------------------------
        # Cantidad promedio de tickets por semana
        # -------------------------
        st.markdown('### Cantidad promedio de tickets por semana')

        # Calcular semana (de lunes a domingo)
        detalle_tickets['semana_inicio_ticket'] = detalle_tickets['fecha'] - pd.to_timedelta(
            detalle_tickets['fecha'].dt.weekday, unit='D'
        )

        # IMPORTANTE: rentabilidad_ticket tiene 1 fila por ticket, pero debemos deduplicar por si acaso
        # Primero deduplicamos por ticket_id para evitar contar duplicados
        tickets_unicos = detalle_tickets.drop_duplicates(subset=['ticket_id'])[['ticket_id', 'semana_inicio_ticket']]

        cantidad_tickets_semanal = (
            tickets_unicos.groupby('semana_inicio_ticket', as_index=False)
            .agg(
                tickets=('ticket_id', 'count')
            )
            .sort_values('semana_inicio_ticket')
        )

        # Eliminar las últimas 2 semanas para evitar sesgo de semanas incompletas
        if len(cantidad_tickets_semanal) > 2:
            cantidad_tickets_semanal = cantidad_tickets_semanal.iloc[:-2]

        if not cantidad_tickets_semanal.empty and len(cantidad_tickets_semanal) > 0:
            fig_ticket_semanal = go.Figure()

            # Línea principal de cantidad de tickets
            fig_ticket_semanal.add_trace(
                go.Scatter(
                    x=cantidad_tickets_semanal['semana_inicio_ticket'],
                    y=cantidad_tickets_semanal['tickets'],
                    mode='lines+markers',
                    name='Cantidad de tickets',
                    line=dict(color='#ff9800', width=3),
                    marker=dict(size=7, color='#fb8c00')
                )
            )

            # Línea de promedio
            tickets_promedio_global = cantidad_tickets_semanal['tickets'].mean()
            fig_ticket_semanal.add_trace(
                go.Scatter(
                    x=cantidad_tickets_semanal['semana_inicio_ticket'],
                    y=[tickets_promedio_global] * len(cantidad_tickets_semanal),
                    mode='lines',
                    name='Promedio',
                    line=dict(color='#9c27b0', width=2, dash='dot')
                )
            )

            # Línea de tendencia
            if len(cantidad_tickets_semanal) >= 2:
                cantidad_tickets_semanal['semana_num'] = range(len(cantidad_tickets_semanal))
                z_ticket = np.polyfit(cantidad_tickets_semanal['semana_num'], cantidad_tickets_semanal['tickets'], 1)
                p_ticket = np.poly1d(z_ticket)
                cantidad_tickets_semanal['tendencia'] = p_ticket(cantidad_tickets_semanal['semana_num'])
                pendiente_ticket = z_ticket[0]

                fig_ticket_semanal.add_trace(
                    go.Scatter(
                        x=cantidad_tickets_semanal['semana_inicio_ticket'],
                        y=cantidad_tickets_semanal['tendencia'],
                        mode='lines',
                        name='Tendencia',
                        line=dict(color='#ff7043', width=2, dash='dash')
                    )
                )
            else:
                pendiente_ticket = None

            fig_ticket_semanal.update_layout(
                title='<b><b>Cantidad promedio de tickets por semana</b></b>',
                height=360,
                margin=dict(t=60, r=20, l=60, b=40),
                yaxis_title='Cantidad de tickets',
                yaxis_tickformat=',.0f',
                hovermode='x unified'
            )

            # Generar etiquetas en español
            fechas_ticket = cantidad_tickets_semanal['semana_inicio_ticket']
            etiquetas_ticket_es = [traducir_mes_espanol(f.strftime('%d-%b')) for f in fechas_ticket]
            fig_ticket_semanal.update_xaxes(
                type='category',
                ticktext=etiquetas_ticket_es,
                tickvals=fechas_ticket
            )
            fig_ticket_semanal = configurar_grafico_rendimiento(fig_ticket_semanal)
            render_plotly(fig_ticket_semanal)

            st.caption(
                f'Cantidad promedio de tickets por semana: {formatear_numero_argentino(round(float(tickets_promedio_global), 0), 0)} tickets'
            )

            # Insight menos técnico
            if pendiente_ticket is not None:
                pendiente_ticket_redondeada = round(float(pendiente_ticket), 0)

                if pendiente_ticket_redondeada < -5:
                    st.info(f"📉 **Tendencia a la baja:** La cantidad de tickets está disminuyendo aproximadamente {formatear_numero_argentino(abs(pendiente_ticket_redondeada), 0)} tickets por semana. Hay menos transacciones cada semana.")
                elif pendiente_ticket_redondeada > 5:
                    st.success(f"📈 **Tendencia al alza:** La cantidad de tickets está aumentando aproximadamente {formatear_numero_argentino(abs(pendiente_ticket_redondeada), 0)} tickets por semana. Hay más transacciones cada semana.")
                else:
                    st.info(f"➡️ **Tendencia estable:** La cantidad de tickets se mantiene relativamente constante alrededor de {formatear_numero_argentino(round(float(tickets_promedio_global), 0), 0)} tickets por semana.")
        else:
            st.info('No hay datos suficientes para calcular la cantidad promedio de tickets por semana.')

        # ============================================================================
        # EVOLUCIÓN DEL TICKET PROMEDIO
        # ============================================================================
        st.markdown('### Evolución del ticket promedio')

        # Calcular ticket promedio mensual
        detalle_tickets['mes_ticket_prom'] = detalle_tickets['fecha'].dt.to_period('M').dt.to_timestamp()
        df_ticket_promedio = (
            detalle_tickets.groupby('mes_ticket_prom', as_index=False)
            .agg(
                ticket_promedio=('monto_total_ticket', 'mean')
            )
            .sort_values('mes_ticket_prom')
        )

        if df_ticket_promedio is not None and not df_ticket_promedio.empty and len(df_ticket_promedio) > 1:
            # Calcular promedio global y tendencia
            ticket_prom_global = df_ticket_promedio['ticket_promedio'].mean()

            # Regresión lineal para tendencia
            X_ticket = np.arange(len(df_ticket_promedio)).reshape(-1, 1)
            y_ticket = df_ticket_promedio['ticket_promedio'].values
            model_ticket = LinearRegression()
            model_ticket.fit(X_ticket, y_ticket)
            tendencia_ticket = model_ticket.predict(X_ticket)

            # Crear gráfico
            fig_ticket_evol = go.Figure()

            # Línea de ticket promedio real
            fig_ticket_evol.add_trace(go.Scatter(
                x=df_ticket_promedio['mes_ticket_prom'],
                y=df_ticket_promedio['ticket_promedio'],
                mode='lines+markers',
                name='Ticket promedio',
                line=dict(color='#1976d2', width=3),
                marker=dict(size=10, color='#1976d2')
            ))

            # Línea de tendencia
            fig_ticket_evol.add_trace(go.Scatter(
                x=df_ticket_promedio['mes_ticket_prom'],
                y=tendencia_ticket,
                mode='lines',
                name='Tendencia',
                line=dict(color='#ef6c00', width=2, dash='dash')
            ))

            # Línea de promedio
            fig_ticket_evol.add_trace(go.Scatter(
                x=df_ticket_promedio['mes_ticket_prom'],
                y=[ticket_prom_global] * len(df_ticket_promedio),
                mode='lines',
                name='Promedio',
                line=dict(color='#424242', width=1, dash='dot')
            ))

            # Formato de etiquetas
            etiquetas_ticket_evol = [traducir_mes_espanol(f.strftime('%b. %Y')) for f in df_ticket_promedio['mes_ticket_prom']]

            fig_ticket_evol.update_xaxes(
                type='category',
                ticktext=etiquetas_ticket_evol,
                tickvals=df_ticket_promedio['mes_ticket_prom'],
                title=None
            )

            fig_ticket_evol.update_yaxes(
                title='Ticket promedio ($)',
                tickprefix='$',
                tickformat=',.0f'
            )

            fig_ticket_evol.update_layout(
                title='Mensual - Ticket promedio',
                height=400,
                hovermode='x unified',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                showlegend=True
            )

            fig_ticket_evol = configurar_grafico_rendimiento(fig_ticket_evol)
            render_plotly(fig_ticket_evol)

            st.caption(f'Ticket promedio del periodo: ${formatear_numero_argentino(round(float(ticket_prom_global), 0), 0)}')
        else:
            st.info('No hay datos suficientes para el análisis de ticket promedio.')

        st.markdown('### Ticket promedio por dia de la semana')
        if tickets_dia is not None and not tickets_dia.empty:
            fig_media_dia = px.bar(
                tickets_dia,
                x='dia',
                y='ticket_promedio',
                labels={'dia': 'Dia de la semana', 'ticket_promedio': 'Ticket promedio ($)'},
                color_discrete_sequence=['#ff9800']
            )
            fig_media_dia.update_layout(
                height=360,
                xaxis_title='Dia de la semana',
                yaxis_title='Ticket promedio ($)',
                yaxis_tickprefix='$',
                yaxis_tickformat=',.0f',
                margin=dict(t=60, r=20, l=60, b=40)
            )
            fig_media_dia = configurar_grafico_rendimiento(fig_media_dia)
            render_plotly(fig_media_dia)

        # ============================================================================
        # MARGEN PROMEDIO POR TICKET (%)
        # ============================================================================
        st.markdown('### Margen promedio por ticket (%)')

        st.markdown('Selecciona la granularidad')
        vista_margen = st.radio(
            '',
            ['Mensual', 'Quincenal', 'Semanal'],
            horizontal=True,
            index=0,  # Por defecto Mensual
            key='vista_margen_temporal',
            label_visibility='collapsed'
        )

        # Calcular margen % según granularidad
        df_margen_temporal = None
        periodo_col_margen = None
        titulo_margen = None

        if vista_margen == 'Mensual':
            detalle_tickets['mes_margen'] = detalle_tickets['fecha'].dt.to_period('M').dt.to_timestamp()
            df_margen_temporal = (
                detalle_tickets.groupby('mes_margen', as_index=False)
                .agg(
                    margen_ticket=('margen_ticket', 'sum'),
                    monto_total_ticket=('monto_total_ticket', 'sum')
                )
                .sort_values('mes_margen')
            )
            df_margen_temporal['margen_pct'] = (df_margen_temporal['margen_ticket'] / df_margen_temporal['monto_total_ticket']) * 100
            periodo_col_margen = 'mes_margen'
            titulo_margen = 'Mensual - Margen % por Ticket'

        elif vista_margen == 'Quincenal':
            detalle_tickets['quincena_margen'] = detalle_tickets['fecha'].apply(
                lambda x: pd.Timestamp(year=x.year, month=x.month, day=1 if x.day <= 15 else 15)
            )
            df_margen_temporal = (
                detalle_tickets.groupby('quincena_margen', as_index=False)
                .agg(
                    margen_ticket=('margen_ticket', 'sum'),
                    monto_total_ticket=('monto_total_ticket', 'sum')
                )
                .sort_values('quincena_margen')
            )
            df_margen_temporal['margen_pct'] = (df_margen_temporal['margen_ticket'] / df_margen_temporal['monto_total_ticket']) * 100
            periodo_col_margen = 'quincena_margen'
            titulo_margen = 'Quincenal - Margen % por Ticket'

        else:  # Semanal
            detalle_tickets['semana_margen'] = detalle_tickets['fecha'].dt.to_period('W').apply(lambda x: x.start_time)
            df_margen_temporal = (
                detalle_tickets.groupby('semana_margen', as_index=False)
                .agg(
                    margen_ticket=('margen_ticket', 'sum'),
                    monto_total_ticket=('monto_total_ticket', 'sum')
                )
                .sort_values('semana_margen')
            )
            df_margen_temporal['margen_pct'] = (df_margen_temporal['margen_ticket'] / df_margen_temporal['monto_total_ticket']) * 100
            periodo_col_margen = 'semana_margen'
            titulo_margen = 'Semanal - Margen % por Ticket'

        if df_margen_temporal is not None and not df_margen_temporal.empty and len(df_margen_temporal) > 1:
            # Calcular promedio y tendencia
            margen_promedio_periodo = df_margen_temporal['margen_pct'].mean()

            # Regresión lineal para tendencia
            X_margen = np.arange(len(df_margen_temporal)).reshape(-1, 1)
            y_margen = df_margen_temporal['margen_pct'].values
            model_margen = LinearRegression()
            model_margen.fit(X_margen, y_margen)
            tendencia_margen = model_margen.predict(X_margen)

            # Crear gráfico
            fig_margen_temporal = go.Figure()

            # Línea de margen real
            fig_margen_temporal.add_trace(go.Scatter(
                x=df_margen_temporal[periodo_col_margen],
                y=df_margen_temporal['margen_pct'],
                mode='lines+markers',
                name='Margen',
                line=dict(color='#2e7d32', width=3),
                marker=dict(size=10, color='#2e7d32')
            ))

            # Línea de tendencia
            fig_margen_temporal.add_trace(go.Scatter(
                x=df_margen_temporal[periodo_col_margen],
                y=tendencia_margen,
                mode='lines',
                name='Tendencia',
                line=dict(color='#ef6c00', width=2, dash='dash')
            ))

            # Línea de promedio
            fig_margen_temporal.add_trace(go.Scatter(
                x=df_margen_temporal[periodo_col_margen],
                y=[margen_promedio_periodo] * len(df_margen_temporal),
                mode='lines',
                name='Promedio',
                line=dict(color='#424242', width=1, dash='dot')
            ))

            # Formato de etiquetas según granularidad
            if vista_margen == 'Mensual':
                etiquetas_margen = [traducir_mes_espanol(f.strftime('%b. %Y')) for f in df_margen_temporal[periodo_col_margen]]
            else:
                etiquetas_margen = [traducir_mes_espanol(f.strftime('%d-%b')) for f in df_margen_temporal[periodo_col_margen]]

            fig_margen_temporal.update_xaxes(
                type='category',
                ticktext=etiquetas_margen,
                tickvals=df_margen_temporal[periodo_col_margen],
                title=None
            )

            fig_margen_temporal.update_yaxes(
                title='Margen promedio (%)',
                ticksuffix='%'
            )

            fig_margen_temporal.update_layout(
                title=titulo_margen,
                height=400,
                hovermode='x unified',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                showlegend=True
            )

            fig_margen_temporal = configurar_grafico_rendimiento(fig_margen_temporal)
            render_plotly(fig_margen_temporal)

            # Análisis de variación
            variacion_margen = df_margen_temporal['margen_pct'].std()
            st.markdown(f"Margen promedio del periodo: **{margen_promedio_periodo:.2f}%**")

            # Insight sobre estabilidad del margen
            if variacion_margen < 0.5:
                st.info(f"""
                ✅ **Margen estable:** El margen por ticket se mantiene relativamente constante alrededor del {margen_promedio_periodo:.2f}%.
                La variación es de {variacion_margen:.1f}pp en el período.
                """)
            elif variacion_margen < 1.5:
                st.warning(f"""
                ⚠️ **Margen moderadamente variable:** El margen por ticket muestra cierta variabilidad ({variacion_margen:.1f}pp),
                promediando {margen_promedio_periodo:.2f}%. Revisar factores que afectan la rentabilidad.
                """)
            else:
                st.error(f"""
                🔴 **Margen muy variable:** El margen por ticket presenta alta variabilidad ({variacion_margen:.1f}pp)
                alrededor del promedio de {margen_promedio_periodo:.2f}%. Se recomienda investigar causas.
                """)

        else:
            st.info('No hay datos suficientes para el análisis de margen en esta granularidad.')

        with st.expander('Ver detalle complementario por quincena'):
            if not tickets_quincena.empty:
                fig_quincena = px.bar(
                    tickets_quincena,
                    x='quincena_label',
                    y='tickets',
                    labels={'quincena_label': 'Periodo', 'tickets': 'Tickets unicos'},
                    color_discrete_sequence=['#3949ab']
                )
                fig_quincena.update_layout(
                    height=360,
                    xaxis_title='Periodo',
                    xaxis_tickangle=-35,
                    yaxis_title='Tickets unicos',
                    margin=dict(t=60, r=20, l=60, b=40)
                )
                fig_quincena = configurar_grafico_rendimiento(fig_quincena)
                render_plotly(fig_quincena)
            else:
                st.info('No hay datos suficientes para el analisis por quincena.')
        kpi_tipo_mod = processed_data.get("kpi_tipo_dia_modular")
        if kpi_tipo_mod is not None and not kpi_tipo_mod.empty:
            st.markdown("### Comparativo por tipo de día")
            kpi_tipo_plot = (
                kpi_tipo_mod.copy()
                .groupby("tipo_dia", as_index=False)
                .agg(
                    ticket_promedio=("ticket_promedio", "mean"),
                    upt=("upt", "mean"),
                    margen_pct=("margen_pct", "mean"),
                )
                .sort_values("tipo_dia")
            )
            kpi_tipo_plot["margen_pct"] = kpi_tipo_plot["margen_pct"] * 100

            col_tipo1, col_tipo2, col_tipo3 = st.columns(3)
            fig_ticket_tipo = px.bar(
                kpi_tipo_plot,
                x="tipo_dia",
                y="ticket_promedio",
                labels={"tipo_dia": "Tipo de día", "ticket_promedio": "Ticket promedio ($)"},
                title="Ticket promedio por tipo de día",
            )
            fig_ticket_tipo.update_traces(
                marker_color="#283593",
                texttemplate="%{y:,.0f}",
                textposition="outside",
                textfont=dict(size=13, color="#262730", family="Source Sans")
            )
            # Ajustar el rango del eje Y para dar espacio a los números
            max_y_ticket = kpi_tipo_plot["ticket_promedio"].max()
            fig_ticket_tipo.update_layout(
                height=360,
                yaxis_tickprefix="$",
                yaxis_tickformat=",",
                yaxis_range=[0, max_y_ticket * 1.15],
                margin=dict(t=60, b=60, l=60, r=20)
            )
            col_tipo1.plotly_chart(fig_ticket_tipo, use_container_width=True)

            fig_upt_tipo = px.bar(
                kpi_tipo_plot,
                x="tipo_dia",
                y="upt",
                labels={"tipo_dia": "Tipo de día", "upt": "Unidades por ticket"},
                title="Unidades por ticket",
            )
            fig_upt_tipo.update_traces(
                marker_color="#fb8c00",
                texttemplate="%{y:.2f}",
                textposition="outside",
                textfont=dict(size=13, color="#262730", family="Source Sans")
            )
            # Ajustar el rango del eje Y para dar espacio a los números
            max_y_upt = kpi_tipo_plot["upt"].max()
            fig_upt_tipo.update_layout(
                height=360,
                yaxis_range=[0, max_y_upt * 1.15],
                margin=dict(t=60, b=60, l=60, r=20)
            )
            col_tipo2.plotly_chart(fig_upt_tipo, use_container_width=True)

            fig_margen_tipo = px.bar(
                kpi_tipo_plot,
                x="tipo_dia",
                y="margen_pct",
                labels={"tipo_dia": "Tipo de día", "margen_pct": "Margen (%)"},
                title="Margen promedio",
            )
            fig_margen_tipo.update_traces(
                marker_color="#00897b",
                texttemplate="%{y:.1f}%",
                textposition="outside",
                textfont=dict(size=13, color="#262730", family="Source Sans")
            )
            # Ajustar el rango del eje Y para dar espacio a los números
            max_y_margen = kpi_tipo_plot["margen_pct"].max()
            fig_margen_tipo.update_layout(
                height=360,
                yaxis_ticksuffix="%",
                yaxis_range=[0, max_y_margen * 1.15],
                margin=dict(t=60, b=60, l=60, r=20)
            )
            col_tipo3.plotly_chart(fig_margen_tipo, use_container_width=True)

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
                render_plotly(fig_horario)

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
                print(f"[ERROR] Error creating horario chart: {e}")
                st.info("Error generando gráfico horario. Verificar datos de comprobantes_ventas_horario.csv.")
        else:
            st.info("No se pudo construir la vista horaria; verificar la fuente `comprobantes_ventas_horario.csv`.")

# =============================================================================
# TAB 7: MÁRGENES - COSTOS (movido al final)
# =============================================================================
with tabs[6]:
    st.markdown("## 💰 Análisis de Rentabilidad y Márgenes")

    # Nota metodológica prominente al inicio
    st.markdown("""
    <div style='background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
                padding: 1.5rem 2rem; border-radius: 12px; margin-bottom: 2rem;
                border-left: 6px solid #e65100; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
        <h3 style='margin: 0 0 1rem 0; color: white; font-size: 1.3rem;'>
            ⚠️ NOTA METODOLÓGICA IMPORTANTE
        </h3>
        <p style='font-size: 1.1rem; margin: 0 0 0.8rem 0; line-height: 1.7; color: white; font-weight: 500;'>
            Los márgenes presentados en esta sección fueron calculados utilizando <b>márgenes promedio por categoría</b>
            obtenidos de datos históricos de ventas.
        </p>
        <p style='font-size: 1.1rem; margin: 0; line-height: 1.7; color: white; font-weight: 500;'>
            📊 Estos cálculos son <b>aproximaciones</b> y serán actualizados cuando se disponga de los
            <b>costos reales de cada producto individual</b>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # =========================================================================
    # SECCIÓN 1: ANÁLISIS DE RENTABILIDAD POR PRODUCTO
    # =========================================================================

    # Banner verde informativo
    st.markdown("""
    <div style='background: linear-gradient(135deg, #2e7d32 0%, #388e3c 100%);
                padding: 1.8rem; border-radius: 12px; margin-bottom: 1.5rem; color: white;'>
        <h3 style='margin: 0 0 0.8rem 0; color: white;'>📊 Análisis de Rentabilidad por Producto</h3>
        <p style='margin: 0; font-size: 0.95rem; line-height: 1.5;'>
            Este módulo analiza el <b>margen bruto real</b> de cada producto basado en datos históricos de ventas, identificando:
        </p>
        <ul style='margin: 0.5rem 0 0 1.2rem; padding: 0;'>
            <li>Productos estrella (alto margen + alto volumen)</li>
            <li>Oportunidades de mejora de pricing</li>
            <li>Productos de baja rentabilidad que requieren atención</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # Obtener datos de productos
    pareto_prod = data.get('pareto_prod')

    if pareto_prod is None or pareto_prod.empty:
        st.warning("No hay datos de productos disponibles para el análisis de rentabilidad.")
    else:
        pareto_prod = pareto_prod.copy()

        # Calcular margen_pct si no existe
        if 'margen_pct' not in pareto_prod.columns:
            pareto_prod['margen_pct'] = (pareto_prod['margen_linea'] / pareto_prod['ventas'] * 100).fillna(0)

        # Renombrar margen_linea a margen para consistencia
        if 'margen_linea' in pareto_prod.columns and 'margen' not in pareto_prod.columns:
            pareto_prod['margen'] = pareto_prod['margen_linea']

        # Filtrar productos con datos inconsistentes y reemplazar con promedio por categoría
        # Calcular margen promedio por categoría para productos con margen 0 o negativo
        margen_promedio_global = pareto_prod[pareto_prod['margen_pct'] > 0]['margen_pct'].mean()
        margen_por_categoria = pareto_prod[pareto_prod['margen_pct'] > 0].groupby('categoria')['margen_pct'].mean().to_dict()

        # Reemplazar márgenes <= 0 con el promedio de la categoría, o global si no hay dato
        for idx in pareto_prod[pareto_prod['margen_pct'] <= 0].index:
            categoria = pareto_prod.loc[idx, 'categoria']
            if categoria in margen_por_categoria:
                pareto_prod.loc[idx, 'margen_pct'] = margen_por_categoria[categoria]
            else:
                pareto_prod.loc[idx, 'margen_pct'] = margen_promedio_global

            # Ajustar también el margen absoluto
            ventas = pareto_prod.loc[idx, 'ventas']
            pareto_prod.loc[idx, 'margen'] = ventas * pareto_prod.loc[idx, 'margen_pct'] / 100

        # Vista Ejecutiva de Rentabilidad
        st.markdown("### 📊 Vista Ejecutiva de Rentabilidad")

        # Calcular métricas globales
        ventas_totales = pareto_prod['ventas'].sum()
        margen_total = pareto_prod['margen'].sum()
        margen_promedio_pct = (margen_total / ventas_totales * 100) if ventas_totales > 0 else 0
        productos_rentables = len(pareto_prod[pareto_prod['margen_pct'] > margen_promedio_pct])

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "💰 Ventas Totales",
                formatear_moneda_argentina(ventas_totales, 0),
                help="Facturación total del catálogo"
            )

        with col2:
            st.metric(
                "💎 Margen Total",
                formatear_moneda_argentina(margen_total, 0),
                help="Rentabilidad acumulada"
            )

        with col3:
            st.metric(
                "📈 Margen Promedio",
                f"{margen_promedio_pct:.1f}%",
                help="Margen porcentual promedio"
            )

        with col4:
            st.metric(
                "⭐ Productos Rentables",
                formatear_numero_argentino(productos_rentables, 0),
                help=f"{(productos_rentables/len(pareto_prod)*100):.1f}% del catálogo"
            )

        # Matriz de Productos: Volumen vs Rentabilidad
        st.markdown("### 🎯 Matriz de Productos: Volumen vs Rentabilidad (Top 200)")

        # Preparar datos para scatter plot (solo top 200 por volumen)
        top_productos = pareto_prod.nlargest(200, 'ventas').copy()

        # Clasificar productos en cuadrantes
        ventas_mediana = top_productos['ventas'].median()
        margen_mediano = top_productos['margen_pct'].median()

        def clasificar_producto(row):
            if row['ventas'] > ventas_mediana and row['margen_pct'] > margen_mediano:
                return '⭐ Estrellas'
            elif row['ventas'] > ventas_mediana and row['margen_pct'] <= margen_mediano:
                return '🚦 Generadores de Tráfico'
            elif row['ventas'] <= ventas_mediana and row['margen_pct'] > margen_mediano:
                return '💎 Joyas Ocultas'
            else:
                return '⚠️ A Revisar'

        top_productos['clasificacion'] = top_productos.apply(clasificar_producto, axis=1)

        # Crear scatter plot
        fig_matriz = px.scatter(
            top_productos,
            x='ventas',
            y='margen_pct',
            color='clasificacion',
            size='margen',
            hover_data={
                'descripcion': True,
                'ventas': ':$,.0f',
                'margen': ':$,.0f',
                'margen_pct': ':.1f',
                'clasificacion': True
            },
            labels={
                'ventas': 'Ventas Totales ($)',
                'margen_pct': 'Margen (%)',
                'clasificacion': 'Clasificación'
            },
            color_discrete_map={
                '⭐ Estrellas': '#4caf50',
                '🚦 Generadores de Tráfico': '#2196f3',
                '💎 Joyas Ocultas': '#ff9800',
                '⚠️ A Revisar': '#f44336'
            },
            height=500
        )

        # Agregar líneas de referencia (medianas)
        fig_matriz.add_hline(
            y=margen_mediano,
            line_dash="dash",
            line_color="gray",
            annotation_text=f"Margen mediano: {margen_mediano:.1f}%",
            annotation_position="right"
        )

        fig_matriz.add_vline(
            x=ventas_mediana,
            line_dash="dash",
            line_color="gray",
            annotation_text=f"Ventas medianas: ${formatear_numero_argentino(ventas_mediana, 0)}",
            annotation_position="top"
        )

        fig_matriz.update_layout(
            title="Matriz de Productos: Volumen vs Rentabilidad (Top 200)",
            xaxis_title="Ventas Totales ($)",
            yaxis_title="Margen (%)",
            legend_title="Clasificación en Tráfico",
            hovermode='closest'
        )

        fig_matriz = configurar_grafico_rendimiento(fig_matriz)
        render_plotly(fig_matriz)

        # Interpretación de la Matriz
        st.markdown("### 📖 Interpretación de la Matriz")

        st.markdown("""
        <div style='background: #f5f5f5; padding: 1.2rem; border-radius: 8px; border-left: 4px solid #2196f3;'>
            <ul style='margin: 0; padding-left: 1.5rem; line-height: 1.8;'>
                <li><b>⭐ Estrellas</b> (alto volumen + alto margen): <b>Proteger y promocionar.</b> Son los productos ideales.</li>
                <li><b>🚦 Generadores de Tráfico</b> (alto volumen + bajo margen): <b>Usar para atraer clientes</b>, optimizar costos.</li>
                <li><b>💎 Joyas Ocultas</b> (bajo volumen + alto margen): <b>Impulsar ventas</b> con promociones y mejor exhibición.</li>
                <li><b>⚠️ A Revisar</b> (bajo volumen + bajo margen): <b>Evaluar descatalogar</b> o replantear estrategia de precios.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # Productos Extremos
        st.markdown("### 🔍 Productos Extremos")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### ⭐ Top 10 Más Rentables (P × Q)")
            st.caption("Productos que generan mayor rentabilidad total en $")
            top_rentables = pareto_prod.nlargest(10, 'margen')[
                ['descripcion', 'categoria', 'margen', 'margen_pct', 'ventas']
            ].copy()
            top_rentables['Margen Total'] = top_rentables['margen'].apply(lambda x: formatear_moneda_argentina(x, 0))
            top_rentables['Margen %'] = top_rentables['margen_pct'].apply(lambda x: f"{x:.1f}%")
            top_rentables['Ventas'] = top_rentables['ventas'].apply(lambda x: formatear_moneda_argentina(x, 0))
            top_rentables = top_rentables.drop(columns=['margen', 'margen_pct', 'ventas'])
            top_rentables.columns = ['Producto', 'Categoría', 'Margen Total $', 'Margen %', 'Ventas']
            st.dataframe(top_rentables, use_container_width=True, hide_index=True)

        with col2:
            st.markdown("#### ⚠️ Top 10 Menor Rentabilidad Total")
            st.caption("Productos con menor contribución de margen en $")
            top_bajo_margen = pareto_prod.nsmallest(10, 'margen')[
                ['descripcion', 'categoria', 'margen', 'margen_pct', 'ventas']
            ].copy()
            top_bajo_margen['Margen Total'] = top_bajo_margen['margen'].apply(lambda x: formatear_moneda_argentina(x, 0))
            top_bajo_margen['Margen %'] = top_bajo_margen['margen_pct'].apply(lambda x: f"{x:.1f}%")
            top_bajo_margen['Ventas'] = top_bajo_margen['ventas'].apply(lambda x: formatear_moneda_argentina(x, 0))
            top_bajo_margen = top_bajo_margen.drop(columns=['margen', 'margen_pct', 'ventas'])
            top_bajo_margen.columns = ['Producto', 'Categoría', 'Margen Total $', 'Margen %', 'Ventas']
            st.dataframe(top_bajo_margen, use_container_width=True, hide_index=True)

        # Resumen por Cuadrante
        st.markdown("### 📊 Resumen por Cuadrante")

        resumen_cuadrantes = top_productos.groupby('clasificacion').agg({
            'descripcion': 'count',
            'ventas': 'sum',
            'margen': 'sum',
            'margen_pct': 'mean'
        }).reset_index()

        resumen_cuadrantes.columns = ['Cuadrante', 'Nº Productos', 'Ventas Totales', 'Margen Total', 'Margen % Promedio']
        resumen_cuadrantes['Ventas Totales'] = resumen_cuadrantes['Ventas Totales'].apply(lambda x: formatear_moneda_argentina(x, 0))
        resumen_cuadrantes['Margen Total'] = resumen_cuadrantes['Margen Total'].apply(lambda x: formatear_moneda_argentina(x, 0))
        resumen_cuadrantes['Margen % Promedio'] = resumen_cuadrantes['Margen % Promedio'].apply(lambda x: f"{x:.1f}%")

        st.dataframe(resumen_cuadrantes, use_container_width=True, hide_index=True)

    # =========================================================================
    # SECCIÓN 2: ANÁLISIS DE COSTOS (PROTOTIPO CON DATOS SINTÉTICOS)
    # =========================================================================

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Banner informativo colapsable
    with st.expander("📊 **CÁLCULOS APROXIMADOS** - Requiere Costos Reales de Productos", expanded=False):
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1976d2 0%, #2196f3 100%);
                    padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem; color: white;'>
            <h4 style='margin: 0 0 0.8rem 0; color: white;'>⚠️ Simulación con Datos Ficticios</h4>
            <p style='margin: 0; font-size: 0.95rem; line-height: 1.5;'>
                Esta sección muestra <b>cálculos aproximados basados en datos sintéticos</b>.<br>
                Para análisis reales, se requieren costos unitarios de cada producto.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style='background: #e3f2fd; border-left: 6px solid #2196f3; padding: 1.2rem; border-radius: 8px; margin-bottom: 1.5rem;'>
            <p style='margin: 0; color: #1565c0; line-height: 1.6;'>
                <b>📋 Datos necesarios para activar análisis real:</b>
            </p>
            <ul style='margin: 0.5rem 0 0 1.2rem; padding: 0; color: #1565c0;'>
                <li><b>📦 Costo de compra unitario</b> por producto (precio proveedor)</li>
                <li><b>🚚 Costos logísticos</b> (transporte, almacenamiento, mermas)</li>
                <li><b>💼 Costos fijos mensuales</b> (alquiler, servicios, personal)</li>
                <li><b>📊 Criterio de asignación</b> de costos indirectos (overhead)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # Generar datos sintéticos para la simulación
        # Seleccionar 10 productos de muestra
        productos_muestra = pareto_prod.nlargest(10, 'ventas').copy()

        # Generar costos sintéticos (simulación)
        np.random.seed(42)  # Para reproducibilidad
        productos_muestra['precio_venta'] = productos_muestra['ventas'] / np.maximum(productos_muestra['ventas'] / 43078.348, 1)  # Precio promedio simulado
        productos_muestra['costo_producto'] = productos_muestra['precio_venta'] * (1 - productos_muestra['margen_pct'] / 100)
        productos_muestra['logistica'] = productos_muestra['costo_producto'] * np.random.uniform(0.08, 0.12, len(productos_muestra))
        productos_muestra['overhead'] = productos_muestra['costo_producto'] * np.random.uniform(0.05, 0.10, len(productos_muestra))
        productos_muestra['margen_neto'] = productos_muestra['precio_venta'] - productos_muestra['costo_producto'] - productos_muestra['logistica'] - productos_muestra['overhead']
        productos_muestra['margen_neto_pct'] = (productos_muestra['margen_neto'] / productos_muestra['precio_venta']) * 100

        # Waterfall: De Precio de Venta a Margen Neto (ejemplo con un producto)
        st.markdown("### 💧 Waterfall: De Precio de Venta a Margen Neto")

        st.markdown("**Desglose de Costos: MUSLO DE POLLO (Ejemplo)**")

        # Valores sintéticos para el waterfall
        precio_venta_ej = 43078.348
        costo_producto_ej = 23691.091
        logistica_ej = 2446.246
        overhead_ej = 3012.484
        margen_neto_ej = precio_venta_ej - costo_producto_ej - logistica_ej - overhead_ej

        # Crear waterfall chart
        fig_waterfall = go.Figure(go.Waterfall(
            name = "Desglose",
            orientation = "v",
            measure = ["relative", "relative", "relative", "relative", "total"],
            x = ["Precio Venta", "Costo Producto", "Logística", "Overhead", "Margen Neto"],
            textposition = "outside",
            text = [
                f"${formatear_numero_argentino(precio_venta_ej, 0)}",
                f"-${formatear_numero_argentino(costo_producto_ej, 0)}",
                f"-${formatear_numero_argentino(logistica_ej, 0)}",
                f"-${formatear_numero_argentino(overhead_ej, 0)}",
                f"${formatear_numero_argentino(margen_neto_ej, 0)}"
            ],
            y = [
                precio_venta_ej,
                -costo_producto_ej,
                -logistica_ej,
                -overhead_ej,
                margen_neto_ej
            ],
            connector = {"line":{"color":"rgb(63, 63, 63)"}},
            decreasing = {"marker":{"color":"#f44336"}},
            increasing = {"marker":{"color":"#2196f3"}},
            totals = {"marker":{"color":"#4caf50"}}
        ))

        fig_waterfall.update_layout(
            title="Desglose de Costos: MUSLO DE POLLO",
            showlegend=False,
            height=450,
            yaxis_title="Monto ($)"
        )

        fig_waterfall = configurar_grafico_rendimiento(fig_waterfall)
        render_plotly(fig_waterfall)

        # Estructura de Costos Simulada por Categoría
        st.markdown("### 📊 Estructura de Costos Simulada por Categoría")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Estructura de Costos Promedio**")

            # Calcular promedios para el pie chart
            costo_promedio = 55.0  # % del precio
            logistica_promedio = 9.0
            overhead_promedio = 6.0
            margen_promedio = 30.0

            fig_pie_costos = go.Figure(data=[go.Pie(
                labels=['Costo Producto', 'Margen Neto', 'Logística', 'Overhead'],
                values=[costo_promedio, margen_promedio, logistica_promedio, overhead_promedio],
                marker=dict(colors=['#f44336', '#ff9800', '#4caf50', '#2196f3']),
                textinfo='label+percent',
                textposition='auto',
                hovertemplate='<b>%{label}</b><br>%{percent}<extra></extra>'
            )])

            fig_pie_costos.update_layout(
                showlegend=True,
                height=350,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )

            fig_pie_costos = configurar_grafico_rendimiento(fig_pie_costos)
            render_plotly(fig_pie_costos)

        with col2:
            st.markdown("### 🎯 Análisis de Punto de Equilibrio")

            st.metric(
                "Unidades en Equilibrio/Mes",
                "0",
                help="Unidades necesarias para cubrir costos fijos"
            )

            st.metric(
                "Ventas en Equilibrio/Mes",
                formatear_moneda_argentina(16666.667, 0),
                help="Facturación mínima para alcanzar punto de equilibrio"
            )

            st.metric(
                "Margen de Contribución",
                "30.0%",
                help="Porcentaje que aporta cada venta a cubrir costos fijos"
            )

        # Top 10 Productos: Precio vs Costo Simulado
        st.markdown("### 🔍 Top 10 Productos: Precio vs Costo Simulado")

        tabla_costos = productos_muestra[
            ['descripcion', 'categoria', 'precio_venta', 'costo_producto', 'margen_pct', 'margen_neto_pct']
        ].copy()

        tabla_costos.columns = ['Producto', 'Categoría', 'Precio Venta', 'Costo Unitario', 'Margen $', 'Margen %']
        tabla_costos['Precio Venta'] = tabla_costos['Precio Venta'].apply(lambda x: formatear_moneda_argentina(x, 0))
        tabla_costos['Costo Unitario'] = tabla_costos['Costo Unitario'].apply(lambda x: formatear_moneda_argentina(x, 0))
        tabla_costos['Margen $'] = tabla_costos['Margen $'].apply(lambda x: f"{x:.1f}%")
        tabla_costos['Margen %'] = tabla_costos['Margen %'].apply(lambda x: f"{x:.1f}%")

        st.dataframe(tabla_costos, use_container_width=True, hide_index=True)

        # Banner de próximos pasos
        st.markdown("""
        <div style='background: linear-gradient(135deg, #283593 0%, #3949ab 100%);
                    padding: 1.5rem; border-radius: 12px; margin-top: 1.5rem; color: white;'>
            <h4 style='margin: 0 0 0.8rem 0; color: #ffd54f;'>🚀 Análisis Posible con Datos Reales</h4>
            <p style='margin: 0 0 0.5rem 0; font-size: 0.9rem; line-height: 1.6;'>
                Con costos reales de productos, se podrá realizar:
            </p>
            <ul style='margin: 0; padding-left: 1.2rem; line-height: 1.6; font-size: 0.9rem;'>
                <li>Identificar productos con pricing subóptimo</li>
                <li>Calcular punto de equilibrio real por producto/categoría</li>
                <li>Optimizar márgenes y detectar oportunidades de mejora</li>
                <li>Simular impacto de cambios de precio en rentabilidad</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# TAB 2: PARETO & MIX
# =============================================================================
with tabs[1]:
    st.markdown("## Analisis de Pareto - optimizar mix de productos")

    pareto_prod = data.get('pareto_prod')
    kpi_cat = data.get('kpi_categoria')

    if pareto_prod is None or pareto_prod.empty:
        st.info("No hay datos de productos para construir el Pareto.")
    else:
        categoria_map = {
            "Todo el negocio": "TODOS",
            "Carniceria": "CARNICERIA",
            "Almacen": "ALMACEN",
            "Lacteos": "LACTEOS",
            "Limpieza": "LIMPIEZA"
        }
        st.markdown("### Paretos 80/20 por categoria clave")
        categoria_label = st.radio(
            "Selecciona la categoria a analizar",
            list(categoria_map.keys()),
            horizontal=True
        )
        categoria_clave = categoria_map[categoria_label]

        # Ya viene normalizado desde la carga, solo limpiamos descripción
        data_filtrada = pareto_prod.copy()
        data_filtrada['descripcion'] = data_filtrada['descripcion'].astype(str).str.strip()
        # Si es "Todo el negocio", usar todos los datos; sino filtrar por categoría
        if categoria_clave.upper() == "TODOS":
            categoria_filtrada = data_filtrada
        else:
            categoria_filtrada = data_filtrada[data_filtrada['categoria'] == categoria_clave.upper()]

        if categoria_filtrada.empty:
            st.warning("No hay datos suficientes para la categoria seleccionada.")
        else:
            categoria_filtrada = categoria_filtrada.sort_values('ventas', ascending=False).reset_index(drop=True)
            total_categoria = categoria_filtrada['ventas'].sum()
            categoria_filtrada['ventas_acumuladas_categoria'] = categoria_filtrada['ventas'].cumsum()
            categoria_filtrada['pct_acumulado_categoria'] = np.where(
                total_categoria > 0,
                categoria_filtrada['ventas_acumuladas_categoria'] / total_categoria * 100,
                0
            )
            categoria_filtrada['core_80'] = categoria_filtrada['pct_acumulado_categoria'] <= 80

            vista_pareto = categoria_filtrada.head(20)
            fig_categoria = go.Figure()
            fig_categoria.add_trace(
                go.Bar(
                    x=vista_pareto['descripcion'],
                    y=vista_pareto['ventas'],
                    marker_color=np.where(vista_pareto['core_80'], '#1a237e', '#9fa8da'),
                    name='Ventas'
                )
            )
            fig_categoria.add_trace(
                go.Scatter(
                    x=vista_pareto['descripcion'],
                    y=vista_pareto['pct_acumulado_categoria'],
                    mode='lines+markers',
                    name='% acumulado',
                    line=dict(color='#ff7043', width=3),
                    yaxis='y2'
                )
            )
            fig_categoria.add_shape(
                type='line',
                x0=-0.5,
                x1=len(vista_pareto['descripcion']) - 0.5,
                y0=80,
                y1=80,
                yref='y2',
                line=dict(color='green', width=2, dash='dash')
            )
            fig_categoria.update_layout(
                height=520,
                margin=dict(t=70, r=40, l=40, b=120),
                xaxis=dict(title='Descripción del producto', tickangle=-50),
                yaxis=dict(title='Ventas ($)'),
                yaxis2=dict(title='% acumulado', overlaying='y', side='right', range=[0, 105]),
                hovermode='x unified',
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
            )
            render_plotly(fig_categoria)

            core_df = categoria_filtrada[categoria_filtrada['core_80']].copy()
            core_count = int(core_df.shape[0])
            total_skus_categoria = int(categoria_filtrada.shape[0])
            cobertura_core = float(core_df['pct_acumulado_categoria'].max()) if not core_df.empty else 0.0
            cobertura_texto = formatear_numero_argentino(round(cobertura_core, 1), 1)
            ventas_categoria_formateadas = formatear_moneda_argentina(total_categoria, 0)

            st.markdown(
                f'''
                <div style='background: #e8f5e9; border-left: 6px solid #4caf50; padding: 18px; margin: 16px 0; border-radius: 10px;'>
                    <h4 style='color: #2e7d32; margin: 0;'>Nucleo 80/20 de {categoria_label}</h4>
                    <p style='margin: 8px 0 0 0;'>
                        <b>{core_count} codigos</b> (de {total_skus_categoria}) explican el <b>{cobertura_texto}%</b> de las ventas de {categoria_label.lower()}.
                        Ese nucleo factura {ventas_categoria_formateadas} dentro de la categoria, por lo que requiere
                        reposicion prioritaria, control de precio y presencia en exhibiciones.
                    </p>
                </div>
                ''',
                unsafe_allow_html=True
            )

            tabla_core = categoria_filtrada[
                (categoria_filtrada['core_80']) | (categoria_filtrada.index < 15)
            ].copy().head(15)
            tabla_core['ventas'] = tabla_core['ventas'].apply(lambda x: formatear_moneda_argentina(x, 0))
            tabla_core['margen'] = tabla_core['margen'].apply(lambda x: formatear_moneda_argentina(x, 0))
            tabla_core['pct_acumulado_categoria'] = tabla_core['pct_acumulado_categoria'].round(1).astype(str) + '%'
            tabla_core = tabla_core[['descripcion', 'ventas', 'margen', 'pct_acumulado_categoria']]
            tabla_core.columns = ['Producto', 'Ventas', 'Margen', '% acumulado']
            st.dataframe(tabla_core, use_container_width=True, hide_index=True)

    if kpi_cat is not None and not kpi_cat.empty:
        st.markdown("### Rendimiento por categoría (Top 15)")
        kpi_top = kpi_cat.head(15).copy()

        # Ordenar por ventas descendente para mejor visualización
        kpi_top = kpi_top.sort_values('ventas_totales', ascending=False)

        # Crear dos gráficos separados más claros
        col1, col2 = st.columns(2)

        with col1:
            # Gráfico 1: Top 10 por Ventas
            top10_ventas = kpi_top.head(10).sort_values('ventas_totales', ascending=True)

            fig_ventas = go.Figure()
            fig_ventas.add_trace(
                go.Bar(
                    y=top10_ventas['categoria'],
                    x=top10_ventas['ventas_totales'],
                    orientation='h',
                    marker=dict(
                        color=top10_ventas['ventas_totales'],
                        colorscale='Blues',
                        showscale=False
                    ),
                    text=[formatear_moneda_argentina(v, 0) for v in top10_ventas['ventas_totales']],
                    textposition='outside',
                    textfont=dict(size=10),
                    hovertemplate='<b>%{y}</b><br>Ventas: %{text}<extra></extra>'
                )
            )

            fig_ventas.update_layout(
                title='Top 10 Categorías por Ventas',
                height=450,
                margin=dict(t=50, r=40, l=150, b=40),
                xaxis=dict(title='Ventas ($)', showgrid=True),
                yaxis=dict(title='', tickfont=dict(size=10)),
                showlegend=False
            )

            render_plotly(fig_ventas)

        with col2:
            # Gráfico 2: Top 10 por Margen %
            top10_margen = kpi_top.nlargest(10, 'margen_pct').sort_values('margen_pct', ascending=True)

            fig_margen = go.Figure()
            fig_margen.add_trace(
                go.Bar(
                    y=top10_margen['categoria'],
                    x=top10_margen['margen_pct'],
                    orientation='h',
                    marker=dict(
                        color=top10_margen['margen_pct'],
                        colorscale='Greens',
                        showscale=False
                    ),
                    text=[f"{v:.1f}%" for v in top10_margen['margen_pct']],
                    textposition='outside',
                    textfont=dict(size=10),
                    hovertemplate='<b>%{y}</b><br>Margen: %{x:.1f}%<extra></extra>'
                )
            )

            fig_margen.update_layout(
                title='Top 10 Categorías por Margen %',
                height=450,
                margin=dict(t=50, r=40, l=150, b=40),
                xaxis=dict(title='Margen %', showgrid=True),
                yaxis=dict(title='', tickfont=dict(size=10)),
                showlegend=False
            )

            render_plotly(fig_margen)

        # Calcular segmentación por cuadrantes
        mediana_ventas = kpi_cat.head(15)['ventas_totales'].median()
        mediana_margen = kpi_cat.head(15)['margen_pct'].median()

        def asignar_cuadrante(row):
            if row['ventas_totales'] >= mediana_ventas and row['margen_pct'] >= mediana_margen:
                return 'Estrellas'
            elif row['ventas_totales'] >= mediana_ventas and row['margen_pct'] < mediana_margen:
                return 'Generadores de tráfico'
            elif row['ventas_totales'] < mediana_ventas and row['margen_pct'] >= mediana_margen:
                return 'Alta rentabilidad'
            else:
                return 'A revisar'

        kpi_top['cuadrante'] = kpi_top.apply(asignar_cuadrante, axis=1)

        # Segmentación por cuadrantes
        estrellas = kpi_top[kpi_top['cuadrante'] == 'Estrellas']['categoria'].tolist()
        generadores_trafico = kpi_top[kpi_top['cuadrante'] == 'Generadores de tráfico']['categoria'].tolist()
        alta_rentabilidad = kpi_top[kpi_top['cuadrante'] == 'Alta rentabilidad']['categoria'].tolist()
        a_revisar = kpi_top[kpi_top['cuadrante'] == 'A revisar']['categoria'].tolist()

        st.markdown(
            f'''
            <div style='background: #fff3e0; border-left: 6px solid #ff9800; padding: 18px; margin: 16px 0; border-radius: 10px;'>
                <h4 style='color: #e65100; margin: 0;'>Segmentación estratégica por rentabilidad</h4>
                <p style='margin: 8px 0 0 0;'>
                    {'<b>⭐ Estrellas</b> (Alto volumen + Alto margen): <b>' + ', '.join(estrellas) + '</b><br>' if estrellas else ''}
                    {'<b>🚀 Generadores de tráfico</b> (Alto volumen + Bajo margen): <b>' + ', '.join(generadores_trafico) + '</b><br>' if generadores_trafico else ''}
                    {'<b>💎 Alta rentabilidad</b> (Bajo volumen + Alto margen): <b>' + ', '.join(alta_rentabilidad) + '</b><br>' if alta_rentabilidad else ''}
                    {'<b>⚠️ A revisar</b> (Bajo volumen + Bajo margen): <b>' + ', '.join(a_revisar) + '</b><br>' if a_revisar else ''}
                    <br>
                    <b>Estrategia:</b> Potenciar las estrellas, usar generadores de tráfico para atraer clientes, optimizar precios en alta rentabilidad y evaluar descontinuar categorías a revisar.
                </p>
            </div>
            ''',
            unsafe_allow_html=True
        )
# =============================================================================
# TAB 3: MARKET BASKET (COMBOS)
# =============================================================================
with tabs[2]:
    st.markdown("## Market Basket Analysis - combos estrategicos")

    reglas = data.get('reglas')
    combos = data.get('combos')
    pareto_prod = data.get('pareto_prod')

    if reglas is None or reglas.empty:
        st.info("No hay reglas de asociacion disponibles.")
    else:
        producto_categoria_map = {}
        if pareto_prod is not None and not pareto_prod.empty:
            mapa_df = (
                pareto_prod[['descripcion', 'categoria']]
                .dropna()
                .drop_duplicates(subset=['descripcion'])
            )
            mapa_df['descripcion'] = mapa_df['descripcion'].str.upper().str.strip()
            mapa_df['categoria'] = mapa_df['categoria'].str.upper().str.strip()
            producto_categoria_map = dict(zip(mapa_df['descripcion'], mapa_df['categoria']))

        categorias_carniceria = {
            'CARNICERIA',
            'ELABORADOS DE CARNICERIA',
            'PRODUCTOS PARA CARNEO',
            'POLLO'
        }

        def contiene_carniceria(cadena: str) -> bool:
            if not cadena or not producto_categoria_map:
                return False
            items = [item.strip().upper() for item in cadena.split(',')]
            for item in items:
                categoria_item = producto_categoria_map.get(item)
                if categoria_item and any(cat in categoria_item for cat in categorias_carniceria):
                    return True
            return False

        reglas_mba = reglas.copy()
        reglas_mba['con_carniceria'] = reglas_mba.apply(
            lambda row: contiene_carniceria(row['antecedents']) or contiene_carniceria(row['consequents']),
            axis=1
        )

        if combos is not None and not combos.empty:
            combos_mba = combos.copy()
            combos_mba['con_carniceria'] = combos_mba.apply(
                lambda row: contiene_carniceria(row['antecedent']) or contiene_carniceria(row['consequent']),
                axis=1
            )
        else:
            combos_mba = pd.DataFrame()

        def render_vista(reglas_df: pd.DataFrame, combos_df: pd.DataFrame):
            if reglas_df.empty:
                st.info("No hay reglas de asociacion para esta seleccion.")
                return

            # Explicación del análisis
            st.markdown(
                '''
                <div style='background: #e3f2fd; border-left: 6px solid #2196f3; padding: 18px; margin: 16px 0; border-radius: 10px;'>
                    <h4 style='color: #1565c0; margin: 0;'>¿Qué es el Market Basket Analysis?</h4>
                    <p style='margin: 8px 0 0 0;'>
                        El <b>análisis de canasta de mercado</b> identifica patrones de compra conjunta. Descubre qué productos suelen comprarse juntos
                        para optimizar la ubicación en góndolas, crear promociones cruzadas y aumentar el ticket promedio.
                        <br><br>
                        <b>Métricas clave:</b><br>
                        • <b>Soporte:</b> % de transacciones que contienen la combinación<br>
                        • <b>Confianza:</b> Probabilidad de comprar B cuando se compra A<br>
                        • <b>Lift:</b> Cuánto más probable es la compra conjunta vs. aleatoria (>1 = asociación positiva)
                    </p>
                </div>
                ''',
                unsafe_allow_html=True
            )

            col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
            col_kpi1.metric("Reglas evaluadas", len(reglas_df))
            col_kpi2.metric("Lift máximo", f"{reglas_df['lift'].max():.1f}x")
            col_kpi3.metric("Soporte promedio", f"{(reglas_df['support'].mean() * 100):.2f}%")

            # Gráfico primero
            st.markdown("### Visualización: Confianza vs Soporte")
            fig_scatter = px.scatter(
                reglas_df,
                x='support',
                y='confidence',
                size='lift',
                color='lift',
                hover_data=['antecedents', 'consequents'],
                labels={
                    'support': 'Soporte',
                    'confidence': 'Confianza',
                    'lift': 'Lift'
                },
                title="Reglas de asociación (tamaño y color = lift)",
                color_continuous_scale='Viridis'
            )
            fig_scatter.update_layout(height=480, margin=dict(t=60, r=20, l=20, b=40))
            fig_scatter.update_xaxes(tickformat='.1%', title='Soporte (%)')
            fig_scatter.update_yaxes(tickformat='.1%', title='Confianza (%)')
            render_plotly(fig_scatter)

            # Combos sugeridos después del gráfico
            if combos_df is not None and not combos_df.empty:
                st.markdown("### Top combos sugeridos (ordenados por lift)")
                combos_view = combos_df[['antecedent', 'consequent', 'support', 'confidence', 'lift']].copy()
                combos_view['support'] = (combos_view['support'] * 100).round(2)
                combos_view['confidence'] = (combos_view['confidence'] * 100).round(2)
                combos_view = combos_view.rename(
                    columns={
                        'antecedent': 'Si compra esto →',
                        'consequent': '→ También compra esto',
                        'support': 'Soporte (%)',
                        'confidence': 'Confianza (%)',
                        'lift': 'Lift'
                    }
                )
                st.dataframe(combos_view, use_container_width=True, hide_index=True)

                # Insight estratégico
                top_combo = combos_df.iloc[0]
                st.markdown(
                    f'''
                    <div style='background: #fff3e0; border-left: 6px solid #ff9800; padding: 18px; margin: 16px 0; border-radius: 10px;'>
                        <h4 style='color: #e65100; margin: 0;'>Oportunidad destacada</h4>
                        <p style='margin: 8px 0 0 0;'>
                            <b>Combo top:</b> {top_combo['antecedent']} → {top_combo['consequent']}<br>
                            Con un lift de <b>{top_combo['lift']:.1f}x</b>, esta combinación tiene {top_combo['lift']:.1f} veces más probabilidad de ocurrir juntos que por separado.
                            <br><br>
                            <b>Acciones sugeridas:</b> Ubicar productos cercanos en góndola, crear promoción 2x1 o descuento por combo.
                        </p>
                    </div>
                    ''',
                    unsafe_allow_html=True
                )
            else:
                st.info("No hay combos recomendados para esta selección.")

            # Tabla de reglas detallada al final
            st.markdown("### Top 20 reglas por lift")
            reglas_top = reglas_df.nlargest(20, 'lift').copy()
            tabla_reglas = reglas_top[['antecedents', 'consequents', 'support', 'confidence', 'lift']].rename(
                columns={
                    'antecedents': 'Antecedentes',
                    'consequents': 'Consecuentes',
                    'support': 'Soporte (%)',
                    'confidence': 'Confianza (%)',
                    'lift': 'Lift'
                }
            )
            tabla_reglas['Soporte (%)'] = (tabla_reglas['Soporte (%)'] * 100).round(2)
            tabla_reglas['Confianza (%)'] = (tabla_reglas['Confianza (%)'] * 100).round(2)
            tabla_reglas['Lift'] = tabla_reglas['Lift'].round(2)
            st.dataframe(tabla_reglas, use_container_width=True, hide_index=True)

        general_tab, sin_carniceria_tab = st.tabs(["Vista general", "Sin carniceria"])

        with general_tab:
            render_vista(reglas_mba, combos_mba)

        with sin_carniceria_tab:
            reglas_filtradas = reglas_mba[~reglas_mba['con_carniceria']]
            combos_filtrados = combos_mba[~combos_mba['con_carniceria']] if not combos_mba.empty else combos_mba
            render_vista(reglas_filtradas, combos_filtrados)
# =============================================================================
# TAB 4: SEGMENTACION
# =============================================================================
with tabs[3]:
    st.markdown("## Segmentacion de tickets - personalizar estrategias")

    rentabilidad = data['rentabilidad_ticket'].copy()
    rentabilidad['rentabilidad_pct'] = rentabilidad['rentabilidad_pct_ticket'] * 100
    rentabilidad = rentabilidad[rentabilidad['rentabilidad_pct'].notna()]
    rentabilidad = rentabilidad[rentabilidad['rentabilidad_pct'] > 0]

    fig_hist = px.histogram(
        rentabilidad,
        x='rentabilidad_pct',
        nbins=50,
        title="Distribucion de rentabilidad por ticket",
        labels={'rentabilidad_pct': 'Rentabilidad (%)', 'count': 'Cantidad de tickets'},
        color_discrete_sequence=['#1a237e']
    )
    fig_hist.update_layout(
        height=400,
        showlegend=False,
        xaxis_title="Rentabilidad (%)",
        yaxis_title="Cantidad de tickets"
    )
    if not rentabilidad.empty:
        q1_rent = float(rentabilidad['rentabilidad_pct'].quantile(0.25))
        mediana_rent = float(rentabilidad['rentabilidad_pct'].quantile(0.5))
        q3_rent = float(rentabilidad['rentabilidad_pct'].quantile(0.75))
        min_rent = float(rentabilidad['rentabilidad_pct'].min())
        max_rent = float(rentabilidad['rentabilidad_pct'].max())
        quartile_ranges = [
            ("Bajo", min_rent, q1_rent, "#ffebee"),
            ("Medio-Bajo", q1_rent, mediana_rent, "#fff8e1"),
            ("Medio-Alto", mediana_rent, q3_rent, "#e3f2fd"),
            ("Alto", q3_rent, max_rent, "#e8f5e9"),
        ]
        for label, start, end, color in quartile_ranges:
            if end <= start:
                continue
            fig_hist.add_vrect(
                x0=float(start),
                x1=float(end),
                fillcolor=color,
                opacity=0.25,
                layer='below',
                line_width=2,
                line_color=color
            )
            midpoint = float(start + (end - start) / 2)
            fig_hist.add_annotation(
                x=midpoint,
                y=1.08,
                xref='x',
                yref='paper',
                text=f"<b>{label}</b>",
                showarrow=False,
                font=dict(color='#1a237e', size=13, family="Arial Black")
            )
        # Agregar líneas verticales en los límites con mejor etiquetado
        for boundary, label, color in [
            (float(q1_rent), f"P25: {q1_rent:.1f}%", '#ff6f00'),
            (float(mediana_rent), f"Mediana: {mediana_rent:.1f}%", '#1976d2'),
            (float(q3_rent), f"P75: {q3_rent:.1f}%", '#388e3c')
        ]:
            fig_hist.add_vline(
                x=boundary,
                line_width=2,
                line_dash='dash',
                line_color=color,
                opacity=0.8
            )
            # Agregar etiqueta de valor en la línea
            max_count = rentabilidad['rentabilidad_pct'].value_counts().max() * 1.1
            fig_hist.add_annotation(
                x=boundary,
                y=max_count,
                text=label,
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=1.5,
                arrowcolor=color,
                ax=0,
                ay=-40,
                font=dict(color=color, size=10)
            )
    render_plotly(fig_hist)

    if not rentabilidad.empty:
        st.markdown(
            f'''
            <div style='background: #fff3e0; border-left: 6px solid #ff9800; padding: 18px; margin: 16px 0; border-radius: 10px;'>
                <h4 style='color: #e65100; margin: 0;'>Variabilidad de rentabilidad</h4>
                <p style='margin: 8px 0 0 0;'>
                    Q1={round(q1_rent, 1)}% | Mediana={round(mediana_rent, 1)}% | Q3={round(q3_rent, 1)}%<br>
                    Los tickets con margen bajo (Q1) requieren revisar promociones y precios; los segmentos con margen alto
                    son candidatos para fidelizacion y ofertas personalizadas.
                </p>
            </div>
            ''',
            unsafe_allow_html=True
        )

    tickets_raw = data['rentabilidad_ticket'].copy()
    tickets_raw = tickets_raw.dropna(subset=['monto_total_ticket'])

    if tickets_raw.empty:
        st.info("No hay informacion de montos para segmentar tickets.")
    else:
        st.markdown("### Distribución de ventas por ticket")

        # Calcular rangos de manera más inteligente
        max_monto = tickets_raw['monto_total_ticket'].max()

        # Usar bins de $5000 para reducir cantidad de rangos
        bin_size = 5000
        max_adjusted = int(np.ceil(max_monto / bin_size) * bin_size)

        # Limitar a máximo 12 bins para mejor visualización
        num_bins = min(12, int(max_adjusted / bin_size))
        bin_edges = list(np.arange(0, (num_bins + 1) * bin_size, bin_size))

        # Si quedan datos fuera, agregar categoría final
        if max_adjusted > num_bins * bin_size:
            bin_edges.append(float('inf'))

        etiqueta_bins = []
        for i in range(len(bin_edges) - 1):
            lower = bin_edges[i]
            upper = bin_edges[i + 1]
            if upper == float('inf'):
                etiqueta_bins.append(f">${lower/1000:.0f}k+")
            else:
                etiqueta_bins.append(f"${lower/1000:.0f}k-${upper/1000:.0f}k")

        tickets_raw['rango_ticket'] = pd.cut(
            tickets_raw['monto_total_ticket'],
            bins=bin_edges,
            labels=etiqueta_bins,
            include_lowest=True,
            right=False
        )

        # Eliminar tickets sin categoría asignada (NaN)
        tickets_raw = tickets_raw.dropna(subset=['rango_ticket'])

        hist_monto = (
            tickets_raw.groupby('rango_ticket', dropna=True, observed=True)
            .agg(
                tickets=('ticket_id', 'count'),
                ventas=('monto_total_ticket', 'sum'),
                margen=('margen_ticket', 'sum')
            )
            .reset_index()
        )

        # Filtrar rangos vacíos
        hist_monto = hist_monto[hist_monto['tickets'] > 0].copy()

        # Asegurar que no hay NaN en los resultados
        hist_monto = hist_monto.dropna()

        # Validar que hay datos suficientes para graficar
        if hist_monto.empty or len(hist_monto) == 0:
            st.info("No hay suficientes datos para mostrar la distribución de ventas por ticket.")
        else:
            total_tickets = hist_monto['tickets'].sum()
            if total_tickets > 0:
                hist_monto['pct_tickets'] = (hist_monto['tickets'] / total_tickets * 100).round(1)
                hist_monto['pct_acumulado'] = hist_monto['pct_tickets'].cumsum()
            else:
                hist_monto['pct_tickets'] = 0
                hist_monto['pct_acumulado'] = 0

            # Crear gráfico con doble eje Y - versión compatible (sin make_subplots)
            # Actualizado: 2025-01-19 para compatibilidad con Streamlit Cloud
            # Crear figura con dos ejes Y usando make_subplots
            from plotly.subplots import make_subplots

            fig_monto = make_subplots(specs=[[{"secondary_y": True}]])

            # Agregar barras (eje Y primario)
            fig_monto.add_trace(
                go.Bar(
                    x=hist_monto['rango_ticket'].astype(str),
                    y=hist_monto['tickets'],
                    marker_color='#1a237e',
                    name='Cantidad de tickets',
                    text=[f"{int(v):,}" for v in hist_monto['tickets']],
                    textposition='outside',
                    textfont=dict(size=10),
                    hovertemplate='<b>%{x}</b><br>Tickets: %{y:,}<extra></extra>',
                    showlegend=True
                ),
                secondary_y=False
            )

            # Agregar línea de % acumulado (eje Y secundario)
            fig_monto.add_trace(
                go.Scatter(
                    x=hist_monto['rango_ticket'].astype(str),
                    y=hist_monto['pct_acumulado'],
                    mode='lines+markers',
                    name='% Acumulado',
                    line=dict(color='#ff7043', width=3),
                    marker=dict(size=8),
                    hovertemplate='<b>%{x}</b><br>Acumulado: %{y:.1f}%<extra></extra>',
                    showlegend=True
                ),
                secondary_y=True
            )

            # Agregar línea de referencia 80% en el eje secundario
            fig_monto.add_hline(
                y=80,
                line_dash="dash",
                line_color="green",
                opacity=0.7,
                secondary_y=True
            )

            # Configurar layout
            fig_monto.update_layout(
                height=500,
                margin=dict(t=50, r=80, l=70, b=120),
                hovermode='x unified',
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1
                )
            )

            # Configurar ejes X y Y primario
            fig_monto.update_xaxes(
                title_text="Rango de venta por ticket",
                tickangle=-45,
                tickfont=dict(size=11)
            )

            # Configurar ejes Y de forma explícita para compatibilidad con Plotly 5.17 en Streamlit Cloud
            fig_monto.update_layout(
                yaxis=dict(
                    title_text="Cantidad de tickets",
                    tickfont=dict(color='#1a237e')
                ),
                yaxis2=dict(
                    title_text="% Acumulado",
                    tickfont=dict(color='#ff7043'),
                    ticksuffix="%",
                    range=[0, 105]
                )
            )

            # Agregar anotación para el 80%
            fig_monto.add_annotation(
                x=len(hist_monto)-1,
                y=80,
                text="80% (Pareto)",
                showarrow=False,
                xanchor='left',
                font=dict(color="green", size=10),
                yref="y2"
            )

            render_plotly(fig_monto)

        st.markdown("### Segmentos por cuartil del ticket")
        q1_monto = float(tickets_raw['monto_total_ticket'].quantile(0.25))
        q2_monto = float(tickets_raw['monto_total_ticket'].quantile(0.5))
        q3_monto = float(tickets_raw['monto_total_ticket'].quantile(0.75))
        segmentos_bins = [-np.inf, q1_monto, q2_monto, q3_monto, np.inf]
        segmentos_labels = ['Bajo', 'Medio', 'Alto', 'Premium']
        tickets_raw['segmento_cuartil'] = pd.cut(
            tickets_raw['monto_total_ticket'],
            bins=segmentos_bins,
            labels=segmentos_labels,
            include_lowest=True
        )
        segmento_order = pd.CategoricalDtype(categories=segmentos_labels, ordered=True)
        tickets_raw['segmento_cuartil'] = tickets_raw['segmento_cuartil'].astype(segmento_order)

        segmentos = (
            tickets_raw.groupby('segmento_cuartil')
            .agg(
                cantidad_tickets=('ticket_id', 'count'),
                ticket_promedio=('monto_total_ticket', 'mean'),
                items_promedio=('items_ticket', 'mean'),
                margen_promedio=('margen_ticket', 'mean'),
                ventas=('monto_total_ticket', 'sum'),
                margen_total=('margen_ticket', 'sum')
            )
            .reset_index()
        )
        total_segmentos = segmentos['cantidad_tickets'].sum()
        segmentos['pct_tickets'] = np.where(
            total_segmentos > 0,
            (segmentos['cantidad_tickets'] / total_segmentos * 100).round(1),
            0
        )

        # Mostrar tabla de segmentos directamente
        tabla_segmentos = segmentos.copy()
        tabla_segmentos['ticket_promedio'] = tabla_segmentos['ticket_promedio'].apply(lambda x: formatear_moneda_argentina(x, 0))
        tabla_segmentos['items_promedio'] = tabla_segmentos['items_promedio'].round(2)
        tabla_segmentos['margen_promedio'] = tabla_segmentos['margen_promedio'].apply(lambda x: formatear_moneda_argentina(x, 0))
        tabla_segmentos['ventas'] = tabla_segmentos['ventas'].apply(lambda x: formatear_moneda_argentina(x, 0))
        tabla_segmentos['margen_total'] = tabla_segmentos['margen_total'].apply(lambda x: formatear_moneda_argentina(x, 0))
        tabla_segmentos['pct_tickets'] = tabla_segmentos['pct_tickets'].astype(str) + '%'
        tabla_segmentos.columns = [
            'Segmento',
            'Cantidad de tickets',
            'Ticket promedio',
            'Items promedio',
            'Margen promedio',
            'Ventas',
            'Margen total',
            '% de tickets'
        ]
        st.dataframe(tabla_segmentos, use_container_width=True, hide_index=True)

        # Calcular estadísticas por segmento para visualización
        st.markdown("### Comparación de métricas por segmento")

        # Usar los valores numéricos originales de segmentos (antes de formatear)
        # segmentos ya tiene los valores numéricos sin formatear

        fig_margen_segmentos = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Ticket Promedio por Segmento', 'Margen Promedio por Segmento'),
            specs=[[{"type": "bar"}, {"type": "bar"}]]
        )

        colores_seg = ['#ef5350', '#42a5f5', '#66bb6a', '#ffa726']

        # Gráfico 1: Ticket promedio
        fig_margen_segmentos.add_trace(
            go.Bar(
                x=segmentos['segmento_cuartil'].astype(str),
                y=segmentos['ticket_promedio'],
                marker_color=colores_seg,
                name='Ticket Promedio',
                text=[formatear_moneda_argentina(v, 0) for v in segmentos['ticket_promedio']],
                textposition='outside',
                textfont=dict(size=11),
                hovertemplate='<b>%{x}</b><br>Ticket: %{text}<extra></extra>',
                showlegend=False
            ),
            row=1, col=1
        )

        # Gráfico 2: Margen promedio
        fig_margen_segmentos.add_trace(
            go.Bar(
                x=segmentos['segmento_cuartil'].astype(str),
                y=segmentos['margen_promedio'],
                marker_color=colores_seg,
                name='Margen Promedio',
                text=[formatear_moneda_argentina(v, 0) for v in segmentos['margen_promedio']],
                textposition='outside',
                textfont=dict(size=11),
                hovertemplate='<b>%{x}</b><br>Margen: %{text}<extra></extra>',
                showlegend=False
            ),
            row=1, col=2
        )

        fig_margen_segmentos.update_xaxes(title_text="Segmento", row=1, col=1)
        fig_margen_segmentos.update_xaxes(title_text="Segmento", row=1, col=2)
        fig_margen_segmentos.update_yaxes(title_text="Monto ($)", row=1, col=1)
        fig_margen_segmentos.update_yaxes(title_text="Monto ($)", row=1, col=2)

        fig_margen_segmentos.update_layout(
            height=450,
            margin=dict(t=80, r=40, l=60, b=60),
            hovermode='x unified'
        )

        render_plotly(fig_margen_segmentos)

        q1_monto_txt = formatear_moneda_argentina(q1_monto, 0)
        q2_monto_txt = formatear_moneda_argentina(q2_monto, 0)
        q3_monto_txt = formatear_moneda_argentina(q3_monto, 0)
        st.markdown(
            f'''
            <div style='background: #ede7f6; border-left: 6px solid #5e35b1; padding: 18px; margin: 16px 0; border-radius: 10px;'>
                <h4 style='color: #4527a0; margin: 0;'>Lectura de segmentos por ticket</h4>
                <p style='margin: 8px 0 0 0;'>
                    <b>Bajo:</b> tickets hasta {q1_monto_txt}<br>
                    <b>Medio:</b> entre {q1_monto_txt} y {q2_monto_txt}<br>
                    <b>Alto:</b> entre {q2_monto_txt} y {q3_monto_txt}<br>
                    <b>Premium:</b> superiores a {q3_monto_txt}<br><br>
                    Usar los segmentos Alto y Premium para programas de fidelizacion y upselling; los segmentos Bajo y Medio son utiles para combos y ofertas de volumen.
                </p>
            </div>
            ''',
            unsafe_allow_html=True
        )

        st.info("No se encontraron datos de rotacion de inventario; dejar placeholder para cruce margen vs rotacion en la siguiente iteracion.")
# =============================================================================
# TAB 5: MEDIOS DE PAGO
# =============================================================================
with tabs[4]:
    st.markdown("## Analisis de medios de pago")

    kpi_pago = data.get('kpi_pago')
    tickets_modular = processed_data.get('tickets_modular')

    if kpi_pago is None or kpi_pago.empty:
        st.info("No hay datos de medios de pago disponibles.")
    else:
        def normalizar_medio(valor: str) -> str:
            texto = str(valor).strip()
            if not texto:
                return 'Efectivo'
            texto = unicodedata.normalize('NFKD', texto)
            texto = ''.join(ch for ch in texto if not unicodedata.combining(ch))
            texto = texto.upper()
            mapping = {
                'EFECTIVO': 'Efectivo',
                'SIN DATO': 'Efectivo',
                'SIN DATOS': 'Efectivo',
                'SIN_IDENTIFICAR': 'Efectivo',
                'SIN IDENTIFICAR': 'Efectivo',
                'TARJETA DE DEBITO': 'Debito',
                'TARJETA DEBITO': 'Debito',
                'DEBITO': 'Debito',
                'TARJETA DE CREDITO': 'Credito',
                'TARJETA CREDITO': 'Credito',
                'CREDITO': 'Credito',
                'BILLETERA VIRTUAL': 'Billetera',
                'BILLETERA VITUAL': 'Billetera',
                'MERCADO PAGO': 'Billetera',
                'MP': 'Billetera'
            }
            return mapping.get(texto, 'Efectivo')

        categorias_pago = ['Efectivo', 'Debito', 'Credito', 'Billetera']
        pago_raw = kpi_pago.copy()
        pago_raw['medio'] = pago_raw['tipo_medio_pago'].apply(normalizar_medio)
        pago_summary = (
            pago_raw.groupby('medio', as_index=False)
            .agg(
                tickets=('tickets', 'sum'),
                ventas=('ventas_totales', 'sum'),
                margen=('margen_total', 'sum')
            )
        )
        pago_summary = pago_summary.set_index('medio').reindex(categorias_pago, fill_value=0).reset_index()

        pago_summary['ticket_promedio'] = np.where(
            pago_summary['tickets'] > 0,
            pago_summary['ventas'] / pago_summary['tickets'],
            0
        )
        total_ventas_pago = pago_summary['ventas'].sum()
        pago_summary['participacion'] = np.where(
            total_ventas_pago > 0,
            (pago_summary['ventas'] / total_ventas_pago * 100).round(1),
            0
        )

        fig_pago = px.bar(
            pago_summary,
            x='medio',
            y='ventas',
            labels={'medio': 'Metodo de pago', 'ventas': 'Ventas ($)'},
            color='medio',
            color_discrete_sequence=['#0d47a1', '#1976d2', '#42a5f5', '#90caf9'],
            title="Ventas acumuladas por metodo de pago",
            text=pago_summary['participacion'].astype(str) + '%'
        )
        fig_pago.update_layout(
            height=420,
            showlegend=False,
            xaxis_title='Metodo de pago',
            yaxis_title='Ventas ($)',
            yaxis_tickprefix='$',
            yaxis_tickformat=',.0f',
            bargap=0.3  # Reducir espacio entre barras (0.15 = 15% de espacio)
        )
        fig_pago.update_traces(textposition='auto', width=0.6)  # Ancho de barras más estrecho
        render_plotly(fig_pago)

        cols = st.columns(len(categorias_pago))
        for col, metodo in zip(cols, categorias_pago):
            fila = pago_summary[pago_summary['medio'] == metodo]
            participacion = float(fila['participacion'].iloc[0]) if not fila.empty else 0.0
            ticket_promedio = float(fila['ticket_promedio'].iloc[0]) if not fila.empty else 0.0
            col.metric(
                f"% {metodo}",
                f"{participacion:.1f}%",
                help=f"Ticket promedio: {formatear_moneda_argentina(ticket_promedio, 0)}"
            )

        pago_summary['modalidad'] = pago_summary['medio'].apply(lambda m: 'Efectivo' if m == 'Efectivo' else 'Digitales')
        resumen_modalidad = (
            pago_summary.groupby('modalidad', as_index=False)
            .agg(
                ventas=('ventas', 'sum'),
                tickets=('tickets', 'sum'),
                margen=('margen', 'sum')
            )
        )
        resumen_modalidad['ticket_promedio'] = np.where(
            resumen_modalidad['tickets'] > 0,
            resumen_modalidad['ventas'] / resumen_modalidad['tickets'],
            0
        )
        total_modalidad = resumen_modalidad['ventas'].sum()
        resumen_modalidad['participacion'] = np.where(
            total_modalidad > 0,
            (resumen_modalidad['ventas'] / total_modalidad * 100).round(1),
            0
        )

        tabla_modalidad = resumen_modalidad.copy()
        tabla_modalidad['ventas'] = tabla_modalidad['ventas'].apply(lambda x: formatear_moneda_argentina(x, 0))
        tabla_modalidad['margen'] = tabla_modalidad['margen'].apply(lambda x: formatear_moneda_argentina(x, 0))
        tabla_modalidad['ticket_promedio'] = tabla_modalidad['ticket_promedio'].apply(lambda x: formatear_moneda_argentina(x, 0))
        tabla_modalidad['participacion'] = tabla_modalidad['participacion'].astype(str) + '%'
        tabla_modalidad.columns = ['Modalidad', 'Ventas', 'Tickets', 'Margen', 'Ticket promedio', '% de ventas']
        st.markdown("### Comparativo Efectivo vs Digitales")
        st.dataframe(tabla_modalidad, use_container_width=True, hide_index=True)

        efectivo_part = float(pago_summary.loc[pago_summary['medio'] == 'Efectivo', 'participacion'].fillna(0).iloc[0])
        debito_part = float(pago_summary.loc[pago_summary['medio'] == 'Debito', 'participacion'].fillna(0).iloc[0])
        credito_part = float(pago_summary.loc[pago_summary['medio'] == 'Credito', 'participacion'].fillna(0).iloc[0])
        billetera_part = float(pago_summary.loc[pago_summary['medio'] == 'Billetera', 'participacion'].fillna(0).iloc[0])
        digital_part = float(resumen_modalidad.loc[resumen_modalidad['modalidad'] == 'Digitales', 'participacion'].fillna(0).iloc[0])


        st.markdown(
            f'''
            <div style='background: #e1f5fe; border-left: 6px solid #039be5; padding: 18px; margin: 16px 0; border-radius: 10px;'>
                <h4 style='color: #0277bd; margin: 0;'>Lecturas clave</h4>
                <p style='margin: 8px 0 0 0;'>
                    Efectivo representa {efectivo_part:.1f}% de las ventas. Los medios digitales abarcan {digital_part:.1f}% (Debito {debito_part:.1f}%, Credito {credito_part:.1f}%, Billetera {billetera_part:.1f}%),
                    por lo que las promos bancarias y billeteras explican buena parte del mix.
                </p>
            </div>
            ''',
            unsafe_allow_html=True
        )
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
        <h4>📦 Estrategia #1: Pack Despensa Mensual - Almacén & Limpieza</h4>
        <p><b>Dato que respalda:</b> Aceite Grisasol, Azúcar Ledesma, Arroz y Campanita están en Top 30 productos más vendidos. Categoría Limpieza genera $665M/año (3ra categoría por ventas)</p>
        <p><b>Acción:</b></p>
        <ul>
            <li>Crear "PACK DESPENSA MENSUAL": Aceite Grisasol 1.5L + Azúcar Ledesma 1kg + Arroz Tío Carlos 1kg + Campanita Papel Higiénico</li>
            <li>Precio pack: 12% descuento vs compra individual</li>
            <li>Display destacado entrada del local con cartel "TODO LO QUE NECESITAS DEL MES"</li>
            <li>Promoción primera quincena de cada mes (cuando cobra la gente)</li>
        </ul>
        <p><b>Meta:</b> Generar compra "ancla" mensual recurrente, aumentar ticket promedio en productos básicos</p>
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
        <p><b>Inversión:</b> $50.000 (reposicionamiento, cartelería)</p>
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

    q1_val = 20.0
    q3_val = 35.0
    if "q1_rent" in locals() and isinstance(q1_rent, (int, float, np.floating)):
        q1_val = float(q1_rent)
    if "q3_rent" in locals() and isinstance(q3_rent, (int, float, np.floating)):
        q3_val = float(q3_rent)

    estrategias_html = estrategias_html.replace(
        "(Q1=20%, Q3=35%)",
        f"(Q1={q1_val:.1f}%, Q3={q3_val:.1f}%)"
    )

    st.markdown(estrategias_html, unsafe_allow_html=True)


# =============================================================================
# TAB 8: INFORME EJECUTIVO
# =============================================================================
with tabs[7]:
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
    # Calcular el porcentaje de ventas respecto al total
    total_ventas_cat = top_categorias['ventas_totales'].sum()
    categorias_texto = ", ".join(
        f"{str(row['categoria']).title()} ({round(row['ventas_totales'] / total_ventas_cat * 100 if total_ventas_cat > 0 else 0, 1)}% de las ventas)"
        for _, row in top_categorias.iterrows()
    )

    pago_mix = (
        data['kpi_pago']
        .groupby('tipo_medio_pago', as_index=False)['ventas_totales']
        .sum()
        .rename(columns={'ventas_totales': 'ventas'})
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
    if kpi_dia is not None and not kpi_dia.empty and 'ventas' in kpi_dia.columns:
        dia_pico = kpi_dia.loc[kpi_dia['ventas'].idxmax()]
        dia_pico_nombre = dia_map.get(str(dia_pico['dia_semana']), str(dia_pico['dia_semana']).lower())
        ventas_dia_pico = formatear_moneda_argentina(dia_pico['ventas'], 0)
    else:
        dia_pico_nombre = 'el período analizado'
        ventas_dia_pico = 'N/A'

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
        <h3 style='margin: 0 0 14px 0; color: #0d47a1;'>Transformando Datos en Estrategias: El Camino de NINO hacia el Crecimiento</h3>
        <p style='margin: 0 0 12px 0;'>
            Con el termometro propio en mano podemos adaptar lo que funciona afuera. Cada insight del dataset activa una palanca concreta.
        </p>
        <ul style='margin: 0; padding-left: 22px; line-height: 1.5;'>
            <li><b>Plan de fin de semana:</b> Los días <b>Lunes</b> son críticos, concentrando el <b>0.7% del total de ventas semanales</b>. La acción es clara: lanzar <b>ofertas y combos financiados</b> durante estos días para maximizar el ticket promedio. El análisis de compra conjunta revela oportunidades para potenciar ventas cruzadas con combos estratégicos.</li>
            <li><b>Curar el mix core:</b> El principio de Pareto es evidente: el 80% de las ventas se concentra en pocas categorías. Nuestras tres principales son <b>Carniceria</b> (19.3%), <b>Almacen</b> (18.4%), <b>Lacteos</b> (8.6%). La estrategia es <b>defender el margen</b> en estas áreas clave, optimizando el surtido y potenciando el cross-merchandising basado en los patrones de compra de nuestros clientes.</li>
            <li><b>Fidelizar bolsillo digital:</b> El mix de pagos muestra una fuerte digitalización: <b>Efectivo</b> (31.3%), <b>Tarjeta De Débito</b> (29.7%), <b>Tarjeta De Crédito</b> (19.8%). Esto confirma la oportunidad de <b>diseñar promociones ancla segmentadas</b>, negociando acuerdos con entidades financieras clave para ofrecer beneficios exclusivos y fidelizar a nuestros clientes más rentables.</li>
            <li><b>Pizarra de seguimiento:</b> La rentabilidad global del <b>27.8%</b> y el margen promedio de <b>$7.469 por ticket</b> definen nuestros umbrales de éxito. Cada nueva iniciativa será medida contra estos indicadores clave para asegurar un impacto positivo y cuantificable en el negocio.</li>
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

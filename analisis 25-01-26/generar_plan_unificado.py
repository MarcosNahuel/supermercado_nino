#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PLAN ESTRATEGICO 2026 - VERSION UNIFICADA (CODEX + V2)
Documento optimizado para impresion PDF

Combina:
- Estructura ejecutiva de CODEX (decisiones, gobernanza, preguntas)
- Graficos embebidos de V2 (Matplotlib PNG base64)
- 21 propuestas completas
- Anexos de evidencia

Autor: Claude Code (Pyme Inside)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import base64
from io import BytesIO
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10
plt.rcParams['figure.dpi'] = 100

COLORS = {
    'primary': '#1E3A5F',
    'secondary': '#d06224',
    'accent': '#2d6f66',
    'success': '#27AE60',
    'warning': '#F39C12',
    'light': '#f7f2ea',
    'dark': '#1f2a2e',
    'muted': '#6b6f6f',
}

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / 'outputs'


def fig_to_base64(fig):
    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', facecolor='white', edgecolor='none', dpi=120)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return f"data:image/png;base64,{img_base64}"


def load_data():
    data = {}
    data['top_ventas'] = pd.read_csv(OUTPUT_DIR / 'top_products_sales.csv')
    data['top_frecuencia'] = pd.read_csv(OUTPUT_DIR / 'top_products_frequency.csv')
    data['combos'] = pd.read_csv(OUTPUT_DIR / 'actionable_combos.csv')
    data['tribus'] = pd.read_csv(OUTPUT_DIR / 'tribes_profile.csv')
    data['kvi'] = pd.read_csv(OUTPUT_DIR / 'kvi_candidates.csv')
    data['quick_wins'] = pd.read_csv(OUTPUT_DIR / 'quick_wins_promociones.csv')
    data['rentabilidad'] = pd.read_csv(BASE_DIR.parent / 'data' / 'raw' / 'RENTABILIDAD.csv')
    return data


# ============== GRAFICOS ==============

def crear_grafico_share_categorias():
    """Grafico pie de share de ventas por categoria"""
    categorias = ['Carniceria 10.5%', 'Almacen', 'Lacteos', 'Limpieza', 'Bebidas', 'Fiambreria', 'Otros']
    valores = [19.6, 17.9, 8.5, 7.9, 7.0, 4.4, 34.7]
    colors = [COLORS['secondary'], COLORS['primary'], COLORS['accent'], COLORS['warning'],
              COLORS['success'], '#8B4513', COLORS['muted']]

    fig, ax = plt.subplots(figsize=(10, 8))
    wedges, texts, autotexts = ax.pie(valores, labels=categorias, autopct='%1.1f%%',
                                       colors=colors, explode=(0.05, 0, 0, 0, 0, 0, 0),
                                       shadow=True, startangle=90)
    ax.set_title('SHARE DE VENTAS POR CATEGORIA\nTotal: $9.564M (Oct 2024 - Oct 2025)',
                 fontsize=14, fontweight='bold', color=COLORS['dark'])
    plt.tight_layout()
    return fig_to_base64(fig)


def crear_grafico_distribucion_ticket():
    """Grafico de barras con percentiles de ticket"""
    percentiles = ['P25', 'P50', 'P75', 'P90', 'P95']
    valores = [7141, 15824, 32963, 61472, 88316]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(percentiles, [v/1000 for v in valores], color=COLORS['primary'], edgecolor='white')

    for bar, val in zip(bars, valores):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'${val:,.0f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax.axhline(y=27.671, color=COLORS['secondary'], linestyle='--', linewidth=2, label='Promedio: $27,671')
    ax.set_ylabel('Ticket (Miles $)', fontweight='bold')
    ax.set_title('DISTRIBUCION DE TICKET POR PERCENTILES\nBase para disenar umbrales y promociones',
                 fontsize=14, fontweight='bold', color=COLORS['dark'])
    ax.legend()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    return fig_to_base64(fig)


def crear_grafico_top_ventas(data):
    df = data['top_ventas'].head(10).copy()
    df['ventas_millones'] = df['ventas_totales'] / 1_000_000
    df = df.sort_values('ventas_millones', ascending=True)

    fig, ax = plt.subplots(figsize=(12, 7))
    bars = ax.barh(df['descripcion'], df['ventas_millones'], color=COLORS['primary'], edgecolor='white')

    for bar, val in zip(bars, df['ventas_millones']):
        ax.text(val + 2, bar.get_y() + bar.get_height()/2, f'${val:.1f}M',
                va='center', fontsize=9, fontweight='bold', color=COLORS['dark'])

    ax.set_xlabel('Ventas (Millones $)', fontweight='bold')
    ax.set_title('TOP 10 PRODUCTOS POR VENTAS\n345,130 tickets analizados | Oct 2024 - Oct 2025',
                 fontsize=14, fontweight='bold', color=COLORS['dark'])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    return fig_to_base64(fig)


def crear_grafico_penetracion(data):
    df = data['top_frecuencia'].head(10).copy()
    df = df.sort_values('penetracion_pct', ascending=True)

    fig, ax = plt.subplots(figsize=(12, 7))
    colors = [COLORS['secondary'] if 'TORTA' in d or 'PAN' in d else COLORS['primary'] for d in df['descripcion']]
    bars = ax.barh(df['descripcion'], df['penetracion_pct'], color=colors, edgecolor='white')

    for bar, val in zip(bars, df['penetracion_pct']):
        ax.text(val + 0.2, bar.get_y() + bar.get_height()/2, f'{val:.1f}%',
                va='center', fontsize=9, fontweight='bold', color=COLORS['dark'])

    ax.set_xlabel('Penetracion (%)', fontweight='bold')
    ax.set_title('TOP 10 PRODUCTOS POR PENETRACION\nPanaderia destacada en naranja (motor de trafico)',
                 fontsize=14, fontweight='bold', color=COLORS['dark'])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    return fig_to_base64(fig)


def crear_grafico_combos(data):
    df = data['combos'].head(8).copy()
    df['combo_label'] = df['antecedents'].str[:25] + ' + ' + df['consequents'].str[:20]
    df = df.sort_values('lift', ascending=True)

    fig, ax = plt.subplots(figsize=(12, 8))
    colors = [COLORS['secondary'] if l > 15 else COLORS['accent'] if l > 10 else COLORS['primary'] for l in df['lift']]
    bars = ax.barh(df['combo_label'], df['lift'], color=colors, edgecolor='white')

    for bar, val in zip(bars, df['lift']):
        ax.text(val + 0.5, bar.get_y() + bar.get_height()/2, f'{val:.1f}x',
                va='center', fontsize=9, fontweight='bold', color=COLORS['dark'])

    ax.axvline(x=10, color=COLORS['warning'], linestyle='--', linewidth=2, alpha=0.7)
    ax.set_xlabel('Lift (veces mas probable que el azar)', fontweight='bold')
    ax.set_title('COMBOS ACCIONABLES - MARKET BASKET ANALYSIS\nNaranja: >15x | Verde: 10-15x | Azul: <10x',
                 fontsize=14, fontweight='bold', color=COLORS['dark'])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    return fig_to_base64(fig)


def crear_grafico_pareto(data):
    df = data['top_ventas'].head(50).copy()
    df['ventas_acum'] = df['ventas_totales'].cumsum()
    total_ventas = df['ventas_totales'].sum()
    df['pct_acum'] = df['ventas_acum'] / total_ventas * 100

    fig, ax1 = plt.subplots(figsize=(14, 7))
    x = range(len(df))
    ax1.bar(x, df['ventas_totales']/1_000_000, color=COLORS['primary'], alpha=0.7)
    ax1.set_xlabel('Productos (ordenados por venta)', fontweight='bold')
    ax1.set_ylabel('Ventas (Millones $)', color=COLORS['primary'], fontweight='bold')

    ax2 = ax1.twinx()
    ax2.plot(x, df['pct_acum'], color=COLORS['secondary'], linewidth=3, marker='o', markersize=4)
    ax2.axhline(y=80, color=COLORS['warning'], linestyle='--', linewidth=2)
    ax2.set_ylabel('% Acumulado', color=COLORS['secondary'], fontweight='bold')
    ax2.set_ylim(0, 105)

    ax1.set_title('ANALISIS PARETO - 14.2% de SKUs = 80% de Ventas\n1,289 de 9,058 SKUs generan el 80% de la facturacion',
                  fontsize=14, fontweight='bold', color=COLORS['dark'])
    plt.tight_layout()
    return fig_to_base64(fig)


def crear_grafico_tribus(data):
    df = data['tribus'].copy()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    colors_pie = [COLORS['primary'], COLORS['secondary'], COLORS['accent']]
    explode = (0.02, 0.1, 0.02)
    ax1.pie(df['pct_tickets'], labels=df['nombre_tribu'], autopct='%1.1f%%',
            colors=colors_pie, explode=explode, shadow=True, startangle=90)
    ax1.set_title('Distribucion de Tickets por Tribu', fontsize=12, fontweight='bold')

    df_sorted = df.sort_values('ticket_medio', ascending=True)
    bars = ax2.barh(df_sorted['nombre_tribu'], df_sorted['ticket_medio']/1000,
                    color=colors_pie, edgecolor='white')
    for bar, val in zip(bars, df_sorted['ticket_medio']/1000):
        ax2.text(val + 0.5, bar.get_y() + bar.get_height()/2, f'${val:.0f}K',
                 va='center', fontsize=10, fontweight='bold')
    ax2.set_xlabel('Ticket Medio (Miles $)', fontweight='bold')
    ax2.set_title('Ticket Medio por Tribu', fontsize=12, fontweight='bold')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    fig.suptitle('SEGMENTACION DE CLIENTES - TRIBUS DE COMPRA\n87.6% Compra Rapida = Oportunidad de +2-4 items',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    return fig_to_base64(fig)


def crear_grafico_objetivos():
    """Grafico de objetivos 90/180 dias"""
    kpis = ['UPT', 'Golosinas\n(penetracion)', 'Bebidas\n(unidades)', 'Elaborados\ncarniceria', 'SKUs C\n(reduccion)']
    base = [10.1, 14.24, 2.96, 9, 5377]
    meta_90 = [10.6, 16.5, 3.10, 12, 5108]
    meta_180 = [10.9, 18.0, 3.25, 15, 4839]

    x = np.arange(len(kpis))
    width = 0.25

    fig, ax = plt.subplots(figsize=(14, 7))

    # Normalizar para comparacion visual
    base_norm = [100] * 5
    meta_90_norm = [(m/b)*100 for m, b in zip(meta_90, base)]
    meta_180_norm = [(m/b)*100 for m, b in zip(meta_180, base)]
    # SKUs C es reduccion, invertir
    meta_90_norm[4] = (base[4]/meta_90[4])*100
    meta_180_norm[4] = (base[4]/meta_180[4])*100

    bars1 = ax.bar(x - width, base_norm, width, label='Linea Base', color=COLORS['muted'])
    bars2 = ax.bar(x, meta_90_norm, width, label='Meta 90 dias', color=COLORS['accent'])
    bars3 = ax.bar(x + width, meta_180_norm, width, label='Meta 180 dias', color=COLORS['secondary'])

    ax.set_ylabel('% vs Linea Base', fontweight='bold')
    ax.set_title('OBJETIVOS 2026 - METAS CUANTIFICADAS\nComparacion vs linea base (100%)',
                 fontsize=14, fontweight='bold', color=COLORS['dark'])
    ax.set_xticks(x)
    ax.set_xticklabels(kpis)
    ax.legend()
    ax.axhline(y=100, color=COLORS['dark'], linestyle='-', linewidth=1, alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    return fig_to_base64(fig)


def crear_grafico_roadmap():
    """Grafico Gantt simplificado del roadmap"""
    fig, ax = plt.subplots(figsize=(14, 8))

    fases = [
        ('Fila Unica + Tunel', 1, 2, COLORS['secondary']),
        ('Rincon Olvido / Bajo $1000', 1, 2, COLORS['secondary']),
        ('Maridaje (3 parejas)', 2, 2, COLORS['secondary']),
        ('Scripting mostradores', 2, 2, COLORS['secondary']),
        ('Elaborados carniceria', 5, 8, COLORS['accent']),
        ('Meal kits (piloto)', 5, 8, COLORS['accent']),
        ('2da unidad al 70%', 5, 8, COLORS['accent']),
        ('Escandallos (top 15)', 5, 8, COLORS['accent']),
        ('Marca propia (10 SKUs)', 13, 8, COLORS['primary']),
        ('Ticket umbral gamificado', 13, 8, COLORS['primary']),
        ('Origen local', 13, 8, COLORS['primary']),
        ('Retail media (piloto)', 15, 6, COLORS['primary']),
    ]

    for i, (tarea, inicio, duracion, color) in enumerate(fases):
        ax.barh(i, duracion, left=inicio, color=color, edgecolor='white', height=0.6)
        ax.text(inicio + duracion/2, i, tarea, va='center', ha='center',
                fontsize=9, fontweight='bold', color='white')

    ax.set_xlabel('Semanas', fontweight='bold')
    ax.set_yticks(range(len(fases)))
    ax.set_yticklabels(['' for _ in fases])
    ax.set_xlim(0, 26)

    # Lineas de fase
    ax.axvline(x=4, color=COLORS['dark'], linestyle=':', alpha=0.5)
    ax.axvline(x=12, color=COLORS['dark'], linestyle=':', alpha=0.5)

    ax.text(2, len(fases)+0.5, 'FASE 1\nGolpe de Efecto', ha='center', fontsize=10, fontweight='bold', color=COLORS['secondary'])
    ax.text(8, len(fases)+0.5, 'FASE 2\nIngenieria de Valor', ha='center', fontsize=10, fontweight='bold', color=COLORS['accent'])
    ax.text(18, len(fases)+0.5, 'FASE 3\nConsolidacion', ha='center', fontsize=10, fontweight='bold', color=COLORS['primary'])

    ax.set_title('ROADMAP DE IMPLEMENTACION - 6 MESES\nPlan escalonado para asegurar ejecucion y medicion',
                 fontsize=14, fontweight='bold', color=COLORS['dark'])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.invert_yaxis()

    plt.tight_layout()
    return fig_to_base64(fig)


def crear_grafico_roi():
    """Grafico de ROI por estrategia"""
    estrategias = ['Combos\nFernet+Coca', 'Marca\nPropia', 'Cross-merch\nLayout', 'Upselling\nCaja', 'Fila Unica\n+Tunel']
    inversion = [150, 500, 80, 120, 300]
    margen_mensual = [27200, 9790, 860, 420, 1500]
    payback = [0.01, 0.05, 0.09, 0.29, 0.20]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    x = np.arange(len(estrategias))
    width = 0.35

    bars1 = ax1.bar(x - width/2, [i/1000 for i in inversion], width, label='Inversion (M$)', color=COLORS['primary'])
    bars2 = ax1.bar(x + width/2, [m/1000 for m in margen_mensual], width, label='Margen Mensual (M$)', color=COLORS['success'])

    ax1.set_ylabel('Miles de Pesos', fontweight='bold')
    ax1.set_title('Inversion vs Margen Incremental Mensual', fontsize=12, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(estrategias, fontsize=8)
    ax1.legend()
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    colors_pb = [COLORS['success'] if p < 0.1 else COLORS['accent'] if p < 0.3 else COLORS['warning'] for p in payback]
    bars3 = ax2.barh(estrategias, payback, color=colors_pb, edgecolor='white')
    for bar, val in zip(bars3, payback):
        ax2.text(val + 0.01, bar.get_y() + bar.get_height()/2, f'{val:.2f} meses',
                va='center', fontsize=9, fontweight='bold')
    ax2.set_xlabel('Payback (meses)', fontweight='bold')
    ax2.set_title('Tiempo de Recuperacion de Inversion', fontsize=12, fontweight='bold')
    ax2.axvline(x=0.1, color=COLORS['dark'], linestyle='--', alpha=0.5)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    fig.suptitle('ANALISIS DE ROI - RETORNO INMEDIATO\nTodas las estrategias con payback < 1 mes',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    return fig_to_base64(fig)


def generar_html(graficos, data):
    """Genera el HTML completo unificado"""

    # Datos para tablas
    top_ventas = data['top_ventas'].head(5)
    top_freq = data['top_frecuencia'].head(5)
    combos = data['combos'].head(8)

    html = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Plan Estrategico 2026 - Evolucion Don Nino (Unificado)</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Inter', sans-serif;
            line-height: 1.6;
            color: #1f2a2e;
            background: #f7f2ea;
        }}
        .container {{ max-width: 1100px; margin: 0 auto; padding: 20px; background: white; }}

        /* PORTADA */
        .cover {{
            background: linear-gradient(135deg, #1E3A5F 0%, #2d6f66 100%);
            color: white;
            padding: 60px 40px;
            text-align: center;
            margin-bottom: 30px;
            border-radius: 8px;
        }}
        .cover h1 {{ font-size: 2.5rem; font-weight: 700; margin-bottom: 10px; }}
        .cover .subtitle {{ font-size: 1.3rem; font-weight: 300; margin-bottom: 20px; opacity: 0.9; }}
        .cover .objetivo {{ font-size: 1rem; background: rgba(255,255,255,0.15); padding: 15px; border-radius: 8px; margin: 20px 0; }}
        .cover .meta {{ font-size: 0.9rem; opacity: 0.8; }}

        /* KPIs HEADER */
        .kpis-header {{
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 15px;
            margin-bottom: 30px;
        }}
        .kpi-card {{
            background: white;
            border: 1px solid rgba(0,0,0,0.08);
            border-radius: 12px;
            padding: 15px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }}
        .kpi-card .value {{ font-size: 1.5rem; font-weight: 700; color: #1E3A5F; }}
        .kpi-card .label {{ font-size: 0.8rem; color: #6b6f6f; }}

        /* SECCIONES */
        .section {{ margin-bottom: 40px; page-break-inside: avoid; }}
        .section-title {{
            font-size: 1.6rem;
            font-weight: 700;
            color: #1E3A5F;
            border-bottom: 3px solid #d06224;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .section-subtitle {{ font-size: 1.2rem; font-weight: 600; color: #2C3E50; margin: 20px 0 15px 0; }}

        /* DECISIONES BOX */
        .decisiones-box {{
            background: linear-gradient(90deg, rgba(208,98,36,0.1) 0%, white 100%);
            border-left: 4px solid #d06224;
            padding: 25px;
            margin: 20px 0;
            border-radius: 0 8px 8px 0;
        }}
        .decisiones-box h3 {{ color: #d06224; margin-bottom: 15px; }}
        .decisiones-box ol {{ margin-left: 20px; }}
        .decisiones-box li {{ margin: 10px 0; }}

        /* TABLAS */
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 0.9rem; }}
        th {{ background: #1E3A5F; color: white; padding: 12px 15px; text-align: left; font-weight: 600; }}
        td {{ padding: 10px 15px; border-bottom: 1px solid #ECF0F1; }}
        tr:nth-child(even) {{ background: #f8f9fa; }}
        tr:hover {{ background: #ECF0F1; }}

        /* GRAFICOS */
        .chart {{ text-align: center; margin: 25px 0; }}
        .chart img {{ max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}

        /* GRID 2 COLUMNAS */
        .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}

        /* PROPUESTAS */
        .propuesta {{
            background: #f8f9fa;
            border-left: 4px solid #1E3A5F;
            padding: 20px;
            margin: 20px 0;
            border-radius: 0 8px 8px 0;
        }}
        .propuesta.estructural {{
            border-left-color: #d06224;
            background: linear-gradient(90deg, rgba(208,98,36,0.05) 0%, #f8f9fa 100%);
        }}
        .propuesta-header {{ display: flex; align-items: center; margin-bottom: 15px; }}
        .propuesta-numero {{
            background: #1E3A5F;
            color: white;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            margin-right: 15px;
            font-size: 0.9rem;
        }}
        .propuesta.estructural .propuesta-numero {{ background: #d06224; }}
        .propuesta-titulo {{ font-size: 1.1rem; font-weight: 600; color: #2C3E50; }}
        .propuesta-eje {{ font-size: 0.75rem; color: #6b6f6f; text-transform: uppercase; letter-spacing: 1px; }}

        /* EVIDENCIA BOX */
        .evidencia {{
            background: #fff2df;
            padding: 15px 20px;
            border-radius: 8px;
            margin: 15px 0;
            font-size: 0.9rem;
        }}
        .evidencia strong {{ color: #d06224; }}

        /* GOBERNANZA */
        .gobernanza {{
            background: linear-gradient(135deg, #2d6f66 0%, #1E3A5F 100%);
            color: white;
            padding: 30px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .gobernanza h3 {{ color: #F39C12; margin-bottom: 15px; }}
        .gobernanza ul {{ margin-left: 20px; }}

        /* PREGUNTAS */
        .preguntas {{
            background: #f0e7d9;
            padding: 25px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .preguntas h3 {{ color: #1E3A5F; margin-bottom: 15px; }}
        .preguntas ol {{ margin-left: 20px; }}
        .preguntas li {{ margin: 8px 0; }}

        /* FOOTER */
        .footer {{
            text-align: center;
            padding: 30px;
            background: #1f2a2e;
            color: white;
            margin-top: 40px;
            border-radius: 8px;
        }}

        /* PRINT */
        .page-break {{ page-break-before: always; }}
        @media print {{
            body {{ background: white; }}
            .container {{ max-width: 100%; padding: 0; }}
            .cover {{ page-break-after: always; }}
            .section {{ page-break-inside: avoid; }}
        }}
    </style>
</head>
<body>
    <div class="container">

        <!-- PORTADA -->
        <div class="cover">
            <div style="font-size: 0.9rem; background: rgba(255,255,255,0.2); display: inline-block; padding: 5px 15px; border-radius: 20px; margin-bottom: 15px;">Plan Estrategico 2026</div>
            <h1>PROYECTO "EVOLUCION DON NINO"</h1>
            <div class="subtitle">Version Unificada - Documento Ejecutivo</div>
            <div class="objetivo">
                <strong>Objetivo 2026:</strong> Maximizacion de Densidad de Ticket (UPT), Blindaje de Margen y Excelencia Operativa<br>
                <strong>Base analitica:</strong> Oct 2024 - Oct 2025 (345,130 tickets) + repositorio de analisis
            </div>
            <hr style="border: 1px solid rgba(255,255,255,0.3); margin: 20px 0;">
            <div class="meta">
                <p><strong>Para:</strong> Directorio / Gerencia General</p>
                <p><strong>Fecha:</strong> Enero 2026</p>
                <p><strong>Elaborado por:</strong> Equipo de Analitica - Pyme Inside</p>
            </div>
        </div>

        <!-- KPIs PRINCIPALES -->
        <div class="kpis-header">
            <div class="kpi-card"><div class="value">345,130</div><div class="label">Tickets analizados</div></div>
            <div class="kpi-card"><div class="value">$27,671</div><div class="label">Ticket promedio</div></div>
            <div class="kpi-card"><div class="value">10.10</div><div class="label">UPT promedio</div></div>
            <div class="kpi-card"><div class="value">7.94</div><div class="label">Productos/ticket</div></div>
            <div class="kpi-card"><div class="value">28.23%</div><div class="label">Margen bruto est.</div></div>
            <div class="kpi-card"><div class="value">$15,824</div><div class="label">Mediana ticket</div></div>
        </div>

        <!-- DECISIONES DIRECTORIO -->
        <div class="section">
            <h2 class="section-title">0. DECISIONES SOLICITADAS AL DIRECTORIO (15 minutos)</h2>
            <div class="decisiones-box">
                <h3>Aprobaciones requeridas para iniciar ejecucion:</h3>
                <ol>
                    <li><strong>Aprobar implementacion de Fila Unica + "Tunel de Tentacion"</strong> (reconfiguracion fisica de cajas + exhibidores)</li>
                    <li><strong>Aprobar politica comercial 2026</strong> (promos, surtido, marca propia tactica) y esquema de gobernanza (Comite Comercial)</li>
                    <li><strong>Aprobar presupuesto inicial de ejecucion</strong> (~$1.15M en senaletica, exhibidores, packaging, capacitacion)</li>
                    <li><strong>Aprobar metas 90/180/365 dias</strong> y responsables por iniciativa (control semanal)</li>
                </ol>
            </div>
        </div>

        <!-- RESUMEN EJECUTIVO -->
        <div class="section">
            <h2 class="section-title">1. RESUMEN EJECUTIVO</h2>

            <div class="gobernanza" style="background: linear-gradient(135deg, #1E3A5F 0%, #2C3E50 100%);">
                <h3>TESIS DEL PLAN EN 30 SEGUNDOS</h3>
                <p>Don Nino tiene una base solida: <strong>345,130 tickets</strong> con ticket promedio de <strong>$27,671</strong>.
                La Panaderia atrae clientes (Tortas x6 en 12.5% de tickets) pero la Carniceria genera ingresos (Molida Especial: $188M).
                El <strong>87.6%</strong> son compras rapidas con ticket bajo.</p>
                <p style="margin-top: 15px;"><strong>Oportunidad:</strong> Cambiar el paradigma de "despachar mercaderia" a "gestionar experiencia + margen".
                Elevar UPT de 10.1 a 10.9 (+8%) y capturar impulso con Fila Unica + Tunel de Tentacion.</p>
            </div>

            <h3 class="section-subtitle">Linea Base (KPIs actuales)</h3>
            <div class="grid-2">
                <table>
                    <tr><th>KPI</th><th>Valor</th></tr>
                    <tr><td>Tickets analizados</td><td>345,130</td></tr>
                    <tr><td>Ticket promedio ($)</td><td>27,671</td></tr>
                    <tr><td>Unidades por ticket (UPT)</td><td>10.10</td></tr>
                    <tr><td>Productos unicos por ticket</td><td>7.94</td></tr>
                    <tr><td>Margen bruto estimado (%)</td><td>28.23%</td></tr>
                </table>
                <table>
                    <tr><th>Percentil</th><th>Ticket ($)</th></tr>
                    <tr><td>P25</td><td>7,141</td></tr>
                    <tr><td>P50 (mediana)</td><td>15,824</td></tr>
                    <tr><td>P75</td><td>32,963</td></tr>
                    <tr><td>P90</td><td>61,472</td></tr>
                    <tr><td>P95</td><td>88,316</td></tr>
                </table>
            </div>

            <div class="evidencia">
                <strong>Notas de calidad de datos:</strong> El dataset incluye anulaciones/devoluciones. Para KPIs operativos, tomar tickets con ventas > 0.
                Datos horarios no son confiables; se propone muestreo manual 2 semanas + ajuste de captura POS.
            </div>
        </div>

        <div class="page-break"></div>

        <!-- DIAGNOSTICO -->
        <div class="section">
            <h2 class="section-title">2. DIAGNOSTICO: OPORTUNIDAD LATENTE</h2>

            <h3 class="section-subtitle">2.1 Trafico vs Margen</h3>
            <div class="grid-2">
                <div class="chart"><img src="{graficos['share_cat']}" alt="Share Categorias"></div>
                <div>
                    <ul>
                        <li><strong>Carniceria</strong> concentra facturacion: 19.6% de ventas totales</li>
                        <li><strong>Panaderia</strong> es "motor de tickets": ~51% de tickets llevan panificados</li>
                        <li><strong>Golosinas</strong> tiene baja participacion (1.5%) pero alta rentabilidad (~45%)</li>
                    </ul>
                    <table style="margin-top: 15px;">
                        <tr><th>Categoria</th><th>Share</th><th>Margen%</th><th>Ventas (M$)</th></tr>
                        <tr><td>CARNICERIA 10.5%</td><td>19.6%</td><td>20%</td><td>1,876</td></tr>
                        <tr><td>ALMACEN</td><td>17.9%</td><td>28%</td><td>1,713</td></tr>
                        <tr><td>LACTEOS</td><td>8.5%</td><td>30%</td><td>810</td></tr>
                        <tr><td>FIAMBRERIA</td><td>4.4%</td><td>45%</td><td>424</td></tr>
                    </table>
                </div>
            </div>

            <h3 class="section-subtitle">Top Productos: Ventas vs Penetracion</h3>
            <div class="grid-2">
                <div class="chart"><img src="{graficos['top_ventas']}" alt="Top Ventas"></div>
                <div class="chart"><img src="{graficos['penetracion']}" alt="Penetracion"></div>
            </div>
            <div class="evidencia">
                <strong>Insight:</strong> Carniceria domina en ventas ($188M Molida Especial) pero Panaderia domina en penetracion (Tortas 12.5%). Oportunidad de cross-sell entre categorias.
            </div>

            <h3 class="section-subtitle">2.2 Potencial de Venta Cruzada (Market Basket)</h3>
            <div class="chart"><img src="{graficos['combos']}" alt="Combos"></div>
            <table>
                <tr><th>Antecedente</th><th>Consecuente</th><th>Lift</th><th>Soporte</th><th>Confianza</th></tr>
                <tr style="background: rgba(208,98,36,0.1);"><td>FERNET BRANCA X 750 CC</td><td>COCA COLA PET X2.5LT</td><td><strong>28.3x</strong></td><td>1.02%</td><td>76.4%</td></tr>
                <tr><td>COSTILLA + CHORIZO</td><td>MORCILLA VALENCIANA</td><td><strong>15.4x</strong></td><td>0.77%</td><td>62.3%</td></tr>
                <tr><td>ILOLAY QUESO BARRA</td><td>PALADINI JAMON COCIDO</td><td><strong>5.3x</strong></td><td>1.62%</td><td>35.9%</td></tr>
            </table>

            <h3 class="section-subtitle">2.3 Concentracion Pareto</h3>
            <div class="chart"><img src="{graficos['pareto']}" alt="Pareto"></div>
            <div class="evidencia">
                <strong>Hallazgo clave:</strong> 14.2% de SKUs (1,289 de 9,058) explican el 80% de las ventas.
                El 50% de SKUs de menor venta explica apenas 3% de facturacion.
                Esto habilita <strong>racionalizacion de surtido</strong> para liberar capital.
            </div>

            <h3 class="section-subtitle">2.4 Segmentacion de Clientes (Tribus)</h3>
            <div class="chart"><img src="{graficos['tribus']}" alt="Tribus"></div>
            <table>
                <tr><th>Tribu</th><th>% Tickets</th><th>Ticket Medio</th><th>UPT</th><th>Implicancia</th></tr>
                <tr><td>Compra Rapida/Conveniencia</td><td>87.6%</td><td>$17,974</td><td>6.6</td><td>Foco de aumento UPT (+2-4 items)</td></tr>
                <tr><td>Reposicion Regular</td><td>12.4%</td><td>$94,642</td><td>34.5</td><td>Foco de bundles/meal kits</td></tr>
            </table>
        </div>

        <div class="page-break"></div>

        <!-- OBJETIVOS 2026 -->
        <div class="section">
            <h2 class="section-title">3. OBJETIVOS 2026 (Metas Cuantificadas)</h2>
            <div class="chart"><img src="{graficos['objetivos']}" alt="Objetivos"></div>
            <table>
                <tr><th>Objetivo</th><th>Linea Base</th><th>Meta 90 dias</th><th>Meta 180 dias</th></tr>
                <tr><td>Densidad (UPT)</td><td>10.10</td><td>10.6</td><td>10.9</td></tr>
                <tr><td>Penetracion GOLOSINAS (% tickets)</td><td>14.24%</td><td>16.5%</td><td>18.0%</td></tr>
                <tr><td>Unidades BEBIDAS por ticket</td><td>2.96</td><td>3.10</td><td>3.25</td></tr>
                <tr><td>% tickets con >=4 BEBIDAS</td><td>8.04%</td><td>9.0%</td><td>10.0%</td></tr>
                <tr><td>Mix elaborados carniceria</td><td>~9%</td><td>12%</td><td>15%</td></tr>
                <tr><td>Merma panaderia/rotiseria</td><td>a medir</td><td>-10%</td><td>-20%</td></tr>
                <tr><td>SKUs "C" (cola larga)</td><td>5,377</td><td>-5%</td><td>-10%</td></tr>
            </table>
        </div>

        <!-- PROPUESTAS -->
        <div class="section">
            <h2 class="section-title">4. NUCLEO ESTRATEGICO: 21 PROPUESTAS DE VALOR</h2>

            <h3 class="section-subtitle">Matriz de Priorizacion</h3>
            <table>
                <tr><th>#</th><th>Iniciativa</th><th>Eje</th><th>Impacto</th><th>Esfuerzo</th><th>Horizonte</th></tr>
                <tr style="background: rgba(208,98,36,0.1);"><td>21</td><td><strong>Fila Unica + Tunel Tentacion</strong></td><td>C</td><td>Alto</td><td>Medio</td><td>2-4 sem</td></tr>
                <tr><td>1</td><td>Maridaje en gondola</td><td>A</td><td>Alto</td><td>Bajo</td><td>2-4 sem</td></tr>
                <tr><td>2</td><td>Packs "Solucion de Cena"</td><td>A</td><td>Medio/Alto</td><td>Medio</td><td>4-8 sem</td></tr>
                <tr><td>3</td><td>2da unidad al 70%</td><td>A</td><td>Medio</td><td>Bajo</td><td>2-4 sem</td></tr>
                <tr><td>11</td><td>Carniceria "Listos para cocinar"</td><td>B</td><td>Alto</td><td>Medio</td><td>6-12 sem</td></tr>
                <tr><td>12</td><td>Auditoria recetas (escandallos)</td><td>B</td><td>Alto</td><td>Medio/Alto</td><td>6-12 sem</td></tr>
                <tr><td>13</td><td>Marca propia tactica</td><td>B</td><td>Alto</td><td>Medio</td><td>8-16 sem</td></tr>
            </table>
            <p style="font-size: 0.85rem; color: #6b6f6f; margin-top: 10px;">Ejes: A = Aumento de Volumen | B = Maximizacion de Margen | C = Excelencia Operativa</p>
        </div>

        <div class="page-break"></div>

        <!-- EJE C: FILA UNICA (PROPUESTA ESTRUCTURAL) -->
        <div class="section">
            <h2 class="section-title">PROPUESTA ESTRUCTURAL: FILA UNICA + TUNEL DE TENTACION</h2>

            <div class="propuesta estructural">
                <div class="propuesta-header">
                    <div class="propuesta-numero">21</div>
                    <div>
                        <div class="propuesta-eje">EJE C: Excelencia Operativa</div>
                        <div class="propuesta-titulo">Sistema de Fila Unica ("Snake Queue") + Tunel de Tentacion</div>
                    </div>
                </div>

                <p><strong>Diagnostico:</strong> Filas multiples generan tiempos muertos, puntos ciegos de seguridad y menor exposicion a impulso.</p>
                <p><strong>Solucion:</strong> Unificar espera en un solo pasillo serpenteante delimitado por gondolas bajas que deriva al proximo cajero libre.</p>

                <h4 style="margin-top: 20px;">Impacto Triple (con numeros base):</h4>
                <table>
                    <tr><th>Dimension</th><th>Situacion Actual</th><th>Impacto Esperado</th></tr>
                    <tr><td><strong>1. Ventas (efecto tunel)</strong></td><td>GOLOSINAS en 14.24% tickets, ~$9.65M/mes</td><td>Uplift 25-40% = +$2.4M a $3.9M/mes</td></tr>
                    <tr><td><strong>2. Seguridad (panoptico)</strong></td><td>Multiples puntos de salida</td><td>Punto unico de control visual</td></tr>
                    <tr><td><strong>3. Experiencia (FIFO)</strong></td><td>Ansiedad por "elegir fila"</td><td>Percepcion de justicia</td></tr>
                </table>

                <h4 style="margin-top: 20px;">Planograma del Tunel:</h4>
                <table>
                    <tr><th>Zona</th><th>Categorias</th><th>Productos Ejemplo</th></tr>
                    <tr><td>Inicio (espera)</td><td>GOLOSINAS</td><td>Turrones, alfajores, chocolates</td></tr>
                    <tr><td>Medio</td><td>Olvidables</td><td>Bolsas, fosforos, pilas, encendedor</td></tr>
                    <tr><td>Final (caja)</td><td>Bajo desembolso</td><td>Chicles, caramelos, panuelos</td></tr>
                </table>

                <div class="evidencia" style="margin-top: 15px;">
                    <strong>KPIs de control:</strong> % tickets con producto del tunel | Ventas GOLOSINAS before/after | Tiempo de espera (muestreo)
                </div>
            </div>
        </div>

        <!-- EJE A: VOLUMEN -->
        <div class="section">
            <h2 class="section-title">EJE A: AUMENTO DE VOLUMEN (Cross-selling + Ticket)</h2>
            <p><em>Objetivo: que el cliente que viene por el pan o "compra rapida" se lleve 2-4 items adicionales.</em></p>

            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">1</div>
                    <div>
                        <div class="propuesta-eje">EJE A: Aumento de Volumen</div>
                        <div class="propuesta-titulo">Maridaje en Gondola (Cross-Merchandising)</div>
                    </div>
                </div>
                <p><strong>Que es:</strong> Romper la logica "por pasillo" y armar micro-misiones de compra (asado, picada, fernet, desayuno).</p>
                <p><strong>Dato clave:</strong> Existen lifts de 5x a 28x en productos complementarios.</p>
                <table>
                    <tr><th>Pareja/Combo</th><th>Lift</th><th>Accion</th></tr>
                    <tr><td>FERNET BRANCA + COCA COLA 2.5L</td><td>28.3x</td><td>Isla conjunta + cartel</td></tr>
                    <tr><td>COSTILLA + CHORIZO + MORCILLA</td><td>15.4x</td><td>Cabecera "Asado Completo"</td></tr>
                    <tr><td>JAMON COCIDO + QUESO BARRA</td><td>5.3x</td><td>Exhibidor "Picada Lista"</td></tr>
                </table>
                <div class="evidencia"><strong>KPI:</strong> % tickets con pareja/triada | Margen incremental semanal</div>
            </div>

            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">2</div>
                    <div>
                        <div class="propuesta-eje">EJE A: Aumento de Volumen</div>
                        <div class="propuesta-titulo">Packs "Solucion de Cena" (Meal Kits)</div>
                    </div>
                </div>
                <p><strong>Que es:</strong> Agrupar fisicamente ingredientes para resolver una ocasion (cena rapida) con precio unico y receta.</p>
                <table>
                    <tr><th>Kit</th><th>Componentes</th><th>Precio Est.</th><th>Objetivo</th></tr>
                    <tr><td>Pasta Express</td><td>Fideos + Pure tomate + Queso rallado</td><td>$7,576</td><td>Subir UPT compra rapida</td></tr>
                    <tr><td>Milanesa + Pure</td><td>Milanesas pollo + Pure papas + Aceite</td><td>$14,035</td><td>Migrar a "cena"</td></tr>
                    <tr><td>Picada Mendocina</td><td>Salame + Mortadela + Queso</td><td>$37,020</td><td>Aumentar ticket</td></tr>
                </table>
                <div class="evidencia"><strong>KPI:</strong> tickets con kit/semana | UPT promedio de esos tickets</div>
            </div>

            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">3</div>
                    <div>
                        <div class="propuesta-eje">EJE A: Aumento de Volumen</div>
                        <div class="propuesta-titulo">Estrategia "2da Unidad al 70%"</div>
                    </div>
                </div>
                <p><strong>Objetivo:</strong> Aumentar unidades por compra sin destruir margen como ocurre con 2x1 masivo.</p>
                <table>
                    <tr><th>SKU Candidato</th><th>Categoria</th><th>Tickets</th><th>Precio</th></tr>
                    <tr><td>COCA COLA PET X2.5LT</td><td>BEBIDAS</td><td>6,031</td><td>$3,990</td></tr>
                    <tr><td>ARCOR PURE TOMATE 520g</td><td>ALMACEN</td><td>7,833</td><td>$785</td></tr>
                    <tr><td>SALCHICHAS PANCHIN X6</td><td>FIAMBRERIA</td><td>6,111</td><td>$825</td></tr>
                </table>
            </div>

            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">4</div>
                    <div>
                        <div class="propuesta-eje">EJE A: Aumento de Volumen</div>
                        <div class="propuesta-titulo">Venta Sugestiva (Scripting en Mostradores)</div>
                    </div>
                </div>
                <table>
                    <tr><th>Mostrador</th><th>Script de Cierre</th><th>Upsell</th></tr>
                    <tr><td>Carniceria</td><td>"Le agrego chorizo/morcilla para completar el asado?"</td><td>CHORIZO / MORCILLA</td></tr>
                    <tr><td>Fiambreria</td><td>"Lo acompanamos con queso en oferta?"</td><td>ILOLAY QUESO BARRA</td></tr>
                    <tr><td>Panaderia</td><td>"Sumamos tortitas para la merienda?"</td><td>TORTAS X 6U.</td></tr>
                </table>
            </div>

            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">5</div>
                    <div>
                        <div class="propuesta-eje">EJE A: Aumento de Volumen</div>
                        <div class="propuesta-titulo">El "Rincon del Olvido"</div>
                    </div>
                </div>
                <p>Exhibidor vertical a la salida con productos "olvidables" de alta recurrencia.</p>
                <table>
                    <tr><th>Producto</th><th>Tickets</th><th>Precio</th><th>Nota</th></tr>
                    <tr><td>BOLSAS PLASTICAS NINO</td><td>16,494</td><td>$100</td><td>Top frecuencia</td></tr>
                    <tr><td>FOSFOROS RODEO X 220</td><td>2,705</td><td>$520</td><td>Asado/hogar</td></tr>
                    <tr><td>DURACELL PILAS AAA X2</td><td>513</td><td>$2,950</td><td>Alto margen</td></tr>
                </table>
            </div>

            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">6</div>
                    <div>
                        <div class="propuesta-eje">EJE A: Aumento de Volumen</div>
                        <div class="propuesta-titulo">Degustacion Cruzada "In Situ"</div>
                    </div>
                </div>
                <p>Degustacion cruzada viernes/sabado: fiambres sobre pan (vehiculo alto trafico) para empujar productos de margen.</p>
                <div class="evidencia"><strong>Dato:</strong> Panificados aparecen en ~51% de tickets. <strong>Meta:</strong> +15% ventas SKU degustado en 60 dias.</div>
            </div>

            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">7</div>
                    <div>
                        <div class="propuesta-eje">EJE A: Aumento de Volumen</div>
                        <div class="propuesta-titulo">Ticket Umbral Gamificado</div>
                    </div>
                </div>
                <p>Incentivo para superar umbral de ticket. Hoy 11.4% tickets estan entre $30k-$45k (tramo convertible).</p>
                <p><strong>Diseno:</strong> Umbral $45,000 = 1/2 docena facturas gratis. <strong>Meta:</strong> % tickets >= $45k de 16.5% a 18%.</p>
            </div>

            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">8</div>
                    <div>
                        <div class="propuesta-eje">EJE A: Aumento de Volumen</div>
                        <div class="propuesta-titulo">Multipacks de Bebidas</div>
                    </div>
                </div>
                <p>Pasar de venta unitaria a packs 4/6 unidades. Hoy solo 8.04% de tickets tiene >=4 unidades BEBIDAS.</p>
            </div>

            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">9</div>
                    <div>
                        <div class="propuesta-eje">EJE A: Aumento de Volumen</div>
                        <div class="propuesta-titulo">Seccion "Bajo $1,000"</div>
                    </div>
                </div>
                <table>
                    <tr><th>Producto</th><th>Tickets</th><th>Precio</th></tr>
                    <tr><td>TURRON ARCOR 3X25 GR</td><td>6,288</td><td>$800</td></tr>
                    <tr><td>ARCOR PURE TOMATE 520g</td><td>7,833</td><td>$785</td></tr>
                    <tr><td>CALSA LEVADURA 50g</td><td>6,248</td><td>$620</td></tr>
                </table>
            </div>

            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">10</div>
                    <div>
                        <div class="propuesta-eje">EJE A: Aumento de Volumen</div>
                        <div class="propuesta-titulo">Retail Media / Alquiler de Cabeceras</div>
                    </div>
                </div>
                <p>Monetizar espacios preferenciales cobrando a proveedores por visibilidad.</p>
                <table>
                    <tr><th>Activo</th><th>Precio/semana</th><th>Incluye</th></tr>
                    <tr><td>Cabecera Premium</td><td>$120,000</td><td>Cartel + foto ejecucion</td></tr>
                    <tr><td>Tunel Tentacion</td><td>$150,000 (2 sem)</td><td>2 SKUs + facing</td></tr>
                    <tr><td>Degustacion</td><td>$100,000 (finde)</td><td>Mesa + personal</td></tr>
                </table>
            </div>
        </div>

        <div class="page-break"></div>

        <!-- EJE B: MARGEN -->
        <div class="section">
            <h2 class="section-title">EJE B: MAXIMIZACION DE MARGEN</h2>
            <p><em>Objetivo: mejorar mezcla hacia productos mas rentables y evitar "margen ciego".</em></p>

            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">11</div>
                    <div>
                        <div class="propuesta-eje">EJE B: Maximizacion de Margen</div>
                        <div class="propuesta-titulo">Transformacion de Carniceria (Valor Agregado)</div>
                    </div>
                </div>
                <p>Pasar de commodity a soluciones "listas para cocinar" (milanesas, brochettes, arrollados).</p>
                <table>
                    <tr><th>Producto</th><th>Situacion</th><th>Ventas (M$)</th></tr>
                    <tr><td>MILANESAS DE POLLO NINO</td><td>Alta venta - estandarizar</td><td>94.5</td></tr>
                    <tr><td>MILANESAS DE CARNE NINO</td><td>Alta venta - estandarizar</td><td>71.6</td></tr>
                    <tr><td>Brochettes (pollo/carne)</td><td>A crear</td><td>-</td></tr>
                </table>
                <div class="evidencia"><strong>Meta:</strong> Mix elaborados sobre carniceria de ~9% a 15% en 180 dias.</div>
            </div>

            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">12</div>
                    <div>
                        <div class="propuesta-eje">EJE B: Maximizacion de Margen</div>
                        <div class="propuesta-titulo">Auditoria de Recetas (Escandallos)</div>
                    </div>
                </div>
                <p>Recetas estandar valorizadas para controlar costo oculto por sobre-uso de insumos caros.</p>
                <div class="evidencia"><strong>Meta:</strong> 80% de top 15 recetas con escandallo en 90 dias. Desvio costo real vs estandar < 5%.</div>
            </div>

            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">13</div>
                    <div>
                        <div class="propuesta-eje">EJE B: Maximizacion de Margen</div>
                        <div class="propuesta-titulo">Marca Propia "Tactica" (Don Nino)</div>
                    </div>
                </div>
                <table>
                    <tr><th>SKU Marca Propia</th><th>Formato</th><th>Objetivo</th></tr>
                    <tr><td>Pan rallado Don Nino</td><td>500g</td><td>Margen alto + rotacion</td></tr>
                    <tr><td>Lentejas/Garbanzos Don Nino</td><td>500g</td><td>Commodity, buen margen</td></tr>
                    <tr><td>Oregano/Aji/Pimenton Don Nino</td><td>50g</td><td>Margen alto</td></tr>
                    <tr><td>Mix "condimento asado"</td><td>80g</td><td>Cross-sell carniceria</td></tr>
                </table>
                <div class="evidencia"><strong>Modelo:</strong> Margen incremental estimado ~$9.79M/mes con inversion $500k (payback < 1 mes).</div>
            </div>

            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">14</div>
                    <div>
                        <div class="propuesta-eje">EJE B: Maximizacion de Margen</div>
                        <div class="propuesta-titulo">Precio Ancla (Decoy Pricing) en Vinos</div>
                    </div>
                </div>
                <table>
                    <tr><th>Rol</th><th>SKU Ejemplo</th><th>Precio</th></tr>
                    <tr><td>Entrada</td><td>VINO TERNUVA TINTO 1 LT</td><td>$1,400</td></tr>
                    <tr><td>Medio (target)</td><td>VINO NAMPE MALBEC 750</td><td>$2,810</td></tr>
                    <tr><td>Premium</td><td>SANTA JULIA CHENIN 750</td><td>$4,900</td></tr>
                    <tr><td>Ancla</td><td>NORTON DOC MALBEC 750</td><td>$8,400</td></tr>
                </table>
            </div>

            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">15</div>
                    <div>
                        <div class="propuesta-eje">EJE B: Maximizacion de Margen</div>
                        <div class="propuesta-titulo">Venta Fraccionada de Lujos</div>
                    </div>
                </div>
                <p>Bajar "ticket facial" de productos premium vendiendo bandejas de 80g.</p>
                <table>
                    <tr><th>Producto</th><th>Precio/kg</th><th>Bandeja 80g</th></tr>
                    <tr><td>JAMON CRUDO LA MUNDIAL</td><td>$19,865</td><td>$1,589</td></tr>
                    <tr><td>FOX JAMON CRUDO PARMA</td><td>$41,700</td><td>$3,336</td></tr>
                    <tr><td>RICOLAC REGGIANITO</td><td>$17,530</td><td>$1,402</td></tr>
                </table>
            </div>

            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">16</div>
                    <div>
                        <div class="propuesta-eje">EJE B: Maximizacion de Margen</div>
                        <div class="propuesta-titulo">Happy Hour en Panaderia</div>
                    </div>
                </div>
                <p>Descuento controlado 30-40% en facturas/panificados 30-45 min antes del cierre para convertir merma en recuperacion.</p>
            </div>

            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">17</div>
                    <div>
                        <div class="propuesta-eje">EJE B: Maximizacion de Margen</div>
                        <div class="propuesta-titulo">Monetizacion de la "Cola Larga" (Bazar)</div>
                    </div>
                </div>
                <p>Ajustar margen en articulos donde el cliente no compara (utilitarios, descartables). BAZAR tiene margen ~45%.</p>
            </div>

            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">18</div>
                    <div>
                        <div class="propuesta-eje">EJE B: Maximizacion de Margen</div>
                        <div class="propuesta-titulo">Diferenciacion "Origen Local"</div>
                    </div>
                </div>
                <p>Gondola "Hecho en Mendoza" con vinos, aceites, conservas locales. Storytelling de proveedores para sostener precio premium.</p>
            </div>

            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">19</div>
                    <div>
                        <div class="propuesta-eje">EJE B: Maximizacion de Margen</div>
                        <div class="propuesta-titulo">Eliminacion de Competencia Interna (Racionalizacion)</div>
                    </div>
                </div>
                <table>
                    <tr><th>Segmento Pareto</th><th># SKUs</th><th>Share Ventas</th><th>Accion</th></tr>
                    <tr><td>A</td><td>1,288</td><td>80%</td><td>Proteger (nunca quiebre)</td></tr>
                    <tr><td>B</td><td>2,393</td><td>15%</td><td>Reducir duplicados</td></tr>
                    <tr><td>C</td><td>5,377</td><td>5%</td><td>Liquidar/eliminar</td></tr>
                </table>
            </div>

            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">20</div>
                    <div>
                        <div class="propuesta-eje">EJE B: Maximizacion de Margen</div>
                        <div class="propuesta-titulo">Venta de Servicios (Margen 100%)</div>
                    </div>
                </div>
                <table>
                    <tr><th>Servicio</th><th>Precio</th><th>Operacion</th></tr>
                    <tr><td>Afilado de cuchillos</td><td>$2,500/unidad</td><td>Tercerizado 1 dia/semana</td></tr>
                    <tr><td>Armado de picadas</td><td>Fee $1,500</td><td>In-house</td></tr>
                    <tr><td>Hielo "evento"</td><td>+15% vs estandar</td><td>Compra y reventa</td></tr>
                </table>
            </div>
        </div>

        <div class="page-break"></div>

        <!-- ROADMAP -->
        <div class="section">
            <h2 class="section-title">5. ROADMAP DE IMPLEMENTACION (6 Meses)</h2>
            <div class="chart"><img src="{graficos['roadmap']}" alt="Roadmap"></div>

            <div class="grid-2">
                <div>
                    <h4 style="color: #d06224;">FASE 1: Golpe de Efecto (Mes 1)</h4>
                    <ul>
                        <li>Montaje Fila Unica + Tunel Tentacion</li>
                        <li>Rincon del Olvido + Bajo $1000</li>
                        <li>Maridaje (3 parejas) + carteleria</li>
                        <li>Capacitacion Venta Sugestiva</li>
                    </ul>
                </div>
                <div>
                    <h4 style="color: #2d6f66;">FASE 2: Ingenieria de Valor (Meses 2-3)</h4>
                    <ul>
                        <li>Elaborados de Carniceria (8-12 SKUs)</li>
                        <li>Meal Kits (3 kits piloto)</li>
                        <li>2da unidad al 70% (10 SKUs)</li>
                        <li>Escandallos (top 15 recetas)</li>
                    </ul>
                </div>
            </div>
            <div>
                <h4 style="color: #1E3A5F;">FASE 3: Consolidacion (Meses 4-6)</h4>
                <ul>
                    <li>Marca Propia Tactica (10 SKUs)</li>
                    <li>Ticket Umbral Gamificado + calendario mensual</li>
                    <li>Origen Local (gondola + activaciones)</li>
                    <li>Retail Media (cabeceras + tunel)</li>
                </ul>
            </div>
        </div>

        <!-- ROI -->
        <div class="section">
            <h2 class="section-title">6. ANALISIS DE INVERSION Y RETORNO</h2>
            <div class="chart"><img src="{graficos['roi']}" alt="ROI"></div>

            <table>
                <tr><th>Estrategia</th><th>Inversion</th><th>Margen Mensual</th><th>Payback</th></tr>
                <tr style="background: rgba(39,174,96,0.1);"><td>Combos focalizados (Fernet+Coca)</td><td>$150,000</td><td>$27.2M</td><td><strong>0.01 meses</strong></td></tr>
                <tr style="background: rgba(39,174,96,0.1);"><td>Marca propia categorias A</td><td>$500,000</td><td>$9.79M</td><td><strong>0.05 meses</strong></td></tr>
                <tr><td>Cross-merchandising layout</td><td>$80,000</td><td>$860K</td><td>0.09 meses</td></tr>
                <tr><td>Fila Unica + Tunel</td><td>$300,000</td><td>$1.5M</td><td>0.20 meses</td></tr>
                <tr><td>Upselling en caja</td><td>$120,000</td><td>$420K</td><td>0.29 meses</td></tr>
            </table>

            <div class="evidencia" style="margin-top: 20px;">
                <strong>Inversion total estimada:</strong> $1,150,000 (unica vez)<br>
                <strong>Margen incremental mensual:</strong> ~$40M<br>
                <strong>Payback promedio:</strong> < 1 mes
            </div>
        </div>

        <!-- GOBERNANZA -->
        <div class="section">
            <h2 class="section-title">7. GOBERNANZA Y CONTROL</h2>

            <div class="gobernanza">
                <h3>COMITE COMERCIAL SEMANAL</h3>
                <p><strong>Rutina:</strong></p>
                <ul>
                    <li><strong>Lunes:</strong> Comite (30-45 min), revisar KPIs y decidir 2 acciones de la semana</li>
                    <li><strong>Viernes:</strong> Control de ejecucion (foto + checklist por sector)</li>
                </ul>
                <p style="margin-top: 15px;"><strong>KPIs de control minimos:</strong></p>
                <ol>
                    <li>UPT semanal (densidad de ticket)</li>
                    <li>Conversion de impulso: % tickets con GOLOSINAS y tunel</li>
                    <li>Mix carniceria: % elaborados vs cortes tradicionales</li>
                    <li>Merma recuperada: $ recuperados por Happy Hour</li>
                    <li>Surtido: SKUs A sin quiebre + reduccion SKUs C</li>
                </ol>
            </div>

            <h3 class="section-subtitle">Roles Sugeridos</h3>
            <table>
                <tr><th>Rol</th><th>Responsable</th><th>Ambito</th></tr>
                <tr><td>Sponsor</td><td>Directorio / Gerencia General</td><td>Aprobaciones estrategicas</td></tr>
                <tr><td>Dueno comercial</td><td>Gerente de Local</td><td>P&L diario</td></tr>
                <tr><td>Compras/Precios</td><td>Responsable Compras</td><td>KVIs, promo, surtido</td></tr>
                <tr><td>Operaciones</td><td>Jefe de Sala</td><td>Planogramas, exhibicion</td></tr>
                <tr><td>Produccion</td><td>Jefes Carniceria/Panaderia</td><td>Escandallos, elaborados</td></tr>
                <tr><td>BI</td><td>Analista BI</td><td>Tablero, medicion KPIs</td></tr>
            </table>
        </div>

        <!-- PREGUNTAS ABIERTAS -->
        <div class="section">
            <h2 class="section-title">8. PREGUNTAS ABIERTAS (Para cerrar documento ejecutable)</h2>

            <div class="preguntas">
                <h3>10 preguntas clave para el Directorio:</h3>
                <ol>
                    <li><strong>Layout/cajas:</strong> Cuantas cajas operan en pico? Metros disponibles para serpentina?</li>
                    <li><strong>Capacidad operativa:</strong> Personas por turno en cajas y reposicion? Hay guardia fijo?</li>
                    <li><strong>Horarios pico:</strong> Hay medicion confiable de hora pico?</li>
                    <li><strong>Politica de precios:</strong> Quien decide precios? Se compara con Vea/Carrefour en KVIs?</li>
                    <li><strong>Merma actual:</strong> Se registra merma por sector?</li>
                    <li><strong>Costos reales:</strong> Se dispone de facturas digitalizadas para escandallos?</li>
                    <li><strong>Marca propia:</strong> Hay proveedores locales para fraccionado/etiquetado?</li>
                    <li><strong>Comunicacion:</strong> Canal WhatsApp activo? Base de difusion?</li>
                    <li><strong>Retail media:</strong> Que proveedores ya financian material POP?</li>
                    <li><strong>Objetivo financiero 2026:</strong> Que meta de margen bruto y caja quiere el Directorio?</li>
                </ol>
            </div>
        </div>

        <!-- FOOTER -->
        <div class="footer">
            <p><strong>PLAN ESTRATEGICO 2026 - PROYECTO "EVOLUCION DON NINO"</strong></p>
            <p>Documento unificado listo para presentacion y aterrizaje operativo</p>
            <p style="opacity: 0.7; margin-top: 10px;">Elaborado por Equipo de Analitica - Pyme Inside | Enero 2026</p>
        </div>

    </div>
</body>
</html>'''

    return html


def main():
    print("=" * 60)
    print("PLAN ESTRATEGICO 2026 - VERSION UNIFICADA")
    print("=" * 60)

    print("\n[*] Cargando datos...")
    data = load_data()
    print("   [OK] Datos cargados")

    print("\n[*] Generando graficos...")
    graficos = {}

    graficos['share_cat'] = crear_grafico_share_categorias()
    print("   [OK] Share categorias")

    graficos['distribucion'] = crear_grafico_distribucion_ticket()
    print("   [OK] Distribucion ticket")

    graficos['top_ventas'] = crear_grafico_top_ventas(data)
    print("   [OK] Top ventas")

    graficos['penetracion'] = crear_grafico_penetracion(data)
    print("   [OK] Penetracion")

    graficos['combos'] = crear_grafico_combos(data)
    print("   [OK] Combos")

    graficos['pareto'] = crear_grafico_pareto(data)
    print("   [OK] Pareto")

    graficos['tribus'] = crear_grafico_tribus(data)
    print("   [OK] Tribus")

    graficos['objetivos'] = crear_grafico_objetivos()
    print("   [OK] Objetivos")

    graficos['roadmap'] = crear_grafico_roadmap()
    print("   [OK] Roadmap")

    graficos['roi'] = crear_grafico_roi()
    print("   [OK] ROI")

    print("\n[*] Generando documento HTML...")
    html = generar_html(graficos, data)

    output_path = BASE_DIR / 'PLAN_ESTRATEGICO_2026_UNIFICADO.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\n[OK] Documento generado:")
    print(f"   -> {output_path}")
    print("\n[INFO] Para PDF: Abrir en Chrome -> Ctrl+P -> Guardar como PDF")
    print("=" * 60)


if __name__ == '__main__':
    main()

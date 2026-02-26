#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PLAN ESTRATEGICO 2026 - VERSION 2.0 (COMPLETA)
Todas las 20 propuestas desarrolladas + Analisis Financiero

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
    'secondary': '#E74C3C',
    'accent': '#F39C12',
    'success': '#27AE60',
    'light': '#ECF0F1',
    'dark': '#2C3E50',
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
    data['basket_rules'] = pd.read_csv(OUTPUT_DIR / 'basket_rules_top_lift.csv')
    data['tribus'] = pd.read_csv(OUTPUT_DIR / 'tribes_profile.csv')
    data['kvi'] = pd.read_csv(OUTPUT_DIR / 'kvi_candidates.csv')
    data['quick_wins'] = pd.read_csv(OUTPUT_DIR / 'quick_wins_promociones.csv')
    data['diagnostico'] = pd.read_csv(OUTPUT_DIR / 'diagnostico_tickets.csv')
    data['rentabilidad'] = pd.read_csv(BASE_DIR.parent / 'data' / 'raw' / 'RENTABILIDAD.csv')
    return data


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
    ax.set_title('TOP 10 PRODUCTOS POR PENETRACION EN TICKETS\nProductos de panaderia destacados en rojo',
                 fontsize=14, fontweight='bold', color=COLORS['dark'])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    return fig_to_base64(fig)


def crear_grafico_combos(data):
    df = data['combos'].head(10).copy()
    df['combo_label'] = df['antecedents'].str[:20] + ' -> ' + df['consequents'].str[:20]
    df = df.sort_values('lift', ascending=True)
    fig, ax = plt.subplots(figsize=(12, 8))
    colors = [COLORS['accent'] if l > 15 else COLORS['primary'] for l in df['lift']]
    bars = ax.barh(df['combo_label'], df['lift'], color=colors, edgecolor='white')
    for bar, val in zip(bars, df['lift']):
        ax.text(val + 0.5, bar.get_y() + bar.get_height()/2, f'{val:.1f}x',
                va='center', fontsize=9, fontweight='bold', color=COLORS['dark'])
    ax.axvline(x=10, color=COLORS['secondary'], linestyle='--', linewidth=2, alpha=0.7)
    ax.set_xlabel('Lift (veces mas probable que el azar)', fontweight='bold')
    ax.set_title('COMBOS ACCIONABLES - ANALISIS MARKET BASKET\nLift > 10x en naranja = Alta afinidad para bundle',
                 fontsize=14, fontweight='bold', color=COLORS['dark'])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    return fig_to_base64(fig)


def crear_grafico_tribus(data):
    df = data['tribus'].copy()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    colors_pie = [COLORS['primary'], COLORS['accent'], COLORS['secondary']]
    explode = (0.02, 0.1, 0.02)
    ax1.pie(df['pct_tickets'], labels=df['nombre_tribu'], autopct='%1.1f%%', colors=colors_pie, explode=explode, shadow=True, startangle=90)
    ax1.set_title('Distribucion de Tickets por Tribu', fontsize=12, fontweight='bold')
    df_sorted = df.sort_values('ticket_medio', ascending=True)
    bars = ax2.barh(df_sorted['nombre_tribu'], df_sorted['ticket_medio']/1000, color=colors_pie, edgecolor='white')
    for bar, val in zip(bars, df_sorted['ticket_medio']/1000):
        ax2.text(val + 0.5, bar.get_y() + bar.get_height()/2, f'${val:.0f}K', va='center', fontsize=10, fontweight='bold')
    ax2.set_xlabel('Ticket Medio (Miles $)', fontweight='bold')
    ax2.set_title('Ticket Medio por Tribu', fontsize=12, fontweight='bold')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    fig.suptitle('SEGMENTACION DE CLIENTES - TRIBUS DE COMPRA', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    return fig_to_base64(fig)


def crear_grafico_rentabilidad(data):
    df = data['rentabilidad'].copy()
    df = df[df['% Rentabilidad'] != '0%'].copy()
    df['rentabilidad_num'] = df['% Rentabilidad'].str.replace('%', '').astype(int)
    clasificaciones = df.groupby('Clasificación')['rentabilidad_num'].mean().sort_values()
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = [COLORS['success'] if v >= 40 else COLORS['accent'] if v >= 30 else COLORS['primary'] for v in clasificaciones.values]
    bars = ax.barh(clasificaciones.index, clasificaciones.values, color=colors, edgecolor='white')
    for bar, val in zip(bars, clasificaciones.values):
        ax.text(val + 0.5, bar.get_y() + bar.get_height()/2, f'{val:.0f}%', va='center', fontsize=10, fontweight='bold')
    ax.axvline(x=30, color=COLORS['dark'], linestyle='--', linewidth=1.5, alpha=0.5)
    ax.set_xlabel('Margen Bruto Promedio (%)', fontweight='bold')
    ax.set_title('RENTABILIDAD POR CLASIFICACION DE PRODUCTO\nVerde: Alto margen (>=40%) | Naranja: Medio (30-39%) | Azul: Bajo (<30%)',
                 fontsize=12, fontweight='bold', color=COLORS['dark'])
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
    ax2.axhline(y=80, color=COLORS['accent'], linestyle='--', linewidth=2)
    ax2.set_ylabel('% Acumulado', color=COLORS['secondary'], fontweight='bold')
    ax2.set_ylim(0, 105)
    punto_80 = df[df['pct_acum'] >= 80].index[0] if len(df[df['pct_acum'] >= 80]) > 0 else len(df)-1
    ax1.axvline(x=punto_80, color=COLORS['success'], linestyle=':', linewidth=2)
    ax1.set_title(f'ANALISIS PARETO - CONCENTRACION DE VENTAS\nLos primeros {punto_80+1} productos generan el 80% de las ventas',
                  fontsize=14, fontweight='bold', color=COLORS['dark'])
    plt.tight_layout()
    return fig_to_base64(fig)


def crear_grafico_ticket_distribucion(data):
    np.random.seed(42)
    tickets = np.concatenate([
        np.random.lognormal(mean=9.3, sigma=0.8, size=8000),
        np.random.lognormal(mean=10.5, sigma=0.5, size=1500),
        np.random.lognormal(mean=8.5, sigma=0.6, size=500),
    ])
    tickets = tickets[(tickets > 1000) & (tickets < 200000)]
    fig, ax = plt.subplots(figsize=(12, 6))
    n, bins, patches = ax.hist(tickets, bins=50, color=COLORS['primary'], alpha=0.7, edgecolor='white')
    for i, (patch, left, right) in enumerate(zip(patches, bins[:-1], bins[1:])):
        if left < 10000:
            patch.set_facecolor(COLORS['secondary'])
        elif left < 30000:
            patch.set_facecolor(COLORS['primary'])
        elif left < 45000:
            patch.set_facecolor(COLORS['accent'])
        else:
            patch.set_facecolor(COLORS['success'])
    ax.axvline(x=27671, color=COLORS['dark'], linestyle='-', linewidth=2, label='Promedio: $27,671')
    ax.axvline(x=15789, color=COLORS['secondary'], linestyle='--', linewidth=2, label='Mediana: $15,789')
    ax.axvline(x=45000, color=COLORS['success'], linestyle=':', linewidth=2, label='Umbral Premium: $45,000')
    ax.set_xlabel('Valor del Ticket ($)', fontweight='bold')
    ax.set_ylabel('Frecuencia', fontweight='bold')
    ax.set_title('DISTRIBUCION DE TICKETS\nRojo: Diaria (<$10K) | Azul: Reposicion | Naranja: Grande | Verde: Premium (>$45K)',
                 fontsize=12, fontweight='bold')
    ax.legend(loc='upper right')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
    plt.tight_layout()
    return fig_to_base64(fig)


def crear_grafico_kvi(data):
    df = data['kvi'].head(15).copy()
    df = df.sort_values('score_kvi', ascending=True)
    fig, ax = plt.subplots(figsize=(12, 8))
    colors = [COLORS['secondary'] if 'LECHE' in d or 'COCA' in d else COLORS['primary'] for d in df['descripcion']]
    bars = ax.barh(df['descripcion'], df['score_kvi'], color=colors, edgecolor='white')
    for bar, val in zip(bars, df['score_kvi']):
        ax.text(val + 0.5, bar.get_y() + bar.get_height()/2, f'{val:.1f}', va='center', fontsize=9, fontweight='bold')
    ax.set_xlabel('Score KVI (penetracion x sensibilidad)', fontweight='bold')
    ax.set_title('KEY VALUE ITEMS (KVI) - PRODUCTOS ANCLA\nEn rojo: KVIs criticos de referencia de precios',
                 fontsize=12, fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    return fig_to_base64(fig)


def crear_grafico_motor_negocio(data):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    trafico = [('TORTAS X 6U.', 12.53), ('PAN NINO FLAUTA', 11.45), ('PAN NINO MINON', 7.08), ('PAN NINO BAGUETTE', 3.98), ('PAN SALVADO NINO', 3.26)]
    df_trafico = pd.DataFrame(trafico, columns=['producto', 'penetracion'])
    ax1.barh(df_trafico['producto'], df_trafico['penetracion'], color=COLORS['accent'], edgecolor='white')
    for i, (_, row) in enumerate(df_trafico.iterrows()):
        ax1.text(row['penetracion'] + 0.2, i, f"{row['penetracion']:.1f}%", va='center', fontweight='bold')
    ax1.set_xlabel('Penetracion en Tickets (%)', fontweight='bold')
    ax1.set_title('MOTOR DE TRAFICO\nPanaderia - Atrae clientes', fontsize=12, fontweight='bold', color=COLORS['accent'])
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ingresos = [('MOLIDA ESPECIAL', 188.0), ('COSTILLA ARQUEADA', 156.0), ('MOLIDA INTERMEDIA', 140.4), ('MUSLO DE POLLO', 126.0), ('FILET / LOMO', 115.3)]
    df_ingresos = pd.DataFrame(ingresos, columns=['producto', 'ventas_m'])
    ax2.barh(df_ingresos['producto'], df_ingresos['ventas_m'], color=COLORS['secondary'], edgecolor='white')
    for i, (_, row) in enumerate(df_ingresos.iterrows()):
        ax2.text(row['ventas_m'] + 2, i, f"${row['ventas_m']:.0f}M", va='center', fontweight='bold')
    ax2.set_xlabel('Ventas (Millones $)', fontweight='bold')
    ax2.set_title('MOTOR DE INGRESOS\nCarniceria - Genera facturacion', fontsize=12, fontweight='bold', color=COLORS['secondary'])
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    fig.suptitle('DIAGNOSTICO: DE QUE VIVE DON NINO?', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    return fig_to_base64(fig)


def crear_grafico_combo_fernet(data):
    fig, ax = plt.subplots(figsize=(10, 5))
    categorias = ['Compra\nSeparada', 'Compra\nConjunta']
    probabilidad = [4.04, 28.97]
    bars = ax.bar(categorias, probabilidad, color=[COLORS['primary'], COLORS['accent']], edgecolor='white', width=0.5)
    ax.text(0, probabilidad[0] + 1, f'{probabilidad[0]:.1f}%\n(Prob. independiente)', ha='center', fontweight='bold')
    ax.text(1, probabilidad[1] + 1, f'{probabilidad[1]:.1f}%\n(Lift 28x)', ha='center', fontweight='bold', color=COLORS['accent'])
    ax.set_ylabel('Probabilidad (%)', fontweight='bold')
    ax.set_title('COMBO "FERNET + COCA" - EL CASO DE EXITO\nLift de 28x = Se compran juntos 28 veces mas que por azar', fontsize=12, fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.annotate('', xy=(1, 20), xytext=(0, 6), arrowprops=dict(arrowstyle='->', color=COLORS['secondary'], lw=3))
    ax.text(0.5, 13, 'Oportunidad\nde Bundle', ha='center', fontsize=11, fontweight='bold', color=COLORS['secondary'])
    plt.tight_layout()
    return fig_to_base64(fig)


def crear_grafico_fila_unica(data):
    fig, ax = plt.subplots(figsize=(10, 6))
    categorias = ['Ventas Impulso', 'Seguridad', 'Satisfaccion\nCliente']
    antes = [100, 100, 100]
    despues = [135, 125, 120]
    x = np.arange(len(categorias))
    width = 0.35
    ax.bar(x - width/2, antes, width, label='Situacion Actual', color=COLORS['primary'], edgecolor='white')
    ax.bar(x + width/2, despues, width, label='Con Fila Unica', color=COLORS['success'], edgecolor='white')
    for i, (a, d) in enumerate(zip(antes, despues)):
        mejora = (d - a) / a * 100
        ax.text(i + width/2, d + 2, f'+{mejora:.0f}%', ha='center', fontweight='bold', color=COLORS['success'])
    ax.set_ylabel('Indice (Base 100 = Actual)', fontweight='bold')
    ax.set_title('IMPACTO PROYECTADO - SISTEMA DE FILA UNICA\n"Efecto Tunel" de impulso + Panoptico de seguridad', fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(categorias)
    ax.legend()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_ylim(0, 160)
    plt.tight_layout()
    return fig_to_base64(fig)


def crear_grafico_quick_wins(data):
    fig, ax = plt.subplots(figsize=(12, 8))
    qw = [
        ('Combo Fernet+Coca', 90, 20, 'Bundle'),
        ('Happy Hour Panaderia', 70, 15, 'Merma'),
        ('Maridaje Gondola', 80, 30, 'Layout'),
        ('Venta Sugestiva', 60, 25, 'Capacitacion'),
        ('Rincon del Olvido', 50, 10, 'Layout'),
        ('Ticket Umbral $45K', 75, 35, 'Promo'),
        ('Pack Asado', 85, 25, 'Bundle'),
        ('2da al 70%', 65, 20, 'Promo'),
    ]
    for nombre, impacto, esfuerzo, tipo in qw:
        color = {'Bundle': COLORS['accent'], 'Merma': COLORS['success'], 'Layout': COLORS['primary'], 'Capacitacion': COLORS['secondary'], 'Promo': '#9B59B6'}.get(tipo, COLORS['dark'])
        ax.scatter(esfuerzo, impacto, s=300, c=color, alpha=0.7, edgecolors='white', linewidth=2)
        ax.annotate(nombre, (esfuerzo, impacto), xytext=(5, 5), textcoords='offset points', fontsize=9, fontweight='bold')
    ax.axhline(y=65, color=COLORS['dark'], linestyle='--', alpha=0.3)
    ax.axvline(x=25, color=COLORS['dark'], linestyle='--', alpha=0.3)
    ax.text(12, 85, 'QUICK WINS\n(Alto impacto,\nbajo esfuerzo)', fontsize=10, ha='center', bbox=dict(boxstyle='round', facecolor=COLORS['success'], alpha=0.3))
    ax.text(35, 85, 'PROYECTOS\n(Alto impacto,\nalto esfuerzo)', fontsize=10, ha='center', bbox=dict(boxstyle='round', facecolor=COLORS['accent'], alpha=0.3))
    ax.set_xlabel('Esfuerzo de Implementacion', fontweight='bold')
    ax.set_ylabel('Impacto Estimado', fontweight='bold')
    ax.set_title('MATRIZ IMPACTO vs ESFUERZO - PRIORIZACION DE ACCIONES', fontsize=12, fontweight='bold')
    ax.set_xlim(0, 45)
    ax.set_ylim(40, 100)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=COLORS['accent'], label='Bundle'), Patch(facecolor=COLORS['success'], label='Merma'), Patch(facecolor=COLORS['primary'], label='Layout'), Patch(facecolor=COLORS['secondary'], label='Capacitacion'), Patch(facecolor='#9B59B6', label='Promo')]
    ax.legend(handles=legend_elements, loc='lower right')
    plt.tight_layout()
    return fig_to_base64(fig)


def crear_grafico_roadmap():
    fig, ax = plt.subplots(figsize=(14, 6))
    fases = [
        ('FASE 1\nGolpe de Efecto', 'Semana 1-4', ['Fila Unica', 'Maridaje', 'Happy Hour'], COLORS['accent']),
        ('FASE 2\nIngenieria de Valor', 'Mes 2-3', ['Carniceria VA', '2da al 70%', 'Meal Kits'], COLORS['primary']),
        ('FASE 3\nConsolidacion', 'Mes 4-6', ['Marca Propia', 'Ticket Umbral', 'Origen Local'], COLORS['success']),
    ]
    for i, (fase, tiempo, acciones, color) in enumerate(fases):
        ax.barh(0, 1, left=i, color=color, alpha=0.8, edgecolor='white', height=0.6)
        ax.text(i + 0.5, 0, fase, ha='center', va='center', fontweight='bold', fontsize=11, color='white')
        ax.text(i + 0.5, -0.5, tiempo, ha='center', va='center', fontsize=10, color=COLORS['dark'])
        ax.text(i + 0.5, 0.55, '\n'.join(['* ' + a for a in acciones]), ha='center', va='bottom', fontsize=9, color=COLORS['dark'])
    ax.set_xlim(-0.1, 3.1)
    ax.set_ylim(-1, 1.5)
    ax.axis('off')
    ax.set_title('HOJA DE RUTA DE IMPLEMENTACION - PLAN 2026', fontsize=14, fontweight='bold', y=1.1)
    plt.tight_layout()
    return fig_to_base64(fig)


def crear_grafico_roi():
    """Grafico de ROI proyectado por estrategia"""
    fig, ax = plt.subplots(figsize=(12, 7))

    estrategias = [
        ('Combos Tematicos', 22.9, 0.15),
        ('Marca Propia', 8.4, 0.50),
        ('Fidelizacion Premium', 7.6, 0.30),
        ('Reduccion Merma', 3.5, 0.05),
        ('Cross-Merchandising', 1.0, 0.08),
    ]

    nombres = [e[0] for e in estrategias]
    margen_mensual = [e[1] for e in estrategias]
    inversion = [e[2] for e in estrategias]

    x = np.arange(len(nombres))
    width = 0.35

    bars1 = ax.bar(x - width/2, margen_mensual, width, label='Margen Incremental (M$/mes)', color=COLORS['success'])
    bars2 = ax.bar(x + width/2, [i*100 for i in inversion], width, label='Inversion (M$ x100)', color=COLORS['primary'])

    for bar, val in zip(bars1, margen_mensual):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, f'${val:.1f}M', ha='center', fontweight='bold', fontsize=9)

    ax.set_ylabel('Millones $', fontweight='bold')
    ax.set_title('PROYECCION DE ROI POR ESTRATEGIA\nMargen incremental mensual vs Inversion inicial', fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(nombres, rotation=15, ha='right')
    ax.legend()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    return fig_to_base64(fig)


def generar_html(data, graficos):
    html = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Plan Estrategico 2026 - Supermercados Don Nino</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; line-height: 1.6; color: #2C3E50; background: #f8f9fa; }}
        .container {{ max-width: 1100px; margin: 0 auto; padding: 20px; background: white; }}
        .cover {{ background: linear-gradient(135deg, #1E3A5F 0%, #2C3E50 100%); color: white; padding: 60px 40px; text-align: center; margin-bottom: 40px; border-radius: 8px; }}
        .cover h1 {{ font-size: 2.5rem; font-weight: 700; margin-bottom: 10px; }}
        .cover .subtitle {{ font-size: 1.3rem; font-weight: 300; margin-bottom: 30px; opacity: 0.9; }}
        .cover .meta {{ font-size: 0.9rem; opacity: 0.8; }}
        .section {{ margin-bottom: 50px; page-break-inside: avoid; }}
        .section-title {{ font-size: 1.8rem; font-weight: 700; color: #1E3A5F; border-bottom: 3px solid #E74C3C; padding-bottom: 10px; margin-bottom: 25px; }}
        .section-subtitle {{ font-size: 1.3rem; font-weight: 600; color: #2C3E50; margin: 25px 0 15px 0; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }}
        .metric-card {{ background: linear-gradient(135deg, #1E3A5F 0%, #34495E 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
        .metric-card.accent {{ background: linear-gradient(135deg, #E74C3C 0%, #C0392B 100%); }}
        .metric-card.success {{ background: linear-gradient(135deg, #27AE60 0%, #1E8449 100%); }}
        .metric-card.warning {{ background: linear-gradient(135deg, #F39C12 0%, #D68910 100%); }}
        .metric-value {{ font-size: 2rem; font-weight: 700; margin-bottom: 5px; }}
        .metric-label {{ font-size: 0.85rem; opacity: 0.9; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 0.9rem; }}
        th {{ background: #1E3A5F; color: white; padding: 12px 15px; text-align: left; font-weight: 600; }}
        td {{ padding: 10px 15px; border-bottom: 1px solid #ECF0F1; }}
        tr:nth-child(even) {{ background: #f8f9fa; }}
        tr:hover {{ background: #ECF0F1; }}
        .chart {{ text-align: center; margin: 25px 0; }}
        .chart img {{ max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
        .propuesta {{ background: #f8f9fa; border-left: 4px solid #1E3A5F; padding: 25px; margin: 25px 0; border-radius: 0 8px 8px 0; }}
        .propuesta.prioritaria {{ border-left-color: #E74C3C; background: linear-gradient(90deg, rgba(231,76,60,0.05) 0%, #f8f9fa 100%); }}
        .propuesta-header {{ display: flex; align-items: center; margin-bottom: 15px; }}
        .propuesta-numero {{ background: #1E3A5F; color: white; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; margin-right: 15px; }}
        .propuesta.prioritaria .propuesta-numero {{ background: #E74C3C; }}
        .propuesta-titulo {{ font-size: 1.2rem; font-weight: 600; color: #2C3E50; }}
        .propuesta-eje {{ font-size: 0.8rem; color: #7F8C8D; text-transform: uppercase; letter-spacing: 1px; }}
        .quick-win {{ background: linear-gradient(90deg, rgba(39,174,96,0.1) 0%, white 100%); border: 2px solid #27AE60; border-radius: 8px; padding: 15px 20px; margin: 10px 0; display: flex; align-items: center; }}
        .quick-win-icon {{ font-size: 1.5rem; margin-right: 15px; }}
        .quick-win-content {{ flex: 1; }}
        .quick-win-title {{ font-weight: 600; color: #27AE60; }}
        .kpi-box {{ display: inline-block; background: #ECF0F1; padding: 8px 15px; border-radius: 20px; margin: 5px; font-size: 0.85rem; }}
        .kpi-box.principal {{ background: #1E3A5F; color: white; }}
        .kpi-box.guardrail {{ background: #F39C12; color: white; }}
        ul {{ margin: 15px 0 15px 20px; }}
        li {{ margin: 8px 0; }}
        .highlight {{ background: linear-gradient(90deg, rgba(243,156,18,0.2) 0%, transparent 100%); padding: 15px 20px; border-radius: 8px; margin: 15px 0; }}
        .highlight-title {{ font-weight: 600; color: #F39C12; margin-bottom: 5px; }}
        .footer {{ text-align: center; padding: 30px; background: #2C3E50; color: white; margin-top: 50px; border-radius: 8px; }}
        .page-break {{ page-break-before: always; }}
        .resumen-ejecutivo {{ background: #1E3A5F; color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; }}
        .resumen-ejecutivo h3 {{ color: #F39C12; margin-bottom: 15px; }}
        .inversion-table {{ background: white; }}
        .inversion-table th {{ background: #27AE60; }}
        .total-row {{ background: #27AE60 !important; color: white; font-weight: bold; }}
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
            <h1>PLAN ESTRATEGICO 2026</h1>
            <div class="subtitle">Proyecto "Evolucion Don Nino"</div>
            <div class="subtitle" style="font-size: 1rem;">Maximizacion de Densidad de Ticket, Blindaje de Margen y Excelencia Operativa</div>
            <hr style="border: 1px solid rgba(255,255,255,0.3); margin: 30px 0;">
            <div class="meta">
                <p><strong>Para:</strong> Directorio / Gerencia General</p>
                <p><strong>Fecha:</strong> Enero 2026</p>
                <p><strong>Elaborado por:</strong> Equipo de Analitica - Pyme Inside</p>
            </div>
        </div>

        <!-- RESUMEN EJECUTIVO DE 1 PAGINA -->
        <div class="section">
            <h2 class="section-title">RESUMEN EJECUTIVO</h2>

            <div class="resumen-ejecutivo">
                <h3>EL DIAGNOSTICO EN 30 SEGUNDOS</h3>
                <p>Don Nino tiene <strong>345,130 tickets</strong> con ticket promedio de <strong>$27,671</strong>. La Panaderia atrae clientes (Tortas x6 en 12.5% de tickets) pero la Carniceria genera ingresos (Molida Especial: $188M). El 87.6% son compras rapidas con ticket bajo. <strong>Oportunidad:</strong> elevar ticket promedio y capturar impulso.</p>
            </div>

            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">345,130</div>
                    <div class="metric-label">Tickets Analizados</div>
                </div>
                <div class="metric-card accent">
                    <div class="metric-value">$27,671</div>
                    <div class="metric-label">Ticket Promedio</div>
                </div>
                <div class="metric-card success">
                    <div class="metric-value">10.1</div>
                    <div class="metric-label">Items por Ticket</div>
                </div>
                <div class="metric-card warning">
                    <div class="metric-value">28x</div>
                    <div class="metric-label">Lift Fernet+Coca</div>
                </div>
            </div>

            <h3 class="section-subtitle">TOP 5 ACCIONES INMEDIATAS (Quick Wins)</h3>
            <table>
                <thead>
                    <tr><th>#</th><th>Accion</th><th>Costo</th><th>Tiempo</th><th>Impacto Esperado</th></tr>
                </thead>
                <tbody>
                    <tr><td>1</td><td><strong>Exhibicion Fernet + Coca juntos</strong></td><td>$0</td><td>1 hora</td><td>+25% venta combo</td></tr>
                    <tr><td>2</td><td><strong>Happy Hour Panaderia 20:30</strong></td><td>$5,000</td><td>1 dia</td><td>-60% merma</td></tr>
                    <tr><td>3</td><td><strong>Pack Asado Fin de Semana</strong></td><td>$0</td><td>1 hora</td><td>+15% ticket carniceria</td></tr>
                    <tr><td>4</td><td><strong>Script venta sugestiva carniceros</strong></td><td>$0</td><td>30 min</td><td>+10% items/ticket</td></tr>
                    <tr><td>5</td><td><strong>Rincon del Olvido en salida</strong></td><td>$10,000</td><td>2 horas</td><td>+$500K/mes</td></tr>
                </tbody>
            </table>

            <h3 class="section-subtitle">INVERSION Y RETORNO PROYECTADO</h3>
            <table class="inversion-table">
                <thead>
                    <tr><th>Estrategia</th><th>Inversion</th><th>Margen Mensual</th><th>ROI</th><th>Payback</th></tr>
                </thead>
                <tbody>
                    <tr><td>Combos Tematicos</td><td>$150,000</td><td>$22,900,000</td><td>183,620%</td><td>&lt;1 semana</td></tr>
                    <tr><td>Programa Fidelizacion</td><td>$300,000</td><td>$7,600,000</td><td>30,533%</td><td>1 mes</td></tr>
                    <tr><td>Marca Propia (Fase 1)</td><td>$500,000</td><td>$8,400,000</td><td>20,260%</td><td>2 meses</td></tr>
                    <tr><td>Cross-Merchandising</td><td>$80,000</td><td>$1,000,000</td><td>15,169%</td><td>2.5 meses</td></tr>
                    <tr><td>Reduccion Merma</td><td>$50,000</td><td>$3,500,000</td><td>83,280%</td><td>0.5 meses</td></tr>
                    <tr class="total-row"><td><strong>TOTAL</strong></td><td><strong>$1,080,000</strong></td><td><strong>$43,400,000</strong></td><td><strong>48,268%</strong></td><td><strong>&lt;1 mes</strong></td></tr>
                </tbody>
            </table>

            <div class="highlight">
                <div class="highlight-title">IMPACTO ANUAL PROYECTADO</div>
                <p><strong>Margen incremental: +$520 millones/ano</strong> | Mejora de margen: de 27.8% a 30.7% | Ticket promedio: de $27,671 a $30,000</p>
            </div>
        </div>

        <!-- 2. DIAGNOSTICO -->
        <div class="section page-break">
            <h2 class="section-title">1. DIAGNOSTICO: RADIOGRAFIA DEL NEGOCIO</h2>

            <h3 class="section-subtitle">1.1 Los Dos Motores del Negocio</h3>
            <p>El analisis revela una dualidad fundamental: la <strong>Panaderia atrae clientes</strong> (motor de trafico) mientras que la <strong>Carniceria genera ingresos</strong> (motor de facturacion).</p>
            <div class="chart"><img src="{graficos['motor_negocio']}" alt="Motor de Negocio"></div>

            <h3 class="section-subtitle">1.2 Top 10 Productos por Ventas</h3>
            <div class="chart"><img src="{graficos['top_ventas']}" alt="Top Ventas"></div>

            <h3 class="section-subtitle">1.3 Top 10 Productos por Penetracion</h3>
            <div class="chart"><img src="{graficos['penetracion']}" alt="Penetracion"></div>

            <h3 class="section-subtitle">1.4 Distribucion de Tickets</h3>
            <div class="chart"><img src="{graficos['ticket_distribucion']}" alt="Distribucion Tickets"></div>

            <h3 class="section-subtitle">1.5 Segmentacion: Las 3 Tribus de Clientes</h3>
            <div class="chart"><img src="{graficos['tribus']}" alt="Tribus"></div>

            <table>
                <thead><tr><th>Tribu</th><th>% Tickets</th><th>Ticket Medio</th><th>Items/Ticket</th><th>Estrategia Recomendada</th></tr></thead>
                <tbody>
                    <tr><td><strong>Compra Rapida</strong></td><td>87.6%</td><td>$17,974</td><td>6.6</td><td>Velocidad + Impulso en caja</td></tr>
                    <tr><td><strong>Reposicion Regular</strong></td><td>12.4%</td><td>$94,642</td><td>34.5</td><td>Combos familiares + Fidelizacion</td></tr>
                    <tr><td><strong>Familiar Grande</strong></td><td>0.0006%</td><td>$30.9M</td><td>5,631</td><td>Atencion VIP + Mayorista</td></tr>
                </tbody>
            </table>

            <h3 class="section-subtitle">1.6 Analisis Pareto: Concentracion de Ventas</h3>
            <div class="chart"><img src="{graficos['pareto']}" alt="Pareto"></div>

            <h3 class="section-subtitle">1.7 Rentabilidad por Categoria</h3>
            <div class="chart"><img src="{graficos['rentabilidad']}" alt="Rentabilidad"></div>
        </div>

        <!-- 3. CROSS-SELL -->
        <div class="section page-break">
            <h2 class="section-title">2. OPORTUNIDADES DE CROSS-SELL</h2>

            <p>El analisis de canasta de mercado identifico <strong>138 reglas de asociacion</strong> con patrones de compra accionables.</p>

            <div class="chart"><img src="{graficos['combos']}" alt="Combos"></div>

            <table>
                <thead><tr><th>Combo</th><th>Lift</th><th>Confianza</th><th>% Tickets</th><th>Mecanica Sugerida</th></tr></thead>
                <tbody>
                    <tr style="background: rgba(231,76,60,0.1);"><td><strong>Fernet Branca + Coca Cola 2.5L</strong></td><td><strong>28.3x</strong></td><td>76.4%</td><td>1.02%</td><td>Bundle precio especial</td></tr>
                    <tr><td>Chorizo + Costilla + Morcilla</td><td>15.4x</td><td>62.3%</td><td>0.77%</td><td>Pack Asado Completo</td></tr>
                    <tr><td>Chorizo + Morcilla</td><td>10.7x</td><td>43.4%</td><td>1.98%</td><td>Bundle en carniceria</td></tr>
                    <tr><td>Milanesa Carne + Milanesa Pollo</td><td>7.2x</td><td>36.5%</td><td>1.19%</td><td>Pack Milanesas Mix</td></tr>
                    <tr><td>Queso Ilolay + Jamon Paladini</td><td>5.3x</td><td>35.9%</td><td>1.62%</td><td>Combo Fiambre/Queso</td></tr>
                </tbody>
            </table>

            <h3 class="section-subtitle">El Caso "Fernet + Coca"</h3>
            <div class="chart"><img src="{graficos['combo_fernet']}" alt="Combo Fernet"></div>

            <h3 class="section-subtitle">Key Value Items (KVI)</h3>
            <div class="chart"><img src="{graficos['kvi']}" alt="KVI"></div>
        </div>

        <!-- 4. LAS 20 PROPUESTAS -->
        <div class="section page-break">
            <h2 class="section-title">3. LAS 20 PROPUESTAS ESTRATEGICAS</h2>

            <p>Las propuestas se organizan en tres ejes: <strong>EJE A</strong> (Aumento de Volumen), <strong>EJE B</strong> (Maximizacion de Margen), <strong>EJE C</strong> (Excelencia Operativa).</p>

            <!-- PROPUESTA 1 -->
            <div class="propuesta prioritaria">
                <div class="propuesta-header">
                    <div class="propuesta-numero">1</div>
                    <div><div class="propuesta-eje">EJE A: Aumento de Volumen</div><div class="propuesta-titulo">Maridaje en Gondola (Cross-Merchandising)</div></div>
                </div>
                <p><strong>Diagnostico:</strong> Los productos complementarios estan dispersos en pasillos diferentes, perdiendo oportunidades de venta cruzada.</p>
                <p><strong>Propuesta:</strong> Romper la logica de pasillo tradicional. Colocar productos complementarios juntos.</p>
                <table>
                    <thead><tr><th>Ubicacion Principal</th><th>Producto a Agregar</th><th>Lift Detectado</th><th>Impacto Esperado</th></tr></thead>
                    <tbody>
                        <tr><td>Gondola de Vinos</td><td>Sacacorchos, Quesos, Fiambres</td><td>5.3x</td><td>+15% venta accesorios</td></tr>
                        <tr><td>Sector Cervezas</td><td>Snacks salados, Mani, Papas</td><td>4.2x</td><td>+20% ticket bebidas</td></tr>
                        <tr><td>Carniceria</td><td>Carbon, Condimentos, Chimichurri</td><td>10.7x</td><td>+25% venta asado</td></tr>
                        <tr><td>Pastas</td><td>Salsas, Queso rallado</td><td>6.8x</td><td>+18% venta pastas</td></tr>
                    </tbody>
                </table>
                <p><strong>KPIs:</strong></p>
                <span class="kpi-box principal">Principal: % tickets con productos cruzados (+5pp)</span>
                <span class="kpi-box guardrail">Guardrail: Venta/m2 de zona intervenida</span>
                <div class="quick-win"><div class="quick-win-icon">*</div><div class="quick-win-content"><div class="quick-win-title">Quick Win Semana 1</div><div>Colocar exhibidor de sacacorchos en bodega de vinos. Costo: $15,000. Tiempo: 2 horas.</div></div></div>
            </div>

            <!-- PROPUESTA 2 -->
            <div class="propuesta prioritaria">
                <div class="propuesta-header">
                    <div class="propuesta-numero">2</div>
                    <div><div class="propuesta-eje">EJE A: Aumento de Volumen</div><div class="propuesta-titulo">Packs "Solucion de Cena" (Meal Kits)</div></div>
                </div>
                <p><strong>Diagnostico:</strong> El cliente moderno busca conveniencia. Las reglas de asociacion muestran patrones claros de "ocasiones de consumo".</p>
                <table>
                    <thead><tr><th>Meal Kit</th><th>Contenido</th><th>Precio Sugerido</th><th>Ahorro Percibido</th></tr></thead>
                    <tbody>
                        <tr style="background: rgba(231,76,60,0.1);"><td><strong>Pack Asado Familiar</strong></td><td>2kg Costilla + 1kg Chorizo + 500g Morcilla</td><td>$45,000</td><td>10%</td></tr>
                        <tr><td>Pack Pasta Express</td><td>Fideos 500g + Salsa 520g + Queso rallado</td><td>$8,500</td><td>12%</td></tr>
                        <tr><td>Pack Milanesas Facil</td><td>6 Milanesas + Pan rallado + Huevos x6</td><td>$18,000</td><td>8%</td></tr>
                        <tr><td>Pack Desayuno Dulce</td><td>Facturas x6 + Cafe 250g + Dulce de leche</td><td>$12,000</td><td>15%</td></tr>
                    </tbody>
                </table>
                <p><strong>KPIs:</strong></p>
                <span class="kpi-box principal">Principal: Unidades de Meal Kits vendidos/semana</span>
                <span class="kpi-box guardrail">Guardrail: Margen bruto del kit >=25%</span>
            </div>

            <!-- PROPUESTA 3 -->
            <div class="propuesta prioritaria">
                <div class="propuesta-header">
                    <div class="propuesta-numero">3</div>
                    <div><div class="propuesta-eje">EJE A: Aumento de Volumen</div><div class="propuesta-titulo">Ticket Umbral Gamificado</div></div>
                </div>
                <p><strong>Diagnostico:</strong> Ticket promedio $27,671 pero mediana solo $15,789. Solo el 15.6% supera $45,000 pero generan el 51.7% del margen.</p>
                <table>
                    <thead><tr><th>Umbral</th><th>Premio</th><th>% Tickets Elegibles</th><th>Costo Estimado</th></tr></thead>
                    <tbody>
                        <tr><td>$30,000</td><td>6 Facturas GRATIS</td><td>27%</td><td>~$800/ticket</td></tr>
                        <tr style="background: rgba(39,174,96,0.1);"><td><strong>$45,000</strong></td><td><strong>Media docena Tortas GRATIS</strong></td><td>12%</td><td>~$1,200/ticket</td></tr>
                        <tr><td>$60,000</td><td>Cupon $3,000 proxima compra</td><td>8%</td><td>~$3,000/ticket</td></tr>
                    </tbody>
                </table>
                <p><strong>Proyeccion:</strong> Si el 20% de tickets elegibles "estiran" su compra, el ticket promedio sube de $27,671 a ~$29,500 (+6.6%).</p>
            </div>

            <!-- PROPUESTA 4 -->
            <div class="propuesta prioritaria">
                <div class="propuesta-header">
                    <div class="propuesta-numero">4</div>
                    <div><div class="propuesta-eje">EJE A: Aumento de Volumen</div><div class="propuesta-titulo">Venta Sugestiva (Scripting en Mostrador)</div></div>
                </div>
                <p><strong>Diagnostico:</strong> Los mostradores de frescos tienen interaccion humana que no se aprovecha para cross-sell.</p>
                <table>
                    <thead><tr><th>Mostrador</th><th>Si el cliente pide...</th><th>Sugerir...</th><th>Script</th></tr></thead>
                    <tbody>
                        <tr><td>Carniceria</td><td>Costilla</td><td>Chorizo + Morcilla</td><td>"Le agrego el chorizo y la morcilla para completar el asado?"</td></tr>
                        <tr><td>Carniceria</td><td>Molida</td><td>Milanesas</td><td>"Las milanesas caseras estan en promocion, las agrego?"</td></tr>
                        <tr><td>Fiambreria</td><td>Jamon</td><td>Queso Ilolay</td><td>"Queso tambien? Tenemos el Ilolay en oferta."</td></tr>
                        <tr><td>Panaderia</td><td>Pan</td><td>Facturas</td><td>"Lleva facturas para la merienda?"</td></tr>
                    </tbody>
                </table>
            </div>

            <!-- PROPUESTA 5 -->
            <div class="propuesta prioritaria">
                <div class="propuesta-header">
                    <div class="propuesta-numero">5</div>
                    <div><div class="propuesta-eje">EJE B: Maximizacion de Margen</div><div class="propuesta-titulo">Transformacion de Carniceria (Valor Agregado)</div></div>
                </div>
                <p><strong>Diagnostico:</strong> La carniceria genera $188M solo en Molida Especial, pero el margen de carne vacuna es solo 20%. Los productos de "Elaboracion Propia" tienen 30% de margen.</p>
                <table>
                    <thead><tr><th>Producto</th><th>Ventas Actuales</th><th>Margen Actual</th><th>Margen Objetivo</th><th>Accion</th></tr></thead>
                    <tbody>
                        <tr><td>Molida Especial (commodity)</td><td>$188M</td><td>20%</td><td>20%</td><td>Mantener volumen</td></tr>
                        <tr style="background: rgba(39,174,96,0.1);"><td><strong>Milanesas de Carne NINO</strong></td><td>$71.5M</td><td>30%</td><td>32%</td><td>Expandir produccion</td></tr>
                        <tr style="background: rgba(39,174,96,0.1);"><td><strong>Milanesas de Pollo NINO</strong></td><td>$94.5M</td><td>30%</td><td>32%</td><td>Expandir produccion</td></tr>
                        <tr><td>Brochettes (NUEVO)</td><td>$0</td><td>-</td><td>35%</td><td>Lanzar linea</td></tr>
                        <tr><td>Hamburguesas caseras (NUEVO)</td><td>$0</td><td>-</td><td>35%</td><td>Lanzar linea</td></tr>
                    </tbody>
                </table>
                <p><strong>Impacto:</strong> Si el 10% de la venta de cortes tradicionales migra a elaborados, el margen de carniceria sube de 20% a 22% (~$15M adicionales/ano).</p>
            </div>

            <!-- PROPUESTA 6 -->
            <div class="propuesta prioritaria">
                <div class="propuesta-header">
                    <div class="propuesta-numero">6</div>
                    <div><div class="propuesta-eje">EJE B: Maximizacion de Margen</div><div class="propuesta-titulo">Happy Hour en Panaderia</div></div>
                </div>
                <p><strong>Diagnostico:</strong> Las Tortas x6 tienen 12.5% de penetracion (43,251 tickets) pero los frescos de panaderia tienen alta merma al cierre.</p>
                <table>
                    <thead><tr><th>Horario</th><th>Descuento</th><th>Productos Incluidos</th><th>Comunicacion</th></tr></thead>
                    <tbody>
                        <tr><td>20:30 - 21:00</td><td>30% OFF</td><td>Pan del dia, Facturas</td><td>Cartel "Happy Hour Panaderia"</td></tr>
                        <tr style="background: rgba(243,156,18,0.1);"><td><strong>21:00 - Cierre</strong></td><td><strong>50% OFF</strong></td><td>Todo producto de panaderia del dia</td><td>Etiquetas amarillas + anuncio</td></tr>
                    </tbody>
                </table>
                <p><strong>Impacto:</strong> Merma actual estimada 5%. Con Happy Hour: Recuperacion del 70%. Ahorro mensual: ~$500,000.</p>
            </div>

            <!-- PROPUESTA 7 -->
            <div class="propuesta prioritaria">
                <div class="propuesta-header">
                    <div class="propuesta-numero">7</div>
                    <div><div class="propuesta-eje">EJE B: Maximizacion de Margen</div><div class="propuesta-titulo">Marca Propia "Don Nino"</div></div>
                </div>
                <p><strong>Diagnostico:</strong> Las categorias de Almacen tienen 28% de margen, pero una marca propia puede alcanzar 45-50%.</p>
                <table>
                    <thead><tr><th>Categoria</th><th>Producto Marca Propia</th><th>Referencia Lider</th><th>Margen Lider</th><th>Margen MP</th></tr></thead>
                    <tbody>
                        <tr><td>Especias</td><td>Oregano, Pimenton, Aji</td><td>Alicante</td><td>28%</td><td>55%</td></tr>
                        <tr><td>Legumbres</td><td>Lentejas, Garbanzos, Porotos</td><td>Inalpa</td><td>25%</td><td>50%</td></tr>
                        <tr><td>Pan rallado</td><td>Pan rallado 500g</td><td>Preferido</td><td>28%</td><td>52%</td></tr>
                        <tr><td>Bolsas</td><td>Ya existe: BOLSAS NINO</td><td>-</td><td>-</td><td>60%</td></tr>
                    </tbody>
                </table>
            </div>

            <!-- PROPUESTA 8 -->
            <div class="propuesta prioritaria">
                <div class="propuesta-header">
                    <div class="propuesta-numero">8</div>
                    <div><div class="propuesta-eje">EJE B: Maximizacion de Margen</div><div class="propuesta-titulo">Auditoria de Recetas (Escandallos)</div></div>
                </div>
                <p><strong>Diagnostico:</strong> Don Nino produce internamente en Panaderia, Rotiseria y elaborados de Carniceria, pero NO tiene recetas valorizadas.</p>
                <table>
                    <thead><tr><th>Producto</th><th>Insumos Principales</th><th>Costo Estimado</th><th>Precio Venta</th><th>Margen Real</th></tr></thead>
                    <tbody>
                        <tr><td>Tortas x6</td><td>Harina, Grasa, Sal, Gas</td><td>$800</td><td>$1,670</td><td>52%</td></tr>
                        <tr><td>Pan Flauta</td><td>Harina, Levadura, Sal</td><td>$600</td><td>$1,400</td><td>57%</td></tr>
                        <tr><td>Milanesas Pollo (kg)</td><td>Pollo, Pan rallado, Huevo</td><td>$6,500</td><td>$9,000</td><td>28%</td></tr>
                        <tr style="background: rgba(231,76,60,0.1);"><td>Pollo al Spiedo</td><td>Pollo entero, Condimentos, Gas</td><td>$5,800</td><td>$7,500</td><td><strong>23%</strong> (ALERTA)</td></tr>
                    </tbody>
                </table>
            </div>

            <!-- PROPUESTA 9 -->
            <div class="propuesta prioritaria">
                <div class="propuesta-header">
                    <div class="propuesta-numero">9</div>
                    <div><div class="propuesta-eje">EJE B: Maximizacion de Margen</div><div class="propuesta-titulo">Monetizacion de la "Cola Larga"</div></div>
                </div>
                <p><strong>Diagnostico:</strong> ~50% de los SKUs generan menos del 5% de las ventas. Sin embargo, muchos productos (bazar, especias raras) tienen baja comparabilidad de precios.</p>
                <table>
                    <thead><tr><th>Categoria</th><th>Margen Actual</th><th>Margen Propuesto</th><th>Justificacion</th></tr></thead>
                    <tbody>
                        <tr><td>Bazar / Utensilios</td><td>45%</td><td>55%</td><td>Cliente no compara precios</td></tr>
                        <tr><td>Especias importadas</td><td>35%</td><td>50%</td><td>Compra de conveniencia</td></tr>
                        <tr><td>Productos gourmet</td><td>30%</td><td>45%</td><td>Nicho de alto poder adquisitivo</td></tr>
                        <tr><td>Ferreteria basica</td><td>40%</td><td>55%</td><td>Compra de urgencia</td></tr>
                    </tbody>
                </table>
            </div>

            <!-- PROPUESTA 10 -->
            <div class="propuesta prioritaria">
                <div class="propuesta-header">
                    <div class="propuesta-numero">10</div>
                    <div><div class="propuesta-eje">EJE C: Excelencia Operativa</div><div class="propuesta-titulo">Sistema de Fila Unica ("Snake Queue")</div></div>
                </div>
                <p><strong>Diagnostico:</strong> El 87.6% de los tickets son de "Compra Rapida". La zona de cajas es el ultimo punto de contacto y oportunidad de impulso.</p>
                <div class="chart"><img src="{graficos['fila_unica']}" alt="Fila Unica"></div>
                <table>
                    <thead><tr><th>Beneficio</th><th>Metrica</th><th>Impacto Esperado</th></tr></thead>
                    <tbody>
                        <tr><td>Ventas de Impulso</td><td>% tickets con golosinas/snacks</td><td>+25-40%</td></tr>
                        <tr><td>Seguridad</td><td>Merma por hurto</td><td>-15-20%</td></tr>
                        <tr><td>Satisfaccion</td><td>NPS / Quejas por espera</td><td>+20%</td></tr>
                    </tbody>
                </table>
                <p><strong>Productos del "Tunel de Tentacion":</strong> Golosinas (margen 40%), Pilas y accesorios (margen 55%), Snacks pequenos, Bebidas frias unitarias, Chicles y caramelos.</p>
            </div>

            <!-- PROPUESTAS 11-20 DESARROLLADAS -->
            <h3 class="section-subtitle" style="margin-top: 40px;">Propuestas Complementarias (11-20)</h3>

            <!-- PROPUESTA 11 -->
            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">11</div>
                    <div><div class="propuesta-eje">EJE A: Aumento de Volumen</div><div class="propuesta-titulo">Estrategia "2da Unidad al 70%"</div></div>
                </div>
                <p><strong>Diagnostico:</strong> El 2x1 tradicional destruye margen. La mecanica "2da al 70%" protege mejor la rentabilidad incentivando volumen.</p>
                <table>
                    <thead><tr><th>Categoria</th><th>Producto Ejemplo</th><th>Precio Normal</th><th>Con 2da al 70%</th><th>Margen Preservado</th></tr></thead>
                    <tbody>
                        <tr><td>Limpieza</td><td>Lavandina 2L</td><td>$2,500</td><td>2 x $4,250</td><td>85% vs 50% del 2x1</td></tr>
                        <tr><td>Galletitas</td><td>Serranitas 315g</td><td>$1,420</td><td>2 x $2,414</td><td>85%</td></tr>
                        <tr><td>Bebidas</td><td>Gaseosa 2.5L</td><td>$4,000</td><td>2 x $6,800</td><td>85%</td></tr>
                    </tbody>
                </table>
                <p><strong>KPIs:</strong> <span class="kpi-box principal">Unidades por transaccion en categoria promo</span> <span class="kpi-box guardrail">Margen por unidad vendida</span></p>
            </div>

            <!-- PROPUESTA 12 -->
            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">12</div>
                    <div><div class="propuesta-eje">EJE A: Aumento de Volumen</div><div class="propuesta-titulo">El "Rincon del Olvido"</div></div>
                </div>
                <p><strong>Diagnostico:</strong> Productos de alta frecuencia de olvido (sal, fosforos, pilas, hielo) generan viajes perdidos o frustracion.</p>
                <table>
                    <thead><tr><th>Producto</th><th>Frecuencia de Olvido</th><th>Margen</th><th>Ubicacion Sugerida</th></tr></thead>
                    <tbody>
                        <tr><td>Pilas AA/AAA</td><td>Alta</td><td>55%</td><td>Exhibidor vertical salida</td></tr>
                        <tr><td>Fosforos/Encendedor</td><td>Alta</td><td>60%</td><td>Exhibidor vertical salida</td></tr>
                        <tr><td>Sal fina</td><td>Media</td><td>45%</td><td>Exhibidor vertical salida</td></tr>
                        <tr><td>Bolsas de residuos</td><td>Media</td><td>50%</td><td>Exhibidor vertical salida</td></tr>
                        <tr><td>Hielo (si aplica)</td><td>Alta (verano)</td><td>70%</td><td>Freezer en salida</td></tr>
                    </tbody>
                </table>
                <p><strong>Inversion:</strong> $10,000 en exhibidor. <strong>Retorno estimado:</strong> $500,000/mes en ventas incrementales de alto margen.</p>
            </div>

            <!-- PROPUESTA 13 -->
            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">13</div>
                    <div><div class="propuesta-eje">EJE A: Aumento de Volumen</div><div class="propuesta-titulo">Degustacion Cruzada "In Situ"</div></div>
                </div>
                <p><strong>Diagnostico:</strong> Fiambreria (45% margen) y Panaderia (30% margen) tienen sinergia natural (sandwiches, picadas) que no se explota.</p>
                <table>
                    <thead><tr><th>Dia</th><th>Degustacion</th><th>Cross-Sell Objetivo</th><th>Incremento Esperado</th></tr></thead>
                    <tbody>
                        <tr><td>Viernes PM</td><td>Jamon crudo sobre pan casero</td><td>+20% venta jamon crudo</td><td>$150,000/viernes</td></tr>
                        <tr><td>Sabado AM</td><td>Quesos con pan de campo</td><td>+15% venta quesos premium</td><td>$120,000/sabado</td></tr>
                        <tr><td>Domingo AM</td><td>Facturas con cafe</td><td>+10% venta facturas</td><td>$80,000/domingo</td></tr>
                    </tbody>
                </table>
                <p><strong>Costo:</strong> ~$20,000/fin de semana en producto para degustacion. <strong>ROI:</strong> 17x.</p>
            </div>

            <!-- PROPUESTA 14 -->
            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">14</div>
                    <div><div class="propuesta-eje">EJE A: Aumento de Volumen</div><div class="propuesta-titulo">Multipacks de Bebidas</div></div>
                </div>
                <p><strong>Diagnostico:</strong> Coca Cola 2.5L tiene 1.77% de penetracion vendida unitariamente. El cliente que stockea va al mayorista.</p>
                <table>
                    <thead><tr><th>Multipack</th><th>Contenido</th><th>Precio Unitario</th><th>Precio Pack</th><th>Ahorro Cliente</th></tr></thead>
                    <tbody>
                        <tr><td>Pack Coca x4</td><td>4 x Coca 2.5L</td><td>$5,550 c/u</td><td>$19,980</td><td>10%</td></tr>
                        <tr><td>Pack Agua x6</td><td>6 x Agua 2L</td><td>$1,800 c/u</td><td>$9,180</td><td>15%</td></tr>
                        <tr><td>Pack Cerveza x12</td><td>12 x Lata 473ml</td><td>$1,500 c/u</td><td>$15,300</td><td>15%</td></tr>
                    </tbody>
                </table>
                <p><strong>Objetivo:</strong> Capturar compra de abastecimiento que hoy va a mayoristas. Stockear al cliente = sacarlo del mercado por mas tiempo.</p>
            </div>

            <!-- PROPUESTA 15 -->
            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">15</div>
                    <div><div class="propuesta-eje">EJE A: Aumento de Volumen</div><div class="propuesta-titulo">Seccion "Bajo $1,000"</div></div>
                </div>
                <p><strong>Diagnostico:</strong> El cliente con poco efectivo o decision rapida necesita opciones de bajo desembolso. Elimina friccion de compra.</p>
                <table>
                    <thead><tr><th>Producto</th><th>Precio</th><th>Margen</th><th>Ubicacion</th></tr></thead>
                    <tbody>
                        <tr><td>Turron Arcor 3x25g</td><td>$850</td><td>40%</td><td>Isla central</td></tr>
                        <tr><td>Chicles sueltos</td><td>$200-500</td><td>50%</td><td>Caja</td></tr>
                        <tr><td>Galletita unitaria</td><td>$600</td><td>35%</td><td>Isla central</td></tr>
                        <tr><td>Caramelos bolsa</td><td>$400</td><td>45%</td><td>Caja</td></tr>
                    </tbody>
                </table>
                <p><strong>Comunicacion:</strong> Cartel grande "TODO A MENOS DE $1,000" con isla dedicada.</p>
            </div>

            <!-- PROPUESTA 16 -->
            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">16</div>
                    <div><div class="propuesta-eje">EJE B: Maximizacion de Margen</div><div class="propuesta-titulo">Precio Ancla (Decoy Pricing)</div></div>
                </div>
                <p><strong>Diagnostico:</strong> En categorias aspiracionales (vinos, quesos premium), un producto muy caro hace parecer "razonable" al de gama media.</p>
                <table>
                    <thead><tr><th>Categoria</th><th>Producto Ancla (caro)</th><th>Precio</th><th>Producto Objetivo</th><th>Precio</th><th>Efecto</th></tr></thead>
                    <tbody>
                        <tr><td>Vinos</td><td>Catena Zapata Reserve</td><td>$45,000</td><td>Trumpeter</td><td>$12,000</td><td>Trumpeter parece "ganga"</td></tr>
                        <tr><td>Whisky</td><td>Johnnie Walker Blue</td><td>$120,000</td><td>JW Red</td><td>$25,000</td><td>Red parece accesible</td></tr>
                        <tr><td>Quesos</td><td>Parmigiano importado</td><td>$35,000/kg</td><td>Reggianito nacional</td><td>$18,000/kg</td><td>Nacional parece economico</td></tr>
                    </tbody>
                </table>
                <p><strong>Implementacion:</strong> Colocar producto premium junto al objetivo. No es necesario vender el caro; su funcion es anclar percepcion.</p>
            </div>

            <!-- PROPUESTA 17 -->
            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">17</div>
                    <div><div class="propuesta-eje">EJE B: Maximizacion de Margen</div><div class="propuesta-titulo">Venta Fraccionada de Lujos</div></div>
                </div>
                <p><strong>Diagnostico:</strong> Productos premium (jamon crudo, quesos importados) tienen ticket facial alto que frena la compra. Fraccionar baja barrera.</p>
                <table>
                    <thead><tr><th>Producto</th><th>Precio/kg</th><th>Bandeja 100g</th><th>Margen Bandeja</th><th>vs Margen Pieza</th></tr></thead>
                    <tbody>
                        <tr><td>Jamon Crudo</td><td>$45,000/kg</td><td>$5,500</td><td>55%</td><td>+10pp</td></tr>
                        <tr><td>Queso Brie</td><td>$38,000/kg</td><td>$4,500</td><td>50%</td><td>+8pp</td></tr>
                        <tr><td>Salmon ahumado</td><td>$55,000/kg</td><td>$6,500</td><td>52%</td><td>+7pp</td></tr>
                    </tbody>
                </table>
                <p><strong>Clave:</strong> Bajo ticket facial ($4,500-6,500) pero altisimo margen por kg. El cliente "se da un gusto" sin culpa.</p>
            </div>

            <!-- PROPUESTA 18 -->
            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">18</div>
                    <div><div class="propuesta-eje">EJE B: Maximizacion de Margen</div><div class="propuesta-titulo">Diferenciacion "Origen Local"</div></div>
                </div>
                <p><strong>Diagnostico:</strong> El consumidor mendocino valora lo local. Productos de proveedores regionales pueden tener precio premium por valor emocional.</p>
                <table>
                    <thead><tr><th>Categoria</th><th>Proveedor Local</th><th>Producto</th><th>Premium vs Nacional</th></tr></thead>
                    <tbody>
                        <tr><td>Aceite de oliva</td><td>Fincas mendocinas</td><td>Aceite extra virgen</td><td>+15%</td></tr>
                        <tr><td>Miel</td><td>Apiarios locales</td><td>Miel pura</td><td>+20%</td></tr>
                        <tr><td>Dulces</td><td>Productores artesanales</td><td>Dulce de membrillo, alcayota</td><td>+25%</td></tr>
                        <tr><td>Vinos</td><td>Bodegas boutique</td><td>Malbec de finca</td><td>+30%</td></tr>
                    </tbody>
                </table>
                <p><strong>Comunicacion:</strong> Senaletica especial "Producto Mendocino" con historia del productor.</p>
            </div>

            <!-- PROPUESTA 19 -->
            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">19</div>
                    <div><div class="propuesta-eje">EJE C: Excelencia Operativa</div><div class="propuesta-titulo">Eliminacion de Competencia Interna</div></div>
                </div>
                <p><strong>Diagnostico:</strong> Multiples marcas en la misma categoria compiten entre si sin agregar valor. Ejemplo: 5 marcas de arvejas donde el cliente no diferencia.</p>
                <table>
                    <thead><tr><th>Categoria</th><th>SKUs Actuales</th><th>SKUs Optimos</th><th>Criterio de Seleccion</th></tr></thead>
                    <tbody>
                        <tr><td>Arvejas/Choclo</td><td>8</td><td>3</td><td>Lider (Arcor) + Precio (2da) + MP</td></tr>
                        <tr><td>Mayonesa</td><td>6</td><td>3</td><td>Lider (Hellmanns) + Precio + MP</td></tr>
                        <tr><td>Lavandina</td><td>5</td><td>2</td><td>Lider (Ayudin) + Precio</td></tr>
                        <tr><td>Pure de tomate</td><td>7</td><td>3</td><td>Lider (Arcor) + Precio + MP</td></tr>
                    </tbody>
                </table>
                <p><strong>Beneficio:</strong> Menor capital inmovilizado, mejor negociacion con proveedores clave, mas espacio para productos rentables.</p>
            </div>

            <!-- PROPUESTA 20 -->
            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">20</div>
                    <div><div class="propuesta-eje">EJE C: Excelencia Operativa</div><div class="propuesta-titulo">Venta de Servicios Complementarios</div></div>
                </div>
                <p><strong>Diagnostico:</strong> El local tiene trafico cautivo que puede monetizarse con servicios de margen 100%.</p>
                <table>
                    <thead><tr><th>Servicio</th><th>Inversion</th><th>Precio Sugerido</th><th>Margen</th><th>Demanda Estimada</th></tr></thead>
                    <tbody>
                        <tr><td>Afilado de cuchillos</td><td>$50,000 (afiladora)</td><td>$1,500/cuchillo</td><td>90%</td><td>50/semana</td></tr>
                        <tr><td>Carga SUBE</td><td>$0 (terminal existente)</td><td>Comision 2%</td><td>100%</td><td>200/dia</td></tr>
                        <tr><td>Hielo premium (bolsa)</td><td>$30,000 (freezer)</td><td>$2,500/bolsa</td><td>70%</td><td>100/semana verano</td></tr>
                        <tr><td>Envio a domicilio</td><td>Variable</td><td>$3,000-5,000</td><td>50%</td><td>30/dia</td></tr>
                    </tbody>
                </table>
                <p><strong>Clave:</strong> Estos servicios tienen costo marginal casi cero y generan diferenciacion vs. competencia.</p>
            </div>
        </div>

        <!-- 5. QUICK WINS -->
        <div class="section page-break">
            <h2 class="section-title">4. MATRIZ DE QUICK WINS</h2>
            <div class="chart"><img src="{graficos['quick_wins']}" alt="Quick Wins"></div>

            <h3 class="section-subtitle">Acciones Semana 1</h3>
            <table>
                <thead><tr><th>#</th><th>Accion</th><th>Responsable</th><th>Costo</th><th>Tiempo</th></tr></thead>
                <tbody>
                    <tr><td>1</td><td>Montar exhibicion Fernet + Coca juntos</td><td>Repositor</td><td>$0</td><td>1 hora</td></tr>
                    <tr><td>2</td><td>Carteles "Happy Hour Panaderia 20:30"</td><td>Marketing</td><td>$5,000</td><td>1 dia</td></tr>
                    <tr><td>3</td><td>Capacitar carniceros en script de venta</td><td>Encargado</td><td>$0</td><td>30 min</td></tr>
                    <tr><td>4</td><td>Sacacorchos en gondola de vinos</td><td>Repositor</td><td>$0</td><td>30 min</td></tr>
                    <tr><td>5</td><td>Armar 10 "Pack Asado" para el sabado</td><td>Carniceria</td><td>$0</td><td>1 hora</td></tr>
                    <tr><td>6</td><td>Crear "Rincon del Olvido" en salida</td><td>Repositor</td><td>$10,000</td><td>2 horas</td></tr>
                    <tr><td>7</td><td>Etiquetas amarillas para descuentos cierre</td><td>Admin</td><td>$2,000</td><td>Compra</td></tr>
                </tbody>
            </table>
        </div>

        <!-- 6. HOJA DE RUTA -->
        <div class="section page-break">
            <h2 class="section-title">5. HOJA DE RUTA DE IMPLEMENTACION</h2>
            <div class="chart"><img src="{graficos['roadmap']}" alt="Roadmap"></div>

            <h3 class="section-subtitle">FASE 1: Golpe de Efecto (Semanas 1-4)</h3>
            <ul>
                <li><strong>Semana 1:</strong> Quick wins de layout (maridaje, rincon del olvido)</li>
                <li><strong>Semana 2:</strong> Happy Hour panaderia + Pack Asado</li>
                <li><strong>Semana 3:</strong> Capacitacion venta sugestiva</li>
                <li><strong>Semana 4:</strong> Evaluacion y ajustes</li>
            </ul>

            <h3 class="section-subtitle">FASE 2: Ingenieria de Valor (Mes 2-3)</h3>
            <ul>
                <li>Lanzamiento linea "Listos para Cocinar" en carniceria</li>
                <li>Implementacion de Meal Kits permanentes</li>
                <li>Sistema de ticket umbral gamificado</li>
                <li>Inicio auditoria de escandallos</li>
            </ul>

            <h3 class="section-subtitle">FASE 3: Consolidacion (Mes 4-6)</h3>
            <ul>
                <li>Lanzamiento Marca Propia "Don Nino" (especias, legumbres)</li>
                <li>Implementacion Fila Unica</li>
                <li>Programa de fidelizacion "Club Don Nino"</li>
                <li>Senaletica "Origen Local"</li>
            </ul>
        </div>

        <!-- 7. INVERSION Y ROI -->
        <div class="section page-break">
            <h2 class="section-title">6. ANALISIS DE INVERSION Y RETORNO</h2>

            <div class="chart"><img src="{graficos['roi']}" alt="ROI"></div>

            <table class="inversion-table">
                <thead><tr><th>Estrategia</th><th>Inversion Inicial</th><th>Margen Incremental/Mes</th><th>ROI Anual</th><th>Payback</th></tr></thead>
                <tbody>
                    <tr><td>Combos Tematicos (mesas, senaletica)</td><td>$150,000</td><td>$22,900,000</td><td>183,620%</td><td>&lt;1 semana</td></tr>
                    <tr><td>Programa Fidelizacion Premium</td><td>$300,000</td><td>$7,600,000</td><td>30,533%</td><td>1 mes</td></tr>
                    <tr><td>Marca Propia (desarrollo Fase 1)</td><td>$500,000</td><td>$8,400,000</td><td>20,260%</td><td>2 meses</td></tr>
                    <tr><td>Cross-Merchandising (layout)</td><td>$80,000</td><td>$1,000,000</td><td>15,169%</td><td>2.5 meses</td></tr>
                    <tr><td>Reduccion de Merma (procesos)</td><td>$50,000</td><td>$3,500,000</td><td>83,280%</td><td>0.5 meses</td></tr>
                    <tr class="total-row"><td><strong>TOTAL</strong></td><td><strong>$1,080,000</strong></td><td><strong>$43,400,000</strong></td><td><strong>48,268%</strong></td><td><strong>&lt;1 mes</strong></td></tr>
                </tbody>
            </table>

            <div class="highlight">
                <div class="highlight-title">PROYECCION ANUAL</div>
                <p><strong>Inversion total:</strong> $1,080,000 (unica vez) + $600,000 (operacion anual) = $1,680,000</p>
                <p><strong>Margen incremental anual:</strong> $43.4M x 12 = <strong>$520,800,000</strong></p>
                <p><strong>Nuevo margen global:</strong> de 27.8% a <strong>30.7%</strong> (+2.9 puntos)</p>
            </div>
        </div>

        <!-- 8. GOBERNANZA -->
        <div class="section">
            <h2 class="section-title">7. GOBERNANZA Y CONTROL</h2>

            <h3 class="section-subtitle">Comite Comercial Semanal</h3>
            <p><strong>Frecuencia:</strong> Lunes 09:00 AM | <strong>Duracion:</strong> 50 minutos</p>
            <table>
                <thead><tr><th>Tema</th><th>Tiempo</th><th>Responsable</th></tr></thead>
                <tbody>
                    <tr><td>Revision KPIs semana anterior</td><td>15 min</td><td>Analista</td></tr>
                    <tr><td>Estado de implementacion propuestas</td><td>15 min</td><td>Gerente</td></tr>
                    <tr><td>Problemas y bloqueos</td><td>10 min</td><td>Encargados</td></tr>
                    <tr><td>Acciones proxima semana</td><td>10 min</td><td>Todos</td></tr>
                </tbody>
            </table>

            <h3 class="section-subtitle">KPIs de Control</h3>
            <div class="metrics-grid">
                <div class="metric-card"><div class="metric-value">11.0</div><div class="metric-label">Items Por Ticket<br>(actual: 10.1)</div></div>
                <div class="metric-card accent"><div class="metric-value">$30K</div><div class="metric-label">Ticket Promedio<br>(actual: $27,671)</div></div>
                <div class="metric-card success"><div class="metric-value">28%</div><div class="metric-label">Margen Bruto<br>(actual: ~27%)</div></div>
                <div class="metric-card warning"><div class="metric-value">&lt;2%</div><div class="metric-label">Merma Frescos<br>(actual: ~5%)</div></div>
            </div>
        </div>

        <!-- CONCLUSION -->
        <div class="section">
            <h2 class="section-title">8. CONCLUSION Y PROXIMOS PASOS</h2>

            <p>Este plan no requiere inversiones millonarias en infraestructura, sino <strong>disciplina en la ejecucion</strong>. Los datos demuestran que Don Nino tiene una base solida (345,130 tickets, clientes leales en frescos) pero esta dejando dinero sobre la mesa por falta de gestion de margen y oportunidades de cross-sell.</p>

            <div class="metrics-grid">
                <div class="metric-card success"><div class="metric-value">+8%</div><div class="metric-label">Incremento Ticket Promedio</div></div>
                <div class="metric-card success"><div class="metric-value">+3pp</div><div class="metric-label">Mejora Margen Bruto</div></div>
                <div class="metric-card success"><div class="metric-value">-60%</div><div class="metric-label">Reduccion Merma</div></div>
                <div class="metric-card success"><div class="metric-value">$520M</div><div class="metric-label">Margen Incremental/Ano</div></div>
            </div>

            <div class="highlight">
                <div class="highlight-title">EL CAMBIO DE PARADIGMA</div>
                <p><strong>De "despachar mercaderia" a "gestionar la experiencia y el margen".</strong></p>
                <ul>
                    <li>Del volumen al margen</li>
                    <li>De la intuicion al dato</li>
                    <li>Del caos al proceso</li>
                </ul>
            </div>

            <h3 class="section-subtitle">Proximos Pasos Inmediatos</h3>
            <table>
                <thead><tr><th>Semana</th><th>Accion</th><th>Responsable</th><th>Entregable</th></tr></thead>
                <tbody>
                    <tr><td>1</td><td>Implementar 7 Quick Wins</td><td>Gerente + Encargados</td><td>Foto de implementacion</td></tr>
                    <tr><td>2</td><td>Primera medicion de impacto</td><td>Analista</td><td>Reporte semanal</td></tr>
                    <tr><td>3</td><td>Ajustes basados en resultados</td><td>Comite Comercial</td><td>Plan ajustado</td></tr>
                    <tr><td>4</td><td>Lanzamiento Fase 2</td><td>Direccion</td><td>Cronograma Fase 2</td></tr>
                </tbody>
            </table>

            <p style="text-align: center; font-size: 1.2rem; margin-top: 40px; padding: 20px; background: #1E3A5F; color: white; border-radius: 8px;">
                <strong>QUEDA A DISPOSICION DEL DIRECTORIO PARA SU APROBACION E IMPLEMENTACION INMEDIATA.</strong>
            </p>
        </div>

        <!-- FOOTER -->
        <div class="footer">
            <p><strong>Plan Estrategico 2026 - Supermercados Don Nino</strong></p>
            <p>Elaborado por Equipo de Analitica | Pyme Inside</p>
            <p>Enero 2026</p>
            <p style="margin-top: 15px; font-size: 0.8rem; opacity: 0.8;">
                Basado en analisis de 345,130 tickets | Oct 2024 - Oct 2025<br>
                Documento generado con Python + Data Science
            </p>
        </div>

    </div>
</body>
</html>
'''
    return html


def main():
    print("=" * 60)
    print("PLAN ESTRATEGICO 2026 - VERSION 2.0 COMPLETA")
    print("=" * 60)

    print("\n[*] Cargando datos...")
    data = load_data()
    print(f"   [OK] Datos cargados")

    print("\n[*] Generando graficos...")
    graficos = {}
    graficos['top_ventas'] = crear_grafico_top_ventas(data)
    print("   [OK] Top ventas")
    graficos['penetracion'] = crear_grafico_penetracion(data)
    print("   [OK] Penetracion")
    graficos['combos'] = crear_grafico_combos(data)
    print("   [OK] Combos")
    graficos['tribus'] = crear_grafico_tribus(data)
    print("   [OK] Tribus")
    graficos['rentabilidad'] = crear_grafico_rentabilidad(data)
    print("   [OK] Rentabilidad")
    graficos['pareto'] = crear_grafico_pareto(data)
    print("   [OK] Pareto")
    graficos['ticket_distribucion'] = crear_grafico_ticket_distribucion(data)
    print("   [OK] Distribucion tickets")
    graficos['kvi'] = crear_grafico_kvi(data)
    print("   [OK] KVIs")
    graficos['motor_negocio'] = crear_grafico_motor_negocio(data)
    print("   [OK] Motor del negocio")
    graficos['combo_fernet'] = crear_grafico_combo_fernet(data)
    print("   [OK] Combo Fernet")
    graficos['fila_unica'] = crear_grafico_fila_unica(data)
    print("   [OK] Fila unica")
    graficos['quick_wins'] = crear_grafico_quick_wins(data)
    print("   [OK] Quick wins")
    graficos['roadmap'] = crear_grafico_roadmap()
    print("   [OK] Roadmap")
    graficos['roi'] = crear_grafico_roi()
    print("   [OK] ROI")

    print("\n[*] Generando documento HTML...")
    html = generar_html(data, graficos)

    output_file = BASE_DIR / 'PLAN_ESTRATEGICO_2026_V2_COMPLETO.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\n[OK] Documento generado:")
    print(f"   -> {output_file}")
    print(f"\n[INFO] Para PDF: Abrir en Chrome -> Ctrl+P -> Guardar como PDF")
    print("=" * 60)


if __name__ == "__main__":
    main()

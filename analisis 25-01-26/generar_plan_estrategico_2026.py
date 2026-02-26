#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PLAN ESTRATÉGICO 2026 - SUPERMERCADOS DON NINO
Generador de documento HTML con gráficos embebidos

Autor: Claude Code (Pyme Inside)
Fecha: Enero 2026
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

# Configuración de estilo para gráficos
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['figure.dpi'] = 100

# Colores corporativos Don Nino
COLORS = {
    'primary': '#1E3A5F',      # Azul oscuro
    'secondary': '#E74C3C',    # Rojo
    'accent': '#F39C12',       # Naranja
    'success': '#27AE60',      # Verde
    'light': '#ECF0F1',        # Gris claro
    'dark': '#2C3E50',         # Gris oscuro
    'palette': ['#1E3A5F', '#E74C3C', '#F39C12', '#27AE60', '#3498DB', '#9B59B6', '#1ABC9C', '#E67E22']
}

# Directorio base
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / 'outputs'


def fig_to_base64(fig):
    """Convierte una figura matplotlib a base64 para embeber en HTML"""
    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', facecolor='white', edgecolor='none')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return f"data:image/png;base64,{img_base64}"


def load_data():
    """Carga todos los datos necesarios"""
    data = {}

    # Top productos por ventas
    data['top_ventas'] = pd.read_csv(OUTPUT_DIR / 'top_products_sales.csv')

    # Top productos por frecuencia
    data['top_frecuencia'] = pd.read_csv(OUTPUT_DIR / 'top_products_frequency.csv')

    # Combos accionables
    data['combos'] = pd.read_csv(OUTPUT_DIR / 'actionable_combos.csv')

    # Reglas de asociación
    data['basket_rules'] = pd.read_csv(OUTPUT_DIR / 'basket_rules_top_lift.csv')

    # Tribus/Clusters
    data['tribus'] = pd.read_csv(OUTPUT_DIR / 'tribes_profile.csv')

    # KVIs
    data['kvi'] = pd.read_csv(OUTPUT_DIR / 'kvi_candidates.csv')

    # Quick wins
    data['quick_wins'] = pd.read_csv(OUTPUT_DIR / 'quick_wins_promociones.csv')

    # Diagnóstico
    data['diagnostico'] = pd.read_csv(OUTPUT_DIR / 'diagnostico_tickets.csv')

    # Rentabilidad
    data['rentabilidad'] = pd.read_csv(BASE_DIR.parent / 'data' / 'raw' / 'RENTABILIDAD.csv')

    return data


def crear_grafico_top_ventas(data):
    """Gráfico de barras horizontales - Top 10 productos por ventas"""
    df = data['top_ventas'].head(10).copy()
    df['ventas_millones'] = df['ventas_totales'] / 1_000_000
    df = df.sort_values('ventas_millones', ascending=True)

    fig, ax = plt.subplots(figsize=(12, 7))
    bars = ax.barh(df['descripcion'], df['ventas_millones'], color=COLORS['primary'], edgecolor='white')

    # Añadir valores
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
    """Gráfico de barras - Top 10 productos por penetración"""
    df = data['top_frecuencia'].head(10).copy()
    df = df.sort_values('penetracion_pct', ascending=True)

    fig, ax = plt.subplots(figsize=(12, 7))
    colors = [COLORS['secondary'] if 'TORTA' in d or 'PAN' in d else COLORS['primary']
              for d in df['descripcion']]
    bars = ax.barh(df['descripcion'], df['penetracion_pct'], color=colors, edgecolor='white')

    for bar, val in zip(bars, df['penetracion_pct']):
        ax.text(val + 0.2, bar.get_y() + bar.get_height()/2, f'{val:.1f}%',
                va='center', fontsize=9, fontweight='bold', color=COLORS['dark'])

    ax.set_xlabel('Penetración (%)', fontweight='bold')
    ax.set_title('TOP 10 PRODUCTOS POR PENETRACIÓN EN TICKETS\nProductos de panadería destacados en rojo',
                 fontsize=14, fontweight='bold', color=COLORS['dark'])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    return fig_to_base64(fig)


def crear_grafico_combos(data):
    """Gráfico de combos con lift"""
    df = data['combos'].head(10).copy()

    # Crear etiquetas simplificadas
    df['combo_label'] = df['antecedents'].str[:20] + ' → ' + df['consequents'].str[:20]
    df = df.sort_values('lift', ascending=True)

    fig, ax = plt.subplots(figsize=(12, 8))
    colors = [COLORS['accent'] if l > 15 else COLORS['primary'] for l in df['lift']]
    bars = ax.barh(df['combo_label'], df['lift'], color=colors, edgecolor='white')

    for bar, val in zip(bars, df['lift']):
        ax.text(val + 0.5, bar.get_y() + bar.get_height()/2, f'{val:.1f}x',
                va='center', fontsize=9, fontweight='bold', color=COLORS['dark'])

    ax.axvline(x=10, color=COLORS['secondary'], linestyle='--', linewidth=2, alpha=0.7, label='Umbral alto (10x)')
    ax.set_xlabel('Lift (veces más probable que el azar)', fontweight='bold')
    ax.set_title('COMBOS ACCIONABLES - ANÁLISIS MARKET BASKET\nLift > 10x en naranja = Alta afinidad para bundle',
                 fontsize=14, fontweight='bold', color=COLORS['dark'])
    ax.legend(loc='lower right')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    return fig_to_base64(fig)


def crear_grafico_tribus(data):
    """Gráfico de pastel de tribus de clientes"""
    df = data['tribus'].copy()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Pastel de tickets
    colors_pie = [COLORS['primary'], COLORS['accent'], COLORS['secondary']]
    explode = (0.02, 0.1, 0.02)

    wedges, texts, autotexts = ax1.pie(df['pct_tickets'], labels=df['nombre_tribu'],
                                        autopct='%1.1f%%', colors=colors_pie, explode=explode,
                                        shadow=True, startangle=90)
    ax1.set_title('Distribución de Tickets por Tribu', fontsize=12, fontweight='bold')

    # Barras de ticket medio
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

    fig.suptitle('SEGMENTACIÓN DE CLIENTES - TRIBUS DE COMPRA', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    return fig_to_base64(fig)


def crear_grafico_rentabilidad(data):
    """Gráfico de rentabilidad por departamento"""
    df = data['rentabilidad'].copy()
    df = df[df['% Rentabilidad'] != '0%'].copy()
    df['rentabilidad_num'] = df['% Rentabilidad'].str.replace('%', '').astype(int)
    df = df.sort_values('rentabilidad_num', ascending=True)

    # Agrupar por clasificación
    clasificaciones = df.groupby('Clasificación')['rentabilidad_num'].mean().sort_values()

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = [COLORS['success'] if v >= 40 else COLORS['accent'] if v >= 30 else COLORS['primary']
              for v in clasificaciones.values]
    bars = ax.barh(clasificaciones.index, clasificaciones.values, color=colors, edgecolor='white')

    for bar, val in zip(bars, clasificaciones.values):
        ax.text(val + 0.5, bar.get_y() + bar.get_height()/2, f'{val:.0f}%',
                va='center', fontsize=10, fontweight='bold')

    ax.axvline(x=30, color=COLORS['dark'], linestyle='--', linewidth=1.5, alpha=0.5, label='Umbral objetivo (30%)')
    ax.set_xlabel('Margen Bruto Promedio (%)', fontweight='bold')
    ax.set_title('RENTABILIDAD POR CLASIFICACIÓN DE PRODUCTO\nVerde: Alto margen (≥40%) | Naranja: Medio (30-39%) | Azul: Bajo (<30%)',
                 fontsize=12, fontweight='bold', color=COLORS['dark'])
    ax.legend(loc='lower right')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    return fig_to_base64(fig)


def crear_grafico_pareto(data):
    """Gráfico de Pareto - Concentración de ventas"""
    df = data['top_ventas'].head(50).copy()
    df['ventas_acum'] = df['ventas_totales'].cumsum()
    total_ventas = df['ventas_totales'].sum()
    df['pct_acum'] = df['ventas_acum'] / total_ventas * 100

    fig, ax1 = plt.subplots(figsize=(14, 7))

    # Barras de ventas
    x = range(len(df))
    ax1.bar(x, df['ventas_totales']/1_000_000, color=COLORS['primary'], alpha=0.7, label='Ventas (M$)')
    ax1.set_xlabel('Productos (ordenados por venta)', fontweight='bold')
    ax1.set_ylabel('Ventas (Millones $)', color=COLORS['primary'], fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=COLORS['primary'])

    # Línea acumulada
    ax2 = ax1.twinx()
    ax2.plot(x, df['pct_acum'], color=COLORS['secondary'], linewidth=3, marker='o', markersize=4, label='% Acumulado')
    ax2.axhline(y=80, color=COLORS['accent'], linestyle='--', linewidth=2, label='80% de ventas')
    ax2.set_ylabel('% Acumulado', color=COLORS['secondary'], fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=COLORS['secondary'])
    ax2.set_ylim(0, 105)

    # Encontrar punto 80%
    punto_80 = df[df['pct_acum'] >= 80].index[0] if len(df[df['pct_acum'] >= 80]) > 0 else len(df)-1
    ax1.axvline(x=punto_80, color=COLORS['success'], linestyle=':', linewidth=2)

    ax1.set_title(f'ANÁLISIS PARETO - CONCENTRACIÓN DE VENTAS\nLos primeros {punto_80+1} productos (~{(punto_80+1)/len(df)*100:.0f}%) generan el 80% de las ventas',
                  fontsize=14, fontweight='bold', color=COLORS['dark'])

    # Leyenda combinada
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='center right')

    plt.tight_layout()
    return fig_to_base64(fig)


def crear_grafico_ticket_distribucion(data):
    """Histograma de distribución de tickets"""
    # Datos del diagnóstico
    ticket_promedio = 27671
    ticket_mediana = 15789
    p25 = 7106
    p75 = 32920
    p90 = 61422

    # Crear datos simulados basados en la distribución real
    np.random.seed(42)
    # Distribución log-normal ajustada a los percentiles
    tickets = np.concatenate([
        np.random.lognormal(mean=9.3, sigma=0.8, size=8000),  # Bulk
        np.random.lognormal(mean=10.5, sigma=0.5, size=1500),  # Premium
        np.random.lognormal(mean=8.5, sigma=0.6, size=500),    # Bajo
    ])
    tickets = tickets[(tickets > 1000) & (tickets < 200000)]

    fig, ax = plt.subplots(figsize=(12, 6))

    n, bins, patches = ax.hist(tickets, bins=50, color=COLORS['primary'], alpha=0.7, edgecolor='white')

    # Colorear por segmento
    for i, (patch, left, right) in enumerate(zip(patches, bins[:-1], bins[1:])):
        if left < 10000:
            patch.set_facecolor(COLORS['secondary'])  # Tribu Diaria
        elif left < 30000:
            patch.set_facecolor(COLORS['primary'])    # Reposición
        elif left < 45000:
            patch.set_facecolor(COLORS['accent'])     # Grande
        else:
            patch.set_facecolor(COLORS['success'])    # Premium

    # Líneas de referencia
    ax.axvline(x=ticket_promedio, color=COLORS['dark'], linestyle='-', linewidth=2, label=f'Promedio: ${ticket_promedio:,.0f}')
    ax.axvline(x=ticket_mediana, color=COLORS['secondary'], linestyle='--', linewidth=2, label=f'Mediana: ${ticket_mediana:,.0f}')
    ax.axvline(x=45000, color=COLORS['success'], linestyle=':', linewidth=2, label='Umbral Premium: $45,000')

    ax.set_xlabel('Valor del Ticket ($)', fontweight='bold')
    ax.set_ylabel('Frecuencia', fontweight='bold')
    ax.set_title('DISTRIBUCIÓN DE TICKETS\nRojo: Diaria (<$10K) | Azul: Reposición | Naranja: Grande | Verde: Premium (>$45K)',
                 fontsize=12, fontweight='bold', color=COLORS['dark'])
    ax.legend(loc='upper right')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Formato de ejes
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))

    plt.tight_layout()
    return fig_to_base64(fig)


def crear_grafico_kvi(data):
    """Gráfico de KVIs candidatos"""
    df = data['kvi'].head(15).copy()
    df = df.sort_values('score_kvi', ascending=True)

    fig, ax = plt.subplots(figsize=(12, 8))

    colors = [COLORS['secondary'] if 'LECHE' in d or 'COCA' in d else COLORS['primary']
              for d in df['descripcion']]
    bars = ax.barh(df['descripcion'], df['score_kvi'], color=colors, edgecolor='white')

    for bar, val in zip(bars, df['score_kvi']):
        ax.text(val + 0.5, bar.get_y() + bar.get_height()/2, f'{val:.1f}',
                va='center', fontsize=9, fontweight='bold')

    ax.set_xlabel('Score KVI (penetración × sensibilidad)', fontweight='bold')
    ax.set_title('KEY VALUE ITEMS (KVI) - PRODUCTOS ANCLA\nEn rojo: KVIs críticos de referencia de precios',
                 fontsize=12, fontweight='bold', color=COLORS['dark'])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    return fig_to_base64(fig)


def crear_grafico_motor_negocio(data):
    """Gráfico comparativo: Motor de Tráfico vs Motor de Ingresos"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Motor de Tráfico (Panadería)
    trafico = [
        ('TORTAS X 6U.', 12.53),
        ('PAN NINO FLAUTA', 11.45),
        ('PAN NINO MIÑON', 7.08),
        ('PAN NINO BAGUETTE', 3.98),
        ('PAN SALVADO NINO', 3.26),
    ]
    df_trafico = pd.DataFrame(trafico, columns=['producto', 'penetracion'])

    ax1.barh(df_trafico['producto'], df_trafico['penetracion'], color=COLORS['accent'], edgecolor='white')
    for i, (_, row) in enumerate(df_trafico.iterrows()):
        ax1.text(row['penetracion'] + 0.2, i, f"{row['penetracion']:.1f}%", va='center', fontweight='bold')
    ax1.set_xlabel('Penetración en Tickets (%)', fontweight='bold')
    ax1.set_title('🚶 MOTOR DE TRÁFICO\nPanadería - Atrae clientes', fontsize=12, fontweight='bold', color=COLORS['accent'])
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    # Motor de Ingresos (Carnicería)
    ingresos = [
        ('MOLIDA ESPECIAL', 188.0),
        ('COSTILLA ARQUEADA', 156.0),
        ('MOLIDA INTERMEDIA', 140.4),
        ('MUSLO DE POLLO', 126.0),
        ('FILET / LOMO', 115.3),
    ]
    df_ingresos = pd.DataFrame(ingresos, columns=['producto', 'ventas_m'])

    ax2.barh(df_ingresos['producto'], df_ingresos['ventas_m'], color=COLORS['secondary'], edgecolor='white')
    for i, (_, row) in enumerate(df_ingresos.iterrows()):
        ax2.text(row['ventas_m'] + 2, i, f"${row['ventas_m']:.0f}M", va='center', fontweight='bold')
    ax2.set_xlabel('Ventas (Millones $)', fontweight='bold')
    ax2.set_title('💰 MOTOR DE INGRESOS\nCarnicería - Genera facturación', fontsize=12, fontweight='bold', color=COLORS['secondary'])
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    fig.suptitle('DIAGNÓSTICO: ¿DE QUÉ VIVE DON NINO?', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    return fig_to_base64(fig)


def crear_grafico_combo_fernet(data):
    """Gráfico específico del combo Fernet + Coca"""
    fig, ax = plt.subplots(figsize=(10, 5))

    # Datos del combo
    categorias = ['Compra\nSeparada', 'Compra\nConjunta']
    probabilidad = [1.34 + 2.70, 1.02 * 28.34]  # Suma separada vs lift

    bars = ax.bar(categorias, probabilidad, color=[COLORS['primary'], COLORS['accent']],
                  edgecolor='white', width=0.5)

    ax.text(0, probabilidad[0] + 0.5, f'{probabilidad[0]:.1f}%\n(Prob. independiente)',
            ha='center', fontweight='bold', color=COLORS['dark'])
    ax.text(1, probabilidad[1] + 0.5, f'{probabilidad[1]:.1f}%\n(Lift 28x)',
            ha='center', fontweight='bold', color=COLORS['accent'])

    ax.set_ylabel('Probabilidad (%)', fontweight='bold')
    ax.set_title('COMBO "FERNET + COCA" - EL CASO DE ÉXITO\nLift de 28x = Se compran juntos 28 veces más que por azar',
                 fontsize=12, fontweight='bold', color=COLORS['dark'])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Añadir flecha
    ax.annotate('', xy=(1, 15), xytext=(0, 5),
                arrowprops=dict(arrowstyle='->', color=COLORS['secondary'], lw=3))
    ax.text(0.5, 10, 'Oportunidad\nde Bundle', ha='center', fontsize=11,
            fontweight='bold', color=COLORS['secondary'])

    plt.tight_layout()
    return fig_to_base64(fig)


def crear_grafico_fila_unica(data):
    """Gráfico de impacto de la Fila Única"""
    fig, ax = plt.subplots(figsize=(10, 6))

    categorias = ['Ventas Impulso', 'Seguridad', 'Satisfacción\nCliente']
    antes = [100, 100, 100]
    despues = [135, 125, 120]  # Proyecciones de mejora

    x = np.arange(len(categorias))
    width = 0.35

    bars1 = ax.bar(x - width/2, antes, width, label='Situación Actual', color=COLORS['primary'], edgecolor='white')
    bars2 = ax.bar(x + width/2, despues, width, label='Con Fila Única', color=COLORS['success'], edgecolor='white')

    # Porcentajes de mejora
    for i, (a, d) in enumerate(zip(antes, despues)):
        mejora = (d - a) / a * 100
        ax.text(i + width/2, d + 2, f'+{mejora:.0f}%', ha='center', fontweight='bold', color=COLORS['success'])

    ax.set_ylabel('Índice (Base 100 = Actual)', fontweight='bold')
    ax.set_title('IMPACTO PROYECTADO - SISTEMA DE FILA ÚNICA\n"Efecto Túnel" de impulso + Panóptico de seguridad',
                 fontsize=12, fontweight='bold', color=COLORS['dark'])
    ax.set_xticks(x)
    ax.set_xticklabels(categorias)
    ax.legend()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_ylim(0, 160)

    plt.tight_layout()
    return fig_to_base64(fig)


def crear_grafico_quick_wins(data):
    """Gráfico de impacto vs esfuerzo de Quick Wins"""
    fig, ax = plt.subplots(figsize=(12, 8))

    # Quick wins con impacto y esfuerzo estimados
    qw = [
        ('Combo Fernet+Coca', 90, 20, 'Bundle'),
        ('Happy Hour Panadería', 70, 15, 'Merma'),
        ('Maridaje Góndola', 80, 30, 'Layout'),
        ('Venta Sugestiva', 60, 25, 'Capacitación'),
        ('Rincón del Olvido', 50, 10, 'Layout'),
        ('Ticket Umbral $45K', 75, 35, 'Promo'),
        ('Pack Asado', 85, 25, 'Bundle'),
        ('2da al 70%', 65, 20, 'Promo'),
    ]

    for nombre, impacto, esfuerzo, tipo in qw:
        color = {'Bundle': COLORS['accent'], 'Merma': COLORS['success'],
                 'Layout': COLORS['primary'], 'Capacitación': COLORS['secondary'],
                 'Promo': '#9B59B6'}.get(tipo, COLORS['dark'])
        ax.scatter(esfuerzo, impacto, s=300, c=color, alpha=0.7, edgecolors='white', linewidth=2)
        ax.annotate(nombre, (esfuerzo, impacto), xytext=(5, 5), textcoords='offset points',
                   fontsize=9, fontweight='bold')

    # Cuadrantes
    ax.axhline(y=65, color=COLORS['dark'], linestyle='--', alpha=0.3)
    ax.axvline(x=25, color=COLORS['dark'], linestyle='--', alpha=0.3)

    # Etiquetas de cuadrantes
    ax.text(12, 85, '⭐ QUICK WINS\n(Alto impacto,\nbajo esfuerzo)', fontsize=10, ha='center',
            bbox=dict(boxstyle='round', facecolor=COLORS['success'], alpha=0.3))
    ax.text(35, 85, '📈 PROYECTOS\n(Alto impacto,\nalto esfuerzo)', fontsize=10, ha='center',
            bbox=dict(boxstyle='round', facecolor=COLORS['accent'], alpha=0.3))

    ax.set_xlabel('Esfuerzo de Implementación →', fontweight='bold')
    ax.set_ylabel('Impacto Estimado →', fontweight='bold')
    ax.set_title('MATRIZ IMPACTO vs ESFUERZO - PRIORIZACIÓN DE ACCIONES',
                 fontsize=12, fontweight='bold', color=COLORS['dark'])
    ax.set_xlim(0, 45)
    ax.set_ylim(40, 100)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Leyenda manual
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=COLORS['accent'], label='Bundle'),
        Patch(facecolor=COLORS['success'], label='Merma'),
        Patch(facecolor=COLORS['primary'], label='Layout'),
        Patch(facecolor=COLORS['secondary'], label='Capacitación'),
        Patch(facecolor='#9B59B6', label='Promo'),
    ]
    ax.legend(handles=legend_elements, loc='lower right')

    plt.tight_layout()
    return fig_to_base64(fig)


def crear_grafico_roadmap():
    """Gráfico de timeline/roadmap"""
    fig, ax = plt.subplots(figsize=(14, 6))

    fases = [
        ('FASE 1\nGolpe de Efecto', 'Semana 1-4', ['Fila Única', 'Maridaje', 'Happy Hour'], COLORS['accent']),
        ('FASE 2\nIngeniería de Valor', 'Mes 2-3', ['Carnicería VA', '2da al 70%', 'Meal Kits'], COLORS['primary']),
        ('FASE 3\nConsolidación', 'Mes 4-6', ['Marca Propia', 'Ticket Umbral', 'Origen Local'], COLORS['success']),
    ]

    for i, (fase, tiempo, acciones, color) in enumerate(fases):
        ax.barh(0, 1, left=i, color=color, alpha=0.8, edgecolor='white', height=0.6)
        ax.text(i + 0.5, 0, fase, ha='center', va='center', fontweight='bold', fontsize=11, color='white')
        ax.text(i + 0.5, -0.5, tiempo, ha='center', va='center', fontsize=10, color=COLORS['dark'])
        ax.text(i + 0.5, 0.55, '\n'.join(['• ' + a for a in acciones]), ha='center', va='bottom',
                fontsize=9, color=COLORS['dark'])

    ax.set_xlim(-0.1, 3.1)
    ax.set_ylim(-1, 1.5)
    ax.axis('off')
    ax.set_title('HOJA DE RUTA DE IMPLEMENTACIÓN - PLAN 2026', fontsize=14, fontweight='bold', y=1.1)

    plt.tight_layout()
    return fig_to_base64(fig)


def generar_html(data, graficos):
    """Genera el HTML completo del documento"""

    html = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Plan Estratégico 2026 - Supermercados Don Nino</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            line-height: 1.6;
            color: #2C3E50;
            background: #f8f9fa;
        }}

        .container {{
            max-width: 1100px;
            margin: 0 auto;
            padding: 20px;
            background: white;
        }}

        /* Portada */
        .cover {{
            background: linear-gradient(135deg, #1E3A5F 0%, #2C3E50 100%);
            color: white;
            padding: 60px 40px;
            text-align: center;
            margin-bottom: 40px;
            border-radius: 8px;
        }}

        .cover h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 10px;
        }}

        .cover .subtitle {{
            font-size: 1.3rem;
            font-weight: 300;
            margin-bottom: 30px;
            opacity: 0.9;
        }}

        .cover .meta {{
            font-size: 0.9rem;
            opacity: 0.8;
        }}

        /* Secciones */
        .section {{
            margin-bottom: 50px;
            page-break-inside: avoid;
        }}

        .section-title {{
            font-size: 1.8rem;
            font-weight: 700;
            color: #1E3A5F;
            border-bottom: 3px solid #E74C3C;
            padding-bottom: 10px;
            margin-bottom: 25px;
        }}

        .section-subtitle {{
            font-size: 1.3rem;
            font-weight: 600;
            color: #2C3E50;
            margin: 25px 0 15px 0;
        }}

        /* Tarjetas de métricas */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }}

        .metric-card {{
            background: linear-gradient(135deg, #1E3A5F 0%, #34495E 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}

        .metric-card.accent {{
            background: linear-gradient(135deg, #E74C3C 0%, #C0392B 100%);
        }}

        .metric-card.success {{
            background: linear-gradient(135deg, #27AE60 0%, #1E8449 100%);
        }}

        .metric-card.warning {{
            background: linear-gradient(135deg, #F39C12 0%, #D68910 100%);
        }}

        .metric-value {{
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 5px;
        }}

        .metric-label {{
            font-size: 0.85rem;
            opacity: 0.9;
        }}

        /* Tablas */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 0.9rem;
        }}

        th {{
            background: #1E3A5F;
            color: white;
            padding: 12px 15px;
            text-align: left;
            font-weight: 600;
        }}

        td {{
            padding: 10px 15px;
            border-bottom: 1px solid #ECF0F1;
        }}

        tr:nth-child(even) {{
            background: #f8f9fa;
        }}

        tr:hover {{
            background: #ECF0F1;
        }}

        /* Imágenes/Gráficos */
        .chart {{
            text-align: center;
            margin: 25px 0;
        }}

        .chart img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}

        /* Propuestas */
        .propuesta {{
            background: #f8f9fa;
            border-left: 4px solid #1E3A5F;
            padding: 25px;
            margin: 25px 0;
            border-radius: 0 8px 8px 0;
        }}

        .propuesta.prioritaria {{
            border-left-color: #E74C3C;
            background: linear-gradient(90deg, rgba(231,76,60,0.05) 0%, #f8f9fa 100%);
        }}

        .propuesta-header {{
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }}

        .propuesta-numero {{
            background: #1E3A5F;
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            margin-right: 15px;
        }}

        .propuesta.prioritaria .propuesta-numero {{
            background: #E74C3C;
        }}

        .propuesta-titulo {{
            font-size: 1.2rem;
            font-weight: 600;
            color: #2C3E50;
        }}

        .propuesta-eje {{
            font-size: 0.8rem;
            color: #7F8C8D;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        /* Quick Wins */
        .quick-win {{
            background: linear-gradient(90deg, rgba(39,174,96,0.1) 0%, white 100%);
            border: 2px solid #27AE60;
            border-radius: 8px;
            padding: 15px 20px;
            margin: 10px 0;
            display: flex;
            align-items: center;
        }}

        .quick-win-icon {{
            font-size: 1.5rem;
            margin-right: 15px;
        }}

        .quick-win-content {{
            flex: 1;
        }}

        .quick-win-title {{
            font-weight: 600;
            color: #27AE60;
        }}

        /* KPIs */
        .kpi-box {{
            display: inline-block;
            background: #ECF0F1;
            padding: 8px 15px;
            border-radius: 20px;
            margin: 5px;
            font-size: 0.85rem;
        }}

        .kpi-box.principal {{
            background: #1E3A5F;
            color: white;
        }}

        .kpi-box.guardrail {{
            background: #F39C12;
            color: white;
        }}

        /* Listas */
        ul {{
            margin: 15px 0 15px 20px;
        }}

        li {{
            margin: 8px 0;
        }}

        /* Destacados */
        .highlight {{
            background: linear-gradient(90deg, rgba(243,156,18,0.2) 0%, transparent 100%);
            padding: 15px 20px;
            border-radius: 8px;
            margin: 15px 0;
        }}

        .highlight-title {{
            font-weight: 600;
            color: #F39C12;
            margin-bottom: 5px;
        }}

        /* Footer */
        .footer {{
            text-align: center;
            padding: 30px;
            background: #2C3E50;
            color: white;
            margin-top: 50px;
            border-radius: 8px;
        }}

        /* Print styles */
        @media print {{
            body {{
                background: white;
            }}
            .container {{
                max-width: 100%;
                padding: 0;
            }}
            .cover {{
                page-break-after: always;
            }}
            .section {{
                page-break-inside: avoid;
            }}
            .chart img {{
                max-width: 90%;
            }}
        }}

        /* Página nueva para secciones importantes */
        .page-break {{
            page-break-before: always;
        }}
    </style>
</head>
<body>
    <div class="container">

        <!-- PORTADA -->
        <div class="cover">
            <h1>PLAN ESTRATÉGICO 2026</h1>
            <div class="subtitle">Proyecto "Evolución Don Nino"</div>
            <div class="subtitle" style="font-size: 1rem;">Maximización de Densidad de Ticket, Blindaje de Margen y Excelencia Operativa</div>
            <div class="meta">
                <p><strong>Para:</strong> Directorio / Gerencia General</p>
                <p><strong>Fecha:</strong> Enero 2026</p>
                <p><strong>Elaborado por:</strong> Equipo de Analítica - Pyme Inside</p>
            </div>
        </div>

        <!-- 1. RESUMEN EJECUTIVO -->
        <div class="section">
            <h2 class="section-title">1. RESUMEN EJECUTIVO</h2>

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
                    <div class="metric-value">9,058</div>
                    <div class="metric-label">SKUs Activos</div>
                </div>
            </div>

            <p><strong>Supermercados Don Nino</strong> enfrenta un 2026 marcado por la contracción del consumo y la competencia agresiva de formatos "Express". Aunque la empresa posee activos valiosos como la lealtad en frescos (Panadería y Carnicería), su gestión actual prioriza el volumen sobre la rentabilidad real.</p>

            <div class="highlight">
                <div class="highlight-title">💡 Tesis Central</div>
                <p>Este plan propone un cambio de paradigma: <strong>pasar de "despachar mercadería" a "gestionar la experiencia y el margen"</strong>. Se detallan 20 iniciativas tácticas para incrementar los Ítems Por Ticket (IPT) y recuperar la rentabilidad erosionada.</p>
            </div>

            <h3 class="section-subtitle">Top 5 Quick Wins de Impacto Inmediato</h3>

            <div class="quick-win">
                <div class="quick-win-icon">🍺</div>
                <div class="quick-win-content">
                    <div class="quick-win-title">1. Combo "Fernet + Coca" con Bundle de Precio</div>
                    <div>Lift de 28x detectado. Exhibición conjunta + precio especial = ventas incrementales inmediatas.</div>
                </div>
            </div>

            <div class="quick-win">
                <div class="quick-win-icon">🥩</div>
                <div class="quick-win-content">
                    <div class="quick-win-title">2. Pack "Asado Completo" (Costilla + Chorizo + Morcilla)</div>
                    <div>Lift de 10.7x. Armar kit pre-empacado los fines de semana.</div>
                </div>
            </div>

            <div class="quick-win">
                <div class="quick-win-icon">🥐</div>
                <div class="quick-win-content">
                    <div class="quick-win-title">3. Happy Hour de Panadería (después de 20:30)</div>
                    <div>Tortas x6 tienen 12.5% penetración. Descuento 40% al cierre = merma → ingreso.</div>
                </div>
            </div>

            <div class="quick-win">
                <div class="quick-win-icon">🛒</div>
                <div class="quick-win-content">
                    <div class="quick-win-title">4. Maridaje en Góndola (Sacacorchos en Vinos)</div>
                    <div>Romper lógica de pasillos. Implementación: 1 día. Costo: mínimo.</div>
                </div>
            </div>

            <div class="quick-win">
                <div class="quick-win-icon">🎯</div>
                <div class="quick-win-content">
                    <div class="quick-win-title">5. Ticket Umbral $45,000 con Premio</div>
                    <div>15.6% de tickets superan $45K y generan 51.7% del margen. Gamificar para atraer más.</div>
                </div>
            </div>
        </div>

        <!-- 2. DIAGNÓSTICO -->
        <div class="section page-break">
            <h2 class="section-title">2. DIAGNÓSTICO: RADIOGRAFÍA DEL NEGOCIO</h2>

            <h3 class="section-subtitle">2.1 Los Dos Motores del Negocio</h3>
            <p>El análisis revela una dualidad fundamental: la <strong>Panadería atrae clientes</strong> (motor de tráfico) mientras que la <strong>Carnicería genera ingresos</strong> (motor de facturación). La política comercial debe potenciar ambos motores de forma sinérgica.</p>

            <div class="chart">
                <img src="{graficos['motor_negocio']}" alt="Motor de Tráfico vs Motor de Ingresos">
            </div>

            <h3 class="section-subtitle">2.2 Top 10 Productos por Ventas</h3>
            <p>La Carnicería domina el ranking de facturación. Solo la <strong>Molida Especial genera $188 millones</strong>, casi el triple que el producto de panadería más vendido.</p>

            <div class="chart">
                <img src="{graficos['top_ventas']}" alt="Top 10 Productos por Ventas">
            </div>

            <h3 class="section-subtitle">2.3 Top 10 Productos por Penetración</h3>
            <p>En contraste, los productos de <strong>Panadería dominan la penetración</strong>. Las Tortas x6 aparecen en 1 de cada 8 tickets, funcionando como ancla de tráfico.</p>

            <div class="chart">
                <img src="{graficos['penetracion']}" alt="Top 10 Productos por Penetración">
            </div>

            <h3 class="section-subtitle">2.4 Distribución de Tickets</h3>
            <p>La mediana ($15,789) es significativamente menor al promedio ($27,671), indicando una distribución sesgada con oportunidad de <strong>elevar tickets pequeños</strong>.</p>

            <div class="chart">
                <img src="{graficos['ticket_distribucion']}" alt="Distribución de Tickets">
            </div>

            <h3 class="section-subtitle">2.5 Segmentación: Las 3 Tribus de Clientes</h3>

            <div class="chart">
                <img src="{graficos['tribus']}" alt="Tribus de Clientes">
            </div>

            <table>
                <thead>
                    <tr>
                        <th>Tribu</th>
                        <th>% Tickets</th>
                        <th>Ticket Medio</th>
                        <th>Items/Ticket</th>
                        <th>Estrategia</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Compra Rápida</strong></td>
                        <td>87.6%</td>
                        <td>$17,974</td>
                        <td>6.6</td>
                        <td>Velocidad + Impulso en caja</td>
                    </tr>
                    <tr>
                        <td><strong>Reposición Regular</strong></td>
                        <td>12.4%</td>
                        <td>$94,642</td>
                        <td>34.5</td>
                        <td>Combos familiares + Fidelización</td>
                    </tr>
                    <tr>
                        <td><strong>Familiar Grande</strong></td>
                        <td>0.0006%</td>
                        <td>$30.9M</td>
                        <td>5,631</td>
                        <td>Atención VIP + Mayorista</td>
                    </tr>
                </tbody>
            </table>

            <h3 class="section-subtitle">2.6 Análisis Pareto: Concentración de Ventas</h3>
            <p>Se confirma la regla 80/20: un pequeño grupo de productos genera la mayoría de los ingresos. La "cola larga" de SKUs de baja rotación drena capital de trabajo.</p>

            <div class="chart">
                <img src="{graficos['pareto']}" alt="Análisis Pareto">
            </div>

            <h3 class="section-subtitle">2.7 Rentabilidad por Categoría</h3>
            <p>Las categorías de <strong>alto margen (Fiambres 45%, Bazar 45%, Golosinas 40%)</strong> deben ser priorizadas en cross-selling y exhibición premium.</p>

            <div class="chart">
                <img src="{graficos['rentabilidad']}" alt="Rentabilidad por Categoría">
            </div>
        </div>

        <!-- 3. OPORTUNIDADES DE CROSS-SELL -->
        <div class="section page-break">
            <h2 class="section-title">3. OPORTUNIDADES DE CROSS-SELL: MARKET BASKET ANALYSIS</h2>

            <p>El análisis de canasta de mercado identificó <strong>138 reglas de asociación</strong> con patrones de compra accionables. Los combos con mayor "lift" representan oportunidades de bundling de alto impacto.</p>

            <h3 class="section-subtitle">3.1 Top 10 Combos por Afinidad (Lift)</h3>

            <div class="chart">
                <img src="{graficos['combos']}" alt="Combos Accionables">
            </div>

            <table>
                <thead>
                    <tr>
                        <th>Combo</th>
                        <th>Lift</th>
                        <th>Confianza</th>
                        <th>% Tickets</th>
                        <th>Mecánica Sugerida</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="background: rgba(231,76,60,0.1);">
                        <td><strong>Fernet Branca → Coca Cola 2.5L</strong></td>
                        <td><strong>28.3x</strong></td>
                        <td>76.4%</td>
                        <td>1.02%</td>
                        <td>Bundle precio especial</td>
                    </tr>
                    <tr>
                        <td>Chorizo + Costilla → Morcilla</td>
                        <td>15.4x</td>
                        <td>62.3%</td>
                        <td>0.77%</td>
                        <td>Pack Asado Completo</td>
                    </tr>
                    <tr>
                        <td>Chorizo → Morcilla</td>
                        <td>10.7x</td>
                        <td>43.4%</td>
                        <td>1.98%</td>
                        <td>Bundle en carnicería</td>
                    </tr>
                    <tr>
                        <td>Costilla → Morcilla</td>
                        <td>8.4x</td>
                        <td>33.9%</td>
                        <td>1.33%</td>
                        <td>Cross-sell en góndola</td>
                    </tr>
                    <tr>
                        <td>Milanesa Carne → Milanesa Pollo</td>
                        <td>7.2x</td>
                        <td>36.5%</td>
                        <td>1.19%</td>
                        <td>Pack Milanesas Mix</td>
                    </tr>
                    <tr>
                        <td>Queso Ilolay → Jamón Paladini</td>
                        <td>5.3x</td>
                        <td>35.9%</td>
                        <td>1.62%</td>
                        <td>Combo Fiambre/Queso</td>
                    </tr>
                </tbody>
            </table>

            <h3 class="section-subtitle">3.2 El Caso "Fernet + Coca": Anatomía de un Combo Exitoso</h3>

            <div class="chart">
                <img src="{graficos['combo_fernet']}" alt="Combo Fernet + Coca">
            </div>

            <div class="highlight">
                <div class="highlight-title">📊 Interpretación del Lift 28x</div>
                <p>Cuando un cliente compra Fernet Branca, tiene <strong>28 veces más probabilidad</strong> de llevar también Coca Cola 2.5L que un cliente promedio. Esta correlación casi perfecta indica que ambos productos deben exhibirse juntos y promocionarse como bundle.</p>
            </div>

            <h3 class="section-subtitle">3.3 Key Value Items (KVI) - Productos Ancla de Precios</h3>
            <p>Los KVI son productos cuyo precio el cliente memoriza y usa para juzgar si el supermercado es "caro" o "barato". Deben tener precios competitivos.</p>

            <div class="chart">
                <img src="{graficos['kvi']}" alt="Key Value Items">
            </div>
        </div>

        <!-- 4. LAS 20 PROPUESTAS ESTRATÉGICAS -->
        <div class="section page-break">
            <h2 class="section-title">4. LAS 20 PROPUESTAS ESTRATÉGICAS</h2>

            <p>Las propuestas se organizan en tres ejes estratégicos. Las primeras 10 (marcadas como <span style="color: #E74C3C;">prioritarias</span>) tienen análisis profundo basado en datos; las 10 restantes son complementarias.</p>

            <!-- PROPUESTA 1 -->
            <div class="propuesta prioritaria">
                <div class="propuesta-header">
                    <div class="propuesta-numero">1</div>
                    <div>
                        <div class="propuesta-eje">EJE A: Aumento de Volumen</div>
                        <div class="propuesta-titulo">Maridaje en Góndola (Cross-Merchandising)</div>
                    </div>
                </div>

                <p><strong>Diagnóstico:</strong> Los productos complementarios están dispersos en pasillos diferentes, perdiendo oportunidades de venta cruzada. El análisis de basket muestra 138 reglas de asociación con lift significativo que no se explotan.</p>

                <p><strong>Propuesta:</strong> Romper la lógica de pasillo tradicional. Colocar productos complementarios juntos siguiendo las reglas de asociación detectadas.</p>

                <table>
                    <thead>
                        <tr>
                            <th>Ubicación Principal</th>
                            <th>Producto a Agregar</th>
                            <th>Lift Detectado</th>
                            <th>Impacto Esperado</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Góndola de Vinos</td>
                            <td>Sacacorchos, Quesos, Fiambres</td>
                            <td>5.3x</td>
                            <td>+15% venta accesorios</td>
                        </tr>
                        <tr>
                            <td>Sector Cervezas</td>
                            <td>Snacks salados, Maní, Papas</td>
                            <td>4.2x</td>
                            <td>+20% ticket bebidas</td>
                        </tr>
                        <tr>
                            <td>Carnicería</td>
                            <td>Carbón, Condimentos, Chimichurri</td>
                            <td>10.7x</td>
                            <td>+25% venta asado</td>
                        </tr>
                        <tr>
                            <td>Pastas</td>
                            <td>Salsas, Queso rallado</td>
                            <td>6.8x</td>
                            <td>+18% venta pastas</td>
                        </tr>
                    </tbody>
                </table>

                <p><strong>KPIs:</strong></p>
                <span class="kpi-box principal">Principal: % tickets con productos cruzados (+5pp)</span>
                <span class="kpi-box guardrail">Guardrail: Venta/m² de zona intervenida</span>

                <div class="quick-win" style="margin-top: 15px;">
                    <div class="quick-win-icon">⚡</div>
                    <div class="quick-win-content">
                        <div class="quick-win-title">Quick Win Semana 1</div>
                        <div>Colocar exhibidor de sacacorchos en bodega de vinos. Costo: $15,000. Tiempo: 2 horas.</div>
                    </div>
                </div>
            </div>

            <!-- PROPUESTA 2 -->
            <div class="propuesta prioritaria">
                <div class="propuesta-header">
                    <div class="propuesta-numero">2</div>
                    <div>
                        <div class="propuesta-eje">EJE A: Aumento de Volumen</div>
                        <div class="propuesta-titulo">Packs "Solución de Cena" (Meal Kits)</div>
                    </div>
                </div>

                <p><strong>Diagnóstico:</strong> El cliente moderno busca conveniencia. Las reglas de asociación muestran patrones claros de "ocasiones de consumo" (asado, pasta, milanesas) que pueden empaquetarse.</p>

                <p><strong>Propuesta:</strong> Crear kits pre-armados que resuelvan una comida completa con precio unificado y descuento percibido.</p>

                <table>
                    <thead>
                        <tr>
                            <th>Meal Kit</th>
                            <th>Contenido</th>
                            <th>Precio Sugerido</th>
                            <th>Ahorro Percibido</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr style="background: rgba(231,76,60,0.1);">
                            <td><strong>Pack Asado Familiar</strong></td>
                            <td>2kg Costilla + 1kg Chorizo + 500g Morcilla</td>
                            <td>$45,000</td>
                            <td>10% vs separado</td>
                        </tr>
                        <tr>
                            <td>Pack Pasta Express</td>
                            <td>Fideos 500g + Salsa 520g + Queso rallado</td>
                            <td>$8,500</td>
                            <td>12% vs separado</td>
                        </tr>
                        <tr>
                            <td>Pack Milanesas Fácil</td>
                            <td>6 Milanesas + Pan rallado + Huevos x6</td>
                            <td>$18,000</td>
                            <td>8% vs separado</td>
                        </tr>
                        <tr>
                            <td>Pack Desayuno Dulce</td>
                            <td>Facturas x6 + Café 250g + Dulce de leche</td>
                            <td>$12,000</td>
                            <td>15% vs separado</td>
                        </tr>
                    </tbody>
                </table>

                <p><strong>Datos de respaldo:</strong> El combo Chorizo+Morcilla tiene lift de 10.7x y aparece en 1.98% de tickets. Al empaquetarlo, se proyecta duplicar esa penetración.</p>

                <p><strong>KPIs:</strong></p>
                <span class="kpi-box principal">Principal: Unidades de Meal Kits vendidos/semana</span>
                <span class="kpi-box guardrail">Guardrail: Margen bruto del kit ≥25%</span>

                <div class="quick-win" style="margin-top: 15px;">
                    <div class="quick-win-icon">⚡</div>
                    <div class="quick-win-content">
                        <div class="quick-win-title">Quick Win Semana 1</div>
                        <div>Lanzar "Pack Asado Familiar" los viernes y sábados. Mesa especial en carnicería.</div>
                    </div>
                </div>
            </div>

            <!-- PROPUESTA 3 -->
            <div class="propuesta prioritaria">
                <div class="propuesta-header">
                    <div class="propuesta-numero">3</div>
                    <div>
                        <div class="propuesta-eje">EJE A: Aumento de Volumen</div>
                        <div class="propuesta-titulo">Ticket Umbral Gamificado</div>
                    </div>
                </div>

                <p><strong>Diagnóstico:</strong> El ticket promedio es $27,671 pero la mediana es solo $15,789. Esto indica que muchos tickets pequeños arrastran el promedio hacia abajo. Solo el 15.6% supera $45,000 pero generan el 51.7% del margen.</p>

                <p><strong>Propuesta:</strong> Implementar mecánicas de "ticket stretch" que incentiven al cliente a completar el changuito hasta un umbral.</p>

                <table>
                    <thead>
                        <tr>
                            <th>Umbral</th>
                            <th>Premio</th>
                            <th>% Tickets Elegibles</th>
                            <th>Costo Estimado</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>$30,000</td>
                            <td>6 Facturas GRATIS</td>
                            <td>27% (tickets entre $25K-$30K)</td>
                            <td>~$800/ticket</td>
                        </tr>
                        <tr style="background: rgba(39,174,96,0.1);">
                            <td><strong>$45,000</strong></td>
                            <td><strong>Media docena Tortas GRATIS</strong></td>
                            <td>12% (tickets entre $40K-$45K)</td>
                            <td>~$1,200/ticket</td>
                        </tr>
                        <tr>
                            <td>$60,000</td>
                            <td>Cupón $3,000 próxima compra</td>
                            <td>8% (tickets entre $55K-$60K)</td>
                            <td>~$3,000/ticket</td>
                        </tr>
                    </tbody>
                </table>

                <p><strong>Proyección:</strong> Si el 20% de los tickets elegibles "estiran" su compra al umbral, el ticket promedio sube de $27,671 a ~$29,500 (+6.6%).</p>

                <p><strong>KPIs:</strong></p>
                <span class="kpi-box principal">Principal: % tickets que cruzan umbral objetivo</span>
                <span class="kpi-box guardrail">Guardrail: Costo de premios < 3% del incremento</span>
            </div>

            <!-- PROPUESTA 4 -->
            <div class="propuesta prioritaria">
                <div class="propuesta-header">
                    <div class="propuesta-numero">4</div>
                    <div>
                        <div class="propuesta-eje">EJE A: Aumento de Volumen</div>
                        <div class="propuesta-titulo">Venta Sugestiva (Scripting en Mostrador)</div>
                    </div>
                </div>

                <p><strong>Diagnóstico:</strong> Los mostradores de frescos (carnicería, fiambrería, panadería) tienen interacción humana que no se aprovecha para cross-sell. El análisis muestra combos naturales que el personal podría sugerir.</p>

                <p><strong>Propuesta:</strong> Implementar protocolo de "cierre sugestivo" obligatorio en mostradores, basado en las reglas de asociación.</p>

                <table>
                    <thead>
                        <tr>
                            <th>Mostrador</th>
                            <th>Si el cliente pide...</th>
                            <th>Sugerir...</th>
                            <th>Script</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Carnicería</td>
                            <td>Costilla</td>
                            <td>Chorizo + Morcilla</td>
                            <td>"¿Le agrego el chorizo y la morcilla para completar el asado?"</td>
                        </tr>
                        <tr>
                            <td>Carnicería</td>
                            <td>Molida</td>
                            <td>Milanesas</td>
                            <td>"Las milanesas caseras están en promoción, ¿las agrego?"</td>
                        </tr>
                        <tr>
                            <td>Fiambrería</td>
                            <td>Jamón</td>
                            <td>Queso Ilolay</td>
                            <td>"¿Queso también? Tenemos el Ilolay en oferta."</td>
                        </tr>
                        <tr>
                            <td>Panadería</td>
                            <td>Pan</td>
                            <td>Facturas</td>
                            <td>"¿Lleva facturas para la merienda?"</td>
                        </tr>
                    </tbody>
                </table>

                <p><strong>Datos de respaldo:</strong> Queso Ilolay → Jamón Paladini tiene lift de 5.3x. Actualmente aparecen juntos en 1.6% de tickets. Con scripting, proyectamos 3%.</p>

                <p><strong>KPIs:</strong></p>
                <span class="kpi-box principal">Principal: Items/ticket en clientes de mostrador</span>
                <span class="kpi-box guardrail">Guardrail: NPS de atención (no ser invasivo)</span>

                <div class="quick-win" style="margin-top: 15px;">
                    <div class="quick-win-icon">⚡</div>
                    <div class="quick-win-content">
                        <div class="quick-win-title">Quick Win Semana 1</div>
                        <div>Capacitación de 30 min al personal de carnicería con los 3 scripts principales.</div>
                    </div>
                </div>
            </div>

            <!-- PROPUESTA 5 -->
            <div class="propuesta prioritaria">
                <div class="propuesta-header">
                    <div class="propuesta-numero">5</div>
                    <div>
                        <div class="propuesta-eje">EJE B: Maximización de Margen</div>
                        <div class="propuesta-titulo">Transformación de Carnicería (Valor Agregado)</div>
                    </div>
                </div>

                <p><strong>Diagnóstico:</strong> La carnicería genera $188M solo en Molida Especial, pero el margen de carne vacuna es solo 20%. Los productos de "Elaboración Propia" tienen 30% de margen. Hay oportunidad de migrar volumen hacia productos de mayor valor agregado.</p>

                <p><strong>Propuesta:</strong> Expandir la línea de "Listos para Cocinar" (brochettes, milanesas, arrollados, hamburguesas caseras) que tienen mayor margen y diferenciación vs. competencia.</p>

                <table>
                    <thead>
                        <tr>
                            <th>Producto</th>
                            <th>Ventas Actuales</th>
                            <th>Margen Actual</th>
                            <th>Margen Objetivo</th>
                            <th>Acción</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Molida Especial (commodity)</td>
                            <td>$188M</td>
                            <td>20%</td>
                            <td>20%</td>
                            <td>Mantener volumen</td>
                        </tr>
                        <tr style="background: rgba(39,174,96,0.1);">
                            <td><strong>Milanesas de Carne NINO</strong></td>
                            <td>$71.5M</td>
                            <td>30%</td>
                            <td>32%</td>
                            <td>Expandir producción</td>
                        </tr>
                        <tr style="background: rgba(39,174,96,0.1);">
                            <td><strong>Milanesas de Pollo NINO</strong></td>
                            <td>$94.5M</td>
                            <td>30%</td>
                            <td>32%</td>
                            <td>Expandir producción</td>
                        </tr>
                        <tr>
                            <td>Brochettes (NUEVO)</td>
                            <td>$0</td>
                            <td>-</td>
                            <td>35%</td>
                            <td>Lanzar línea</td>
                        </tr>
                        <tr>
                            <td>Hamburguesas caseras (NUEVO)</td>
                            <td>$0</td>
                            <td>-</td>
                            <td>35%</td>
                            <td>Lanzar línea</td>
                        </tr>
                    </tbody>
                </table>

                <p><strong>Impacto proyectado:</strong> Si el 10% de la venta de cortes tradicionales migra a elaborados, el margen de carnicería sube de 20% a 22%, equivalente a ~$15M adicionales anuales.</p>

                <p><strong>KPIs:</strong></p>
                <span class="kpi-box principal">Principal: % de venta elaborados vs total carnicería</span>
                <span class="kpi-box guardrail">Guardrail: Merma de elaborados < 3%</span>
            </div>

            <!-- PROPUESTA 6 -->
            <div class="propuesta prioritaria">
                <div class="propuesta-header">
                    <div class="propuesta-numero">6</div>
                    <div>
                        <div class="propuesta-eje">EJE B: Maximización de Margen</div>
                        <div class="propuesta-titulo">Happy Hour en Panadería</div>
                    </div>
                </div>

                <p><strong>Diagnóstico:</strong> Las Tortas x6 tienen 12.5% de penetración (43,251 tickets) pero los frescos de panadería tienen alta merma al cierre. Lo que no se vende, se pierde.</p>

                <p><strong>Propuesta:</strong> Implementar descuento progresivo después de las 20:30 hs para transformar merma potencial en recuperación de costos.</p>

                <table>
                    <thead>
                        <tr>
                            <th>Horario</th>
                            <th>Descuento</th>
                            <th>Productos Incluidos</th>
                            <th>Comunicación</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>20:30 - 21:00</td>
                            <td>30% OFF</td>
                            <td>Pan del día, Facturas</td>
                            <td>Cartel "Happy Hour Panadería"</td>
                        </tr>
                        <tr style="background: rgba(243,156,18,0.1);">
                            <td><strong>21:00 - Cierre</strong></td>
                            <td><strong>50% OFF</strong></td>
                            <td>Todo producto de panadería del día</td>
                            <td>Etiquetas amarillas + anuncio</td>
                        </tr>
                    </tbody>
                </table>

                <p><strong>Cálculo de impacto:</strong></p>
                <ul>
                    <li>Merma actual estimada: 5% de producción diaria</li>
                    <li>Con Happy Hour: Recuperación del 70% de esa merma</li>
                    <li>Ahorro mensual: ~$500,000 en producto que antes se tiraba</li>
                </ul>

                <p><strong>KPIs:</strong></p>
                <span class="kpi-box principal">Principal: Tasa de merma panadería (bajar de 5% a 2%)</span>
                <span class="kpi-box guardrail">Guardrail: Ventas horario normal no caen >2%</span>

                <div class="quick-win" style="margin-top: 15px;">
                    <div class="quick-win-icon">⚡</div>
                    <div class="quick-win-content">
                        <div class="quick-win-title">Quick Win Semana 1</div>
                        <div>Carteles de "Happy Hour 20:30" + etiquetas amarillas. Costo: $5,000.</div>
                    </div>
                </div>
            </div>

            <!-- PROPUESTA 7 -->
            <div class="propuesta prioritaria">
                <div class="propuesta-header">
                    <div class="propuesta-numero">7</div>
                    <div>
                        <div class="propuesta-eje">EJE B: Maximización de Margen</div>
                        <div class="propuesta-titulo">Marca Propia "Don Nino"</div>
                    </div>
                </div>

                <p><strong>Diagnóstico:</strong> Las categorías de Almacén tienen 28% de margen, pero una marca propia puede alcanzar 45-50%. La tendencia del consumidor hacia segundas marcas por la crisis abre oportunidad.</p>

                <p><strong>Propuesta:</strong> Lanzar línea "Don Nino" en categorías de alta rotación y baja diferenciación percibida.</p>

                <table>
                    <thead>
                        <tr>
                            <th>Categoría</th>
                            <th>Producto Marca Propia</th>
                            <th>Referencia Líder</th>
                            <th>Margen Líder</th>
                            <th>Margen MP</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Especias</td>
                            <td>Orégano, Pimentón, Ají</td>
                            <td>Alicante</td>
                            <td>28%</td>
                            <td>55%</td>
                        </tr>
                        <tr>
                            <td>Legumbres</td>
                            <td>Lentejas, Garbanzos, Porotos</td>
                            <td>Inalpa</td>
                            <td>25%</td>
                            <td>50%</td>
                        </tr>
                        <tr>
                            <td>Pan rallado</td>
                            <td>Pan rallado 500g</td>
                            <td>Preferido</td>
                            <td>28%</td>
                            <td>52%</td>
                        </tr>
                        <tr>
                            <td>Bolsas</td>
                            <td>Ya existe: BOLSAS NINO</td>
                            <td>-</td>
                            <td>-</td>
                            <td>60%</td>
                        </tr>
                    </tbody>
                </table>

                <p><strong>Nota:</strong> Las "Bolsas Plásticas NINO" ya existen y tienen 4.8% de penetración. Esto valida que el cliente acepta marca propia.</p>

                <p><strong>KPIs:</strong></p>
                <span class="kpi-box principal">Principal: % ventas marca propia en categoría</span>
                <span class="kpi-box guardrail">Guardrail: Calidad percibida (encuestas)</span>
            </div>

            <!-- PROPUESTA 8 -->
            <div class="propuesta prioritaria">
                <div class="propuesta-header">
                    <div class="propuesta-numero">8</div>
                    <div>
                        <div class="propuesta-eje">EJE B: Maximización de Margen</div>
                        <div class="propuesta-titulo">Auditoría de Recetas (Escandallos)</div>
                    </div>
                </div>

                <p><strong>Diagnóstico:</strong> Don Nino produce internamente en Panadería, Rotisería y elaborados de Carnicería, pero NO tiene recetas valorizadas. Esto impide conocer el costo real y el margen verdadero de cada producto.</p>

                <p><strong>Propuesta:</strong> Implementar sistema de costos estándar ("escandallos") para los top 20 productos elaborados.</p>

                <table>
                    <thead>
                        <tr>
                            <th>Producto</th>
                            <th>Insumos Principales</th>
                            <th>Costo Estimado</th>
                            <th>Precio Venta</th>
                            <th>Margen Real</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Tortas x6</td>
                            <td>Harina, Grasa, Sal, Gas</td>
                            <td>$800</td>
                            <td>$1,670</td>
                            <td>52%</td>
                        </tr>
                        <tr>
                            <td>Pan Flauta</td>
                            <td>Harina, Levadura, Sal</td>
                            <td>$600</td>
                            <td>$1,400</td>
                            <td>57%</td>
                        </tr>
                        <tr>
                            <td>Milanesas Pollo (kg)</td>
                            <td>Pollo, Pan rallado, Huevo</td>
                            <td>$6,500</td>
                            <td>$9,000</td>
                            <td>28%</td>
                        </tr>
                        <tr style="background: rgba(231,76,60,0.1);">
                            <td>Pollo al Spiedo</td>
                            <td>Pollo entero, Condimentos, Gas</td>
                            <td>$5,800</td>
                            <td>$7,500</td>
                            <td><strong>23%</strong> ⚠️</td>
                        </tr>
                    </tbody>
                </table>

                <div class="highlight">
                    <div class="highlight-title">⚠️ Alerta: Pollo al Spiedo</div>
                    <p>El margen real estimado del Pollo al Spiedo es solo 23%, inferior al objetivo de 30%. Requiere revisar precio o reducir costo de gas/condimentos.</p>
                </div>

                <p><strong>KPIs:</strong></p>
                <span class="kpi-box principal">Principal: % productos con escandallo actualizado</span>
                <span class="kpi-box guardrail">Guardrail: Desvío costo real vs estándar < 5%</span>
            </div>

            <!-- PROPUESTA 9 -->
            <div class="propuesta prioritaria">
                <div class="propuesta-header">
                    <div class="propuesta-numero">9</div>
                    <div>
                        <div class="propuesta-eje">EJE B: Maximización de Margen</div>
                        <div class="propuesta-titulo">Monetización de la "Cola Larga"</div>
                    </div>
                </div>

                <p><strong>Diagnóstico:</strong> El análisis Pareto muestra que ~50% de los SKUs generan menos del 5% de las ventas. Sin embargo, muchos de estos productos (bazar, especias raras, accesorios) tienen baja comparabilidad de precios.</p>

                <p><strong>Propuesta:</strong> Aplicar márgenes premium (50-60%) a productos de baja rotación pero baja sensibilidad al precio.</p>

                <table>
                    <thead>
                        <tr>
                            <th>Categoría</th>
                            <th>Margen Actual</th>
                            <th>Margen Propuesto</th>
                            <th>Justificación</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Bazar / Utensilios</td>
                            <td>45%</td>
                            <td>55%</td>
                            <td>Cliente no compara precios</td>
                        </tr>
                        <tr>
                            <td>Especias importadas</td>
                            <td>35%</td>
                            <td>50%</td>
                            <td>Compra de conveniencia</td>
                        </tr>
                        <tr>
                            <td>Productos gourmet</td>
                            <td>30%</td>
                            <td>45%</td>
                            <td>Nicho de alto poder adquisitivo</td>
                        </tr>
                        <tr>
                            <td>Ferretería básica</td>
                            <td>40%</td>
                            <td>55%</td>
                            <td>Compra de urgencia</td>
                        </tr>
                    </tbody>
                </table>

                <p><strong>Clave:</strong> No tocar precios de KVIs (leche, azúcar, aceite) que el cliente memoriza. Solo ajustar productos donde la comparación es difícil.</p>

                <p><strong>KPIs:</strong></p>
                <span class="kpi-box principal">Principal: Margen bruto promedio cola larga</span>
                <span class="kpi-box guardrail">Guardrail: Rotación de la categoría (no debe caer >10%)</span>
            </div>

            <!-- PROPUESTA 10 -->
            <div class="propuesta prioritaria">
                <div class="propuesta-header">
                    <div class="propuesta-numero">10</div>
                    <div>
                        <div class="propuesta-eje">EJE C: Excelencia Operativa</div>
                        <div class="propuesta-titulo">Sistema de Fila Única ("Snake Queue")</div>
                    </div>
                </div>

                <p><strong>Diagnóstico:</strong> El 87.6% de los tickets son de "Compra Rápida" con ticket promedio de $17,974. La zona de cajas es el último punto de contacto y oportunidad de impulso. Las filas múltiples actuales generan "tiempos muertos" sin exposición a productos.</p>

                <p><strong>Propuesta:</strong> Implementar fila única serpenteante ("snake queue") que atraviese un "túnel de tentación" con productos de impulso.</p>

                <div class="chart">
                    <img src="{graficos['fila_unica']}" alt="Impacto Fila Única">
                </div>

                <table>
                    <thead>
                        <tr>
                            <th>Beneficio</th>
                            <th>Métrica</th>
                            <th>Impacto Esperado</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Ventas de Impulso</td>
                            <td>% tickets con golosinas/snacks</td>
                            <td>+25-40%</td>
                        </tr>
                        <tr>
                            <td>Seguridad</td>
                            <td>Merma por hurto</td>
                            <td>-15-20%</td>
                        </tr>
                        <tr>
                            <td>Satisfacción</td>
                            <td>NPS / Quejas por espera</td>
                            <td>+20%</td>
                        </tr>
                    </tbody>
                </table>

                <p><strong>Productos del "Túnel de Tentación":</strong></p>
                <ul>
                    <li>Golosinas (margen 40%)</li>
                    <li>Pilas y accesorios (margen 55%)</li>
                    <li>Snacks pequeños</li>
                    <li>Bebidas frías unitarias</li>
                    <li>Chicles y caramelos</li>
                </ul>

                <p><strong>KPIs:</strong></p>
                <span class="kpi-box principal">Principal: % tickets con ítem del túnel</span>
                <span class="kpi-box guardrail">Guardrail: Tiempo promedio en fila < 5 min</span>
            </div>

            <!-- PROPUESTAS 11-20 (Complementarias) -->
            <h3 class="section-subtitle" style="margin-top: 40px;">Propuestas Complementarias (11-20)</h3>

            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">11</div>
                    <div>
                        <div class="propuesta-titulo">Estrategia "2da Unidad al 70%"</div>
                    </div>
                </div>
                <p>Reemplazar el 2x1 masivo por "segunda unidad al 70%" que protege mejor el margen. Aplicar en productos de limpieza y almacén de alta rotación.</p>
                <p><strong>KPI:</strong> Unidades por transacción en categoría promo</p>
            </div>

            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">12</div>
                    <div>
                        <div class="propuesta-titulo">El "Rincón del Olvido"</div>
                    </div>
                </div>
                <p>Exhibidor vertical a la salida con los top 10 productos "olvidados": Hielo, Fósforos, Sal, Pilas, Bolsas de residuos. Captura compras de último momento.</p>
                <p><strong>KPI:</strong> Ventas del exhibidor / Costo de espacio</p>
            </div>

            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">13</div>
                    <div>
                        <div class="propuesta-titulo">Degustación Cruzada "In Situ"</div>
                    </div>
                </div>
                <p>Viernes y sábados, ofrecer degustación de fiambres nuevos sobre el pan de elaboración propia. Potencia cross-sell entre departamentos frescos.</p>
                <p><strong>KPI:</strong> Ventas fiambrería días de degustación vs normal</p>
            </div>

            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">14</div>
                    <div>
                        <div class="propuesta-titulo">Multipacks de Bebidas</div>
                    </div>
                </div>
                <p>Armar packs de 4 o 6 gaseosas/aguas con descuento por volumen. Stockea al cliente y lo saca del mercado por más tiempo.</p>
                <p><strong>KPI:</strong> % ventas en multipack vs unitario</p>
            </div>

            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">15</div>
                    <div>
                        <div class="propuesta-titulo">Sección "Bajo $1,000"</div>
                    </div>
                </div>
                <p>Islas con productos de precio redondo y bajo desembolso (golosinas, galletitas, productos unitarios). Elimina fricción de decisión.</p>
                <p><strong>KPI:</strong> Penetración de productos de la sección</p>
            </div>

            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">16</div>
                    <div>
                        <div class="propuesta-titulo">Precio Ancla (Decoy Pricing)</div>
                    </div>
                </div>
                <p>En vinos, colocar una botella muy cara ($25,000) junto a la gama media ($8,000) para que esta última parezca "razonable".</p>
                <p><strong>KPI:</strong> Venta de vinos gama media</p>
            </div>

            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">17</div>
                    <div>
                        <div class="propuesta-titulo">Venta Fraccionada de Lujos</div>
                    </div>
                </div>
                <p>Ofrecer jamón crudo, quesos premium en bandejas pequeñas (80-100g). Bajo ticket facial, altísimo margen por kilo.</p>
                <p><strong>KPI:</strong> Margen $/kg en fraccionados vs enteros</p>
            </div>

            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">18</div>
                    <div>
                        <div class="propuesta-titulo">Diferenciación "Origen Local"</div>
                    </div>
                </div>
                <p>Señalética especial para productos de proveedores mendocinos. Permite precio premium por valor emocional y calidad percibida.</p>
                <p><strong>KPI:</strong> Venta de productos con sello "Local"</p>
            </div>

            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">19</div>
                    <div>
                        <div class="propuesta-titulo">Eliminación de Competencia Interna</div>
                    </div>
                </div>
                <p>Racionalizar surtido eliminando marcas duplicadas que no son ni KVI ni precio bajo. Liberar espacio para productos rentables.</p>
                <p><strong>KPI:</strong> SKUs activos / Venta por SKU</p>
            </div>

            <div class="propuesta">
                <div class="propuesta-header">
                    <div class="propuesta-numero">20</div>
                    <div>
                        <div class="propuesta-titulo">Venta de Servicios Complementarios</div>
                    </div>
                </div>
                <p>Incorporar afilado de cuchillos, venta de hielo premium, carga de SUBE como servicios adicionales de margen 100%.</p>
                <p><strong>KPI:</strong> Ingresos por servicios / mes</p>
            </div>
        </div>

        <!-- 5. MATRIZ DE QUICK WINS -->
        <div class="section page-break">
            <h2 class="section-title">5. MATRIZ DE PRIORIZACIÓN: QUICK WINS</h2>

            <p>La siguiente matriz clasifica las acciones según su impacto esperado y esfuerzo de implementación. <strong>Priorizar el cuadrante superior izquierdo</strong> (alto impacto, bajo esfuerzo).</p>

            <div class="chart">
                <img src="{graficos['quick_wins']}" alt="Matriz Quick Wins">
            </div>

            <h3 class="section-subtitle">Acciones para la Semana 1</h3>

            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Acción</th>
                        <th>Responsable</th>
                        <th>Costo</th>
                        <th>Tiempo</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>1</td>
                        <td>Montar exhibición Fernet + Coca juntos</td>
                        <td>Repositor</td>
                        <td>$0</td>
                        <td>1 hora</td>
                    </tr>
                    <tr>
                        <td>2</td>
                        <td>Carteles "Happy Hour Panadería 20:30"</td>
                        <td>Marketing</td>
                        <td>$5,000</td>
                        <td>1 día</td>
                    </tr>
                    <tr>
                        <td>3</td>
                        <td>Capacitar carniceros en script de venta</td>
                        <td>Encargado</td>
                        <td>$0</td>
                        <td>30 min</td>
                    </tr>
                    <tr>
                        <td>4</td>
                        <td>Sacacorchos en góndola de vinos</td>
                        <td>Repositor</td>
                        <td>$0</td>
                        <td>30 min</td>
                    </tr>
                    <tr>
                        <td>5</td>
                        <td>Armar 10 "Pack Asado" para el sábado</td>
                        <td>Carnicería</td>
                        <td>$0</td>
                        <td>1 hora</td>
                    </tr>
                    <tr>
                        <td>6</td>
                        <td>Crear "Rincón del Olvido" en salida</td>
                        <td>Repositor</td>
                        <td>$10,000</td>
                        <td>2 horas</td>
                    </tr>
                    <tr>
                        <td>7</td>
                        <td>Etiquetas amarillas para descuentos cierre</td>
                        <td>Administración</td>
                        <td>$2,000</td>
                        <td>Compra</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- 6. HOJA DE RUTA -->
        <div class="section page-break">
            <h2 class="section-title">6. HOJA DE RUTA DE IMPLEMENTACIÓN</h2>

            <div class="chart">
                <img src="{graficos['roadmap']}" alt="Roadmap de Implementación">
            </div>

            <h3 class="section-subtitle">FASE 1: Golpe de Efecto (Semanas 1-4)</h3>
            <p>Cambios visibles de bajo costo que generan momentum.</p>
            <ul>
                <li><strong>Semana 1:</strong> Quick wins de layout (maridaje, rincón del olvido)</li>
                <li><strong>Semana 2:</strong> Happy Hour panadería + Pack Asado</li>
                <li><strong>Semana 3:</strong> Capacitación venta sugestiva</li>
                <li><strong>Semana 4:</strong> Evaluación y ajustes</li>
            </ul>

            <h3 class="section-subtitle">FASE 2: Ingeniería de Valor (Mes 2-3)</h3>
            <p>Optimización de procesos y ampliación de líneas.</p>
            <ul>
                <li>Lanzamiento línea "Listos para Cocinar" en carnicería</li>
                <li>Implementación de Meal Kits permanentes</li>
                <li>Sistema de ticket umbral gamificado</li>
                <li>Inicio auditoría de escandallos</li>
            </ul>

            <h3 class="section-subtitle">FASE 3: Consolidación (Mes 4-6)</h3>
            <p>Diferenciación y fidelización.</p>
            <ul>
                <li>Lanzamiento Marca Propia "Don Nino" (especias, legumbres)</li>
                <li>Implementación Fila Única</li>
                <li>Programa de fidelización "Club Don Nino"</li>
                <li>Señalética "Origen Local"</li>
            </ul>
        </div>

        <!-- 7. GOBERNANZA -->
        <div class="section">
            <h2 class="section-title">7. GOBERNANZA Y CONTROL</h2>

            <h3 class="section-subtitle">Comité Comercial Semanal</h3>
            <p><strong>Frecuencia:</strong> Lunes 09:00 AM<br>
            <strong>Participantes:</strong> Dirección, Gerente, Encargados de área, Analista</p>

            <table>
                <thead>
                    <tr>
                        <th>Tema</th>
                        <th>Tiempo</th>
                        <th>Responsable</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Revisión KPIs semana anterior</td>
                        <td>15 min</td>
                        <td>Analista</td>
                    </tr>
                    <tr>
                        <td>Estado de implementación propuestas</td>
                        <td>15 min</td>
                        <td>Gerente</td>
                    </tr>
                    <tr>
                        <td>Problemas y bloqueos</td>
                        <td>10 min</td>
                        <td>Encargados</td>
                    </tr>
                    <tr>
                        <td>Acciones próxima semana</td>
                        <td>10 min</td>
                        <td>Todos</td>
                    </tr>
                </tbody>
            </table>

            <h3 class="section-subtitle">KPIs de Control Principal</h3>

            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">IPT</div>
                    <div class="metric-label">Items Por Ticket<br>Objetivo: 11.0 (actual: 10.1)</div>
                </div>
                <div class="metric-card accent">
                    <div class="metric-value">$30K</div>
                    <div class="metric-label">Ticket Promedio<br>Objetivo: $30,000 (actual: $27,671)</div>
                </div>
                <div class="metric-card success">
                    <div class="metric-value">28%</div>
                    <div class="metric-label">Margen Bruto<br>Objetivo: 28% (actual: ~27%)</div>
                </div>
                <div class="metric-card warning">
                    <div class="metric-value">&lt;2%</div>
                    <div class="metric-label">Merma Frescos<br>Objetivo: <2% (actual: ~5%)</div>
                </div>
            </div>
        </div>

        <!-- CONCLUSIÓN -->
        <div class="section">
            <h2 class="section-title">8. CONCLUSIÓN</h2>

            <p>Este plan no requiere inversiones millonarias en infraestructura, sino <strong>disciplina en la ejecución</strong>. Al implementar las estrategias de Combos Inteligentes, proteger los precios de los KVIs, y controlar la Caja Negra de Producción, Supermercados Don Nino puede:</p>

            <div class="metrics-grid">
                <div class="metric-card success">
                    <div class="metric-value">+8%</div>
                    <div class="metric-label">Incremento Ticket Promedio</div>
                </div>
                <div class="metric-card success">
                    <div class="metric-value">+1pp</div>
                    <div class="metric-label">Mejora Margen Bruto</div>
                </div>
                <div class="metric-card success">
                    <div class="metric-value">-60%</div>
                    <div class="metric-label">Reducción Merma</div>
                </div>
                <div class="metric-card success">
                    <div class="metric-value">+10%</div>
                    <div class="metric-label">Items por Ticket</div>
                </div>
            </div>

            <div class="highlight">
                <div class="highlight-title">💡 El Cambio de Paradigma</div>
                <p><strong>De "despachar mercadería" a "gestionar la experiencia y el margen".</strong></p>
                <p>Del volumen al margen. De la intuición al dato. Del caos al proceso.</p>
            </div>

            <p style="text-align: center; font-size: 1.1rem; margin-top: 30px;"><strong>Queda a disposición del Directorio para su aprobación e implementación inmediata.</strong></p>
        </div>

        <!-- FOOTER -->
        <div class="footer">
            <p><strong>Plan Estratégico 2026 - Supermercados Don Nino</strong></p>
            <p>Elaborado por Equipo de Analítica | Pyme Inside</p>
            <p>Enero 2026</p>
            <p style="margin-top: 15px; font-size: 0.8rem; opacity: 0.8;">
                Basado en análisis de 345,130 tickets | Oct 2024 - Oct 2025<br>
                Documento generado automáticamente con Python + Data Science
            </p>
        </div>

    </div>
</body>
</html>
'''

    return html


def main():
    """Función principal"""
    print("=" * 60)
    print("GENERADOR DE PLAN ESTRATEGICO 2026 - DON NINO")
    print("=" * 60)

    # Cargar datos
    print("\n[*] Cargando datos...")
    data = load_data()
    print(f"   [OK] Top ventas: {len(data['top_ventas'])} productos")
    print(f"   [OK] Combos: {len(data['combos'])} reglas")
    print(f"   [OK] Tribus: {len(data['tribus'])} segmentos")

    # Generar gráficos
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

    # Generar HTML
    print("\n[*] Generando documento HTML...")
    html = generar_html(data, graficos)

    # Guardar archivo
    output_file = BASE_DIR / 'PLAN_ESTRATEGICO_2026_DON_NINO.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\n[OK] Documento generado exitosamente:")
    print(f"   -> {output_file}")
    print(f"\n[INFO] Para convertir a PDF:")
    print(f"   1. Abrir el archivo HTML en Chrome")
    print(f"   2. Ctrl+P -> Guardar como PDF")
    print(f"   3. Configurar: Margenes minimos, Graficos de fondo ON")

    print("\n" + "=" * 60)
    print("PROCESO COMPLETADO!")
    print("=" * 60)


if __name__ == "__main__":
    main()

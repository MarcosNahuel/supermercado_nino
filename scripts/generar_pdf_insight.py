"""Genera PDF Infográfico - Insight Estratégico Rotisería & Panadería NINO"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

# Configuración visual
plt.rcParams['font.family'] = 'Segoe UI'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.facecolor'] = '#FAFAFA'
plt.rcParams['figure.facecolor'] = '#FFFFFF'

# Colores corporativos
AZUL = '#1F4E79'
AZUL_C = '#4472C4'
VERDE = '#2E7D32'
ROJO = '#C62828'
NARANJA = '#E65100'
GRIS = '#616161'
GRIS_C = '#E0E0E0'
AMARILLO = '#F9A825'
BG = '#FAFAFA'

out = "nino/Insight_Rotiseria_Panaderia_NINO.pdf"

with PdfPages(out) as pdf:

    # =============================================
    # PAGINA 1: RESUMEN EJECUTIVO
    # =============================================
    fig = plt.figure(figsize=(11.69, 8.27))  # A4 landscape
    fig.patch.set_facecolor('white')

    # Header
    fig.text(0.5, 0.95, 'INSIGHT ESTRATÉGICO', fontsize=28, fontweight='bold',
             ha='center', va='top', color=AZUL)
    fig.text(0.5, 0.91, 'Rotisería & Panadería — Supermercado NINO (BOSIN S.A.)',
             fontsize=14, ha='center', va='top', color=GRIS)
    fig.text(0.5, 0.88, 'Datos: últimos 30 días (Feb-Mar 2026) | 24,978 tickets analizados',
             fontsize=10, ha='center', va='top', color=GRIS)

    # Línea separadora
    fig.add_artist(plt.Line2D([0.05, 0.95], [0.86, 0.86], color=AZUL, linewidth=2))

    # --- LA PREGUNTA ---
    fig.text(0.5, 0.83, '¿Conviene mantener la rotisería si pierde plata?',
             fontsize=18, fontweight='bold', ha='center', va='top', color=ROJO,
             style='italic')

    # --- 3 COLUMNAS DE MÉTRICAS ---
    # Columna 1: Visión Contable
    fig.text(0.18, 0.76, 'VISIÓN CONTABLE', fontsize=13, fontweight='bold',
             ha='center', color=AZUL)
    fig.text(0.18, 0.72, 'Rotisería', fontsize=11, ha='center', color=GRIS)
    fig.text(0.18, 0.67, '-$3.1M', fontsize=26, fontweight='bold',
             ha='center', color=ROJO)
    fig.text(0.18, 0.63, '/mes', fontsize=11, ha='center', color=GRIS)
    fig.text(0.18, 0.58, 'DEFICITARIO', fontsize=12, fontweight='bold',
             ha='center', color=ROJO)

    fig.text(0.18, 0.52, 'Panadería', fontsize=11, ha='center', color=GRIS)
    fig.text(0.18, 0.47, '+$12M', fontsize=26, fontweight='bold',
             ha='center', color=VERDE)
    fig.text(0.18, 0.43, '/mes', fontsize=11, ha='center', color=GRIS)
    fig.text(0.18, 0.39, 'SUPERAVITARIO', fontsize=12, fontweight='bold',
             ha='center', color=VERDE)

    # Columna 2: Visión Comercial
    fig.text(0.50, 0.76, 'VISIÓN COMERCIAL', fontsize=13, fontweight='bold',
             ha='center', color=AZUL)
    fig.text(0.50, 0.72, 'Cross-sell Rotisería', fontsize=11, ha='center', color=GRIS)
    fig.text(0.50, 0.67, '4.8x', fontsize=32, fontweight='bold',
             ha='center', color=NARANJA)
    fig.text(0.50, 0.62, 'Por cada $1 de rotis,\nel cliente compra $4.8 de\notros rubros',
             fontsize=10, ha='center', va='top', color=GRIS)

    fig.text(0.50, 0.50, 'Ticket promedio', fontsize=11, ha='center', color=GRIS)
    fig.text(0.50, 0.46, 'CON rotis: $56,637', fontsize=12, fontweight='bold',
             ha='center', color=VERDE)
    fig.text(0.50, 0.42, 'SIN rotis: $31,175', fontsize=12,
             ha='center', color=GRIS)
    fig.text(0.50, 0.38, '+82% más por ticket', fontsize=13, fontweight='bold',
             ha='center', color=NARANJA)

    # Columna 3: La Decisión
    fig.text(0.82, 0.76, 'SI SE CIERRA', fontsize=13, fontweight='bold',
             ha='center', color=AZUL)
    fig.text(0.82, 0.72, 'Ahorro (pérdida evitada)', fontsize=10, ha='center', color=GRIS)
    fig.text(0.82, 0.67, '+$3.1M', fontsize=22, fontweight='bold',
             ha='center', color=VERDE)
    fig.text(0.82, 0.60, 'Cross-sell en riesgo real', fontsize=10, ha='center', color=GRIS)
    fig.text(0.82, 0.55, '-$6.3M', fontsize=22, fontweight='bold',
             ha='center', color=ROJO)
    fig.text(0.82, 0.48, 'RESULTADO NETO', fontsize=11, fontweight='bold',
             ha='center', color=GRIS)
    fig.text(0.82, 0.43, 'PIERDE', fontsize=20, fontweight='bold',
             ha='center', color=ROJO)
    fig.text(0.82, 0.39, '$3.2M/mes', fontsize=18, fontweight='bold',
             ha='center', color=ROJO)

    # Separadores verticales
    fig.add_artist(plt.Line2D([0.34, 0.34], [0.35, 0.78], color=GRIS_C, linewidth=1))
    fig.add_artist(plt.Line2D([0.66, 0.66], [0.35, 0.78], color=GRIS_C, linewidth=1))

    # --- BARRA INFERIOR: SEGMENTACIÓN ---
    fig.add_artist(plt.Line2D([0.05, 0.95], [0.32, 0.32], color=AZUL, linewidth=1))
    fig.text(0.5, 0.30, 'SEGMENTACIÓN CAUSAL: ¿El cliente viene POR la rotisería?',
             fontsize=13, fontweight='bold', ha='center', color=AZUL)

    # Barras de segmentos
    segs = [
        ('< 10%\nagrega\nde paso', 29.7, VERDE, '5%'),
        ('10-30%\ncomple-\nmento', 34.9, '#66BB6A', '15%'),
        ('30-50%\nmotivo\nparcial', 16.1, AMARILLO, '40%'),
        ('50-75%\nmotivo\nprincipal', 8.4, NARANJA, '70%'),
        ('> 75%\nviene por\nrotis', 11.0, ROJO, '95%'),
    ]

    x_start = 0.08
    bar_width = 0.16
    for i, (label, pct, color, risk) in enumerate(segs):
        x = x_start + i * (bar_width + 0.02)
        # Barra
        rect = mpatches.FancyBboxPatch((x, 0.12), bar_width, pct/100 * 0.15,
                                        boxstyle="round,pad=0.005",
                                        facecolor=color, edgecolor='white', linewidth=2,
                                        transform=fig.transFigure)
        fig.add_artist(rect)
        # Label
        fig.text(x + bar_width/2, 0.10, label, fontsize=8, ha='center', va='top', color=GRIS)
        fig.text(x + bar_width/2, 0.12 + pct/100*0.15 + 0.01, f'{pct:.0f}%',
                fontsize=11, fontweight='bold', ha='center', color=color)
        fig.text(x + bar_width/2, 0.12 + pct/100*0.15 + 0.04, f'Riesgo: {risk}',
                fontsize=8, ha='center', color=GRIS)

    # Footer
    fig.text(0.5, 0.03, 'PYMEINSIDE — Análisis basado en 234,943 líneas de detalle | Técnicas: Association Rules, Chi-Squared, Segmentación Causal',
             fontsize=8, ha='center', color=GRIS)
    fig.text(0.95, 0.03, '1/4', fontsize=9, ha='right', color=GRIS)

    pdf.savefig(fig)
    plt.close()


    # =============================================
    # PAGINA 2: CROSS-SELL POR PRODUCTO
    # =============================================
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.69, 8.27))
    fig.patch.set_facecolor('white')
    fig.suptitle('CROSS-SELLING: ¿Qué productos de rotisería arrastran más ventas?',
                 fontsize=16, fontweight='bold', color=AZUL, y=0.96)
    fig.text(0.5, 0.93, 'Últimos 30 días — Cada barra muestra cuánto compran de OTROS rubros los clientes de ese producto',
             fontsize=10, ha='center', color=GRIS)

    # Datos top 10 productos por cross-sell
    prods = ['Matambre', 'Empanada Carne x6', 'Ensalada Mixta', 'Ensalada Rusa',
             'Empanada J&Q x6', 'Patitas Aliñadas', 'Lengua Vinagreta',
             'Empanada Carne x12', 'Empanada Pollo x6', 'Miga Triple x6']
    cross_vals = [8.93, 7.44, 6.51, 4.71, 4.61, 3.64, 3.30, 3.21, 3.07, 2.26]  # millones
    ratios = [5.5, 5.1, 36.9, 24.5, 7.1, 18.3, 9.4, 2.0, 5.5, 9.1]

    colors = [ROJO if r > 15 else (NARANJA if r > 7 else AZUL_C) for r in ratios]

    y_pos = np.arange(len(prods))
    ax1.barh(y_pos, cross_vals, color=colors, height=0.7, edgecolor='white', linewidth=0.5)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(prods, fontsize=10)
    ax1.invert_yaxis()
    ax1.set_xlabel('Cross-sell generado (millones $)', fontsize=10)
    ax1.set_title('Top 10 por volumen de cross-sell', fontsize=12, fontweight='bold', color=AZUL)
    for i, (v, r) in enumerate(zip(cross_vals, ratios)):
        ax1.text(v + 0.1, i, f'${v:.1f}M ({r:.0f}x)', va='center', fontsize=9, color=GRIS)
    ax1.set_xlim(0, max(cross_vals) * 1.4)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    # Gráfico 2: Rubros arrastrados
    deptos = ['Carnicería', 'Almacén', 'Lácteos', 'Bebidas', 'Perfumería',
              'Fiambrería', 'Limpieza', 'Pollo', 'Panadería', 'Elab. Carnic.']
    dept_vals = [12.40, 8.40, 5.50, 3.63, 3.32, 3.12, 3.09, 2.39, 1.73, 1.37]

    dept_colors = [AZUL if v > 5 else (AZUL_C if v > 3 else '#90CAF9') for v in dept_vals]

    y_pos2 = np.arange(len(deptos))
    ax2.barh(y_pos2, dept_vals, color=dept_colors, height=0.7, edgecolor='white', linewidth=0.5)
    ax2.set_yticks(y_pos2)
    ax2.set_yticklabels(deptos, fontsize=10)
    ax2.invert_yaxis()
    ax2.set_xlabel('Venta en tickets con rotis (millones $)', fontsize=10)
    ax2.set_title('Rubros que se venden junto con rotisería', fontsize=12, fontweight='bold', color=AZUL)
    for i, v in enumerate(dept_vals):
        ax2.text(v + 0.1, i, f'${v:.1f}M', va='center', fontsize=9, color=GRIS)
    ax2.set_xlim(0, max(dept_vals) * 1.3)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    # Leyenda
    fig.text(0.15, 0.04, '● Ratio >15x (ancla fuerte)', fontsize=9, color=ROJO)
    fig.text(0.40, 0.04, '● Ratio 7-15x (moderado)', fontsize=9, color=NARANJA)
    fig.text(0.63, 0.04, '● Ratio <7x', fontsize=9, color=AZUL_C)
    fig.text(0.95, 0.03, '2/4', fontsize=9, ha='right', color=GRIS)

    plt.tight_layout(rect=[0, 0.07, 1, 0.91])
    pdf.savefig(fig)
    plt.close()


    # =============================================
    # PAGINA 3: CORRELACIÓN ROTISERÍA ↔ PANADERÍA
    # =============================================
    fig = plt.figure(figsize=(11.69, 8.27))
    fig.patch.set_facecolor('white')

    fig.text(0.5, 0.95, 'CORRELACIÓN: ¿La rotisería arrastra a la panadería?',
             fontsize=18, fontweight='bold', ha='center', color=AZUL)
    fig.text(0.5, 0.91, 'Pregunta de Sebastián Peña: "¿Hay parte de la producción de panadería que corresponde a rotisería?"',
             fontsize=11, ha='center', color=GRIS, style='italic')

    fig.add_artist(plt.Line2D([0.05, 0.95], [0.89, 0.89], color=AZUL, linewidth=2))

    # Métricas principales en 2 columnas
    # Col izquierda: Rotis → Panad
    fig.text(0.28, 0.85, 'ROTISERÍA → PANADERÍA', fontsize=14, fontweight='bold',
             ha='center', color=AZUL)
    fig.text(0.28, 0.81, '50.8% de tickets con rotis\ntambién compran panadería',
             fontsize=11, ha='center', color=GRIS)
    fig.text(0.28, 0.74, 'vs 39.9% promedio', fontsize=10, ha='center', color=GRIS)
    fig.text(0.28, 0.70, 'Solo 6.1%', fontsize=28, fontweight='bold',
             ha='center', color=VERDE)
    fig.text(0.28, 0.66, 'de la venta de panadería\nestá en tickets con rotisería',
             fontsize=11, ha='center', color=GRIS)
    fig.text(0.28, 0.59, 'Impacto: ~$848K/mes', fontsize=13, fontweight='bold',
             ha='center', color=VERDE)
    fig.text(0.28, 0.55, 'BAJO — Rotis NO arrastra a panadería',
             fontsize=11, fontweight='bold', ha='center', color=VERDE)

    # Separador
    fig.add_artist(plt.Line2D([0.50, 0.50], [0.52, 0.87], color=GRIS_C, linewidth=1))

    # Col derecha: Panad → Rotis
    fig.text(0.72, 0.85, 'PANADERÍA → ROTISERÍA', fontsize=14, fontweight='bold',
             ha='center', color=AZUL)
    fig.text(0.72, 0.81, '5.9% de tickets con panadería\ntambién compran rotisería',
             fontsize=11, ha='center', color=GRIS)
    fig.text(0.72, 0.74, 'vs 4.6% promedio', fontsize=10, ha='center', color=GRIS)
    fig.text(0.72, 0.70, '49.2%', fontsize=28, fontweight='bold',
             ha='center', color=ROJO)
    fig.text(0.72, 0.66, 'de la venta de rotisería\nestá en tickets con panadería',
             fontsize=11, ha='center', color=GRIS)
    fig.text(0.72, 0.59, 'La mitad de rotisería depende\nde clientes de panadería',
             fontsize=11, fontweight='bold', ha='center', color=ROJO)

    # Tests estadísticos
    fig.add_artist(plt.Line2D([0.05, 0.95], [0.49, 0.49], color=AZUL, linewidth=1))
    fig.text(0.5, 0.47, 'TESTS ESTADÍSTICOS', fontsize=13, fontweight='bold',
             ha='center', color=AZUL)

    stats_data = [
        ('Lift = 1.27', 'Se compran juntos 27% más de lo esperado por azar', NARANJA),
        ('Chi² = 59.5 (p < 0.001)', 'Asociación estadísticamente significativa', VERDE),
        ("Cramér's V = 0.049", 'Asociación DÉBIL en magnitud (escala 0-1)', AMARILLO),
    ]
    for i, (metric, desc, color) in enumerate(stats_data):
        y = 0.42 - i * 0.05
        fig.text(0.20, y, metric, fontsize=12, fontweight='bold', color=color)
        fig.text(0.50, y, desc, fontsize=11, color=GRIS)

    # Conclusión
    fig.add_artist(plt.Line2D([0.05, 0.95], [0.24, 0.24], color=AZUL, linewidth=1))
    fig.text(0.5, 0.22, 'CONCLUSIÓN PARA SEBASTIÁN', fontsize=14, fontweight='bold',
             ha='center', color=AZUL)

    conclusions = [
        '→ Sí hay cross-selling, pero la asociación es DÉBIL (Lift=1.27, V=0.05)',
        '→ La "producción de panadería que corresponde a rotisería" es ~$848K/mes (3% de panad)',
        '→ En cambio, 49% de ROTISERÍA depende de tickets con panadería',
        '→ PANADERÍA ARRASTRA A ROTISERÍA, no al revés',
        '→ Cerrar rotisería NO afecta significativamente a panadería',
    ]
    for i, c in enumerate(conclusions):
        color = ROJO if 'ARRASTRA' in c else (VERDE if 'NO afecta' in c else GRIS)
        fig.text(0.10, 0.18 - i * 0.035, c, fontsize=11, color=color,
                fontweight='bold' if 'ARRASTRA' in c or 'NO afecta' in c else 'normal')

    fig.text(0.95, 0.03, '3/4', fontsize=9, ha='right', color=GRIS)
    pdf.savefig(fig)
    plt.close()


    # =============================================
    # PAGINA 4: CORRELACIÓN CON TODOS LOS DEPTOS
    # =============================================
    fig, ax = plt.subplots(figsize=(11.69, 8.27))
    fig.patch.set_facecolor('white')

    fig.suptitle('CORRELACIÓN: Rotisería vs Todos los Departamentos',
                fontsize=16, fontweight='bold', color=AZUL, y=0.96)
    fig.text(0.5, 0.93, 'Lift > 1 = se compra MÁS cuando hay rotis | Lift = 1 = independiente | Lift < 1 = se compra MENOS',
             fontsize=10, ha='center', color=GRIS)

    # Top departamentos por lift
    dept_names = [
        'Pescados Cong.', 'Repostería', 'Pan', 'Embutidos', 'Cong. Helados',
        'Fiambrería', 'Elab. Carnic.', 'Panif. Masas', 'Bebidas', 'Lácteos',
        'Golosinas', 'Panadería EP', 'Leches', 'Huevos', 'Perfumería',
        'Limpieza', 'Almacén', 'Pollo', 'Carnicería', '1ra Necesidad',
        'Harinas', 'Congelados'
    ]
    lift_vals = [3.65, 3.23, 2.39, 1.94, 1.89, 1.57, 1.51, 1.49, 1.47, 1.40,
                 1.32, 1.27, 1.24, 1.23, 1.17, 1.16, 1.10, 1.09, 1.07, 1.05,
                 0.90, 0.26]

    colors = []
    for l in lift_vals:
        if l > 1.5: colors.append(VERDE)
        elif l > 1.2: colors.append(AMARILLO)
        elif l > 0.9: colors.append(GRIS_C)
        else: colors.append(ROJO)

    y_pos = np.arange(len(dept_names))
    bars = ax.barh(y_pos, lift_vals, color=colors, height=0.7, edgecolor='white', linewidth=0.5)
    ax.axvline(x=1.0, color=AZUL, linewidth=2, linestyle='--', alpha=0.7, label='Independiente (Lift=1)')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(dept_names, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel('Lift (probabilidad relativa)', fontsize=11)
    ax.set_xlim(0, max(lift_vals) * 1.15)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    for i, v in enumerate(lift_vals):
        ax.text(v + 0.03, i, f'{v:.2f}', va='center', fontsize=9, color=GRIS)

    # Leyenda
    legend_elements = [
        mpatches.Patch(facecolor=VERDE, label='Lift > 1.5 (fuerte arrastre)'),
        mpatches.Patch(facecolor=AMARILLO, label='Lift 1.2-1.5 (moderado)'),
        mpatches.Patch(facecolor=GRIS_C, label='Lift ~1.0 (independiente)'),
        mpatches.Patch(facecolor=ROJO, label='Lift < 0.9 (relación inversa)'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=9, framealpha=0.9)

    fig.text(0.5, 0.03, 'Método: Market Basket Analysis (Association Rules) + Chi-Squared Test | PYMEINSIDE Marzo 2026',
             fontsize=8, ha='center', color=GRIS)
    fig.text(0.95, 0.03, '4/4', fontsize=9, ha='right', color=GRIS)

    plt.tight_layout(rect=[0, 0.06, 1, 0.91])
    pdf.savefig(fig)
    plt.close()

print(f"PDF guardado: {out}")

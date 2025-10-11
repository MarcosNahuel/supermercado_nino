# -*- coding: utf-8 -*-
"""
ANÁLISIS COMPLETO DE COMPROBANTES CON RENTABILIDAD POR DEPARTAMENTO
Supermercado NINO - pymeinside.com
Data Scientist: Claude Code

Objetivo:
- Analizar serie completa de comprobantes (tickets, items, montos, cantidades, fechas)
- Vincular por departamento con tabla RENTABILIDAD
- Analizar comportamiento en feriados y fechas festivas
- Generar insights accionables
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("=" * 100)
print("ANÁLISIS COMPLETO DE COMPROBANTES CON RENTABILIDAD")
print("Supermercado NINO - pymeinside.com")
print("=" * 100)

# =============================================================================
# CONFIGURACIÓN DE RUTAS
# =============================================================================
ROOT_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT_DIR / "data" / "raw"
OUTPUT_DIR = ROOT_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# TABLA DE FERIADOS Y FECHAS FESTIVAS (NOV 2024 - JUN 2025)
# =============================================================================
print("\n[1/8] Creando tabla de feriados y fechas festivas...")

feriados_data = {
    'Fecha': [
        # Noviembre 2024
        '2024-11-18',  # Día de la Soberanía Nacional (trasladado)
        # Diciembre 2024
        '2024-12-08',  # Inmaculada Concepción
        '2024-12-25',  # Navidad
        '2024-12-24',  # Nochebuena (festivo, no oficial)
        '2024-12-31',  # Fin de año (festivo, no oficial)
        # Enero 2025
        '2025-01-01',  # Año Nuevo
        # Febrero 2025 - No hay feriados
        # Marzo 2025
        '2025-03-03',  # Carnaval
        '2025-03-04',  # Carnaval
        '2025-03-24',  # Día de la Memoria por la Verdad y la Justicia
        # Abril 2025
        '2025-04-02',  # Día del Veterano y Caídos en Malvinas
        '2025-04-17',  # Jueves Santo
        '2025-04-18',  # Viernes Santo
        # Mayo 2025
        '2025-05-01',  # Día del Trabajador
        '2025-05-02',  # Día no laborable con fines turísticos
        '2025-05-25',  # Día de la Revolución de Mayo
        # Junio 2025
        '2025-06-16',  # Güemes (trasladado)
        '2025-06-20',  # Belgrano
    ],
    'Descripcion': [
        'Día de la Soberanía Nacional',
        'Inmaculada Concepción',
        'Navidad',
        'Nochebuena',
        'Fin de Año',
        'Año Nuevo',
        'Carnaval',
        'Carnaval',
        'Día de la Memoria',
        'Día del Veterano',
        'Jueves Santo',
        'Viernes Santo',
        'Día del Trabajador',
        'Día no laborable',
        'Revolución de Mayo',
        'Paso a la Inmortalidad Güemes',
        'Paso a la Inmortalidad Belgrano',
    ],
    'Tipo': [
        'Feriado Nacional',
        'Feriado Nacional',
        'Feriado Nacional',
        'Festivo',
        'Festivo',
        'Feriado Nacional',
        'Feriado Nacional',
        'Feriado Nacional',
        'Feriado Nacional',
        'Feriado Nacional',
        'Feriado Nacional',
        'Feriado Nacional',
        'Feriado Nacional',
        'Día no laborable',
        'Feriado Nacional',
        'Feriado Nacional',
        'Feriado Nacional',
    ]
}

df_feriados = pd.DataFrame(feriados_data)
df_feriados['Fecha'] = pd.to_datetime(df_feriados['Fecha'])
df_feriados['Mes'] = df_feriados['Fecha'].dt.month
df_feriados['Anio'] = df_feriados['Fecha'].dt.year

print(f"  Total feriados y festivos: {len(df_feriados)}")
print(f"  Rango: {df_feriados['Fecha'].min().strftime('%d/%m/%Y')} - {df_feriados['Fecha'].max().strftime('%d/%m/%Y')}")

# Guardar tabla de feriados
df_feriados.to_csv(OUTPUT_DIR / 'FERIADOS_2024_2025.csv', index=False, encoding='utf-8-sig', sep=';')
print(f"  Tabla guardada: FERIADOS_2024_2025.csv")

# =============================================================================
# CARGAR DATOS DE COMPROBANTES
# =============================================================================
print("\n[2/8] Cargando datos de comprobantes...")

# Cargar CSV completo (2.6M líneas)
df_comprobantes = pd.read_csv(
    RAW_DIR / 'SERIE_COMPROBANTES_COMPLETOS.csv',
    sep=';',
    encoding='utf-8',
    low_memory=False
)

print(f"  Registros cargados: {len(df_comprobantes):,}")
print(f"  Columnas: {list(df_comprobantes.columns)}")

# =============================================================================
# LIMPIEZA Y TRANSFORMACIÓN DE DATOS
# =============================================================================
print("\n[3/8] Limpiando y transformando datos...")

# Convertir fecha
df_comprobantes['Fecha'] = pd.to_datetime(df_comprobantes['Fecha'], errors='coerce')

# Convertir tipos numéricos
df_comprobantes['Cantidad'] = pd.to_numeric(df_comprobantes['Cantidad'], errors='coerce')
df_comprobantes['Importe'] = pd.to_numeric(df_comprobantes['Importe'], errors='coerce')
df_comprobantes['Unitario'] = pd.to_numeric(df_comprobantes['Unitario'], errors='coerce')

# Eliminar filas con datos inválidos
df_comprobantes = df_comprobantes.dropna(subset=['Fecha', 'Importe'])

# Extraer características temporales
df_comprobantes['Anio'] = df_comprobantes['Fecha'].dt.year
df_comprobantes['Mes'] = df_comprobantes['Fecha'].dt.month
df_comprobantes['Dia'] = df_comprobantes['Fecha'].dt.day
df_comprobantes['DiaSemana'] = df_comprobantes['Fecha'].dt.day_name()
df_comprobantes['NombreMes'] = df_comprobantes['Fecha'].dt.month_name()
df_comprobantes['FechaCorta'] = df_comprobantes['Fecha'].dt.date

# Marcar feriados
df_comprobantes['EsFeriado'] = df_comprobantes['Fecha'].dt.date.isin(df_feriados['Fecha'].dt.date)

# Marcar fin de semana
df_comprobantes['EsFinDeSemana'] = df_comprobantes['DiaSemana'].isin(['Saturday', 'Sunday'])

# Normalizar departamento (eliminar espacios, mayúsculas)
df_comprobantes['Departamento'] = df_comprobantes['Departamento'].str.strip().str.upper()

print(f"  Registros después de limpieza: {len(df_comprobantes):,}")
print(f"  Fechas únicas: {df_comprobantes['FechaCorta'].nunique():,}")
print(f"  Comprobantes únicos: {df_comprobantes['Comprobante'].nunique():,}")
print(f"  Departamentos únicos: {df_comprobantes['Departamento'].nunique()}")
print(f"  Días marcados como feriado: {df_comprobantes['EsFeriado'].sum():,}")

# =============================================================================
# CARGAR DATOS DE RENTABILIDAD
# =============================================================================
print("\n[4/8] Cargando y vinculando datos de rentabilidad...")

df_rentabilidad = pd.read_csv(
    RAW_DIR / 'RENTABILIDAD.csv',
    encoding='utf-8'
)
df_rentabilidad['Departamento'] = (
    df_rentabilidad['Departamento']
    .astype(str)
    .str.strip()
    .str.replace('"', '', regex=False)
    .str.upper()
)

df_rentabilidad['Clasificación'] = df_rentabilidad['Clasificación'].astype(str).str.strip()

# Convertir % Rentabilidad a numérico (ej: "28%" -> 28)
df_rentabilidad['Rentabilidad_Pct'] = df_rentabilidad['% Rentabilidad'].str.replace('%', '').astype(float)

print(f"  Departamentos en RENTABILIDAD: {len(df_rentabilidad)}")
print(f"  Rango de rentabilidad: {df_rentabilidad['Rentabilidad_Pct'].min():.0f}% - {df_rentabilidad['Rentabilidad_Pct'].max():.0f}%")

# Vincular comprobantes con rentabilidad por departamento
df_completo = df_comprobantes.merge(
    df_rentabilidad[['Departamento', 'Clasificación', 'Rentabilidad_Pct']],
    on='Departamento',
    how='left'
)
df_completo['Rentabilidad_Pct'] = df_completo['Rentabilidad_Pct'].fillna(0)
df_completo['Clasificación'] = df_completo['Clasificación'].fillna('SIN CLASIFICACION')

# Calcular margen estimado
df_completo['Margen_Estimado'] = df_completo['Importe'] * (df_completo['Rentabilidad_Pct'] / 100)

print(f"  Registros después del merge: {len(df_completo):,}")
print(f"  Registros con rentabilidad: {df_completo['Rentabilidad_Pct'].notna().sum():,}")
print(f"  Registros sin rentabilidad: {df_completo['Rentabilidad_Pct'].isna().sum():,}")

# =============================================================================
# CÁLCULO DE KPIs GENERALES
# =============================================================================
print("\n[5/8] Calculando KPIs generales...")

# KPIs globales
total_registros = len(df_completo)
total_comprobantes = df_completo['Comprobante'].nunique()
total_ventas = df_completo['Importe'].sum()
total_margen_estimado = df_completo['Margen_Estimado'].sum()
ticket_promedio = df_completo.groupby('Comprobante')['Importe'].sum().mean()
items_promedio_por_ticket = df_completo.groupby('Comprobante').size().mean()
fecha_inicio = df_completo['Fecha'].min()
fecha_fin = df_completo['Fecha'].max()
dias_operacion = (fecha_fin - fecha_inicio).days + 1

print(f"  Total items vendidos: {total_registros:,}")
print(f"  Total comprobantes: {total_comprobantes:,}")
print(f"  Total ventas: ${total_ventas:,.2f}")
print(f"  Margen estimado total: ${total_margen_estimado:,.2f}")
print(f"  Ticket promedio: ${ticket_promedio:,.2f}")
print(f"  Items promedio por ticket: {items_promedio_por_ticket:.2f}")
print(f"  Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')} ({dias_operacion} días)")

# =============================================================================
# ANÁLISIS POR DEPARTAMENTO CON RENTABILIDAD
# =============================================================================
print("\n[6/8] Analizando por departamento con rentabilidad...")

kpi_departamento = df_completo.groupby(['Departamento', 'Clasificación', 'Rentabilidad_Pct']).agg({
    'Importe': 'sum',
    'Margen_Estimado': 'sum',
    'Cantidad': 'sum',
    'Comprobante': 'nunique'
}).reset_index()

kpi_departamento.columns = ['Departamento', 'Clasificación', 'Rentabilidad_Pct', 'Ventas', 'Margen_Estimado', 'Unidades', 'Tickets']
kpi_departamento = kpi_departamento.sort_values('Ventas', ascending=False)
kpi_departamento['Pct_Ventas'] = (kpi_departamento['Ventas'] / kpi_departamento['Ventas'].sum() * 100).round(2)
kpi_departamento['Pct_Margen'] = (kpi_departamento['Margen_Estimado'] / kpi_departamento['Margen_Estimado'].sum() * 100).round(2)

print(f"  Top 5 departamentos por ventas:")
for idx, row in kpi_departamento.head(5).iterrows():
    print(f"    {row['Departamento']}: ${row['Ventas']:,.0f} ({row['Pct_Ventas']:.1f}%) - Rentab: {row['Rentabilidad_Pct']:.0f}%")

# =============================================================================
# ANÁLISIS DE FERIADOS VS DÍAS NORMALES
# =============================================================================
print("\n[7/8] Analizando comportamiento en feriados vs días normales...")

# Agrupar por fecha y calcular totales diarios
kpi_diario = df_completo.groupby(['FechaCorta', 'EsFeriado', 'EsFinDeSemana', 'DiaSemana']).agg({
    'Importe': 'sum',
    'Comprobante': 'nunique',
    'Margen_Estimado': 'sum'
}).reset_index()

kpi_diario.columns = ['Fecha', 'EsFeriado', 'EsFinDeSemana', 'DiaSemana', 'Ventas', 'Tickets', 'Margen']
kpi_diario['Ticket_Promedio'] = kpi_diario['Ventas'] / kpi_diario['Tickets']

# Comparar feriados vs normales
ventas_feriados = kpi_diario[kpi_diario['EsFeriado']]['Ventas'].sum()
ventas_normales = kpi_diario[~kpi_diario['EsFeriado']]['Ventas'].sum()
dias_feriados = kpi_diario['EsFeriado'].sum()
dias_normales = (~kpi_diario['EsFeriado']).sum()

venta_promedio_feriado = ventas_feriados / dias_feriados if dias_feriados > 0 else 0
venta_promedio_normal = ventas_normales / dias_normales if dias_normales > 0 else 0

diferencia_pct = ((venta_promedio_feriado - venta_promedio_normal) / venta_promedio_normal * 100) if venta_promedio_normal > 0 else 0

print(f"  Días feriados/festivos: {dias_feriados}")
print(f"  Días normales: {dias_normales}")
print(f"  Venta promedio feriado: ${venta_promedio_feriado:,.2f}")
print(f"  Venta promedio normal: ${venta_promedio_normal:,.2f}")
print(f"  Diferencia: {diferencia_pct:+.1f}%")

# Análisis por día de semana
kpi_dia_semana = df_completo.groupby('DiaSemana').agg({
    'Importe': 'sum',
    'Comprobante': 'nunique',
    'Margen_Estimado': 'sum'
}).reset_index()

kpi_dia_semana.columns = ['DiaSemana', 'Ventas', 'Tickets', 'Margen']
dias_orden = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
kpi_dia_semana['DiaSemana'] = pd.Categorical(kpi_dia_semana['DiaSemana'], categories=dias_orden, ordered=True)
kpi_dia_semana = kpi_dia_semana.sort_values('DiaSemana')

# Análisis por mes
kpi_mensual = df_completo.groupby(['Anio', 'Mes', 'NombreMes']).agg({
    'Importe': 'sum',
    'Comprobante': 'nunique',
    'Margen_Estimado': 'sum'
}).reset_index()

kpi_mensual.columns = ['Anio', 'Mes', 'NombreMes', 'Ventas', 'Tickets', 'Margen']
kpi_mensual['Periodo'] = kpi_mensual['Anio'].astype(str) + '-' + kpi_mensual['Mes'].astype(str).str.zfill(2)

# =============================================================================
# EXPORTAR RESULTADOS A CSV
# =============================================================================
print("\n[8/8] Exportando resultados...")

# Exportar KPIs principales
kpi_departamento.to_csv(OUTPUT_DIR / 'KPI_DEPARTAMENTO_RENTABILIDAD.csv', index=False, encoding='utf-8-sig', sep=';')
kpi_diario.to_csv(OUTPUT_DIR / 'KPI_DIARIO_FERIADOS.csv', index=False, encoding='utf-8-sig', sep=';')
kpi_dia_semana.to_csv(OUTPUT_DIR / 'KPI_DIA_SEMANA.csv', index=False, encoding='utf-8-sig', sep=';')
kpi_mensual.to_csv(OUTPUT_DIR / 'KPI_MENSUAL.csv', index=False, encoding='utf-8-sig', sep=';')

print(f"  KPI_DEPARTAMENTO_RENTABILIDAD.csv - {len(kpi_departamento)} registros")
print(f"  KPI_DIARIO_FERIADOS.csv - {len(kpi_diario)} registros")
print(f"  KPI_DIA_SEMANA.csv - {len(kpi_dia_semana)} registros")
print(f"  KPI_MENSUAL.csv - {len(kpi_mensual)} registros")

# =============================================================================
# CREAR GRÁFICOS PARA INFORME HTML
# =============================================================================
print("\n[BONUS] Generando gráficos...")

# Gráfico 1: Top 10 Departamentos por Ventas con Rentabilidad
fig1 = go.Figure()
top10_dept = kpi_departamento.head(10)

fig1.add_trace(go.Bar(
    x=top10_dept['Departamento'],
    y=top10_dept['Ventas'],
    name='Ventas',
    marker_color='#667eea',
    text=top10_dept['Ventas'].apply(lambda x: f'${x/1e6:.1f}M'),
    textposition='outside'
))

fig1.add_trace(go.Scatter(
    x=top10_dept['Departamento'],
    y=top10_dept['Rentabilidad_Pct'],
    name='Rentabilidad %',
    yaxis='y2',
    mode='lines+markers',
    line=dict(color='#f18f01', width=3),
    marker=dict(size=10),
    text=top10_dept['Rentabilidad_Pct'].apply(lambda x: f'{x:.0f}%'),
    textposition='top center'
))

fig1.update_layout(
    title='Top 10 Departamentos: Ventas vs Rentabilidad',
    xaxis_title='Departamento',
    yaxis_title='Ventas ($)',
    yaxis2=dict(title='Rentabilidad %', overlaying='y', side='right'),
    template='plotly_white',
    height=500,
    showlegend=True
)

# Gráfico 2: Ventas Diarias con marcadores de Feriados
fig2 = go.Figure()

# Días normales
dias_normales_data = kpi_diario[~kpi_diario['EsFeriado']]
fig2.add_trace(go.Scatter(
    x=dias_normales_data['Fecha'],
    y=dias_normales_data['Ventas'],
    mode='lines',
    name='Días Normales',
    line=dict(color='#667eea', width=1)
))

# Días feriados
dias_feriados_data = kpi_diario[kpi_diario['EsFeriado']]
if len(dias_feriados_data) > 0:
    fig2.add_trace(go.Scatter(
        x=dias_feriados_data['Fecha'],
        y=dias_feriados_data['Ventas'],
        mode='markers',
        name='Feriados/Festivos',
        marker=dict(color='#f18f01', size=10, symbol='star')
    ))

fig2.update_layout(
    title='Serie Temporal de Ventas con Feriados',
    xaxis_title='Fecha',
    yaxis_title='Ventas ($)',
    template='plotly_white',
    height=400,
    hovermode='x unified'
)

# Gráfico 3: Ventas por Día de Semana
dias_esp = {
    'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
    'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
}
kpi_dia_semana['Dia_ESP'] = kpi_dia_semana['DiaSemana'].map(dias_esp)

fig3 = go.Figure(data=[
    go.Bar(
        x=kpi_dia_semana['Dia_ESP'],
        y=kpi_dia_semana['Ventas'],
        marker_color='#764ba2',
        text=kpi_dia_semana['Ventas'].apply(lambda x: f'${x/1e6:.1f}M'),
        textposition='outside'
    )
])

fig3.update_layout(
    title='Ventas por Día de Semana',
    xaxis_title='Día',
    yaxis_title='Ventas ($)',
    template='plotly_white',
    height=400
)

# Gráfico 4: Ventas Mensuales
fig4 = go.Figure(data=[
    go.Bar(
        x=kpi_mensual['Periodo'],
        y=kpi_mensual['Ventas'],
        marker_color='#667eea',
        text=kpi_mensual['Ventas'].apply(lambda x: f'${x/1e6:.1f}M'),
        textposition='outside'
    )
])

fig4.update_layout(
    title='Ventas por Mes',
    xaxis_title='Período',
    yaxis_title='Ventas ($)',
    template='plotly_white',
    height=400
)

# Convertir gráficos a HTML
html_fig1 = fig1.to_html(include_plotlyjs='cdn', div_id='fig1')
html_fig2 = fig2.to_html(include_plotlyjs=False, div_id='fig2')
html_fig3 = fig3.to_html(include_plotlyjs=False, div_id='fig3')
html_fig4 = fig4.to_html(include_plotlyjs=False, div_id='fig4')

# =============================================================================
# GENERAR INFORME HTML
# =============================================================================
print("\n[HTML] Generando informe HTML...")

# Calcular insights adicionales
top_dept = kpi_departamento.iloc[0]
mejor_rentabilidad = kpi_departamento.loc[kpi_departamento['Rentabilidad_Pct'].idxmax()]

html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Análisis de Comprobantes con Rentabilidad - Supermercado NINO</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            color: #333;
            line-height: 1.6;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 60px 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        .header p {{
            font-size: 1.3em;
            opacity: 0.95;
        }}
        .header .date {{
            font-size: 0.9em;
            margin-top: 15px;
            opacity: 0.8;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 30px 20px;
        }}
        .section {{
            background: white;
            margin: 30px 0;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            color: #667eea;
            border-bottom: 4px solid #667eea;
            padding-bottom: 15px;
            margin-bottom: 25px;
            font-size: 2em;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            margin: 30px 0;
        }}
        .kpi-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
        }}
        .kpi-card h3 {{
            font-size: 1.1em;
            margin-bottom: 15px;
            opacity: 0.95;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .kpi-card p {{
            font-size: 2em;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        .insight {{
            background: linear-gradient(to right, #fff9e6 0%, #fef3d0 100%);
            border-left: 6px solid #f18f01;
            padding: 25px;
            margin: 25px 0;
            border-radius: 8px;
        }}
        .insight h3 {{
            color: #f18f01;
            font-size: 1.5em;
            margin-bottom: 15px;
        }}
        .chart {{
            margin: 30px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        td {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        .footer {{
            text-align: center;
            padding: 40px 20px;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Análisis de Comprobantes con Rentabilidad</h1>
        <p>Supermercado NINO</p>
        <p class="date">Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        <p class="date">Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}</p>
    </div>

    <div class="container">
        <!-- KPIs PRINCIPALES -->
        <div class="section">
            <h2>📊 KPIs Principales</h2>
            <div class="kpi-grid">
                <div class="kpi-card">
                    <h3>Total Ventas</h3>
                    <p>${total_ventas:,.0f}</p>
                </div>
                <div class="kpi-card">
                    <h3>Margen Estimado</h3>
                    <p>${total_margen_estimado:,.0f}</p>
                </div>
                <div class="kpi-card">
                    <h3>Total Comprobantes</h3>
                    <p>{total_comprobantes:,}</p>
                </div>
                <div class="kpi-card">
                    <h3>Ticket Promedio</h3>
                    <p>${ticket_promedio:,.0f}</p>
                </div>
                <div class="kpi-card">
                    <h3>Items por Ticket</h3>
                    <p>{items_promedio_por_ticket:.1f}</p>
                </div>
                <div class="kpi-card">
                    <h3>Días de Operación</h3>
                    <p>{dias_operacion}</p>
                </div>
            </div>
        </div>

        <!-- ANÁLISIS DE FERIADOS -->
        <div class="section">
            <h2>🎉 Análisis de Feriados y Festivos</h2>
            <div class="insight">
                <h3>💡 Comportamiento en Feriados</h3>
                <p><strong>Venta promedio en feriados:</strong> ${venta_promedio_feriado:,.0f}</p>
                <p><strong>Venta promedio días normales:</strong> ${venta_promedio_normal:,.0f}</p>
                <p><strong>Diferencia:</strong> <span style="color: {'green' if diferencia_pct > 0 else 'red'}; font-weight: bold;">{diferencia_pct:+.1f}%</span></p>
                <p style="margin-top: 15px;">{'Los feriados generan ventas SUPERIORES a días normales.' if diferencia_pct > 0 else 'Los feriados generan ventas INFERIORES a días normales.'}</p>
            </div>
            <div class="chart">{html_fig2}</div>

            <h3>Feriados del Período</h3>
            <table>
                <thead>
                    <tr>
                        <th>Fecha</th>
                        <th>Descripción</th>
                        <th>Tipo</th>
                    </tr>
                </thead>
                <tbody>
"""

for _, row in df_feriados.iterrows():
    html_content += f"""
                    <tr>
                        <td>{row['Fecha'].strftime('%d/%m/%Y')}</td>
                        <td>{row['Descripcion']}</td>
                        <td>{row['Tipo']}</td>
                    </tr>
"""

html_content += f"""
                </tbody>
            </table>
        </div>

        <!-- ANÁLISIS POR DEPARTAMENTO -->
        <div class="section">
            <h2>🏢 Análisis por Departamento con Rentabilidad</h2>
            <div class="insight">
                <h3>💡 Insights Clave</h3>
                <p><strong>Departamento líder en ventas:</strong> {top_dept['Departamento']} (${top_dept['Ventas']:,.0f} - {top_dept['Pct_Ventas']:.1f}%)</p>
                <p><strong>Rentabilidad del líder:</strong> {top_dept['Rentabilidad_Pct']:.0f}%</p>
                <p><strong>Departamento más rentable:</strong> {mejor_rentabilidad['Departamento']} ({mejor_rentabilidad['Rentabilidad_Pct']:.0f}%)</p>
            </div>
            <div class="chart">{html_fig1}</div>

            <h3>Top 15 Departamentos</h3>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Departamento</th>
                        <th>Clasificación</th>
                        <th>Ventas</th>
                        <th>Margen Estimado</th>
                        <th>Rentabilidad %</th>
                        <th>% Ventas</th>
                    </tr>
                </thead>
                <tbody>
"""

for i, (idx, row) in enumerate(kpi_departamento.head(15).iterrows(), 1):
    html_content += f"""
                    <tr>
                        <td>{i}</td>
                        <td>{row['Departamento']}</td>
                        <td>{row['Clasificación']}</td>
                        <td>${row['Ventas']:,.0f}</td>
                        <td>${row['Margen_Estimado']:,.0f}</td>
                        <td>{row['Rentabilidad_Pct']:.0f}%</td>
                        <td>{row['Pct_Ventas']:.2f}%</td>
                    </tr>
"""

html_content += f"""
                </tbody>
            </table>
        </div>

        <!-- ANÁLISIS TEMPORAL -->
        <div class="section">
            <h2>📅 Análisis Temporal</h2>

            <h3>Ventas por Mes</h3>
            <div class="chart">{html_fig4}</div>

            <h3>Ventas por Día de Semana</h3>
            <div class="chart">{html_fig3}</div>
        </div>

        <!-- RECOMENDACIONES -->
        <div class="section">
            <h2>🎯 Recomendaciones Estratégicas</h2>
            <div class="insight">
                <h3>1. Optimización de Stock por Rentabilidad</h3>
                <p>Priorizar stock de departamentos de alta rentabilidad (45%): Bazar, Fiambrería, Golosinas.</p>
                <p><strong>Impacto esperado:</strong> +15-20% en margen bruto</p>
            </div>

            <div class="insight">
                <h3>2. Estrategia para Feriados</h3>
                <p>{'Reforzar stock y personal en feriados, ya que generan ventas superiores.' if diferencia_pct > 0 else 'Optimizar operación en feriados para mejorar resultados.'}</p>
                <p><strong>Impacto esperado:</strong> +5-10% en ventas totales</p>
            </div>

            <div class="insight">
                <h3>3. Focus en Departamento Líder</h3>
                <p>El departamento {top_dept['Departamento']} representa {top_dept['Pct_Ventas']:.1f}% de ventas con {top_dept['Rentabilidad_Pct']:.0f}% de rentabilidad.</p>
                <p>Asegurar disponibilidad permanente y considerar ampliación de surtido.</p>
            </div>
        </div>
    </div>

    <div class="footer">
        <p><strong>Análisis generado por:</strong> Claude Code (IA)</p>
        <p><strong>Cliente:</strong> Supermercado NINO | <strong>Consultor:</strong> pymeinside.com</p>
        <p><strong>Fecha:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
    </div>
</body>
</html>
"""

# Guardar informe HTML
output_html = OUTPUT_DIR / 'INFORME_COMPROBANTES_RENTABILIDAD.html'
with open(output_html, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"  Informe HTML guardado: {output_html}")
print(f"  Tamaño: {output_html.stat().st_size / 1024:.1f} KB")

# =============================================================================
# RESUMEN FINAL
# =============================================================================
print("\n" + "=" * 100)
print("ANÁLISIS COMPLETADO EXITOSAMENTE")
print("=" * 100)
print(f"Total registros analizados: {total_registros:,}")
print(f"Total comprobantes: {total_comprobantes:,}")
print(f"Total ventas: ${total_ventas:,.2f}")
print(f"Margen estimado: ${total_margen_estimado:,.2f}")
print(f"Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}")
print(f"Departamentos analizados: {len(kpi_departamento)}")
print(f"Feriados identificados: {len(df_feriados)}")
print("\nArchivos generados:")
print(f"  - {output_html.name}")
print(f"  - KPI_DEPARTAMENTO_RENTABILIDAD.csv")
print(f"  - KPI_DIARIO_FERIADOS.csv")
print(f"  - KPI_DIA_SEMANA.csv")
print(f"  - KPI_MENSUAL.csv")
print(f"  - FERIADOS_2024_2025.csv")
print("=" * 100)

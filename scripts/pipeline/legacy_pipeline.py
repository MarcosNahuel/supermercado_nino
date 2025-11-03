# -*- coding: utf-8 -*-
"""
================================================================================
PIPELINE ESTRATÉGICO - SUPERMERCADO NINO
Implementación completa según PIPELINE_ESTRATEGIAS.md
================================================================================

Genera todos los datasets Parquet necesarios para el dashboard:
- KPIs base y temporales (diario, semanal, mensual, anual, hora)
- Rentabilidad por ticket
- Pareto global y segmentado (weekday/weekend)
- Market Basket + Adyacencias + Combos
- Clusters: departamento, tickets, medios de pago, productos temporales
- Clasificación de productos con IA

================================================================================
"""

import sys
import io
import warnings
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
warnings.filterwarnings('ignore')

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder

# =============================================================================
# CONFIGURACIÓN
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
OUTPUT_DIR = DATA_DIR / "app_dataset"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Archivos fuente
SALES_FILE = RAW_DIR / "SERIE_COMPROBANTES_COMPLETOS.csv"
RENTABILIDAD_FILE = RAW_DIR / "RENTABILIDAD.csv"

# Parámetros Market Basket
MIN_SUPPORT = 0.005
MIN_CONFIDENCE = 0.15
MIN_LIFT = 1.0

# Parámetros clustering
K_MIN = 3
K_MAX = 6
TOP_N_PRODUCTOS_TEMPORALES = 200

def info(msg: str) -> None:
    print(f"[INFO] {msg}")

def warn(msg: str) -> None:
    print(f"[WARN] {msg}")

print("=" * 100)
print("PIPELINE ESTRATÉGICO - SUPERMERCADO NINO")
print("Implementación completa según PIPELINE_ESTRATEGIAS.md")
print("=" * 100)

# =============================================================================
# PASO 1: CARGA DE DATOS
# =============================================================================
print("\n[PASO 1] Cargando datos...")
info(f"Archivo: {SALES_FILE}")

df_raw = pd.read_csv(
    SALES_FILE,
    sep=';',
    decimal=',',
    encoding='utf-8',
    low_memory=False
)

info(f"Registros cargados: {len(df_raw):,}")
info(f"Columnas: {list(df_raw.columns)}")

# =============================================================================
# PASO 2: NORMALIZACIÓN Y ENRIQUECIMIENTO (Sección 3)
# =============================================================================
print("\n[PASO 2] Normalización y enriquecimiento...")

# Renombrar columnas
column_mapping = {
    'Fecha': 'fecha',
    'Comprobante': 'ticket_id',
    'Código': 'producto_id',
    'Código barras': 'codigo_barras',
    'Marca': 'marca',
    'Departamento': 'categoria',
    'Nombre': 'descripcion',
    'Cantidad': 'cantidad',
    'Importe': 'importe_total',
    'Unitario': 'precio_unitario',
    'TIPO FACTURA': 'tipo_factura'
}
df = df_raw.rename(columns=column_mapping)

# Convertir tipos
df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
df['cantidad'] = pd.to_numeric(df['cantidad'].astype(str).str.replace(',', '.'), errors='coerce')
df['precio_unitario'] = pd.to_numeric(df['precio_unitario'].astype(str).str.replace(',', '.'), errors='coerce')

# Normalizar texto (sin acentos, strip, upper)
df['categoria'] = df['categoria'].astype(str).str.strip().str.upper()
df['categoria'] = df['categoria'].replace({'NAN': pd.NA})
df['marca'] = df['marca'].astype(str).str.strip().str.upper().fillna('SIN MARCA')
df['descripcion'] = df['descripcion'].astype(str).str.strip().str.upper()
df['producto_id'] = df['producto_id'].astype(str).str.strip().str.upper()
df['categoria'] = df['categoria'].fillna('SIN CATEGORIA')

# Medios de pago (Sección 3)
if 'Tipo medio de pago' in df.columns:
    df['tipo_medio_pago'] = df['Tipo medio de pago'].astype(str).str.strip().str.upper()
    df['tipo_medio_pago'] = df['tipo_medio_pago'].replace({'NAN': 'EFECTIVO', '': 'EFECTIVO'})
    df['tipo_medio_pago'] = df['tipo_medio_pago'].fillna('EFECTIVO')
    # Estandarizar
    df['tipo_medio_pago'] = df['tipo_medio_pago'].replace({
        'DEBITO': 'TARJETA_DEBITO',
        'CREDITO': 'TARJETA_CREDITO',
        'TARJETA DEBITO': 'TARJETA_DEBITO',
        'TARJETA CREDITO': 'TARJETA_CREDITO',
    })
else:
    df['tipo_medio_pago'] = 'EFECTIVO'

if 'Emisor tarjeta' in df.columns:
    df['emisor_tarjeta'] = df['Emisor tarjeta'].astype(str).str.strip().str.upper()
    df['emisor_tarjeta'] = df['emisor_tarjeta'].replace({'NAN': 'DESCONOCIDO', '': 'DESCONOCIDO'})
    df['emisor_tarjeta'] = df['emisor_tarjeta'].fillna('DESCONOCIDO')
else:
    df['emisor_tarjeta'] = 'DESCONOCIDO'

# Derivar campos temporales (Sección 3)
df['anio'] = df['fecha'].dt.year
df['mes'] = df['fecha'].dt.month
df['dia'] = df['fecha'].dt.day
df['dia_semana'] = df['fecha'].dt.day_name()
df['hora'] = df['fecha'].dt.hour
df['periodo'] = df['anio'].astype(str) + '-' + df['mes'].astype(str).str.zfill(2)

# Semana ISO (YYYY-WW)
iso_calendar = df['fecha'].dt.isocalendar()
df['semana_iso'] = iso_calendar['year'].astype(str) + '-W' + iso_calendar['week'].astype(str).str.zfill(2)

# Fin de semana (Sábado-Domingo)
df['es_fin_semana'] = df['dia_semana'].isin(['Saturday', 'Sunday'])

info("Enriquecimiento temporal completado")

# =============================================================================
# PASO 3: VINCULACIÓN CON RENTABILIDAD (Sección 1)
# =============================================================================
print("\n[PASO 3] Vinculando con rentabilidad por departamento...")

df_rentabilidad = pd.read_csv(RENTABILIDAD_FILE, encoding='utf-8', decimal=',')
df_rentabilidad['Departamento'] = df_rentabilidad['Departamento'].astype(str).str.strip().str.upper()
df_rentabilidad['Clasificación'] = df_rentabilidad['Clasificación'].astype(str).str.strip()

# Convertir rentabilidad de string "28%" a float 28.0
if df_rentabilidad['% Rentabilidad'].dtype == 'object':
    df_rentabilidad['rentabilidad_pct'] = df_rentabilidad['% Rentabilidad'].str.replace('%', '').astype(float)
else:
    df_rentabilidad['rentabilidad_pct'] = df_rentabilidad['% Rentabilidad']

# Mapear rentabilidad
rent_dict = df_rentabilidad.set_index('Departamento')['rentabilidad_pct'].to_dict()
clas_dict = df_rentabilidad.set_index('Departamento')['Clasificación'].to_dict()

df['rentabilidad_pct'] = df['categoria'].map(rent_dict).fillna(18.0)  # Fallback 18%
df['clasificacion_departamento'] = df['categoria'].map(clas_dict).fillna('SIN CLASIFICACION')

# Calcular margen estimado por línea (Sección 1)
df['margen_linea'] = df['importe_total'] * (df['rentabilidad_pct'] / 100)

info(f"Margen estimado total: ${df['margen_linea'].sum():,.2f}")

# =============================================================================
# PASO 4: AGREGACIÓN POR TICKET (base para KPIs)
# =============================================================================
print("\n[PASO 4] Agregando por ticket...")

df_tickets = (
    df.groupby('ticket_id')
    .agg(
        fecha=('fecha', 'first'),
        anio=('anio', 'first'),
        mes=('mes', 'first'),
        periodo=('periodo', 'first'),
        semana_iso=('semana_iso', 'first'),
        dia_semana=('dia_semana', 'first'),
        es_fin_semana=('es_fin_semana', 'first'),
        hora=('hora', 'first'),
        tipo_medio_pago=('tipo_medio_pago', 'first'),
        emisor_tarjeta=('emisor_tarjeta', 'first'),
        monto_total_ticket=('importe_total', 'sum'),
        margen_ticket=('margen_linea', 'sum'),
        items_ticket=('cantidad', 'sum'),
        skus_ticket=('producto_id', 'nunique'),
    )
    .reset_index()
)

df_tickets['rentabilidad_pct_ticket'] = np.where(
    df_tickets['monto_total_ticket'] > 0,
    df_tickets['margen_ticket'] / df_tickets['monto_total_ticket'],
    np.nan
)

df_tickets['fecha_corta'] = df_tickets['fecha'].dt.date

info(f"Tickets agregados: {len(df_tickets):,}")

# =============================================================================
# PASO 5: ALCANCE DEL DATASET (Sección 1)
# =============================================================================
print("\n[PASO 5] Calculando alcance del dataset...")

min_fecha = df['fecha'].min()
max_fecha = df['fecha'].max()
n_tickets = df_tickets['ticket_id'].nunique()
n_skus_unicos = df['producto_id'].nunique()  # SKUs únicos, NO registros
n_registros = len(df)
ventas_total = df['importe_total'].sum()
margen_total = df['margen_linea'].sum()

info(f"Periodo: {min_fecha.strftime('%d/%m/%Y')} - {max_fecha.strftime('%d/%m/%Y')}")
info(f"Tickets: {n_tickets:,}")
info(f"SKUs únicos: {n_skus_unicos:,}")
info(f"Registros/líneas: {n_registros:,}")
info(f"Ventas: ${ventas_total:,.2f} ARS")
info(f"Margen: ${margen_total:,.2f} ARS")

# Guardar alcance para dashboard
alcance_dataset = pd.DataFrame([{
    'min_fecha': min_fecha,
    'max_fecha': max_fecha,
    'n_tickets': n_tickets,
    'n_skus_unicos': n_skus_unicos,
    'n_registros': n_registros,
    'ventas_total': ventas_total,
    'margen_total': margen_total,
}])
alcance_dataset.to_parquet(OUTPUT_DIR / 'alcance_dataset.parquet', index=False)
info("✓ alcance_dataset.parquet")

# =============================================================================
# PASO 6: KPIs BASE (Sección 2)
# =============================================================================
print("\n[PASO 6] Calculando KPIs base...")

ticket_promedio = df_tickets['monto_total_ticket'].mean()
items_promedio_ticket = df_tickets['items_ticket'].mean()
rentabilidad_global = margen_total / ventas_total if ventas_total > 0 else 0
rentabilidad_promedio_ticket = df_tickets['margen_ticket'].mean()

kpis_base = pd.DataFrame([{
    'rentabilidad_global': rentabilidad_global,
    'ticket_promedio': ticket_promedio,
    'items_promedio_ticket': items_promedio_ticket,
    'rentabilidad_promedio_ticket': rentabilidad_promedio_ticket,
}])
kpis_base.to_parquet(OUTPUT_DIR / 'kpis_base.parquet', index=False)
info("✓ kpis_base.parquet")

print(f"\n📊 KPIs BASE:")
print(f"  Rentabilidad Global: {rentabilidad_global*100:.2f}%")
print(f"  Ticket Promedio: ${ticket_promedio:,.2f}")
print(f"  Items Promedio/Ticket: {items_promedio_ticket:.2f}")
print(f"  Rentabilidad Promedio/Ticket: ${rentabilidad_promedio_ticket:,.2f}")

# =============================================================================
# PASO 7: KPIs TEMPORALES (Sección 4)
# =============================================================================
print("\n[PASO 7] Generando KPIs temporales...")

# kpi_diario.parquet
kpi_diario = (
    df_tickets.groupby('fecha_corta')
    .agg(
        ventas=('monto_total_ticket', 'sum'),
        margen=('margen_ticket', 'sum'),
        tickets=('ticket_id', 'count'),
    )
    .reset_index()
)
kpi_diario['fecha'] = pd.to_datetime(kpi_diario['fecha_corta'])
kpi_diario['rentabilidad_pct'] = kpi_diario['margen'] / kpi_diario['ventas']
kpi_diario.to_parquet(OUTPUT_DIR / 'kpi_diario.parquet', index=False)
info(f"✓ kpi_diario.parquet ({len(kpi_diario)} registros)")

# kpi_hora.parquet
df_tickets_hora = df_tickets.copy()
df_tickets_hora['fecha_hora'] = df_tickets_hora['fecha'].dt.floor('H')
kpi_hora = (
    df_tickets_hora.groupby(['fecha_hora', 'hora'])
    .agg(
        ventas=('monto_total_ticket', 'sum'),
        margen=('margen_ticket', 'sum'),
        tickets=('ticket_id', 'count'),
    )
    .reset_index()
)
kpi_hora['rentabilidad_pct'] = kpi_hora['margen'] / kpi_hora['ventas']
kpi_hora.to_parquet(OUTPUT_DIR / 'kpi_hora.parquet', index=False)
info(f"✓ kpi_hora.parquet ({len(kpi_hora)} registros)")

# kpi_semana.parquet
kpi_semana = (
    df_tickets.groupby('semana_iso')
    .agg(
        ventas=('monto_total_ticket', 'sum'),
        margen=('margen_ticket', 'sum'),
        tickets=('ticket_id', 'count'),
    )
    .reset_index()
)
kpi_semana['rentabilidad_pct'] = kpi_semana['margen'] / kpi_semana['ventas']
kpi_semana.to_parquet(OUTPUT_DIR / 'kpi_semana.parquet', index=False)
info(f"✓ kpi_semana.parquet ({len(kpi_semana)} registros)")

# kpi_periodo.parquet (mensual)
kpi_periodo = (
    df_tickets.groupby('periodo')
    .agg(
        ventas=('monto_total_ticket', 'sum'),
        margen=('margen_ticket', 'sum'),
        tickets=('ticket_id', 'count'),
    )
    .reset_index()
)
kpi_periodo['rentabilidad_pct'] = kpi_periodo['margen'] / kpi_periodo['ventas']
kpi_periodo.to_parquet(OUTPUT_DIR / 'kpi_periodo.parquet', index=False)
info(f"✓ kpi_periodo.parquet ({len(kpi_periodo)} registros)")

# kpi_anio.parquet
kpi_anio = (
    df_tickets.groupby('anio')
    .agg(
        ventas=('monto_total_ticket', 'sum'),
        margen=('margen_ticket', 'sum'),
        tickets=('ticket_id', 'count'),
    )
    .reset_index()
)
kpi_anio['rentabilidad_pct'] = kpi_anio['margen'] / kpi_anio['ventas']
kpi_anio.to_parquet(OUTPUT_DIR / 'kpi_anio.parquet', index=False)
info(f"✓ kpi_anio.parquet ({len(kpi_anio)} registros)")

# kpi_dow_weekend.parquet
kpi_dow_weekend = (
    df_tickets.groupby(['dia_semana', 'es_fin_semana'])
    .agg(
        ventas=('monto_total_ticket', 'sum'),
        margen=('margen_ticket', 'sum'),
        tickets=('ticket_id', 'count'),
    )
    .reset_index()
)
kpi_dow_weekend['rentabilidad_pct'] = kpi_dow_weekend['margen'] / kpi_dow_weekend['ventas']
kpi_dow_weekend.to_parquet(OUTPUT_DIR / 'kpi_dow_weekend.parquet', index=False)
info(f"✓ kpi_dow_weekend.parquet ({len(kpi_dow_weekend)} registros)")

# =============================================================================
# PASO 8: RENTABILIDAD POR TICKET (Sección 8)
# =============================================================================
print("\n[PASO 8] Rentabilidad por ticket...")

rentabilidad_ticket = df_tickets[['ticket_id', 'fecha', 'periodo', 'items_ticket', 'monto_total_ticket', 'margen_ticket', 'rentabilidad_pct_ticket']].copy()
rentabilidad_ticket.to_parquet(OUTPUT_DIR / 'rentabilidad_ticket.parquet', index=False)
info(f"✓ rentabilidad_ticket.parquet ({len(rentabilidad_ticket)} registros)")

# =============================================================================
# PASO 9: PARETO GLOBAL Y SEGMENTADO (Sección 5)
# =============================================================================
print("\n[PASO 9] Generando Pareto global y segmentado...")

def calcular_pareto(df_grupo, nombre):
    """Calcula clasificación ABC por ventas y margen"""
    df_sorted = df_grupo.sort_values('ventas', ascending=False).reset_index(drop=True)
    df_sorted['ventas_acumuladas'] = df_sorted['ventas'].cumsum()
    df_sorted['pct_acumulado_ventas'] = (df_sorted['ventas_acumuladas'] / df_sorted['ventas'].sum() * 100).round(2)

    df_sorted['abc_ventas'] = pd.cut(
        df_sorted['pct_acumulado_ventas'],
        bins=[0, 80, 95, 100],
        labels=['A', 'B', 'C']
    )

    # ABC por margen
    df_sorted_margen = df_grupo.sort_values('margen', ascending=False).reset_index(drop=True)
    df_sorted_margen['margen_acumulado'] = df_sorted_margen['margen'].cumsum()
    df_sorted_margen['pct_acumulado_margen'] = (df_sorted_margen['margen_acumulado'] / df_sorted_margen['margen'].sum() * 100).round(2)
    df_sorted_margen['abc_margen'] = pd.cut(
        df_sorted_margen['pct_acumulado_margen'],
        bins=[0, 80, 95, 100],
        labels=['A', 'B', 'C']
    )

    # Merge ABC margen
    if 'producto_id' in df_sorted.columns:
        merge_on = 'producto_id'
    else:
        merge_on = 'categoria'

    df_sorted = df_sorted.merge(
        df_sorted_margen[[merge_on, 'abc_margen']],
        on=merge_on,
        how='left'
    )

    return df_sorted

# Pareto categorías global
pareto_cat_global = df.groupby('categoria').agg({
    'importe_total': 'sum',
    'margen_linea': 'sum'
}).reset_index()
pareto_cat_global.columns = ['categoria', 'ventas', 'margen']
pareto_cat_global = calcular_pareto(pareto_cat_global, 'cat_global')
pareto_cat_global.to_parquet(OUTPUT_DIR / 'pareto_cat_global.parquet', index=False)
info(f"✓ pareto_cat_global.parquet ({len(pareto_cat_global)} registros)")

# Pareto productos global
pareto_prod_global = df.groupby(['producto_id', 'descripcion', 'categoria']).agg({
    'importe_total': 'sum',
    'margen_linea': 'sum'
}).reset_index()
pareto_prod_global.columns = ['producto_id', 'descripcion', 'categoria', 'ventas', 'margen']
pareto_prod_global = calcular_pareto(pareto_prod_global, 'prod_global')
pareto_prod_global.to_parquet(OUTPUT_DIR / 'pareto_prod_global.parquet', index=False)
info(f"✓ pareto_prod_global.parquet ({len(pareto_prod_global)} registros)")

# Pareto categorías weekday
df_weekday = df[~df['es_fin_semana']]
pareto_cat_weekday = df_weekday.groupby('categoria').agg({
    'importe_total': 'sum',
    'margen_linea': 'sum'
}).reset_index()
pareto_cat_weekday.columns = ['categoria', 'ventas', 'margen']
pareto_cat_weekday = calcular_pareto(pareto_cat_weekday, 'cat_weekday')
pareto_cat_weekday.to_parquet(OUTPUT_DIR / 'pareto_cat_weekday.parquet', index=False)
info(f"✓ pareto_cat_weekday.parquet ({len(pareto_cat_weekday)} registros)")

# Pareto categorías weekend
df_weekend = df[df['es_fin_semana']]
pareto_cat_weekend = df_weekend.groupby('categoria').agg({
    'importe_total': 'sum',
    'margen_linea': 'sum'
}).reset_index()
pareto_cat_weekend.columns = ['categoria', 'ventas', 'margen']
pareto_cat_weekend = calcular_pareto(pareto_cat_weekend, 'cat_weekend')
pareto_cat_weekend.to_parquet(OUTPUT_DIR / 'pareto_cat_weekend.parquet', index=False)
info(f"✓ pareto_cat_weekend.parquet ({len(pareto_cat_weekend)} registros)")

# Pareto productos weekday
pareto_prod_weekday = df_weekday.groupby(['producto_id', 'descripcion', 'categoria']).agg({
    'importe_total': 'sum',
    'margen_linea': 'sum'
}).reset_index()
pareto_prod_weekday.columns = ['producto_id', 'descripcion', 'categoria', 'ventas', 'margen']
pareto_prod_weekday = calcular_pareto(pareto_prod_weekday, 'prod_weekday')
pareto_prod_weekday.to_parquet(OUTPUT_DIR / 'pareto_prod_weekday.parquet', index=False)
info(f"✓ pareto_prod_weekday.parquet ({len(pareto_prod_weekday)} registros)")

# Pareto productos weekend
pareto_prod_weekend = df_weekend.groupby(['producto_id', 'descripcion', 'categoria']).agg({
    'importe_total': 'sum',
    'margen_linea': 'sum'
}).reset_index()
pareto_prod_weekend.columns = ['producto_id', 'descripcion', 'categoria', 'ventas', 'margen']
pareto_prod_weekend = calcular_pareto(pareto_prod_weekend, 'prod_weekend')
pareto_prod_weekend.to_parquet(OUTPUT_DIR / 'pareto_prod_weekend.parquet', index=False)
info(f"✓ pareto_prod_weekend.parquet ({len(pareto_prod_weekend)} registros)")

# =============================================================================
# PASO 10: MARKET BASKET + ADYACENCIAS + COMBOS (Sección 6)
# =============================================================================
print("\n[PASO 10] Market Basket Analysis...")

# Identificar productos clave manualmente (COCA, FERNET, etc.) + top ventas
productos_clave = []

# Buscar Coca y Fernet explícitamente
df['desc_upper'] = df['descripcion'].str.upper()
productos_coca = df[df['desc_upper'].str.contains('COCA', na=False)]['producto_id'].unique()
productos_fernet = df[df['desc_upper'].str.contains('FERNET', na=False)]['producto_id'].unique()

# Agregar combos frecuentes conocidos
productos_vino = df[df['desc_upper'].str.contains('VINO', na=False)].groupby('producto_id')['importe_total'].sum().nlargest(5).index.tolist()
productos_carne = df[df['categoria'].str.contains('CARNI', na=False)].groupby('producto_id')['importe_total'].sum().nlargest(5).index.tolist()

# Top 20 productos globales
top_20 = pareto_prod_global.head(20)['producto_id'].tolist()

# Unir todos
productos_clave = list(set(list(productos_coca) + list(productos_fernet) + productos_vino + productos_carne + top_20))
info(f"Productos para basket: {len(productos_clave)} (incluye COCA, FERNET, VINO, CARNE, TOP 20)")

df_basket = df[df['producto_id'].isin(productos_clave)].copy()

# Filtrar tickets con al menos 2 productos
tickets_validos = df_basket.groupby('ticket_id')['producto_id'].nunique()
tickets_validos = tickets_validos[tickets_validos >= 2].index

# Muestra de 25000 tickets
np.random.seed(42)
if len(tickets_validos) > 25000:
    tickets_sample = np.random.choice(tickets_validos, size=25000, replace=False)
else:
    tickets_sample = tickets_validos

df_basket = df_basket[df_basket['ticket_id'].isin(tickets_sample)]

info(f"Tickets para análisis (muestra): {df_basket['ticket_id'].nunique():,}")

# Crear transacciones
transacciones = df_basket.groupby('ticket_id')['descripcion'].apply(list).tolist()

# Encoder
te = TransactionEncoder()
te_ary = te.fit(transacciones).transform(transacciones)
df_encoded = pd.DataFrame(te_ary, columns=te.columns_)

info(f"Matriz: {df_encoded.shape[0]} tickets × {df_encoded.shape[1]} productos")

# Apriori
try:
    frequent_itemsets = apriori(df_encoded, min_support=MIN_SUPPORT, use_colnames=True)

    if len(frequent_itemsets) > 0:
        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=MIN_CONFIDENCE)
        rules = rules[rules['lift'] >= MIN_LIFT]
        rules = rules.sort_values('lift', ascending=False)

        # Reglas
        rules_export = rules.copy()
        rules_export['antecedents'] = rules_export['antecedents'].apply(lambda x: ', '.join(list(x)))
        rules_export['consequents'] = rules_export['consequents'].apply(lambda x: ', '.join(list(x)))
        rules_export.to_parquet(OUTPUT_DIR / 'reglas.parquet', index=False)
        info(f"✓ reglas.parquet ({len(rules_export)} registros)")

        # Adyacencias (pares con lift alto)
        adjacency_pairs = rules[rules['antecedents'].apply(len) == 1][['antecedents', 'consequents', 'support', 'confidence', 'lift']].copy()
        adjacency_pairs['antecedent'] = adjacency_pairs['antecedents'].apply(lambda x: list(x)[0])
        adjacency_pairs['consequent'] = adjacency_pairs['consequents'].apply(lambda x: list(x)[0])
        adjacency_pairs = adjacency_pairs[['antecedent', 'consequent', 'support', 'confidence', 'lift']]
        adjacency_pairs = adjacency_pairs.nlargest(50, 'lift')
        adjacency_pairs.to_parquet(OUTPUT_DIR / 'adjacency_pairs.parquet', index=False)
        info(f"✓ adjacency_pairs.parquet ({len(adjacency_pairs)} registros)")

        # Combos recomendados (con precio y margen estimado)
        combos = rules.nlargest(20, 'lift').copy()
        combos['antecedent'] = combos['antecedents'].apply(lambda x: ', '.join(list(x)))
        combos['consequent'] = combos['consequents'].apply(lambda x: ', '.join(list(x)))

        # Calcular precios (promedio de productos involucrados)
        precio_map = df.groupby('descripcion')['precio_unitario'].mean().to_dict()
        margen_pct_map = df.groupby('descripcion')['rentabilidad_pct'].mean().to_dict()

        def calcular_precio_combo(row):
            items = list(row['antecedents']) + list(row['consequents'])
            precios = [precio_map.get(item, 0) for item in items]
            return sum(precios)

        def calcular_margen_combo(row):
            items = list(row['antecedents']) + list(row['consequents'])
            margen_pcts = [margen_pct_map.get(item, 18) for item in items]
            return np.mean(margen_pcts)

        combos['precio_combo_sugerido'] = combos.apply(calcular_precio_combo, axis=1) * 0.9  # 10% descuento
        combos['margen_combo_estimado'] = combos.apply(calcular_margen_combo, axis=1)
        combos['adopcion_objetivo_pct'] = 2.0  # 2% objetivo

        combos_export = combos[['antecedent', 'consequent', 'support', 'confidence', 'lift', 'precio_combo_sugerido', 'margen_combo_estimado', 'adopcion_objetivo_pct']]
        combos_export.to_parquet(OUTPUT_DIR / 'combos_recomendados.parquet', index=False)
        info(f"✓ combos_recomendados.parquet ({len(combos_export)} registros)")
    else:
        info("No se encontraron itemsets frecuentes")
except Exception as e:
    warn(f"Error en Market Basket: {e}")

# =============================================================================
# PASO 11: CLUSTERING (Sección 7)
# =============================================================================
print("\n[PASO 11] Clustering...")

# 7.0 Clusters por departamento (baseline)
clusters_departamento = df.groupby('categoria').agg({
    'importe_total': 'sum',
    'margen_linea': 'sum',
    'ticket_id': 'nunique',
    'cantidad': 'sum'
}).reset_index()
clusters_departamento.columns = ['departamento', 'ventas', 'margen', 'tickets', 'unidades']
clusters_departamento['ticket_promedio'] = clusters_departamento['ventas'] / clusters_departamento['tickets']
clusters_departamento['items_promedio'] = clusters_departamento['unidades'] / clusters_departamento['tickets']
clusters_departamento['rentabilidad_pct'] = clusters_departamento['margen'] / clusters_departamento['ventas']
clusters_departamento.to_parquet(OUTPUT_DIR / 'clusters_departamento.parquet', index=False)
info(f"✓ clusters_departamento.parquet ({len(clusters_departamento)} registros)")

# 7.1 Clusters de tickets
features_tickets = df_tickets[['monto_total_ticket', 'items_ticket']].copy()
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features_tickets)

best_k = 4
kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
df_tickets['cluster'] = kmeans.fit_predict(features_scaled)

clusters_tickets = (
    df_tickets.groupby('cluster')
    .agg(
        cantidad_tickets=('ticket_id', 'count'),
        ticket_promedio=('monto_total_ticket', 'mean'),
        items_promedio=('items_ticket', 'mean'),
        margen_promedio=('margen_ticket', 'mean'),
    )
    .reset_index()
)
clusters_tickets['pct_tickets'] = (clusters_tickets['cantidad_tickets'] / clusters_tickets['cantidad_tickets'].sum() * 100).round(1)

def etiquetar_cluster(row):
    if row['ticket_promedio'] < 5000:
        return "Compra de Conveniencia"
    elif row['ticket_promedio'] >= 20000:
        return "Compra Grande"
    else:
        return "Compra Mediana"

clusters_tickets['etiqueta'] = clusters_tickets.apply(etiquetar_cluster, axis=1)
clusters_tickets.to_parquet(OUTPUT_DIR / 'clusters_tickets.parquet', index=False)
info(f"✓ clusters_tickets.parquet ({len(clusters_tickets)} registros)")

# 7.2 Clusters de medios de pago
kpi_medio_pago = (
    df_tickets.groupby(['tipo_medio_pago', 'emisor_tarjeta'])
    .agg(
        tickets=('ticket_id', 'count'),
        ventas=('monto_total_ticket', 'sum'),
        margen=('margen_ticket', 'sum'),
        ticket_promedio=('monto_total_ticket', 'mean'),
        ticket_p50=('monto_total_ticket', 'median'),
        ticket_p90=('monto_total_ticket', lambda x: np.percentile(x, 90)),
        pct_fin_semana=('es_fin_semana', lambda x: x.sum() / len(x) * 100),
    )
    .reset_index()
)
kpi_medio_pago['participacion_ventas'] = (kpi_medio_pago['ventas'] / kpi_medio_pago['ventas'].sum() * 100).round(2)
kpi_medio_pago['participacion_margen'] = (kpi_medio_pago['margen'] / kpi_medio_pago['margen'].sum() * 100).round(2)
kpi_medio_pago.to_parquet(OUTPUT_DIR / 'kpi_medio_pago.parquet', index=False)
info(f"✓ kpi_medio_pago.parquet ({len(kpi_medio_pago)} registros)")

# Simplificado: clusters por tipo
clusters_pago_tickets = (
    df_tickets.groupby('tipo_medio_pago')
    .agg(
        tickets=('ticket_id', 'count'),
        ventas=('monto_total_ticket', 'sum'),
        margen=('margen_ticket', 'sum'),
        ticket_promedio=('monto_total_ticket', 'mean'),
    )
    .reset_index()
)
clusters_pago_tickets['cluster'] = range(len(clusters_pago_tickets))
clusters_pago_tickets.to_parquet(OUTPUT_DIR / 'clusters_pago_tickets.parquet', index=False)
info(f"✓ clusters_pago_tickets.parquet ({len(clusters_pago_tickets)} registros)")

# 7.3 Clusters de productos por patrón temporal
top_productos_temp = pareto_prod_global.head(TOP_N_PRODUCTOS_TEMPORALES)['producto_id'].tolist()
df_temp = df[df['producto_id'].isin(top_productos_temp)].copy()

# Ventas semanales por producto
ventas_semanales = df_temp.groupby(['producto_id', 'semana_iso'])['importe_total'].sum().reset_index()
ventas_pivot = ventas_semanales.pivot(index='producto_id', columns='semana_iso', values='importe_total').fillna(0)

# Normalizar
scaler_temp = StandardScaler()
ventas_scaled = scaler_temp.fit_transform(ventas_pivot)

# Clustering
k_temp = min(5, len(ventas_pivot) - 1)
if k_temp >= 2:
    kmeans_temp = KMeans(n_clusters=k_temp, random_state=42, n_init=10)
    clusters_temp = kmeans_temp.fit_predict(ventas_scaled)

    clusters_productos_temporales = pd.DataFrame({
        'producto_id': ventas_pivot.index,
        'cluster_temporal': clusters_temp,
        'etiqueta': ['Cluster ' + str(c) for c in clusters_temp]
    })
    clusters_productos_temporales.to_parquet(OUTPUT_DIR / 'clusters_productos_temporales.parquet', index=False)
    info(f"✓ clusters_productos_temporales.parquet ({len(clusters_productos_temporales)} registros)")
else:
    info("No hay suficientes productos para clustering temporal")

# 7.4 Clasificación de productos con IA
# Features: margen relativo, frecuencia, CV ventas, precio
df_productos_ai = pareto_prod_global[['producto_id', 'descripcion', 'ventas', 'margen']].copy()
df_productos_ai['margen_relativo'] = df_productos_ai['margen'] / df_productos_ai['ventas']

# Frecuencia (semanas con ventas)
frecuencia = df.groupby('producto_id')['semana_iso'].nunique().reset_index()
frecuencia.columns = ['producto_id', 'frecuencia_semanas']
df_productos_ai = df_productos_ai.merge(frecuencia, on='producto_id', how='left')

# CV de ventas semanales
cv_ventas = ventas_semanales.groupby('producto_id')['importe_total'].agg(['mean', 'std']).reset_index()
cv_ventas['cv_ventas'] = cv_ventas['std'] / cv_ventas['mean']
df_productos_ai = df_productos_ai.merge(cv_ventas[['producto_id', 'cv_ventas']], on='producto_id', how='left')

# Precio promedio
precio_promedio = df.groupby('producto_id')['precio_unitario'].mean().reset_index()
precio_promedio.columns = ['producto_id', 'precio_promedio']
df_productos_ai = df_productos_ai.merge(precio_promedio, on='producto_id', how='left')

# Clustering
features_ai = df_productos_ai[['margen_relativo', 'frecuencia_semanas', 'cv_ventas', 'precio_promedio']].fillna(0)
scaler_ai = StandardScaler()
features_ai_scaled = scaler_ai.fit_transform(features_ai)

k_ai = min(6, len(features_ai_scaled) - 1)
if k_ai >= 2:
    kmeans_ai = KMeans(n_clusters=k_ai, random_state=42, n_init=10)
    cluster_ai = kmeans_ai.fit_predict(features_ai_scaled)

    clasificacion_productos = df_productos_ai[['producto_id', 'descripcion']].copy()
    clasificacion_productos['cluster_ai'] = cluster_ai
    clasificacion_productos['etiqueta'] = 'Cluster AI ' + clasificacion_productos['cluster_ai'].astype(str)
    clasificacion_productos.to_parquet(OUTPUT_DIR / 'clasificacion_productos.parquet', index=False)
    info(f"✓ clasificacion_productos.parquet ({len(clasificacion_productos)} registros)")
else:
    info("No hay suficientes productos para clasificación AI")

# =============================================================================
# PASO 12: KPI POR CATEGORÍA (para compatibilidad con dashboard actual)
# =============================================================================
print("\n[PASO 12] KPI por categoría...")

kpi_categoria = df.groupby('categoria').agg({
    'importe_total': 'sum',
    'margen_linea': 'sum',
    'cantidad': 'sum',
    'ticket_id': 'nunique'
}).reset_index()
kpi_categoria.columns = ['categoria', 'ventas', 'margen', 'unidades', 'tickets']
kpi_categoria['margen_pct'] = (kpi_categoria['margen'] / kpi_categoria['ventas'] * 100).round(2)
kpi_categoria['pct_ventas'] = (kpi_categoria['ventas'] / kpi_categoria['ventas'].sum() * 100).round(2)
kpi_categoria = kpi_categoria.sort_values('ventas', ascending=False)
kpi_categoria.to_parquet(OUTPUT_DIR / 'kpi_categoria.parquet', index=False)
info(f"✓ kpi_categoria.parquet ({len(kpi_categoria)} registros)")

# =============================================================================
# PASO 13: KPI POR DÍA (para compatibilidad)
# =============================================================================
kpi_dia_semana = (
    df_tickets.groupby('dia_semana')
    .agg(
        ventas=('monto_total_ticket', 'sum'),
        margen=('margen_ticket', 'sum'),
        tickets=('ticket_id', 'count'),
    )
    .reset_index()
)
kpi_dia_semana['rentabilidad_pct'] = kpi_dia_semana['margen'] / kpi_dia_semana['ventas']
kpi_dia_semana.to_parquet(OUTPUT_DIR / 'kpi_dia.parquet', index=False)
info(f"✓ kpi_dia.parquet ({len(kpi_dia_semana)} registros)")

# =============================================================================
# PASO 14: TICKETS (para compatibilidad con dashboard actual)
# =============================================================================
df_tickets.to_parquet(OUTPUT_DIR / 'tickets.parquet', index=False)
info(f"✓ tickets.parquet ({len(df_tickets)} registros)")

# =============================================================================
# FINALIZACIÓN
# =============================================================================
print("\n" + "=" * 100)
print("PIPELINE COMPLETADO")
print("=" * 100)
print(f"\nArchivos generados en: {OUTPUT_DIR}")
print(f"Total de archivos Parquet: {len(list(OUTPUT_DIR.glob('*.parquet')))}")
print(f"\nPaso siguiente sugerido: streamlit run dashboard_cientifico.py")
print("=" * 100)

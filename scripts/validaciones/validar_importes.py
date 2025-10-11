# -*- coding: utf-8 -*-
"""
VALIDACIÓN DE IMPORTES - Detectar problemas en los datos
"""

import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"

print("="*80)
print("VALIDACIÓN DE ESTRUCTURA DE DATOS")
print("="*80)

# Cargar muestra grande
print("\n[1] Cargando muestra de 10,000 registros...")
df = pd.read_csv(
    BASE_DIR / 'SERIE_COMPROBANTES_COMPLETOS.csv',
    sep=';',
    encoding='utf-8',
    nrows=10000
)

print(f"Registros cargados: {len(df):,}")
print(f"Columnas: {list(df.columns)}")

# Convertir tipos
df['Cantidad'] = pd.to_numeric(df['Cantidad'], errors='coerce')
df['Importe'] = pd.to_numeric(df['Importe'], errors='coerce')
df['Unitario'] = pd.to_numeric(df['Unitario'], errors='coerce')

print("\n[2] Validando fórmula: Importe = Cantidad × Unitario")
df['Importe_Calculado'] = df['Cantidad'] * df['Unitario']
df['Diferencia'] = abs(df['Importe'] - df['Importe_Calculado'])

incorrectos = df[df['Diferencia'] > 0.01]
print(f"Registros con fórmula incorrecta: {len(incorrectos):,} ({len(incorrectos)/len(df)*100:.2f}%)")

if len(incorrectos) > 0:
    print("\nEjemplos de registros incorrectos:")
    print(incorrectos[['Comprobante', 'Nombre', 'Cantidad', 'Unitario', 'Importe', 'Importe_Calculado']].head())

print("\n[3] Detectando duplicados exactos...")
duplicados = df[df.duplicated(keep=False)]
print(f"Filas duplicadas (exactas): {len(duplicados):,}")

if len(duplicados) > 0:
    print("\nEjemplo de duplicados:")
    print(duplicados[['Comprobante', 'Código', 'Nombre', 'Cantidad', 'Importe']].head(10))

print("\n[4] Analizando items por comprobante...")
items_por_comp = df.groupby('Comprobante').size()
print(f"Items por comprobante - Promedio: {items_por_comp.mean():.2f}")
print(f"Items por comprobante - Mediana: {items_por_comp.median():.0f}")
print(f"Items por comprobante - Máximo: {items_por_comp.max()}")
print(f"Items por comprobante - Mínimo: {items_por_comp.min()}")

print("\n[5] Calculando ticket total por comprobante (método correcto)...")
# Método 1: Sumar directamente los importes
total_metodo1 = df['Importe'].sum()
print(f"Método 1 (suma directa de Importe): ${total_metodo1:,.2f}")

# Método 2: Agrupar por comprobante y sumar
tickets = df.groupby('Comprobante').agg({
    'Importe': 'sum',
    'Cantidad': 'sum'
}).reset_index()

total_metodo2 = tickets['Importe'].sum()
comprobantes_unicos = len(tickets)
ticket_promedio = tickets['Importe'].mean()

print(f"Método 2 (agrupar por comprobante):")
print(f"  - Total ventas: ${total_metodo2:,.2f}")
print(f"  - Comprobantes únicos: {comprobantes_unicos:,}")
print(f"  - Ticket promedio: ${ticket_promedio:,.2f}")
print(f"  - Items promedio por ticket: {items_por_comp.mean():.2f}")

print("\n[6] Validando coherencia de métodos...")
if abs(total_metodo1 - total_metodo2) < 0.01:
    print("✓ CORRECTO: Ambos métodos dan el mismo resultado")
else:
    print("✗ ERROR: Los métodos difieren")
    print(f"  Diferencia: ${abs(total_metodo1 - total_metodo2):,.2f}")

print("\n[7] Ejemplos de comprobantes completos:")
for comp_id in df['Comprobante'].unique()[:3]:
    comp_data = df[df['Comprobante'] == comp_id]
    total_comp = comp_data['Importe'].sum()
    items = len(comp_data)
    print(f"\n{comp_id}:")
    print(f"  Items: {items}")
    print(f"  Total: ${total_comp:,.2f}")
    print(comp_data[['Nombre', 'Cantidad', 'Unitario', 'Importe']].to_string(index=False))

print("\n" + "="*80)
print("CONCLUSIÓN")
print("="*80)
print("""
Si la fórmula Importe = Cantidad × Unitario es consistente,
entonces SUMAR directamente la columna 'Importe' es correcto.

Cada fila ya representa el importe total de ese item.
El ticket total se obtiene sumando todos los importes de ese comprobante.
""")

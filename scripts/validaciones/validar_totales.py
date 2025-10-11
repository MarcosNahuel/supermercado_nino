# -*- coding: utf-8 -*-
"""
Validación de Totales - Diagnóstico del problema
"""

import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"

print("="*80)
print("DIAGNÓSTICO: VALIDACIÓN DE TOTALES")
print("="*80)

# Cargar datos originales
print("\n[1] Cargando datos originales...")
df_raw = pd.read_csv(
    BASE_DIR / 'SERIE_COMPROBANTES_COMPLETOS.csv',
    sep=';',
    encoding='utf-8',
    low_memory=False
)

print(f"Total registros brutos: {len(df_raw):,}")

# Convertir tipos
df_raw['Importe'] = pd.to_numeric(df_raw['Importe'], errors='coerce')
df_raw['Cantidad'] = pd.to_numeric(df_raw['Cantidad'], errors='coerce')

# Eliminar NaN en Importe
df_clean = df_raw.dropna(subset=['Importe'])
print(f"Registros con importe válido: {len(df_clean):,}")

print("\n[2] MÉTODO 1: Suma directa de columna Importe")
total_metodo1 = df_clean['Importe'].sum()
print(f"Total Ventas (suma directa): ${total_metodo1:,.2f}")

print("\n[3] MÉTODO 2: Agrupar por ticket y sumar")
tickets = df_clean.groupby('Comprobante')['Importe'].sum().reset_index()
tickets.columns = ['Comprobante', 'Total_Ticket']

total_metodo2 = tickets['Total_Ticket'].sum()
total_tickets = len(tickets)
ticket_promedio = tickets['Total_Ticket'].mean()
ticket_mediano = tickets['Total_Ticket'].median()

print(f"Total Ventas (por tickets): ${total_metodo2:,.2f}")
print(f"Total Tickets: {total_tickets:,}")
print(f"Ticket Promedio: ${ticket_promedio:,.2f}")
print(f"Ticket Mediano: ${ticket_mediano:,.2f}")

print("\n[4] COMPARACIÓN")
diferencia = abs(total_metodo1 - total_metodo2)
print(f"Diferencia entre métodos: ${diferencia:,.2f}")

if diferencia < 1:
    print("✓ CORRECTO: Ambos métodos coinciden")
else:
    print("✗ ERROR: Los métodos difieren")

print("\n[5] VERIFICACIÓN CON MUESTRA")
print("\nPrimeros 5 tickets:")
muestra = tickets.head(5)
print(muestra.to_string(index=False))

print("\n[6] ESTADÍSTICAS DE TICKETS")
print(f"Ticket más bajo: ${tickets['Total_Ticket'].min():,.2f}")
print(f"Ticket más alto: ${tickets['Total_Ticket'].max():,.2f}")
print(f"Percentil 25: ${tickets['Total_Ticket'].quantile(0.25):,.2f}")
print(f"Percentil 75: ${tickets['Total_Ticket'].quantile(0.75):,.2f}")
print(f"Percentil 90: ${tickets['Total_Ticket'].quantile(0.90):,.2f}")
print(f"Percentil 95: ${tickets['Total_Ticket'].quantile(0.95):,.2f}")

print("\n[7] ANÁLISIS POR TIPO DE FACTURA")
tipo_factura = df_clean.groupby('TIPO FACTURA').agg({
    'Importe': 'sum',
    'Comprobante': 'nunique'
}).reset_index()
tipo_factura.columns = ['Tipo', 'Total_Ventas', 'Cantidad_Tickets']
print("\nVentas por tipo de factura:")
print(tipo_factura.to_string(index=False))

print("\n[8] DETECCIÓN DE OUTLIERS")
# Tickets muy grandes (posibles errores)
outliers = tickets[tickets['Total_Ticket'] > tickets['Total_Ticket'].quantile(0.99)]
print(f"\nTickets por encima del percentil 99: {len(outliers)}")
if len(outliers) > 0:
    print("Top 10 tickets más grandes:")
    print(outliers.nlargest(10, 'Total_Ticket').to_string(index=False))

print("\n[9] VERIFICACIÓN DE ITEMS POR TICKET")
items_por_ticket = df_clean.groupby('Comprobante').size().reset_index()
items_por_ticket.columns = ['Comprobante', 'Items']
print(f"Items promedio por ticket: {items_por_ticket['Items'].mean():.2f}")
print(f"Items mediano por ticket: {items_por_ticket['Items'].median():.0f}")
print(f"Máximo items en un ticket: {items_por_ticket['Items'].max()}")

# Tickets con muchos items (posibles duplicados o errores)
tickets_grandes = items_por_ticket[items_por_ticket['Items'] > 100]
print(f"\nTickets con más de 100 items: {len(tickets_grandes)}")

print("\n" + "="*80)
print("RESUMEN DEL DIAGNÓSTICO")
print("="*80)
print(f"TOTAL VENTAS CORRECTO: ${total_metodo2:,.2f}")
print(f"TOTAL TICKETS: {total_tickets:,}")
print(f"TICKET PROMEDIO: ${ticket_promedio:,.2f}")
print("="*80)

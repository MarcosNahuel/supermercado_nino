# -*- coding: utf-8 -*-
"""
Script de prueba para verificar la normalización de medios de pago
"""
import pandas as pd
import unicodedata

# Cargar datos
df = pd.read_parquet('data/app_dataset/kpi_medio_pago.parquet')

print("="*80)
print("ANÁLISIS DE MEDIOS DE PAGO")
print("="*80)

print("\n1. Valores únicos en tipo_medio_pago:")
print(df['tipo_medio_pago'].unique())

print("\n2. Representación de bytes de cada valor:")
for val in df['tipo_medio_pago'].unique():
    print(f"  '{val}' -> bytes: {val.encode('latin-1', errors='ignore')}")

# Función de normalización del dashboard
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

print("\n3. Aplicando normalización:")
df['medio_normalizado'] = df['tipo_medio_pago'].apply(normalizar_medio)

print("\n4. Resultado de normalización:")
for original in df['tipo_medio_pago'].unique():
    normalizado = normalizar_medio(original)
    print(f"  '{original}' -> '{normalizado}'")

print("\n5. Resumen por medio normalizado:")
resumen = df.groupby('medio_normalizado').agg({
    'ventas_totales': 'sum',
    'tickets': 'sum',
    'margen_total': 'sum'
})
resumen['ticket_promedio'] = resumen['ventas_totales'] / resumen['tickets']
resumen['participacion_%'] = (resumen['ventas_totales'] / resumen['ventas_totales'].sum() * 100).round(1)
print(resumen)

print("\n6. Verificación de categorías esperadas:")
categorias_esperadas = ['Efectivo', 'Debito', 'Credito', 'Billetera']
for cat in categorias_esperadas:
    count = (df['medio_normalizado'] == cat).sum()
    if count > 0:
        print(f"  ✓ {cat}: {count} registros")
    else:
        print(f"  ✗ {cat}: NO ENCONTRADO")

print("\n" + "="*80)

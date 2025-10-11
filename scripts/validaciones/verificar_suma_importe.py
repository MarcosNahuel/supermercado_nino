# -*- coding: utf-8 -*-
"""
Verificación DIRECTA de suma de columna Importe
"""

import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"

print("="*80)
print("SUMA DIRECTA DE COLUMNA IMPORTE")
print("="*80)

# Cargar CSV original
print("\n[1] Cargando CSV original...")
df = pd.read_csv(
    BASE_DIR / 'SERIE_COMPROBANTES_COMPLETOS.csv',
    sep=';',
    encoding='utf-8',
    low_memory=False
)

print(f"Total filas en CSV: {len(df):,}")
print(f"Columnas: {list(df.columns)}")

# Convertir Importe a numérico
print("\n[2] Convirtiendo columna 'Importe' a numérico...")
df['Importe_num'] = pd.to_numeric(df['Importe'], errors='coerce')

# Contar NaN
nulos = df['Importe_num'].isna().sum()
validos = df['Importe_num'].notna().sum()

print(f"Importes válidos: {validos:,}")
print(f"Importes nulos/inválidos: {nulos:,}")

# SUMA DIRECTA - Opción 1: Solo válidos
print("\n" + "="*80)
print("OPCIÓN 1: SUMA DE IMPORTES VÁLIDOS (sin NaN)")
print("="*80)
total_opcion1 = df['Importe_num'].sum()
print(f"TOTAL VENTAS: ${total_opcion1:,.2f}")

# SUMA DIRECTA - Opción 2: Rellenar NaN con 0
print("\n" + "="*80)
print("OPCIÓN 2: SUMA DE IMPORTES (NaN = 0)")
print("="*80)
df['Importe_con_ceros'] = df['Importe_num'].fillna(0)
total_opcion2 = df['Importe_con_ceros'].sum()
print(f"TOTAL VENTAS: ${total_opcion2:,.2f}")

# Verificar si son iguales
print("\n" + "="*80)
print("COMPARACIÓN")
print("="*80)
print(f"Diferencia entre opciones: ${abs(total_opcion1 - total_opcion2):,.2f}")

# Mostrar estadísticas
print("\n" + "="*80)
print("ESTADÍSTICAS DE LA COLUMNA IMPORTE")
print("="*80)
print(f"Mínimo: ${df['Importe_num'].min():,.2f}")
print(f"Máximo: ${df['Importe_num'].max():,.2f}")
print(f"Promedio: ${df['Importe_num'].mean():,.2f}")
print(f"Mediana: ${df['Importe_num'].median():,.2f}")

# Verificar algunos registros
print("\n" + "="*80)
print("PRIMEROS 10 REGISTROS")
print("="*80)
muestra = df[['Comprobante', 'Nombre', 'Cantidad', 'Unitario', 'Importe', 'Importe_num']].head(10)
print(muestra.to_string(index=False))

# Verificar cálculo: Cantidad × Unitario vs Importe
print("\n" + "="*80)
print("VERIFICACIÓN: ¿Importe = Cantidad × Unitario?")
print("="*80)
df['Cantidad_num'] = pd.to_numeric(df['Cantidad'], errors='coerce')
df['Unitario_num'] = pd.to_numeric(df['Unitario'], errors='coerce')
df['Importe_calculado'] = df['Cantidad_num'] * df['Unitario_num']
df['Diferencia'] = abs(df['Importe_num'] - df['Importe_calculado'])

errores = df[df['Diferencia'] > 0.01].shape[0]
print(f"Registros donde Importe ≠ Cantidad × Unitario: {errores:,}")

# Suma alternativa usando Cantidad × Unitario
total_alternativo = df['Importe_calculado'].sum()
print(f"\nTotal usando Cantidad × Unitario: ${total_alternativo:,.2f}")

print("\n" + "="*80)
print("RESUMEN FINAL")
print("="*80)
print(f"SUMA DIRECTA COLUMNA 'IMPORTE': ${total_opcion1:,.2f}")
print("="*80)

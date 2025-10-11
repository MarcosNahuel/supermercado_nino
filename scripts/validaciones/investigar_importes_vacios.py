# -*- coding: utf-8 -*-
"""
Investigar los 326,971 registros con Importe vacio/invalido
"""

import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"

print("="*80)
print("INVESTIGACION: IMPORTES VACIOS/INVALIDOS")
print("="*80)

# Cargar CSV
df = pd.read_csv(
    BASE_DIR / 'SERIE_COMPROBANTES_COMPLETOS.csv',
    sep=';',
    encoding='utf-8',
    low_memory=False
)

print(f"\nTotal registros: {len(df):,}")

# Verificar valores en columna Importe ANTES de convertir
print("\n[1] Valores ORIGINALES en columna 'Importe' (antes de conversión):")
print(f"Total filas: {len(df):,}")
print(f"Valores únicos en 'Importe': {df['Importe'].nunique():,}")

# Ver distribución de valores
print("\n[2] Muestra de valores en columna 'Importe':")
print(df['Importe'].value_counts().head(20))

# Identificar vacíos
vacios = df[df['Importe'].isna()]
print(f"\n[3] Registros con Importe = NaN (vacíos verdaderos): {len(vacios):,}")

# Identificar espacios en blanco o strings vacíos
df['Importe_str'] = df['Importe'].astype(str)
espacios = df[df['Importe_str'].str.strip() == '']
print(f"Registros con Importe = string vacío: {len(espacios):,}")

# Ver qué valores NO son numéricos
df['Importe_num'] = pd.to_numeric(df['Importe'], errors='coerce')
no_numericos = df[df['Importe_num'].isna() & df['Importe'].notna()]

print(f"\n[4] Registros con valores NO numéricos: {len(no_numericos):,}")

if len(no_numericos) > 0:
    print("\nEjemplos de valores NO numéricos:")
    print(no_numericos[['Comprobante', 'Nombre', 'Cantidad', 'Importe']].head(20).to_string(index=False))

    print("\nValores únicos NO numéricos:")
    valores_unicos = no_numericos['Importe'].unique()[:20]
    for val in valores_unicos:
        count = (no_numericos['Importe'] == val).sum()
        print(f"  '{val}': {count:,} registros")

# SUMA CORRECTA: Incluir CEROS para los inválidos
print("\n" + "="*80)
print("CALCULO FINAL")
print("="*80)

# Opción 1: Sumar solo válidos (ignora NaN)
total_opcion1 = df['Importe_num'].sum()
print(f"Opción 1 - Solo importes válidos (NaN ignorados): ${total_opcion1:,.2f}")

# Opción 2: Rellenar NaN con 0
df['Importe_final'] = df['Importe_num'].fillna(0)
total_opcion2 = df['Importe_final'].sum()
print(f"Opción 2 - Importes válidos + (NaN=0): ${total_opcion2:,.2f}")

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)
print(f"Total registros analizados: {len(df):,}")
print(f"Registros con importe válido: {df['Importe_num'].notna().sum():,}")
print(f"Registros con importe inválido/vacío: {df['Importe_num'].isna().sum():,}")
print(f"\nSUMA TOTAL DE COLUMNA IMPORTE: ${total_opcion1:,.2f}")
print("(Los negativos YA están incluidos - restan del total)")
print("="*80)

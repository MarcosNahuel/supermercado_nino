# -*- coding: utf-8 -*-
"""
SUMA CORRECTA - Especificando decimal=',' en pandas
"""

import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"

print("="*80)
print("SUMA CORRECTA - CON decimal=','")
print("="*80)

# CARGAR CSV CON DECIMAL COMA
print("\n[1] Cargando CSV con decimal=',' ...")
df = pd.read_csv(
    BASE_DIR / 'SERIE_COMPROBANTES_COMPLETOS.csv',
    sep=';',
    decimal=',',  # <--- ESTO ES LO QUE FALTABA
    encoding='utf-8',
    low_memory=False
)

print(f"Total registros: {len(df):,}")
print(f"Columnas: {list(df.columns)}")

# Verificar tipo de dato de Importe
print(f"\nTipo de dato de 'Importe': {df['Importe'].dtype}")

# Contar NaN
nulos = df['Importe'].isna().sum()
validos = df['Importe'].notna().sum()

print(f"\nImportes válidos: {validos:,}")
print(f"Importes nulos: {nulos:,}")

# SUMA DIRECTA
print("\n" + "="*80)
print("SUMA TOTAL DE COLUMNA IMPORTE")
print("="*80)

total = df['Importe'].sum()
print(f"\nTOTAL VENTAS: ${total:,.2f}")

# Estadísticas
print(f"\nEstadísticas de Importe:")
print(f"Mínimo: ${df['Importe'].min():,.2f}")
print(f"Máximo: ${df['Importe'].max():,.2f}")
print(f"Promedio: ${df['Importe'].mean():,.2f}")
print(f"Mediana: ${df['Importe'].median():,.2f}")

# Muestra
print("\n" + "="*80)
print("MUESTRA DE REGISTROS")
print("="*80)
muestra = df[['Comprobante', 'Nombre', 'Cantidad', 'Unitario', 'Importe']].head(20)
print(muestra.to_string(index=False))

# Verificar importes negativos (devoluciones)
negativos = df[df['Importe'] < 0]
print(f"\n" + "="*80)
print(f"Importes negativos (devoluciones): {len(negativos):,}")
if len(negativos) > 0:
    print(f"Suma de negativos: ${negativos['Importe'].sum():,.2f}")

# Positivos
positivos = df[df['Importe'] > 0]
print(f"Importes positivos: {len(positivos):,}")
print(f"Suma de positivos: ${positivos['Importe'].sum():,.2f}")

# Ceros
ceros = df[df['Importe'] == 0]
print(f"Importes en 0: {len(ceros):,}")

print("\n" + "="*80)
print("RESULTADO FINAL")
print("="*80)
print(f"TOTAL VENTAS (CORRECTO): ${total:,.2f}")
print(f"Total registros sumados: {len(df):,}")
print("="*80)

# Guardar
with open(BASE_DIR / 'TOTAL_VENTAS_FINAL.txt', 'w', encoding='utf-8') as f:
    f.write(f"TOTAL VENTAS: ${total:,.2f}\n")
    f.write(f"Total registros: {len(df):,}\n")
    f.write(f"Registros válidos: {validos:,}\n")
    f.write(f"Método: pd.read_csv con decimal=','\n")

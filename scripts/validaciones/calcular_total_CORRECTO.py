# -*- coding: utf-8 -*-
"""
Cálculo CORRECTO del total - Convertir formato europeo
"""

import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"

print("="*80)
print("CALCULO CORRECTO DEL TOTAL (FORMATO EUROPEO)")
print("="*80)

# Cargar CSV
df = pd.read_csv(
    BASE_DIR / 'SERIE_COMPROBANTES_COMPLETOS.csv',
    sep=';',
    encoding='utf-8',
    low_memory=False
)

print(f"\nTotal registros: {len(df):,}")

# FUNCIÓN DE CONVERSIÓN CORRECTA
def convertir_importe(valor):
    """Convierte formato europeo (coma decimal) a float"""
    if pd.isna(valor):
        return 0.0

    # Convertir a string
    valor_str = str(valor).strip()

    # Si está vacío
    if valor_str == '' or valor_str == 'nan':
        return 0.0

    # Reemplazar COMA por PUNTO
    valor_str = valor_str.replace(',', '.')

    try:
        return float(valor_str)
    except:
        print(f"ERROR convirtiendo: '{valor}' -> '{valor_str}'")
        return 0.0

print("\n[1] Convirtiendo TODOS los importes (incluyendo formato europeo)...")
df['Importe_convertido'] = df['Importe'].apply(convertir_importe)

# Verificar conversión
convertidos = (df['Importe_convertido'] != 0).sum()
ceros = (df['Importe_convertido'] == 0).sum()

print(f"Importes convertidos correctamente: {convertidos:,}")
print(f"Importes que quedaron en 0 (vacíos/errores): {ceros:,}")

# SUMA TOTAL
print("\n" + "="*80)
print("TOTAL CORRECTO")
print("="*80)

total_correcto = df['Importe_convertido'].sum()
print(f"\nTOTAL VENTAS (con formato europeo corregido): ${total_correcto:,.2f}")

# Comparar con total anterior (incorrecto)
total_anterior = 5616345970.00
diferencia = total_correcto - total_anterior

print(f"\nTotal anterior (INCORRECTO): ${total_anterior:,.2f}")
print(f"Diferencia: ${diferencia:,.2f}")
print(f"Incremento: {(diferencia/total_anterior*100):.2f}%")

# Verificar algunos ejemplos
print("\n" + "="*80)
print("EJEMPLOS DE CONVERSION")
print("="*80)
muestra = df[['Comprobante', 'Nombre', 'Importe', 'Importe_convertido']].head(30)
print(muestra.to_string(index=False))

# Guardar el total correcto
with open(BASE_DIR / 'TOTAL_CORRECTO.txt', 'w', encoding='utf-8') as f:
    f.write(f"TOTAL VENTAS CORRECTO: ${total_correcto:,.2f}\n")
    f.write(f"Total registros sumados: {len(df):,}\n")
    f.write(f"Conversión de formato europeo (coma decimal) aplicada\n")

print("\n" + "="*80)
print(f"TOTAL CORRECTO: ${total_correcto:,.2f}")
print("="*80)

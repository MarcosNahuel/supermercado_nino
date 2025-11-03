import pandas as pd
import sys
sys.path.append('d:/OneDrive/GitHub/supermercado_nino definitivo claude')

# Verificar columnas en archivos clave
archivos = [
    'kpi_periodo.parquet',
    'kpi_semana.parquet',
    'kpi_dia.parquet',
    'pareto_cat_global.parquet',
    'pareto_prod_global.parquet',
    'rentabilidad_ticket.parquet'
]

for archivo in archivos:
    try:
        df = pd.read_parquet(f'd:/OneDrive/GitHub/supermercado_nino definitivo claude/data/app_dataset/{archivo}')
        print(f'\n{archivo}:')
        print(f'  Shape: {df.shape}')
        print(f'  Columnas: {df.columns.tolist()}')
        if len(df.columns) > 10:
            print(f'  Primeras columnas: {df.columns[:5].tolist()}')
            print(f'  Últimas columnas: {df.columns[-5:].tolist()}')
    except Exception as e:
        print(f'\n{archivo}: ERROR - {e}')

import pandas as pd
import sys
sys.path.append('d:/OneDrive/GitHub/supermercado_nino definitivo claude')
df = pd.read_parquet('d:/OneDrive/GitHub/supermercado_nino definitivo claude/data/app_dataset/kpi_periodo.parquet')
print('Columnas:', df.columns.tolist())
print('Shape:', df.shape)
print('Primeras filas:')
print(df.head())

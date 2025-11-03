import pandas as pd

# Check specific files for column issues
files_to_check = [
    'data/app_dataset/kpi_semana.parquet',
    'data/app_dataset/kpi_dia.parquet',
    'data/app_dataset/pareto_cat_global.parquet'
]

for file_path in files_to_check:
    try:
        df = pd.read_parquet(file_path)
        print(f"\n{file_path}:")
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")

        # Check specific columns that the code is looking for
        if 'semana_iso' in df.columns:
            print("✓ semana_iso column exists")
        else:
            print("✗ semana_iso column missing")

        if 'dia_semana' in df.columns:
            print("✓ dia_semana column exists")
        else:
            print("✗ dia_semana column missing")

    except Exception as e:
        print(f"\n{file_path}: ERROR - {e}")

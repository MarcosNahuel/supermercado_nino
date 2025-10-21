import pandas as pd
from pathlib import Path

# Test the specific issues that were causing problems in "Análisis Temporal"
DATA_DIR = Path("data/app_dataset")

print("=== TESTING DATA LOADING FOR ANÁLISIS TEMPORAL ===")

# Test files that are critical for the temporal analysis
critical_files = [
    'kpi_semana.parquet',  # Needs 'semana_iso' column
    'kpi_dia.parquet',     # Needs 'dia_semana' column
    'rentabilidad_ticket.parquet',  # Main temporal data
    'pareto_cat_global.parquet',
    'pareto_prod_global.parquet'
]

for file in critical_files:
    try:
        df = pd.read_parquet(DATA_DIR / file)
        print(f"\n✓ {file} loaded successfully")
        print(f"  Shape: {df.shape}")
        print(f"  Columns: {list(df.columns)}")

        # Check for specific columns that the temporal analysis needs
        if file == 'kpi_semana.parquet':
            if 'semana_iso' in df.columns:
                print("  ✓ semana_iso column found")
            else:
                print("  ✗ semana_iso column MISSING")

        if file == 'kpi_dia.parquet':
            if 'dia_semana' in df.columns:
                print("  ✓ dia_semana column found")
            else:
                print("  ✗ dia_semana column MISSING")

    except Exception as e:
        print(f"\n✗ Error loading {file}: {e}")

# Test CSV file for horario data
print("\n=== TESTING HORARIO CSV ===")
horario_path = Path('data/raw/comprobantes_ventas_horario.csv')
if horario_path.exists():
    try:
        horario_df = pd.read_csv(horario_path, sep=';', dtype=str, engine='python')
        print(f"✓ CSV loaded with {len(horario_df)} rows")

        # Check required columns
        required_cols = ['Fecha', 'Hora', 'Comprobante']
        missing_cols = [col for col in required_cols if col not in horario_df.columns]
        if missing_cols:
            print(f"✗ Missing columns: {missing_cols}")
        else:
            print("✓ All required columns present")

        # Test date parsing
        try:
            test_dates = pd.to_datetime(
                horario_df['Fecha'].str.replace(',000', '', regex=False).head(5),
                format='%Y-%m-%d %H:%M:%S',
                errors='coerce'
            )
            if test_dates.isna().all():
                print("✗ Date parsing failed")
            else:
                print("✓ Date parsing works")
        except Exception as e:
            print(f"✗ Date parsing error: {e}")

    except Exception as e:
        print(f"✗ Error loading CSV: {e}")
else:
    print("✗ CSV file not found")

print("\n=== SUMMARY ===")
print("If you see any ✗ symbols above, those indicate issues that need to be fixed.")
print("The dashboard should now handle missing data gracefully and show appropriate warnings.")

import pandas as pd
from pathlib import Path

# Test data loading function similar to the dashboard
DATA_DIR = Path("data/app_dataset")

def test_data_loading():
    data = {}
    try:
        print("Loading alcance_dataset.parquet...")
        data['alcance'] = pd.read_parquet(DATA_DIR / 'alcance_dataset.parquet')
        print("✓ Loaded alcance")

        print("Loading kpis_base.parquet...")
        data['kpis_base'] = pd.read_parquet(DATA_DIR / 'kpis_base.parquet')
        print("✓ Loaded kpis_base")

        print("Loading kpi_periodo.parquet...")
        data['kpi_periodo'] = pd.read_parquet(DATA_DIR / 'kpi_periodo.parquet')
        print("✓ Loaded kpi_periodo")

        print("Loading kpi_semana.parquet...")
        data['kpi_semana'] = pd.read_parquet(DATA_DIR / 'kpi_semana.parquet')
        print("✓ Loaded kpi_semana")

        print("Loading kpi_dia.parquet...")
        data['kpi_dia'] = pd.read_parquet(DATA_DIR / 'kpi_dia.parquet')
        print("✓ Loaded kpi_dia")

        print("Loading pareto_cat_global.parquet...")
        data['pareto_cat'] = pd.read_parquet(DATA_DIR / 'pareto_cat_global.parquet')
        print("✓ Loaded pareto_cat")

        print("Loading rentabilidad_ticket.parquet...")
        data['rentabilidad_ticket'] = pd.read_parquet(DATA_DIR / 'rentabilidad_ticket.parquet')
        print("✓ Loaded rentabilidad_ticket")

        # Test specific columns that might be problematic
        if 'semana_iso' not in data['kpi_semana'].columns:
            print("✗ semana_iso column missing from kpi_semana")
        else:
            print("✓ semana_iso column exists in kpi_semana")

        if 'dia_semana' not in data['kpi_dia'].columns:
            print("✗ dia_semana column missing from kpi_dia")
        else:
            print("✓ dia_semana column exists in kpi_dia")

        print("\nAll data loaded successfully!")
        return data

    except Exception as e:
        print(f"Error loading data: {e}")
        return None

# Run the test
data = test_data_loading()

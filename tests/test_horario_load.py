"""
Script de prueba para verificar que el archivo horario se carga correctamente
"""
import pandas as pd
from pathlib import Path

print("=== TEST DE CARGA DE DATOS HORARIOS ===\n")

# Verificar que el archivo existe
horario_path = Path('data/raw/comprobantes_ventas_horario.csv')
print(f"1. Verificando existencia del archivo...")
print(f"   Ruta: {horario_path}")
print(f"   Existe: {horario_path.exists()}")

if not horario_path.exists():
    print("\n[ERROR] El archivo no existe!")
    exit(1)

print("\n2. Cargando archivo CSV...")
try:
    horario_df = pd.read_csv(
        horario_path,
        sep=';',
        dtype=str,
        nrows=1000  # Solo primeras 1000 para prueba rápida
    )
    print(f"   [OK] Archivo cargado: {len(horario_df)} filas")
except Exception as e:
    print(f"   [ERROR] {e}")
    exit(1)

print("\n3. Verificando columnas...")
required_columns = ['Fecha', 'Comprobante', 'Hora']
print(f"   Columnas requeridas: {required_columns}")
print(f"   Columnas encontradas: {list(horario_df.columns)}")
missing_columns = [col for col in required_columns if col not in horario_df.columns]
if missing_columns:
    print(f"   [ERROR] Faltan columnas: {missing_columns}")
    exit(1)
else:
    print(f"   [OK] Todas las columnas presentes")

print("\n4. Procesando fechas...")
try:
    horario_df['Fecha'] = pd.to_datetime(
        horario_df['Fecha'].str.replace(',000', '', regex=False),
        format='%Y-%m-%d %H:%M:%S',
        errors='coerce'
    )
    horario_df['Hora'] = pd.to_datetime(
        horario_df['Hora'].str.replace(',000', '', regex=False),
        format='%Y-%m-%d %H:%M:%S',
        errors='coerce'
    )
    print(f"   [OK] Fechas procesadas")
except Exception as e:
    print(f"   [ERROR] {e}")
    exit(1)

print("\n5. Validando fechas...")
valid_dates = horario_df['Fecha'].notna() & horario_df['Hora'].notna()
print(f"   Fechas válidas: {valid_dates.sum()} de {len(horario_df)}")
if valid_dates.sum() == 0:
    print(f"   [ERROR] No hay fechas válidas!")
    exit(1)

print("\n6. Generando datos horarios...")
try:
    horario_df = horario_df.dropna(subset=['Fecha', 'Hora'])
    horario_df['hora'] = horario_df['Hora'].dt.hour.astype(int)

    dias_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dias_map = {
        'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
        'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
    }

    horario_df['dia_eng'] = horario_df['Fecha'].dt.day_name()
    horario_df = horario_df[horario_df['dia_eng'].isin(dias_order)]
    horario_df['dia'] = horario_df['dia_eng'].map(dias_map)
    horario_df['dia_idx'] = horario_df['dia_eng'].apply(dias_order.index)

    horario_semana = (
        horario_df.groupby(['dia_idx', 'dia', 'hora'], as_index=False)
        .agg(comprobantes=('Comprobante', 'count'))
        .sort_values(['dia_idx', 'hora'])
    )

    horario_pivot = (
        horario_semana.pivot(index='dia', columns='hora', values='comprobantes')
        .reindex(['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'])
        .fillna(0)
    )

    print(f"   [OK] Datos procesados")
    print(f"   Forma horario_semana: {horario_semana.shape}")
    print(f"   Forma horario_pivot: {horario_pivot.shape}")
except Exception as e:
    print(f"   [ERROR] {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n7. Muestra de datos horarios:")
print("\nPrimeras filas de horario_semana:")
print(horario_semana.head(10))

print("\n\n=== [EXITO] TODAS LAS PRUEBAS PASARON ===")
print("\nResumen:")
print(f"  - Archivo encontrado: {horario_path}")
print(f"  - Registros procesados: {len(horario_df)}")
print(f"  - Días únicos: {horario_semana['dia'].nunique()}")
print(f"  - Horas únicas: {horario_semana['hora'].nunique()}")
print(f"  - Total comprobantes: {horario_semana['comprobantes'].sum()}")

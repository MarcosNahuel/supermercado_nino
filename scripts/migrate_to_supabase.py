# -*- coding: utf-8 -*-
"""
================================================================================
MIGRACIÓN DE DATOS A SUPABASE
Supermercado NINO - Solución para Deploy sin límites de tamaño
================================================================================
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv
from tqdm import tqdm
import time

# Cargar variables de entorno
load_dotenv()

# Configuración
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed" / "FASE1_OUTPUT"

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Tamaño de chunk para inserciones
CHUNK_SIZE = 1000

print("=" * 100)
print("MIGRACIÓN DE DATOS A SUPABASE | SUPERMERCADO NINO")
print("=" * 100)

# Validar credenciales
if not SUPABASE_URL or not SUPABASE_KEY:
    print("\n[ERROR] Credenciales de Supabase no encontradas")
    print("Asegurate de tener un archivo .env con:")
    print("  SUPABASE_URL=https://your-project.supabase.co")
    print("  SUPABASE_KEY=your-anon-key-here")
    sys.exit(1)

# Conectar a Supabase
print(f"\n[1/5] Conectando a Supabase...")
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("[OK] Conexion exitosa")
except Exception as e:
    print(f"[ERROR] Error al conectar: {e}")
    sys.exit(1)

# =============================================================================
# FUNCIÓN PARA INSERTAR DATOS EN CHUNKS
# =============================================================================
def insert_dataframe_to_supabase(df: pd.DataFrame, table_name: str, chunk_size: int = CHUNK_SIZE):
    """
    Inserta un DataFrame en Supabase por chunks para evitar límites de tamaño.
    """
    print(f"\n[Migrando tabla: {table_name}]")
    print(f"Total de registros: {len(df):,}")

    # Convertir NaN a None para compatibilidad con PostgreSQL
    df = df.replace({np.nan: None})

    # Convertir fechas a string ISO
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')

    # Insertar en chunks
    total_chunks = (len(df) // chunk_size) + 1
    errors = []

    for i in tqdm(range(0, len(df), chunk_size), desc=f"Migrando {table_name}"):
        chunk = df.iloc[i:i+chunk_size]
        records = chunk.to_dict('records')

        try:
            # Intentar inserción
            supabase.table(table_name).insert(records).execute()
            time.sleep(0.1)  # Rate limiting
        except Exception as e:
            error_msg = str(e)
            # Si la tabla no existe, crearla
            if "relation" in error_msg and "does not exist" in error_msg:
                print(f"\n[WARNING]  Tabla '{table_name}' no existe. Créala manualmente en Supabase Dashboard.")
                print(f"   Columnas requeridas: {list(df.columns)}")
                return False
            else:
                errors.append(f"Chunk {i//chunk_size}: {error_msg}")

    if errors:
        print(f"\n[WARNING]  Se encontraron {len(errors)} errores durante la migración")
        for error in errors[:5]:  # Mostrar solo los primeros 5
            print(f"   - {error}")
    else:
        print(f"[OK] Tabla '{table_name}' migrada exitosamente")

    return len(errors) == 0

# =============================================================================
# PASO 1: MIGRAR TABLAS AGREGADAS (LIVIANAS)
# =============================================================================
print("\n" + "=" * 100)
print("[2/5] Migrando tablas agregadas (KPIs)")
print("=" * 100)

tablas_ligeras = {
    "kpi_periodo": PROCESSED_DIR / "03_KPI_PERIODO.csv",
    "kpi_categoria": PROCESSED_DIR / "04_KPI_CATEGORIA.csv",
    "kpi_dia_semana": PROCESSED_DIR / "08_KPI_DIA_SEMANA.csv",
    "pareto_productos": PROCESSED_DIR / "05_PARETO_PRODUCTOS.csv",
    "perfiles_clusters": PROCESSED_DIR / "07_PERFILES_CLUSTERS.csv",
}

for table_name, file_path in tablas_ligeras.items():
    if file_path.exists():
        try:
            df = pd.read_csv(file_path, sep=';', encoding='utf-8-sig')
            insert_dataframe_to_supabase(df, table_name, chunk_size=500)
        except Exception as e:
            print(f"[ERROR] Error al migrar {table_name}: {e}")
    else:
        print(f"[WARNING]  Archivo no encontrado: {file_path}")

# =============================================================================
# PASO 2: MIGRAR TABLA DE TICKETS (MEDIANA)
# =============================================================================
print("\n" + "=" * 100)
print("[3/5] Migrando tabla de tickets")
print("=" * 100)

tickets_file = PROCESSED_DIR / "02_TICKETS.csv"
if tickets_file.exists():
    try:
        df_tickets = pd.read_csv(tickets_file, sep=';', encoding='utf-8-sig')
        insert_dataframe_to_supabase(df_tickets, "tickets", chunk_size=1000)
    except Exception as e:
        print(f"[ERROR] Error al migrar tickets: {e}")
else:
    print(f"[WARNING]  Archivo de tickets no encontrado")

# =============================================================================
# PASO 3: MIGRAR REGLAS DE ASOCIACIÓN (SI EXISTE)
# =============================================================================
print("\n" + "=" * 100)
print("[4/5] Migrando reglas de asociación (Market Basket)")
print("=" * 100)

reglas_file = PROCESSED_DIR / "06_REGLAS_ASOCIACION.csv"
if reglas_file.exists():
    try:
        df_reglas = pd.read_csv(reglas_file, sep=';', encoding='utf-8-sig')
        insert_dataframe_to_supabase(df_reglas, "reglas_asociacion", chunk_size=500)
    except Exception as e:
        print(f"[ERROR] Error al migrar reglas: {e}")
else:
    print(f"[WARNING]  Archivo de reglas no encontrado (puede que no se hayan generado)")

# =============================================================================
# PASO 4: MIGRAR ITEMS DE VENTAS (TABLA PESADA) - EN CHUNKS PEQUEÑOS
# =============================================================================
print("\n" + "=" * 100)
print("[5/5] Migrando items de ventas (tabla principal - esto puede tardar)")
print("=" * 100)

items_file = PROCESSED_DIR / "01_ITEMS_VENTAS.csv"

# Estrategia alternativa: Leer el CSV original en chunks y procesar
print("\n[WARNING]  NOTA: La tabla de items es muy grande (3M+ registros)")
print("   Se migrará en chunks pequeños para evitar límites de memoria\n")

csv_raw = RAW_DIR / "SERIE_COMPROBANTES_COMPLETOS2.csv"

if csv_raw.exists():
    print(f"Leyendo desde: {csv_raw}")

    # Leer y procesar en chunks
    chunk_iter = pd.read_csv(
        csv_raw,
        sep=';',
        decimal=',',
        encoding='utf-8',
        low_memory=False,
        chunksize=5000  # Leer 5k registros a la vez
    )

    total_processed = 0

    # Mapeo de columnas
    column_mapping = {
        'Fecha': 'fecha',
        'Comprobante': 'ticket_id',
        'Código': 'producto_id',
        'Marca': 'marca',
        'Departamento': 'categoria',
        'Nombre': 'descripcion',
        'Cantidad': 'cantidad',
        'Importe': 'importe_total',
        'Unitario': 'precio_unitario',
    }

    for i, chunk in enumerate(chunk_iter):
        print(f"\nProcesando chunk {i+1} ({len(chunk):,} registros)...")

        # Renombrar columnas
        chunk = chunk.rename(columns=column_mapping)

        # Seleccionar solo columnas necesarias
        cols_to_keep = ['fecha', 'ticket_id', 'producto_id', 'categoria',
                        'descripcion', 'cantidad', 'importe_total', 'precio_unitario']
        chunk = chunk[[col for col in cols_to_keep if col in chunk.columns]]

        # Convertir fecha
        chunk['fecha'] = pd.to_datetime(chunk['fecha'], errors='coerce')

        # Normalizar texto
        chunk['categoria'] = chunk['categoria'].astype(str).str.strip().str.upper()
        chunk['descripcion'] = chunk['descripcion'].astype(str).str.strip().str.upper()

        # Insertar
        try:
            insert_dataframe_to_supabase(chunk, "items_ventas", chunk_size=500)
            total_processed += len(chunk)
            print(f"[OK] Total procesado: {total_processed:,} registros")
        except Exception as e:
            print(f"[ERROR] Error en chunk {i+1}: {e}")
            continue

        # Limitar a 100k registros para demo (quitar esto para migración completa)
        # COMENTADO PARA MIGRACIÓN COMPLETA
        # if total_processed >= 100000:
        #     print(f"\n[WARNING]  Detenido en {total_processed:,} registros (modo demo)")
        #     print("   Para migración completa, comenta la línea 'if total_processed >= 100000'")
        #     break

    print(f"\n[OK] Migración de items completada: {total_processed:,} registros")
else:
    print(f"[ERROR] Archivo de datos raw no encontrado: {csv_raw}")

# =============================================================================
# RESUMEN FINAL
# =============================================================================
print("\n" + "=" * 100)
print("[OK] MIGRACIÓN COMPLETADA")
print("=" * 100)

print("""
PRÓXIMOS PASOS:

1. Verifica las tablas en Supabase Dashboard:
   https://supabase.com/dashboard/project/yebiszzkrgapfqwngbwj/editor

2. Si alguna tabla no se creó, créala manualmente con el esquema correcto.

3. Actualiza el código de Streamlit para leer desde Supabase.

4. Crea índices en Supabase para mejorar el rendimiento:
   - CREATE INDEX idx_items_ticket ON items_ventas(ticket_id);
   - CREATE INDEX idx_items_categoria ON items_ventas(categoria);
   - CREATE INDEX idx_items_fecha ON items_ventas(fecha);

5. Activa Row Level Security (RLS) si es necesario para seguridad.

6. Publica tu app en Streamlit Cloud sin preocuparte por el tamaño del CSV.
""")

print("=" * 100)

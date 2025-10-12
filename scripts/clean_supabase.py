# -*- coding: utf-8 -*-
"""
================================================================================
LIMPIAR TABLAS DE SUPABASE
Supermercado NINO - Script para borrar datos existentes
================================================================================
"""

import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("=" * 100)
print("LIMPIAR TABLAS DE SUPABASE | SUPERMERCADO NINO")
print("=" * 100)

# Validar credenciales
if not SUPABASE_URL or not SUPABASE_KEY:
    print("\n[ERROR] Credenciales de Supabase no encontradas")
    sys.exit(1)

# Conectar a Supabase
print(f"\n[1/2] Conectando a Supabase...")
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("[OK] Conexión exitosa")
except Exception as e:
    print(f"[ERROR] Error al conectar: {e}")
    sys.exit(1)

# Lista de tablas a limpiar
tablas = [
    "items_ventas",
    "tickets",
    "kpi_periodo",
    "kpi_categoria",
    "kpi_dia_semana",
    "pareto_productos",
    "perfiles_clusters",
    "reglas_asociacion"
]

print(f"\n[2/2] Limpiando tablas...")
print("NOTA: Para tablas grandes, es mejor borrarlas desde Supabase Dashboard\n")

for tabla in tablas:
    try:
        # Contar registros primero
        count_result = supabase.table(tabla).select('id', count='exact').limit(1).execute()
        count = count_result.count if hasattr(count_result, 'count') else 0

        if count == 0:
            print(f"  OK Tabla '{tabla}' ya esta vacia")
        elif count > 100000:
            print(f"  ADVERTENCIA Tabla '{tabla}' tiene {count:,} registros - borrala manualmente desde Dashboard")
        else:
            # Borrar en lotes pequeños
            print(f"  Limpiando tabla '{tabla}' ({count:,} registros)...")
            # Simple delete sin condición funciona en tablas pequeñas
            supabase.table(tabla).delete().gte('id', 0).execute()
            print(f"  OK Tabla '{tabla}' limpiada")
    except Exception as e:
        error_msg = str(e)
        if "relation" in error_msg and "does not exist" in error_msg:
            print(f"  INFO Tabla '{tabla}' no existe (se creara en la migracion)")
        else:
            print(f"  ERROR limpiando '{tabla}': {error_msg}")

print("\n" + "=" * 100)
print("[OK] LIMPIEZA COMPLETADA")
print("=" * 100)
print("\nAhora puedes ejecutar la migración: python scripts/migrate_to_supabase.py")

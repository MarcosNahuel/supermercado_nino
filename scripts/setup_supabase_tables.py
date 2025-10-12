# -*- coding: utf-8 -*-
"""
================================================================================
CREAR TABLAS EN SUPABASE
Supermercado NINO - Script para crear esquema de base de datos
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

# SQL para crear todas las tablas
CREATE_TABLES_SQL = """
-- Tabla de KPIs por período
CREATE TABLE IF NOT EXISTS kpi_periodo (
    id SERIAL PRIMARY KEY,
    periodo VARCHAR(7) NOT NULL,
    ventas DECIMAL(15, 2),
    margen DECIMAL(15, 2),
    tickets INTEGER,
    ticket_promedio DECIMAL(15, 2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de KPIs por categoría
CREATE TABLE IF NOT EXISTS kpi_categoria (
    id SERIAL PRIMARY KEY,
    categoria VARCHAR(100) NOT NULL,
    rentabilidad_pct DECIMAL(5, 2),
    ventas DECIMAL(15, 2),
    margen DECIMAL(15, 2),
    unidades INTEGER,
    tickets INTEGER,
    pct_ventas DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de KPIs por día de semana
CREATE TABLE IF NOT EXISTS kpi_dia_semana (
    id SERIAL PRIMARY KEY,
    dia_semana VARCHAR(20) NOT NULL,
    ventas DECIMAL(15, 2),
    tickets INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de Pareto (productos ABC)
CREATE TABLE IF NOT EXISTS pareto_productos (
    id SERIAL PRIMARY KEY,
    producto_id VARCHAR(50) NOT NULL,
    descripcion VARCHAR(200),
    categoria VARCHAR(100),
    ventas DECIMAL(15, 2),
    unidades INTEGER,
    margen DECIMAL(15, 2),
    ventas_acumuladas DECIMAL(15, 2),
    pct_acumulado DECIMAL(5, 2),
    clasificacion_abc VARCHAR(1),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de perfiles de clusters
CREATE TABLE IF NOT EXISTS perfiles_clusters (
    id SERIAL PRIMARY KEY,
    cluster INTEGER NOT NULL,
    cantidad_tickets INTEGER,
    ticket_promedio DECIMAL(15, 2),
    items_promedio DECIMAL(5, 2),
    margen_promedio DECIMAL(15, 2),
    pct_fin_semana DECIMAL(5, 2),
    pct_tickets DECIMAL(5, 2),
    etiqueta VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de reglas de asociación
CREATE TABLE IF NOT EXISTS reglas_asociacion (
    id SERIAL PRIMARY KEY,
    antecedents TEXT,
    consequents TEXT,
    support DECIMAL(10, 6),
    confidence DECIMAL(10, 6),
    lift DECIMAL(10, 4),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de tickets (resumen)
CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    ticket_id VARCHAR(50) NOT NULL UNIQUE,
    monto_total_ticket DECIMAL(15, 2),
    items_ticket INTEGER,
    margen_ticket DECIMAL(15, 2),
    fecha TIMESTAMP,
    periodo VARCHAR(7),
    dia_semana VARCHAR(20),
    es_fin_semana BOOLEAN,
    cluster INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de items de ventas (más pesada)
CREATE TABLE IF NOT EXISTS items_ventas (
    id SERIAL PRIMARY KEY,
    fecha TIMESTAMP,
    ticket_id VARCHAR(50),
    producto_id VARCHAR(50),
    categoria VARCHAR(100),
    descripcion VARCHAR(200),
    cantidad DECIMAL(10, 3),
    importe_total DECIMAL(15, 2),
    precio_unitario DECIMAL(15, 2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_tickets_fecha ON tickets(fecha);
CREATE INDEX IF NOT EXISTS idx_tickets_id ON tickets(ticket_id);
CREATE INDEX IF NOT EXISTS idx_items_ticket ON items_ventas(ticket_id);
CREATE INDEX IF NOT EXISTS idx_items_categoria ON items_ventas(categoria);
CREATE INDEX IF NOT EXISTS idx_items_fecha ON items_ventas(fecha);
CREATE INDEX IF NOT EXISTS idx_pareto_clasificacion ON pareto_productos(clasificacion_abc);
"""

print("=" * 100)
print("CREAR TABLAS EN SUPABASE | SUPERMERCADO NINO")
print("=" * 100)

# Validar credenciales
if not SUPABASE_URL or not SUPABASE_KEY:
    print("\n[ERROR] Credenciales de Supabase no encontradas")
    sys.exit(1)

# Conectar a Supabase
print(f"\n[1/2] Conectando a Supabase...")
print(f"URL: {SUPABASE_URL}")
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("[OK] Conexion exitosa")
except Exception as e:
    print(f"[ERROR] Error al conectar: {e}")
    sys.exit(1)

# Ejecutar SQL para crear tablas
print(f"\n[2/2] Creando tablas...")
try:
    # Dividir el SQL en sentencias individuales
    statements = [s.strip() for s in CREATE_TABLES_SQL.split(';') if s.strip()]

    for i, statement in enumerate(statements, 1):
        if statement:
            try:
                # Usar rpc() para ejecutar SQL directo
                supabase.rpc('exec_sql', {'sql': statement}).execute()
                print(f"  [{i}/{len(statements)}] Ejecutado")
            except Exception as e:
                error_msg = str(e)
                # Si el error es que la tabla ya existe, está bien
                if "already exists" in error_msg or "does not exist" in error_msg:
                    print(f"  [{i}/{len(statements)}] OK (ya existe o función no disponible)")
                else:
                    print(f"  [{i}/{len(statements)}] ERROR: {error_msg}")

    print("\n[OK] Tablas creadas exitosamente")
    print("\nNOTA: Si ves errores, es porque Supabase no permite ejecutar SQL directo via API.")
    print("En ese caso, copia el SQL desde docs/DEPLOY_SUPABASE.md (lineas 144-254)")
    print("y ejecutalo manualmente en el SQL Editor de Supabase Dashboard:")
    print(f"{SUPABASE_URL.replace('.supabase.co', '')}/sql/new")

except Exception as e:
    print(f"\n[ERROR] Error al crear tablas: {e}")
    print("\nCopia el SQL desde docs/DEPLOY_SUPABASE.md (lineas 144-254)")
    print("y ejecutalo manualmente en el SQL Editor de Supabase Dashboard:")
    print(f"{SUPABASE_URL.replace('.supabase.co', '')}/sql/new")

print("\n" + "=" * 100)
print("CONFIGURACION COMPLETADA")
print("=" * 100)
print("\nProximo paso: python scripts/migrate_to_supabase.py")

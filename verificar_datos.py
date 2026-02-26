#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Verificar datos del dashboard."""
import pandas as pd
from pathlib import Path

app = Path('data/app_dataset')

files = {
    'kpi_dia': app / 'kpi_dia.parquet',
    'kpi_categoria': app / 'kpi_categoria.parquet',
    'tickets': app / 'tickets.parquet',
    'pareto_categoria': app / 'pareto_categoria.parquet',
    'reglas': app / 'reglas.parquet',
    'clusters_tickets': app / 'clusters_tickets.parquet',
    'predicciones': app / 'prediccion_ventas_semanal.parquet',
    'strategy_roi': app / 'strategy_roi_summary.parquet'
}

print('=== VERIFICACION DE DATOS ===\n')
for name, path in files.items():
    if path.exists():
        df = pd.read_parquet(path)
        print(f'{name}: {len(df):,} registros')
    else:
        print(f'{name}: NO ENCONTRADO')

print('\n=== KPIs GLOBALES ===')
kpi = pd.read_parquet(app / 'kpi_dia.parquet')
print(f'Periodo: {kpi["fecha"].min().date()} a {kpi["fecha"].max().date()}')
print(f'Ventas totales: ${kpi["ventas_totales"].sum():,.0f}')
print(f'Margen total: ${kpi["margen_total"].sum():,.0f}')
print(f'Tickets totales: {kpi["tickets"].sum():,}')

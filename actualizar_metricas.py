#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SCRIPT DE ACTUALIZACIÓN AUTOMÁTICA DE MÉTRICAS
==============================================
Ejecuta el pipeline completo cuando se actualiza SERIE_COMPROBANTES_COMPLETOS.csv

Uso:
    python actualizar_metricas.py

Este script:
1. Ejecuta el pipeline de procesamiento de datos
2. Copia archivos procesados a app_dataset
3. Entrena modelos ML
4. Los datos actualizados estarán disponibles al recargar el dashboard
"""

import subprocess
import shutil
from pathlib import Path
import sys
import io

# Forzar UTF-8 en stdout para Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_step(step, message):
    """Imprime un paso del proceso con formato"""
    print(f"\n{Colors.BLUE}[{step}]{Colors.END} {message}")

def print_success(message):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    """Imprime mensaje de error"""
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_warning(message):
    """Imprime mensaje de advertencia"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def main():
    """Ejecuta el pipeline completo de actualización"""

    print(f"\n{Colors.BLUE}{'='*60}")
    print("  ACTUALIZACIÓN AUTOMÁTICA DE MÉTRICAS - SUPERMERCADO NINO")
    print(f"{'='*60}{Colors.END}\n")

    BASE_DIR = Path(__file__).parent

    # Verificar que existe el CSV fuente
    csv_file = BASE_DIR / "data" / "raw" / "SERIE_COMPROBANTES_COMPLETOS.csv"
    if not csv_file.exists():
        print_error(f"No se encontró el archivo: {csv_file}")
        sys.exit(1)

    print_success(f"Archivo CSV encontrado: {csv_file.stat().st_size / (1024**2):.1f} MB")

    # PASO 1: Ejecutar pipeline de procesamiento
    print_step("1/3", "Ejecutando pipeline de procesamiento de datos...")
    print_warning("Esto puede tomar 1-2 horas dependiendo del volumen de datos")

    try:
        result = subprocess.run(
            [sys.executable, "-m", "scripts.pipeline.main_pipeline"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            check=True
        )
        print_success("Pipeline de datos completado exitosamente")
    except subprocess.CalledProcessError as e:
        print_error("Error en el pipeline de datos:")
        print(e.stderr)
        sys.exit(1)

    # PASO 2: Copiar archivos a app_dataset
    print_step("2/3", "Copiando archivos procesados a app_dataset...")

    processed_dir = BASE_DIR / "data" / "processed"
    app_dataset_dir = BASE_DIR / "data" / "app_dataset"
    predictivos_dir = BASE_DIR / "data" / "predictivos"

    # Crear directorio si no existe
    app_dataset_dir.mkdir(parents=True, exist_ok=True)

    # Archivos a copiar
    files_to_copy = [
        "kpi_medio_pago.parquet",
        "kpi_categoria.parquet",
        "kpi_dia.parquet",
        "kpi_tipo_dia.parquet",
        "kpi_periodo.parquet",      # NUEVO: KPIs mensuales con datos normalizados
        "kpi_semana.parquet",       # NUEVO: KPIs semanales con datos normalizados
        "tickets.parquet",
        "reglas.parquet",
        "combos_recomendados.parquet",
        "pareto_categoria.parquet",
        "pareto_producto.parquet",
        "clusters_tickets.parquet",
        "detalle_lineas.parquet",
        "adjacency_pairs.parquet",
        "ventas_semanales_categoria.parquet"
    ]

    copied_count = 0
    for filename in files_to_copy:
        src = processed_dir / filename
        dst = app_dataset_dir / filename

        if src.exists():
            shutil.copy2(src, dst)
            copied_count += 1
        else:
            print_warning(f"Archivo no encontrado: {filename}")

    # Copiar archivos de predicciones
    if predictivos_dir.exists():
        for parquet_file in predictivos_dir.glob("*.parquet"):
            shutil.copy2(parquet_file, app_dataset_dir / parquet_file.name)
            copied_count += 1

    print_success(f"{copied_count} archivos copiados a app_dataset")

    # PASO 3: Entrenar modelos ML
    print_step("3/3", "Entrenando modelos de Machine Learning...")

    try:
        result = subprocess.run(
            [sys.executable, "scripts/train_ml_models.py"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            check=True
        )
        print_success("Modelos ML entrenados exitosamente")

        # Mostrar resumen de ROI si está disponible
        if "Resumen consolidado de ROI" in result.stdout:
            print(f"\n{Colors.YELLOW}Resumen de estrategias ML:{Colors.END}")
            lines = result.stdout.split('\n')
            for i, line in enumerate(lines):
                if "Resumen consolidado de ROI" in line:
                    for summary_line in lines[i+1:i+10]:
                        if summary_line.strip():
                            print(f"  {summary_line}")

    except subprocess.CalledProcessError as e:
        print_error("Error en el entrenamiento de modelos ML:")
        print(e.stderr)
        sys.exit(1)

    # FINALIZACIÓN
    print(f"\n{Colors.GREEN}{'='*60}")
    print("  ✓ ACTUALIZACIÓN COMPLETADA EXITOSAMENTE")
    print(f"{'='*60}{Colors.END}\n")

    print("Próximos pasos:")
    print("  1. Si el dashboard está corriendo, recarga la página (F5 o R)")
    print("  2. Si no está corriendo, ejecuta:")
    print(f"     {Colors.BLUE}streamlit run final/streamlit_app/dashboard_cientifico.py{Colors.END}")
    print()

if __name__ == "__main__":
    main()

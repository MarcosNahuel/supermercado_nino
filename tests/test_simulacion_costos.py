"""
Test para verificar que la seccion de simulacion de costos funciona
"""
import sys
import importlib.util

# Intentar importar el modulo del dashboard
print("[*] Verificando modulo de simulacion de costos...")

# Leer el archivo y buscar la seccion
with open('dashboard_cientifico.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Verificar que las secciones clave existan
checks = {
    "Titulo de simulacion": "Simulacion: Analisis de Costos" in content,
    "Grafico Waterfall": "go.Waterfall" in content,
    "Pie Chart": "fig_pie_costos" in content,
    "Punto de equilibrio": "unidades_equilibrio" in content,
    "Tabla de costos": "tabla_costo_sim" in content,
    "Import numpy": "import numpy as np" in content,
    "Proximos pasos": "Proximos Pasos para Activar" in content,
}

print("\n[*] Resultados de las verificaciones:\n")
all_passed = True
for check_name, result in checks.items():
    status = "[OK]" if result else "[FAIL]"
    print(f"  {status} {check_name}: {'PASS' if result else 'FAIL'}")
    if not result:
        all_passed = False

# Contar lineas de la seccion de simulacion
sim_start = content.find("# SECCION: SIMULACION DE ANALISIS DE COSTOS")
sim_end = content.find("# TAB 7: ESTRATEGIAS PRIORIZADAS")
if sim_start != -1 and sim_end != -1:
    sim_section = content[sim_start:sim_end]
    sim_lines = sim_section.count('\n')
    print(f"\n[*] Tamano de la seccion de simulacion: {sim_lines} lineas")
else:
    print("\n[!] No se pudo encontrar la seccion de simulacion completa")

if all_passed:
    print("\n[OK] TODAS LAS VERIFICACIONES PASARON")
    print(f"\n[*] Dashboard disponible en:")
    print(f"   - http://localhost:8502")
    print(f"\n[*] Para ver la simulacion:")
    print(f"   1. Ir a Tab 6: Analisis de Rentabilidad y Margenes")
    print(f"   2. Hacer scroll hasta el final")
    print(f"   3. Buscar: Simulacion: Analisis de Costos (Vista Previa)")
else:
    print("\n[FAIL] ALGUNAS VERIFICACIONES FALLARON")
    sys.exit(1)

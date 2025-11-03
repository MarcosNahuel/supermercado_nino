"""
Script para generar PDF del informe ejecutivo usando Chrome headless
"""

import subprocess
from pathlib import Path

# Rutas
BASE_DIR = Path(__file__).parent
HTML_PATH = BASE_DIR / "docs" / "entregables" / "INFORME_EJECUTIVO_SUPERMERCADO_NINO.html"
PDF_PATH = BASE_DIR / "docs" / "entregables" / "INFORME_EJECUTIVO_SUPERMERCADO_NINO.pdf"

# Buscar Chrome en ubicaciones comunes de Windows
chrome_paths = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(Path.home().name),
]

chrome_exe = None
for path in chrome_paths:
    if Path(path).exists():
        chrome_exe = path
        break

if not chrome_exe:
    print("[ERROR] No se encontro Google Chrome instalado")
    print("Por favor, abre el HTML en tu navegador y usa Ctrl+P para imprimir a PDF")
    print(f"Ubicacion HTML: {HTML_PATH}")
    exit(1)

print(f"[OK] Chrome encontrado en: {chrome_exe}")
print(f"[INFO] Generando PDF del informe...")
print(f"   HTML: {HTML_PATH}")
print(f"   PDF: {PDF_PATH}")

# Comando para generar PDF con Chrome headless
cmd = [
    chrome_exe,
    '--headless',
    '--disable-gpu',
    '--print-to-pdf=' + str(PDF_PATH),
    '--print-to-pdf-no-header',
    '--no-margins',
    'file:///' + str(HTML_PATH).replace('\\', '/')
]

try:
    # Ejecutar comando
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    # Verificar que se creó el PDF
    if PDF_PATH.exists():
        size_mb = PDF_PATH.stat().st_size / (1024 * 1024)
        print(f"\n[SUCCESS] PDF generado exitosamente!")
        print(f"   Ubicacion: {PDF_PATH}")
        print(f"   Tamano: {size_mb:.2f} MB")
        print(f"\n[OK] Informe ejecutivo listo para presentar al cliente")
    else:
        print(f"[ERROR] El PDF no se genero correctamente")
        if result.stderr:
            print(f"Error: {result.stderr}")

except subprocess.TimeoutExpired:
    print(f"[ERROR] Timeout al generar el PDF")
except Exception as e:
    print(f"[ERROR] {str(e)}")

print(f"\nSi el PDF no se generó correctamente, puedes:")
print(f"1. Abrir el HTML en Chrome: {HTML_PATH}")
print(f"2. Presionar Ctrl+P")
print(f"3. Seleccionar 'Guardar como PDF'")
print(f"4. Guardar en: {PDF_PATH}")

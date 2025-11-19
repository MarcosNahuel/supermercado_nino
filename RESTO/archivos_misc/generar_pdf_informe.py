"""
Script para generar PDF del informe ejecutivo
Usa weasyprint para convertir HTML a PDF con estilos CSS preservados
"""

import os
from pathlib import Path

# Intentar importar weasyprint
try:
    from weasyprint import HTML
    print("✓ weasyprint encontrado")
except ImportError:
    print("⚠ weasyprint no está instalado. Instalando...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'weasyprint'])
    from weasyprint import HTML
    print("✓ weasyprint instalado correctamente")

# Rutas
BASE_DIR = Path(__file__).parent
HTML_PATH = BASE_DIR / "docs" / "entregables" / "INFORME_EJECUTIVO_SUPERMERCADO_NINO.html"
PDF_PATH = BASE_DIR / "docs" / "entregables" / "INFORME_EJECUTIVO_SUPERMERCADO_NINO.pdf"

# Verificar que el HTML existe
if not HTML_PATH.exists():
    print(f"❌ Error: No se encuentra el archivo HTML en {HTML_PATH}")
    exit(1)

print(f"📄 Convirtiendo HTML a PDF...")
print(f"   Entrada: {HTML_PATH}")
print(f"   Salida: {PDF_PATH}")

try:
    # Convertir HTML a PDF
    HTML(str(HTML_PATH)).write_pdf(str(PDF_PATH))

    # Verificar que se creó el PDF
    if PDF_PATH.exists():
        size_mb = PDF_PATH.stat().st_size / (1024 * 1024)
        print(f"\n✅ PDF generado exitosamente!")
        print(f"   Ubicación: {PDF_PATH}")
        print(f"   Tamaño: {size_mb:.2f} MB")
    else:
        print(f"❌ Error: El PDF no se generó correctamente")

except Exception as e:
    print(f"❌ Error al generar PDF: {str(e)}")
    print("\nIntentando método alternativo con pdfkit...")

    try:
        import pdfkit
        pdfkit.from_file(str(HTML_PATH), str(PDF_PATH))
        print(f"✅ PDF generado con pdfkit!")
        print(f"   Ubicación: {PDF_PATH}")
    except Exception as e2:
        print(f"❌ Error con pdfkit: {str(e2)}")
        print("\nPor favor, instala wkhtmltopdf o weasyprint manualmente")

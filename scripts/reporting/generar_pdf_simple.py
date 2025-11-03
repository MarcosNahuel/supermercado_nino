"""Genera PDF usando mdpdf o pypandoc (más compatible con Windows)."""

import os
import subprocess
import sys

md_file = "entregables/informe_integral_supermercado_nino_FINAL.md"
pdf_file = "entregables/Informe_Ejecutivo_Supermercado_NINO.pdf"

print("=" * 70)
print("GENERADOR DE PDF - INFORME EJECUTIVO SUPERMERCADO NINO")
print("=" * 70)
print(f"\nArchivo fuente: {md_file}")
print(f"Archivo destino: {pdf_file}\n")

# Método 1: Intentar con pandoc (más confiable)
print("Método 1: Intentando conversión con Pandoc...")
try:
    # Verificar si pandoc está instalado
    result = subprocess.run(['pandoc', '--version'], capture_output=True, text=True)
    if result.returncode == 0:
        print("✓ Pandoc encontrado:", result.stdout.split('\n')[0])

        # Comando pandoc con configuración profesional
        cmd = [
            'pandoc',
            md_file,
            '-o', pdf_file,
            '--pdf-engine=xelatex',
            '-V', 'geometry:margin=2.5cm',
            '-V', 'fontsize=11pt',
            '-V', 'documentclass=article',
            '-V', 'lang=es',
            '-V', 'colorlinks=true',
            '-V', 'linkcolor=blue',
            '-V', 'urlcolor=blue',
            '--toc',
            '--toc-depth=2'
        ]

        print("Ejecutando conversión...")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            size_mb = os.path.getsize(pdf_file) / (1024 * 1024)
            print(f"✓ PDF generado exitosamente con Pandoc")
            print(f"  Tamaño: {size_mb:.2f} MB")
            print("\n" + "=" * 70)
            print("PROCESO COMPLETADO EXITOSAMENTE")
            print("=" * 70)
            sys.exit(0)
        else:
            print(f"Error en conversión: {result.stderr}")
    else:
        print("✗ Pandoc no está instalado")
except FileNotFoundError:
    print("✗ Pandoc no encontrado en PATH")
except Exception as e:
    print(f"✗ Error: {e}")

# Método 2: Usar mdpdf
print("\nMétodo 2: Intentando con md-to-pdf (Node.js)...")
try:
    result = subprocess.run(['md-to-pdf', '--version'], capture_output=True, text=True)
    if result.returncode == 0:
        print("✓ md-to-pdf encontrado")
        cmd = ['md-to-pdf', md_file]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            # md-to-pdf genera el PDF con el mismo nombre que el MD
            generated_pdf = md_file.replace('.md', '.pdf')
            if os.path.exists(generated_pdf):
                os.rename(generated_pdf, pdf_file)
                size_mb = os.path.getsize(pdf_file) / (1024 * 1024)
                print(f"✓ PDF generado con md-to-pdf")
                print(f"  Tamaño: {size_mb:.2f} MB")
                print("\n" + "=" * 70)
                print("PROCESO COMPLETADO EXITOSAMENTE")
                print("=" * 70)
                sys.exit(0)
except Exception as e:
    print(f"✗ Error: {e}")

# Método 3: Usar markdown-pdf de Python
print("\nMétodo 3: Intentando con markdown-pdf de Python...")
try:
    try:
        import markdown_pdf
    except ImportError:
        print("Instalando markdown-pdf...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'markdown-pdf'], check=True)
        import markdown_pdf

    print("Generando PDF con markdown-pdf...")
    markdown_pdf.convert_markdown_to_pdf(md_file, pdf_file)
    size_mb = os.path.getsize(pdf_file) / (1024 * 1024)
    print(f"✓ PDF generado con markdown-pdf")
    print(f"  Tamaño: {size_mb:.2f} MB")
    print("\n" + "=" * 70)
    print("PROCESO COMPLETADO EXITOSAMENTE")
    print("=" * 70)
    sys.exit(0)
except Exception as e:
    print(f"✗ Error: {e}")

# Si todos los métodos fallan, proporcionar instrucciones
print("\n" + "=" * 70)
print("TODOS LOS MÉTODOS AUTOMÁTICOS FALLARON")
print("=" * 70)
print("\nOPCIONES ALTERNATIVAS:\n")

print("1. INSTALAR PANDOC (Recomendado):")
print("   - Descargar desde: https://pandoc.org/installing.html")
print("   - Instalar y reiniciar la terminal")
print("   - Ejecutar nuevamente: python generar_pdf_simple.py\n")

print("2. CONVERSIÓN ONLINE:")
print("   - Subir el archivo a: https://www.markdowntopdf.com/")
print(f"   - Archivo: {os.path.abspath(md_file)}\n")

print("3. EDITOR DE MARKDOWN:")
print("   - Abrir el archivo en VS Code")
print("   - Instalar extensión 'Markdown PDF'")
print("   - Click derecho > Markdown PDF: Export (pdf)\n")

print("4. EXPORTAR DESDE WORD:")
print("   - Abrir el archivo .md en Word o Google Docs")
print("   - Guardar como PDF\n")

print("=" * 70)

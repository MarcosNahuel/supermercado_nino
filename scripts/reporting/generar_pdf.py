"""Genera PDF profesional del informe integral."""

import os
import sys

# Instalar dependencias si es necesario
try:
    from markdown import markdown
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
except ImportError:
    print("Instalando dependencias necesarias...")
    os.system("pip install markdown weasyprint")
    from markdown import markdown
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration

def markdown_to_pdf(md_file, pdf_file):
    """Convierte Markdown a PDF con formato profesional."""

    # Leer archivo markdown
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convertir markdown a HTML
    html_content = markdown(md_content, extensions=['tables', 'fenced_code', 'codehilite'])

    # CSS para formato profesional A4
    css_content = """
    @page {
        size: A4;
        margin: 2.5cm 2cm;
        @bottom-right {
            content: "Página " counter(page) " de " counter(pages);
            font-size: 9pt;
            color: #666;
        }
        @bottom-left {
            content: "Supermercado NINO - Informe Ejecutivo";
            font-size: 9pt;
            color: #666;
        }
    }

    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 10.5pt;
        line-height: 1.6;
        color: #333;
        text-align: justify;
    }

    h1 {
        color: #1a472a;
        font-size: 24pt;
        font-weight: 700;
        margin-top: 0;
        margin-bottom: 0.5cm;
        page-break-after: avoid;
        border-bottom: 3px solid #2e7d32;
        padding-bottom: 0.3cm;
    }

    h2 {
        color: #2e7d32;
        font-size: 16pt;
        font-weight: 600;
        margin-top: 0.8cm;
        margin-bottom: 0.4cm;
        page-break-after: avoid;
        border-bottom: 2px solid #66bb6a;
        padding-bottom: 0.2cm;
    }

    h3 {
        color: #388e3c;
        font-size: 13pt;
        font-weight: 600;
        margin-top: 0.6cm;
        margin-bottom: 0.3cm;
        page-break-after: avoid;
    }

    h4 {
        color: #43a047;
        font-size: 11.5pt;
        font-weight: 600;
        margin-top: 0.4cm;
        margin-bottom: 0.2cm;
    }

    p {
        margin-bottom: 0.4cm;
        text-align: justify;
    }

    ul, ol {
        margin-bottom: 0.4cm;
        margin-left: 0.8cm;
    }

    li {
        margin-bottom: 0.2cm;
    }

    strong {
        color: #1b5e20;
        font-weight: 600;
    }

    em {
        color: #555;
        font-style: italic;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin: 0.5cm 0;
        font-size: 9.5pt;
        page-break-inside: avoid;
    }

    thead {
        background-color: #2e7d32;
        color: white;
        font-weight: 600;
    }

    th {
        padding: 0.3cm;
        text-align: left;
        border: 1px solid #1b5e20;
    }

    td {
        padding: 0.25cm;
        border: 1px solid #ddd;
    }

    tbody tr:nth-child(even) {
        background-color: #f1f8f4;
    }

    tbody tr:hover {
        background-color: #e8f5e9;
    }

    code {
        background-color: #f5f5f5;
        padding: 0.1cm 0.2cm;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
        font-size: 9pt;
        color: #c7254e;
    }

    pre {
        background-color: #f5f5f5;
        padding: 0.4cm;
        border-left: 4px solid #2e7d32;
        overflow-x: auto;
        font-size: 9pt;
        line-height: 1.4;
    }

    hr {
        border: none;
        border-top: 2px solid #66bb6a;
        margin: 0.6cm 0;
    }

    blockquote {
        border-left: 4px solid #66bb6a;
        padding-left: 0.5cm;
        margin-left: 0;
        color: #555;
        font-style: italic;
        background-color: #f1f8f4;
        padding: 0.4cm 0.4cm 0.4cm 0.6cm;
        margin: 0.4cm 0;
    }

    /* Clases específicas para el informe */
    .metric-box {
        background-color: #e8f5e9;
        border: 2px solid #66bb6a;
        padding: 0.4cm;
        margin: 0.3cm 0;
        border-radius: 5px;
    }

    .warning-box {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 0.4cm;
        margin: 0.3cm 0;
    }

    .success-box {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 0.4cm;
        margin: 0.3cm 0;
    }

    /* Evitar saltos de página indeseados */
    h2, h3, h4 {
        page-break-after: avoid;
    }

    table, figure {
        page-break-inside: avoid;
    }

    /* Estilo para enlaces */
    a {
        color: #2e7d32;
        text-decoration: none;
    }

    a:hover {
        text-decoration: underline;
    }

    /* Primera página - portada */
    h1:first-of-type {
        text-align: center;
        font-size: 28pt;
        margin-top: 3cm;
        border: none;
    }

    /* Metadatos de portada */
    h1:first-of-type + h1 {
        text-align: center;
        font-size: 20pt;
        color: #666;
        font-weight: 400;
        margin-top: 0.5cm;
        margin-bottom: 2cm;
        border: none;
    }
    """

    # HTML completo con estilos
    full_html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Informe Ejecutivo - Supermercado NINO</title>
        <style>{css_content}</style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    # Generar PDF
    font_config = FontConfiguration()
    html = HTML(string=full_html)
    css = CSS(string=css_content, font_config=font_config)

    print("Generando PDF...")
    html.write_pdf(pdf_file, stylesheets=[css], font_config=font_config)
    print(f"✓ PDF generado exitosamente: {pdf_file}")

    # Mostrar tamaño del archivo
    size_mb = os.path.getsize(pdf_file) / (1024 * 1024)
    print(f"  Tamaño: {size_mb:.2f} MB")

if __name__ == "__main__":
    md_file = "entregables/informe_integral_supermercado_nino_FINAL.md"
    pdf_file = "entregables/Informe_Ejecutivo_Supermercado_NINO.pdf"

    if not os.path.exists(md_file):
        print(f"Error: No se encontró el archivo {md_file}")
        sys.exit(1)

    print("=" * 60)
    print("GENERADOR DE PDF - INFORME EJECUTIVO SUPERMERCADO NINO")
    print("=" * 60)
    print(f"\nArchivo fuente: {md_file}")
    print(f"Archivo destino: {pdf_file}")
    print()

    try:
        markdown_to_pdf(md_file, pdf_file)
        print("\n" + "=" * 60)
        print("PROCESO COMPLETADO EXITOSAMENTE")
        print("=" * 60)
    except Exception as e:
        print(f"\nError al generar PDF: {e}")
        print("\nIntentando método alternativo con Pandoc...")

        # Método alternativo con pandoc si weasyprint falla
        try:
            cmd = f'pandoc "{md_file}" -o "{pdf_file}" --pdf-engine=xelatex -V geometry:margin=2.5cm -V fontsize=11pt -V documentclass=article -V lang=es'
            result = os.system(cmd)
            if result == 0:
                print(f"✓ PDF generado con Pandoc: {pdf_file}")
            else:
                print("Error: Pandoc no está instalado o falló la conversión")
                print("Instalar Pandoc: https://pandoc.org/installing.html")
        except Exception as e2:
            print(f"Error con método alternativo: {e2}")
            sys.exit(1)

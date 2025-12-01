import os
import sys

def convert_docx_to_pdf():
    """Convierte el documento Word a PDF usando diferentes métodos según disponibilidad"""

    docx_path = r'd:\OneDrive\GitHub\supermercado_nino\outputs\ENTREGABLE_FASE1_DON_NINO_V2.docx'
    pdf_path = r'd:\OneDrive\GitHub\supermercado_nino\outputs\ENTREGABLE_FASE1_DON_NINO_V2.pdf'

    # Método 1: Intentar con docx2pdf (requiere Word instalado en Windows)
    try:
        from docx2pdf import convert
        print("Convirtiendo con docx2pdf...")
        convert(docx_path, pdf_path)
        print(f"PDF creado exitosamente: {pdf_path}")
        return True
    except ImportError:
        print("docx2pdf no está instalado. Instalando...")
        os.system("pip install docx2pdf")
        try:
            from docx2pdf import convert
            convert(docx_path, pdf_path)
            print(f"PDF creado exitosamente: {pdf_path}")
            return True
        except Exception as e:
            print(f"Error con docx2pdf: {e}")
    except Exception as e:
        print(f"Error al convertir: {e}")

    # Método 2: Usar LibreOffice si está disponible
    try:
        print("\nIntentando con LibreOffice...")
        libre_office_path = r"C:\Program Files\LibreOffice\program\soffice.exe"
        if os.path.exists(libre_office_path):
            cmd = f'"{libre_office_path}" --headless --convert-to pdf --outdir "d:\\OneDrive\\GitHub\\supermercado_nino\\outputs" "{docx_path}"'
            os.system(cmd)
            print(f"PDF creado exitosamente con LibreOffice: {pdf_path}")
            return True
        else:
            print("LibreOffice no encontrado en la ruta predeterminada")
    except Exception as e:
        print(f"Error con LibreOffice: {e}")

    print("\nNo se pudo convertir automáticamente a PDF.")
    print("Para convertir a PDF, puedes:")
    print("1. Abrir el archivo .docx en Word y guardar como PDF")
    print("2. Instalar LibreOffice (gratuito) desde https://www.libreoffice.org/")
    print(f"\nEl archivo Word está listo en: {docx_path}")

    return False

if __name__ == '__main__':
    convert_docx_to_pdf()

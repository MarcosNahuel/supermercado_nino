"""Genera PDF del informe de campos para Caribbean."""
from fpdf import FPDF
from datetime import datetime

class InformePDF(FPDF):
    def __init__(self):
        super().__init__()
        # Usar fuente que soporte caracteres especiales
        self.add_font('DejaVu', '', 'C:/Windows/Fonts/arial.ttf')
        self.add_font('DejaVu', 'B', 'C:/Windows/Fonts/arialbd.ttf')
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()

    def header(self):
        self.set_font('DejaVu', 'B', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, 'Supermercado Don Nino - Requerimientos Caribbean', 0, 1, 'R')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', '', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    def titulo(self, texto):
        self.set_font('DejaVu', 'B', 16)
        self.set_text_color(0, 51, 102)
        self.cell(0, 12, texto, 0, 1, 'C')
        self.ln(4)

    def subtitulo(self, texto):
        self.set_font('DejaVu', 'B', 13)
        self.set_text_color(0, 51, 102)
        self.cell(0, 10, texto, 0, 1, 'L')
        self.ln(2)

    def subtitulo2(self, texto):
        self.set_font('DejaVu', 'B', 11)
        self.set_text_color(51, 51, 51)
        self.cell(0, 8, texto, 0, 1, 'L')
        self.ln(1)

    def texto(self, texto):
        self.set_font('DejaVu', '', 10)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, texto)
        self.ln(2)

    def texto_destacado(self, texto):
        self.set_font('DejaVu', 'B', 10)
        self.set_text_color(180, 0, 0)
        self.multi_cell(0, 6, texto)
        self.ln(2)

    def tabla(self, headers, data, col_widths=None):
        self.set_font('DejaVu', 'B', 9)
        self.set_fill_color(0, 51, 102)
        self.set_text_color(255, 255, 255)

        if col_widths is None:
            col_widths = [190 // len(headers)] * len(headers)

        for i, header in enumerate(headers):
            self.cell(col_widths[i], 8, header, 1, 0, 'C', True)
        self.ln()

        self.set_font('DejaVu', '', 9)
        self.set_text_color(0, 0, 0)
        fill = False
        for row in data:
            self.set_fill_color(240, 240, 240) if fill else self.set_fill_color(255, 255, 255)
            for i, cell in enumerate(row):
                self.cell(col_widths[i], 7, str(cell), 1, 0, 'L', fill)
            self.ln()
            fill = not fill
        self.ln(4)

def generar_pdf():
    pdf = InformePDF()

    # Portada
    pdf.titulo("INFORME DE REQUERIMIENTOS TECNICOS")
    pdf.set_font('DejaVu', 'B', 14)
    pdf.set_text_color(51, 51, 51)
    pdf.cell(0, 10, "Sistema Caribbean Desktop", 0, 1, 'C')
    pdf.cell(0, 10, "Supermercado Don Nino", 0, 1, 'C')
    pdf.ln(10)

    # Info del documento
    pdf.set_font('DejaVu', '', 10)
    pdf.set_text_color(0, 0, 0)
    info_data = [
        ["Fecha:", "16 de Enero 2026"],
        ["Destinatario:", "Tecnico de Sistema Caribbean"],
        ["Solicitante:", "Supermercado Don Nino / PymeInside"],
        ["Prioridad:", "ALTA"]
    ]
    for row in info_data:
        pdf.set_font('DejaVu', 'B', 10)
        pdf.cell(40, 7, row[0], 0, 0)
        pdf.set_font('DejaVu', '', 10)
        pdf.cell(0, 7, row[1], 0, 1)
    pdf.ln(10)

    # Resumen ejecutivo
    pdf.subtitulo("RESUMEN EJECUTIVO")
    pdf.texto("El supermercado ha implementado un sistema de Business Intelligence que analiza los datos de ventas para optimizar la rentabilidad. Para potenciar este sistema y habilitar funcionalidades criticas de FIDELIZACION DE CLIENTES, se requiere que Caribbean habilite/exporte campos adicionales en los reportes de ventas.")
    pdf.ln(5)

    # Sección 1: Campos actuales
    pdf.subtitulo("1. CAMPOS ACTUALES (YA DISPONIBLES)")
    pdf.texto("Actualmente recibimos los siguientes campos en la exportacion de comprobantes:")

    campos_actuales = [
        ["1", "Fecha", "Fecha de transaccion", "OK"],
        ["2", "Comprobante", "Numero de ticket/factura", "OK"],
        ["3", "Codigo", "Codigo interno del producto", "OK"],
        ["4", "Codigo barras", "EAN del producto", "OK"],
        ["5", "Marca", "Marca del producto", "OK"],
        ["6", "Departamento", "Categoria/rubro", "OK"],
        ["7", "Nombre", "Descripcion del producto", "OK"],
        ["8", "Cantidad", "Unidades vendidas", "OK"],
        ["9", "Importe", "Monto total de la linea", "OK"],
        ["10", "Unitario", "Precio unitario", "OK"],
        ["11", "TIPO FACTURA", "Tipo de comprobante", "OK"],
        ["12", "Tipo medio pago", "Efectivo/Tarjeta/etc.", "OK"],
        ["13", "Emisor tarjeta", "Visa, Mastercard, etc.", "OK"],
        ["14", "RENTABILIDAD", "Factor de margen", "OK"],
        ["15", "MARGEN", "Porcentaje de margen", "OK"],
    ]
    pdf.tabla(["#", "Campo", "Descripcion", "Estado"], campos_actuales, [10, 45, 100, 25])

    pdf.texto("Archivo separado con horarios: Tiene columna 'Cliente' pero esta VACIA en el 100% de los registros.")

    # Sección 2: Campos críticos
    pdf.add_page()
    pdf.subtitulo("2. CAMPOS REQUERIDOS - PRIORIDAD CRITICA")
    pdf.texto_destacado("Estos campos son INDISPENSABLES para implementar el programa de fidelizacion:")

    pdf.subtitulo2("2.1 Identificacion de Cliente")
    campos_cliente = [
        ["1", "ID_CLIENTE", "Codigo unico del cliente", "CRITICA"],
        ["2", "DNI_CLIENTE", "Documento de identidad", "CRITICA"],
        ["3", "NOMBRE_CLIENTE", "Nombre completo", "ALTA"],
        ["4", "TELEFONO_CLIENTE", "Numero de celular", "CRITICA"],
        ["5", "EMAIL_CLIENTE", "Correo electronico", "MEDIA"],
    ]
    pdf.tabla(["#", "Campo", "Descripcion", "Prioridad"], campos_cliente, [10, 50, 90, 30])

    pdf.texto_destacado("JUSTIFICACION: El campo 'Cliente' existe pero esta VACIO en el 100% de los registros. Esto impide identificar a los clientes Premium (15.6% de transacciones que generan 52.1% de la ganancia).")

    pdf.subtitulo2("2.2 Unificacion de Archivo de Exportacion")
    pdf.tabla(["#", "Campo", "Descripcion", "Prioridad"],
              [["6", "HORA", "Hora de transaccion (HH:MM:SS)", "CRITICA"]],
              [10, 50, 90, 30])
    pdf.texto("JUSTIFICACION: Actualmente la hora esta en un archivo separado. Se requiere unificar en un solo archivo.")

    # Sección 3: Campos alta prioridad
    pdf.subtitulo("3. CAMPOS REQUERIDOS - PRIORIDAD ALTA")
    pdf.subtitulo2("3.1 Informacion de Punto de Venta")
    campos_pos = [
        ["7", "CODIGO_CAJA", "Numero de caja", "ALTA"],
        ["8", "CODIGO_CAJERO", "ID del empleado", "ALTA"],
        ["9", "TURNO", "Turno de transaccion", "MEDIA"],
    ]
    pdf.tabla(["#", "Campo", "Descripcion", "Prioridad"], campos_pos, [10, 50, 90, 30])

    pdf.subtitulo2("3.2 Informacion Adicional del Producto")
    campos_prod = [
        ["10", "PROVEEDOR", "Codigo/nombre proveedor", "MEDIA"],
        ["11", "COSTO_PRODUCTO", "Costo de adquisicion", "MEDIA"],
    ]
    pdf.tabla(["#", "Campo", "Descripcion", "Prioridad"], campos_prod, [10, 50, 90, 30])

    # Sección 4: Priorizacion
    pdf.add_page()
    pdf.subtitulo("4. PRIORIZACION POR IMPACTO DE NEGOCIO")

    pdf.subtitulo2("ETAPA 1 - INMEDIATA (1-2 semanas)")
    pdf.texto_destacado("Habilitar estos campos es CRITICO para la estrategia de fidelizacion:")
    etapa1 = [
        ["ID_CLIENTE", "Permite identificar clientes recurrentes"],
        ["TELEFONO_CLIENTE", "Habilita comunicacion via WhatsApp"],
        ["HORA (en archivo principal)", "Simplifica el proceso de analisis"],
    ]
    pdf.tabla(["Campo", "Impacto"], etapa1, [60, 120])

    pdf.texto_destacado("Sin estos campos, es imposible implementar el programa de fidelizacion que proteja a los clientes Premium (52% de la ganancia).")

    pdf.subtitulo2("ETAPA 2 - CORTO PLAZO (1 mes)")
    etapa2 = [
        ["DNI_CLIENTE", "Identificacion unica y verificable"],
        ["NOMBRE_CLIENTE", "Comunicacion personalizada"],
        ["CODIGO_CAJA", "Analisis de productividad por caja"],
        ["CODIGO_CAJERO", "Incentivos y capacitacion"],
    ]
    pdf.tabla(["Campo", "Impacto"], etapa2, [60, 120])

    pdf.subtitulo2("ETAPA 3 - MEDIANO PLAZO (2-3 meses)")
    etapa3 = [
        ["EMAIL_CLIENTE", "Marketing digital"],
        ["PROVEEDOR", "Analisis de supply chain"],
        ["COSTO_PRODUCTO", "Margenes precisos"],
        ["DESCUENTO_LINEA", "Efectividad de promociones"],
    ]
    pdf.tabla(["Campo", "Impacto"], etapa3, [60, 120])

    # Sección 5: Preguntas
    pdf.add_page()
    pdf.subtitulo("5. PREGUNTAS PARA EL TECNICO")

    preguntas = [
        "1. El campo 'Cliente' ya existe en Caribbean pero no se esta capturando?",
        "   - El archivo de horarios tiene la columna 'Cliente' pero esta vacia.",
        "",
        "2. Se puede configurar Caribbean para solicitar DNI/telefono en caja?",
        "   - Es un campo obligatorio u opcional?",
        "   - Existe busqueda de cliente por telefono?",
        "",
        "3. Caribbean tiene modulo de clientes/fidelizacion integrado?",
        "   - Si existe, como se activa?",
        "   - Tiene acumulacion de puntos?",
        "",
        "4. Se pueden unificar ambos archivos de exportacion?",
        "   - Actualmente hay uno con detalles y otro con horarios.",
        "",
        "5. Cual es el proceso para agregar campos a la exportacion?",
        "   - Requiere actualizacion de version?",
        "   - Es configurable desde el sistema?",
        "",
        "6. Existe documentacion de la estructura de datos de Caribbean?",
        "   - Manual tecnico de tablas/campos disponibles.",
    ]
    for p in preguntas:
        pdf.texto(p)

    # Sección 6: Resumen final
    pdf.add_page()
    pdf.subtitulo("6. RESUMEN DE CAMPOS REQUERIDOS")

    resumen = [
        ["ID_CLIENTE", "CRITICA", "NO", "SI"],
        ["DNI_CLIENTE", "CRITICA", "NO", "SI"],
        ["TELEFONO_CLIENTE", "CRITICA", "NO", "SI"],
        ["HORA (unificada)", "CRITICA", "Separado", "SI"],
        ["NOMBRE_CLIENTE", "ALTA", "NO", "SI"],
        ["CODIGO_CAJA", "ALTA", "NO", "SI"],
        ["CODIGO_CAJERO", "ALTA", "NO", "SI"],
        ["EMAIL_CLIENTE", "MEDIA", "NO", "Opcional"],
        ["PROVEEDOR", "MEDIA", "NO", "Opcional"],
        ["COSTO_PRODUCTO", "MEDIA", "NO", "Opcional"],
    ]
    pdf.tabla(["Campo", "Prioridad", "Disponible", "Requerido"], resumen, [55, 35, 40, 40])

    # Nota final
    pdf.ln(10)
    pdf.set_font('DejaVu', 'B', 11)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "NOTA IMPORTANTE", 0, 1, 'L')
    pdf.set_font('DejaVu', '', 10)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 6, "El 15.6% de los clientes (Tribu Premium) genera el 52.1% de la ganancia del negocio. Sin identificacion de clientes, es imposible proteger este segmento critico de la competencia. La implementacion de estos campos es fundamental para la supervivencia del negocio.")

    # Guardar
    output_path = "D:/OneDrive/GitHub/supermercado_nino definitivo claude/DOCUMENTACION/INFORME_CAMPOS_CARIBBEAN.pdf"
    pdf.output(output_path)
    print(f"PDF generado: {output_path}")
    return output_path

if __name__ == "__main__":
    generar_pdf()

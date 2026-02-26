"""Genera PDF de respuesta a presupuesto Bosin S.A."""
from fpdf import FPDF


class PDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("Fuente", "I", 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 5, "Respuesta a Presupuesto - Caribbean | Don Nino / PymeInside", align="R")
            self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("Fuente", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Pagina {self.page_no()}/{{nb}}", align="C")

    def reset_x(self):
        self.set_x(self.l_margin)

    def section_title(self, num, title):
        self.reset_x()
        self.set_font("Fuente", "B", 13)
        self.set_text_color(30, 60, 120)
        self.cell(0, 10, f"{num}. {title}", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(30, 60, 120)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)

    def body_text(self, text):
        self.reset_x()
        self.set_font("Fuente", "", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def bold_text(self, text):
        self.reset_x()
        self.set_font("Fuente", "B", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def bullet(self, text, bold_part=""):
        self.reset_x()
        self.set_font("Fuente", "", 10)
        self.set_text_color(40, 40, 40)
        self.cell(6, 5.5, chr(149))
        if bold_part:
            self.set_font("Fuente", "B", 10)
            bw = self.get_string_width(bold_part) + 1
            self.cell(bw, 5.5, bold_part)
            self.set_font("Fuente", "", 10)
        remaining_w = self.w - self.get_x() - self.r_margin
        if remaining_w < 20:
            self.ln(5.5)
            self.reset_x()
            remaining_w = self.w - self.l_margin - self.r_margin - 6
            self.set_x(self.l_margin + 6)
        self.multi_cell(remaining_w, 5.5, text)
        self.ln(1)

    def question_bullet(self, text):
        self.set_x(self.l_margin + 4)
        self.set_font("Fuente", "I", 9.5)
        self.set_text_color(80, 80, 80)
        self.cell(5, 5.5, "-")
        remaining_w = self.w - self.get_x() - self.r_margin
        self.multi_cell(remaining_w, 5.5, text)

    def option_title(self, text):
        self.reset_x()
        self.set_font("Fuente", "B", 11)
        self.set_text_color(30, 60, 120)
        self.multi_cell(0, 6, text)

    def highlight_box(self, text):
        self.reset_x()
        self.set_font("Fuente", "I", 9.5)
        w = self.w - self.l_margin - self.r_margin
        inner_w = w - 10
        lines = self.multi_cell(inner_w, 5, text, dry_run=True, output="LINES")
        h = len(lines) * 5 + 8
        x = self.l_margin
        y = self.get_y()
        self.set_fill_color(240, 245, 255)
        self.set_draw_color(30, 60, 120)
        self.rect(x, y, w, h, style="DF")
        self.set_xy(x + 5, y + 4)
        self.set_text_color(30, 60, 120)
        self.multi_cell(inner_w, 5, text)
        self.set_y(y + h + 3)

    def separator(self):
        self.set_draw_color(180, 180, 180)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)


def generar_pdf():
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)

    # Fuentes Unicode
    pdf.add_font("Fuente", "", "C:/Windows/Fonts/arial.ttf")
    pdf.add_font("Fuente", "B", "C:/Windows/Fonts/arialbd.ttf")
    pdf.add_font("Fuente", "I", "C:/Windows/Fonts/ariali.ttf")
    pdf.add_font("Fuente", "BI", "C:/Windows/Fonts/arialbi.ttf")

    pdf.add_page()

    # === ENCABEZADO ===
    pdf.set_font("Fuente", "B", 18)
    pdf.set_text_color(30, 60, 120)
    pdf.cell(0, 10, "Respuesta a Presupuesto", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Fuente", "", 13)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 7, "Sistema Caribbean", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)

    for label, value in [
        ("Cliente:", "Supermercado Don Nino / PymeInside"),
        ("Fecha:", "6 de Febrero de 2026"),
        ("Referencia:", "Presupuesto Bosin S.A. del 02/02/2026"),
    ]:
        pdf.set_font("Fuente", "B", 10)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(25, 5.5, label)
        pdf.set_font("Fuente", "", 10)
        pdf.cell(0, 5.5, value, new_x="LMARGIN", new_y="NEXT")

    pdf.ln(4)
    pdf.separator()
    pdf.ln(2)

    # === SECCION 1 ===
    pdf.section_title("1", "GRUPO A \u2014 APROBADO")

    pdf.body_text(
        "Agradecemos la propuesta. Vamos a avanzar con el Grupo A ($600.000 + IVA), que incluye:"
    )

    for t in [
        "Ventas - Detalle de Comprobantes",
        "Precios - Hist\u00f3rico",
        "Maestro de Productos",
        "Maestro de Clientes",
    ]:
        pdf.bullet(t)

    pdf.ln(2)
    pdf.body_text(
        "Grupo B y C no aplican por ahora dado que no se gestiona stock en el sistema."
    )
    pdf.body_text(
        "Si las tablas del Grupo A vienen completas con todos los campos seg\u00fan lo propuesto, "
        "estamos de acuerdo. Solo necesitamos confirmar que cada comprobante de venta incluya tambi\u00e9n:"
    )

    for campo, desc in [
        ("ID_CLIENTE", "C\u00f3digo \u00fanico del cliente"),
        ("DNI", "Documento de identidad"),
        ("NOMBRE", "Nombre completo del cliente"),
        ("TEL\u00c9FONO", "N\u00famero de contacto"),
        ("HORA", "Hora de la transacci\u00f3n (hoy viene en archivo separado)"),
    ]:
        pdf.bullet(desc, bold_part=f"{campo} \u2014 ")

    pdf.ln(2)
    pdf.highlight_box(
        "Sin la vinculaci\u00f3n cliente-comprobante, el Maestro de Clientes no tiene utilidad "
        "y el desarrollo pierde su objetivo principal."
    )
    pdf.ln(4)

    # === SECCION 2 ===
    pdf.section_title("2", "DISPONIBILIDAD DE LA INFORMACI\u00d3N")

    pdf.body_text(
        "Nuestro sistema de BI necesita consumir estos datos de forma peri\u00f3dica y autom\u00e1tica "
        "(idealmente diaria). Necesitamos definir c\u00f3mo accedemos a la informaci\u00f3n."
    )
    pdf.bold_text("Planteamos tres opciones, de mayor a menor preferencia:")
    pdf.ln(2)

    # Opcion 1
    pdf.option_title("Opci\u00f3n 1 \u2014 Acceso directo a la base de datos (preferida)")
    pdf.body_text(
        "Conectarnos a la BD de Caribbean en modo lectura (ODBC, JDBC o driver nativo) "
        "para extraer los datos autom\u00e1ticamente. Si es viable, la extracci\u00f3n la resolvemos nosotros."
    )
    pdf.question_bullet("\u00bfEs posible acceder a la base de datos desde un proceso externo?")
    pdf.question_bullet("\u00bfQu\u00e9 tipo de conexi\u00f3n se requiere? (driver, puerto, protocolo)")
    pdf.question_bullet("\u00bfHay restricciones de licencia o de uso?")
    pdf.ln(2)
    pdf.highlight_box(
        "Si esta opci\u00f3n es viable, la extracci\u00f3n la resolvemos desde nuestro lado "
        "y el desarrollo se enfoca en habilitar la captura de clientes en caja."
    )
    pdf.ln(4)

    # Opcion 2
    pdf.option_title("Opci\u00f3n 2 \u2014 Exportaci\u00f3n autom\u00e1tica programada")
    pdf.body_text(
        "Que el m\u00f3dulo genere los archivos CSV autom\u00e1ticamente por tarea programada "
        "y los deposite en una carpeta configurada, sin intervenci\u00f3n del operador."
    )
    pdf.question_bullet("\u00bfEl m\u00f3dulo puede ejecutarse por l\u00ednea de comandos o tarea programada?")
    pdf.question_bullet("\u00bfPuede exportar con rango de fechas din\u00e1mico? (ej: datos del d\u00eda anterior)")
    pdf.ln(4)

    # Opcion 3
    pdf.option_title("Opci\u00f3n 3 \u2014 Exportaci\u00f3n manual asistida")
    pdf.body_text(
        "El operador genera los archivos manualmente y nuestro sistema los detecta y procesa. "
        "Es la opci\u00f3n menos deseable por depender de intervenci\u00f3n diaria."
    )
    pdf.question_bullet("\u00bfLos archivos pueden guardarse en una carpeta de red compartida?")
    pdf.ln(4)

    # === SECCION 3 ===
    pdf.section_title("3", "PREGUNTAS FINALES")

    pdf.bullet("\u00bfCu\u00e1l es el plazo estimado de entrega del Grupo A?")
    pdf.bullet("\u00bfEl presupuesto incluye soporte post-implementaci\u00f3n?")

    pdf.ln(6)

    # === RESUMEN ===
    pdf.separator()

    pdf.bold_text("Resumen \u2014 Confirmamos inter\u00e9s en el Grupo A. Necesitamos respuesta sobre:")
    pdf.ln(1)
    pdf.bullet("Que cada comprobante de venta lleve identificaci\u00f3n del cliente.", bold_part="Clientes: ")
    pdf.bullet("Cu\u00e1l de las tres opciones es viable para automatizar la obtenci\u00f3n de datos.", bold_part="Extracci\u00f3n: ")
    pdf.bullet("Tiempos de entrega y cobertura post-implementaci\u00f3n.", bold_part="Plazos: ")

    pdf.ln(4)
    pdf.body_text("Quedamos a disposici\u00f3n para una reuni\u00f3n t\u00e9cnica si es necesario.")

    pdf.ln(4)
    pdf.separator()

    pdf.set_font("Fuente", "B", 10)
    pdf.set_text_color(30, 60, 120)
    pdf.cell(0, 5.5, "Supermercado Don Nino / PymeInside", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Fuente", "", 10)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 5.5, "Equipo de Business Intelligence", new_x="LMARGIN", new_y="NEXT", align="C")

    out = r"D:\OneDrive\GitHub\supermercado_nino definitivo claude\DOCUMENTACION\RESPUESTA_PRESUPUESTO_BOSIN.pdf"
    pdf.output(out)
    print(f"PDF generado: {out}")


if __name__ == "__main__":
    generar_pdf()

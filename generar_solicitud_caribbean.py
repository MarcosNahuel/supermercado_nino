"""Genera PDF de solicitud de campos para Caribbean."""
from fpdf import FPDF

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font('Arial', '', 'C:/Windows/Fonts/arial.ttf')
        self.add_font('Arial', 'B', 'C:/Windows/Fonts/arialbd.ttf')
        self.set_auto_page_break(auto=True, margin=15)

    def tabla(self, titulo, campos, color=(0, 51, 102)):
        self.set_font('Arial', 'B', 11)
        self.set_fill_color(220, 220, 220)
        self.cell(0, 8, titulo, ln=True, fill=True)
        self.ln(2)

        # Header
        self.set_font('Arial', 'B', 9)
        self.set_fill_color(*color)
        self.set_text_color(255, 255, 255)
        self.cell(55, 6, 'Campo', 1, 0, 'C', True)
        self.cell(0, 6, 'Descripcion', 1, 1, 'C', True)

        # Rows
        self.set_font('Arial', '', 9)
        self.set_text_color(0, 0, 0)
        for campo, desc in campos:
            self.cell(55, 5, campo, 1, 0, 'L')
            self.cell(0, 5, desc, 1, 1, 'L')
        self.ln(5)

pdf = PDF()
pdf.add_page()

# Encabezado
pdf.set_font('Arial', 'B', 16)
pdf.cell(0, 10, 'Solicitud de Datos - Sistema Caribbean', ln=True, align='C')
pdf.set_font('Arial', '', 11)
pdf.cell(0, 7, 'Supermercado Don Nino', ln=True, align='C')
pdf.cell(0, 7, 'Fecha: 16/01/2026', ln=True, align='C')
pdf.ln(8)

# 1. VENTAS
ventas = [
    ("Fecha", "Fecha de la transaccion (YYYY-MM-DD)"),
    ("Hora", "Hora exacta (HH:MM:SS)"),
    ("Comprobante", "Numero de ticket/factura"),
    ("Tipo Comprobante", "FA, FB, NC, ND, etc."),
    ("SKU", "Codigo interno del producto"),
    ("Codigo Barras", "EAN/UPC del producto"),
    ("Descripcion", "Nombre del producto"),
    ("Departamento", "Categoria/rubro"),
    ("Marca", "Marca del producto"),
    ("Cantidad", "Unidades vendidas"),
    ("Precio Unitario", "Precio de venta unitario"),
    ("Descuento Linea %", "Porcentaje de descuento del item"),
    ("Descuento Linea $", "Monto de descuento del item"),
    ("Importe Bruto", "Precio x Cantidad (sin descuento)"),
    ("Importe Neto", "Monto final (con descuento)"),
    ("Descuento Ticket %", "Descuento general del ticket"),
    ("Descuento Ticket $", "Monto descuento general"),
    ("Motivo Descuento", "Codigo/descripcion del motivo"),
    ("Medio de Pago", "Efectivo, Debito, Credito, QR, etc."),
    ("Emisor Tarjeta", "Visa, Mastercard, etc."),
    ("Cuotas", "Cantidad de cuotas (si aplica)"),
    ("ID Cliente", "Codigo unico del cliente"),
    ("DNI Cliente", "Documento del cliente"),
    ("Nombre Cliente", "Nombre completo"),
    ("Telefono Cliente", "Numero de contacto"),
    ("Codigo Caja", "Numero de caja"),
    ("Codigo Cajero", "ID del empleado"),
]
pdf.tabla("1. VENTAS - Detalle de Comprobantes", ventas)

pdf.add_page()

# 2. STOCK
stock = [
    ("Fecha Consulta", "Fecha del corte de inventario"),
    ("Hora Consulta", "Hora del corte"),
    ("SKU", "Codigo interno del producto"),
    ("Codigo Barras", "EAN/UPC"),
    ("Descripcion", "Nombre del producto"),
    ("Departamento", "Categoria/rubro"),
    ("Marca", "Marca del producto"),
    ("Stock Actual", "Unidades disponibles"),
    ("Stock Minimo", "Punto de reposicion"),
    ("Stock Maximo", "Tope de inventario"),
    ("Unidad Medida", "Unidad, Kg, Lt, etc."),
    ("Ubicacion", "Deposito/gondola/sector"),
    ("Proveedor Principal", "Codigo/nombre proveedor"),
    ("Fecha Ultimo Ingreso", "Ultima recepcion"),
    ("Fecha Ultima Venta", "Ultima venta del producto"),
]
pdf.tabla("2. STOCK - Inventario Actual", stock, (0, 102, 51))

# 3. MOVIMIENTOS
movimientos = [
    ("Fecha", "Fecha del movimiento"),
    ("Hora", "Hora exacta del movimiento"),
    ("SKU", "Codigo del producto"),
    ("Codigo Barras", "EAN/UPC"),
    ("Descripcion", "Nombre del producto"),
    ("Departamento", "Categoria"),
    ("Tipo Movimiento", "Entrada / Salida / Ajuste"),
    ("Motivo", "Compra, Venta, Merma, Transferencia, etc."),
    ("Cantidad", "Unidades del movimiento (+/-)"),
    ("Stock Anterior", "Stock antes del movimiento"),
    ("Stock Posterior", "Stock despues del movimiento"),
    ("Documento Referencia", "Remito, Factura, Ticket, etc."),
    ("Numero Documento", "Numero del documento"),
    ("Proveedor", "Codigo/nombre (si es entrada)"),
    ("Lote", "Numero de lote (si aplica)"),
    ("Fecha Vencimiento", "Vencimiento del lote"),
    ("Costo Unitario", "Costo del movimiento"),
    ("Usuario", "Quien registro el movimiento"),
]
pdf.tabla("3. MOVIMIENTOS DE STOCK", movimientos, (102, 51, 0))

pdf.add_page()

# 4. BAJAS/MERMAS
bajas = [
    ("Fecha", "Fecha de la baja"),
    ("Hora", "Hora exacta"),
    ("SKU", "Codigo del producto"),
    ("Codigo Barras", "EAN/UPC"),
    ("Descripcion", "Nombre del producto"),
    ("Departamento", "Categoria"),
    ("Cantidad", "Unidades dadas de baja"),
    ("Motivo Baja", "Vencimiento, Rotura, Deterioro, Hurto, etc."),
    ("Costo Unitario", "Costo del producto"),
    ("Costo Total", "Perdida total"),
    ("Lote", "Numero de lote"),
    ("Fecha Vencimiento", "Si es por vencimiento"),
    ("Documento Baja", "Numero de comprobante interno"),
    ("Usuario", "Quien registro"),
    ("Autorizado Por", "Supervisor que autorizo"),
    ("Observaciones", "Detalle adicional"),
]
pdf.tabla("4. BAJAS / MERMAS (Salidas No Venta)", bajas, (153, 0, 0))

# 5. PRECIOS
precios = [
    ("Fecha Desde", "Inicio de vigencia del precio"),
    ("Fecha Hasta", "Fin de vigencia (vacio si vigente)"),
    ("Hora Cambio", "Hora exacta del cambio"),
    ("SKU", "Codigo del producto"),
    ("Codigo Barras", "EAN/UPC"),
    ("Descripcion", "Nombre del producto"),
    ("Departamento", "Categoria"),
    ("Precio Lista", "Precio regular"),
    ("Precio Promocional", "Precio de oferta (si aplica)"),
    ("Tipo Precio", "Regular, Oferta, Liquidacion, etc."),
    ("Motivo Cambio", "Actualizacion, Promocion, Ajuste, etc."),
    ("Usuario", "Quien modifico"),
]
pdf.tabla("5. PRECIOS - Historico por SKU", precios, (0, 51, 102))

pdf.add_page()

# 6. COSTOS
costos = [
    ("Fecha", "Fecha del costo"),
    ("SKU", "Codigo del producto"),
    ("Codigo Barras", "EAN/UPC"),
    ("Descripcion", "Nombre"),
    ("Costo Unitario", "Costo de adquisicion"),
    ("Costo Promedio", "Costo promedio ponderado"),
    ("Proveedor", "Codigo/nombre"),
    ("Documento", "Factura de compra"),
    ("Numero Documento", "Numero de factura"),
]
pdf.tabla("6. COSTOS - Historico por SKU (si existe)", costos, (102, 102, 0))

# 7. MAESTRO PRODUCTOS
productos = [
    ("SKU", "Codigo interno unico"),
    ("Codigo Barras", "EAN/UPC"),
    ("Descripcion", "Nombre del producto"),
    ("Descripcion Corta", "Nombre abreviado"),
    ("Departamento", "Categoria principal"),
    ("Subdepartamento", "Subcategoria"),
    ("Marca", "Marca del producto"),
    ("Proveedor Principal", "Codigo/nombre"),
    ("Unidad Medida", "Unidad, Kg, Lt, etc."),
    ("Contenido Neto", "Peso/volumen"),
    ("IVA", "Tasa de IVA aplicable"),
    ("Dias Vida Util", "Para productos perecederos"),
    ("Stock Minimo", "Punto de reposicion"),
    ("Stock Maximo", "Tope de inventario"),
    ("Activo", "Si/No"),
    ("Fecha Alta", "Fecha de creacion"),
    ("Fecha Baja", "Si esta inactivo"),
]
pdf.tabla("7. MAESTRO DE PRODUCTOS", productos, (51, 51, 102))

pdf.add_page()

# 8. MAESTRO CLIENTES
clientes = [
    ("ID Cliente", "Codigo unico"),
    ("DNI/CUIT", "Documento"),
    ("Nombre", "Nombre completo / Razon social"),
    ("Telefono", "Numero de contacto"),
    ("Email", "Correo electronico"),
    ("Direccion", "Domicilio"),
    ("Fecha Alta", "Fecha de registro"),
    ("Fecha Ultima Compra", "Ultima transaccion"),
    ("Categoria Cliente", "VIP, Regular, Mayorista, etc."),
]
pdf.tabla("8. MAESTRO DE CLIENTES (si existe)", clientes, (102, 0, 102))

pdf.ln(5)

# Notas técnicas
pdf.set_font('Arial', 'B', 11)
pdf.set_fill_color(220, 220, 220)
pdf.cell(0, 8, 'Notas Tecnicas', ln=True, fill=True)
pdf.ln(2)
pdf.set_font('Arial', '', 10)
notas = [
    "- Vinculacion: Todos los datos se vinculan por SKU y Fecha/Hora",
    "- Formato Fecha: YYYY-MM-DD",
    "- Formato Hora: HH:MM:SS (24 horas)",
    "- Formato Archivo: CSV con separador punto y coma (;)",
    "- Encoding: UTF-8",
    "- Frecuencia: Diaria o segun se acuerde",
]
for nota in notas:
    pdf.cell(0, 6, nota, ln=True)

pdf.ln(8)

# Resumen
pdf.set_font('Arial', 'B', 11)
pdf.set_fill_color(220, 220, 220)
pdf.cell(0, 8, 'Resumen de Tablas Solicitadas', ln=True, fill=True)
pdf.ln(2)

pdf.set_font('Arial', 'B', 9)
pdf.set_fill_color(0, 51, 102)
pdf.set_text_color(255, 255, 255)
pdf.cell(10, 6, '#', 1, 0, 'C', True)
pdf.cell(100, 6, 'Tabla', 1, 0, 'C', True)
pdf.cell(0, 6, 'Prioridad', 1, 1, 'C', True)

pdf.set_font('Arial', '', 9)
pdf.set_text_color(0, 0, 0)
resumen = [
    ("1", "Ventas - Detalle Comprobantes", "Alta"),
    ("2", "Stock - Inventario Actual", "Alta"),
    ("3", "Movimientos de Stock", "Alta"),
    ("4", "Bajas / Mermas", "Alta"),
    ("5", "Precios - Historico", "Alta"),
    ("6", "Costos - Historico", "Media (si existe)"),
    ("7", "Maestro de Productos", "Alta"),
    ("8", "Maestro de Clientes", "Media (si existe)"),
]
for num, tabla, prioridad in resumen:
    pdf.cell(10, 5, num, 1, 0, 'C')
    pdf.cell(100, 5, tabla, 1, 0, 'L')
    pdf.cell(0, 5, prioridad, 1, 1, 'C')

# Guardar
output = "D:/OneDrive/GitHub/supermercado_nino definitivo claude/DOCUMENTACION/SOLICITUD_DATOS_CARIBBEAN.pdf"
pdf.output(output)
print(f"PDF generado: {output}")

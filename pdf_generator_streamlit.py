# -*- coding: utf-8 -*-
"""
================================================================================
INTEGRACIÓN PDF EN STREAMLIT - SUPERMERCADO NINO
================================================================================
Módulo para generar PDF directamente desde el dashboard Streamlit
con los gráficos visualizados en la sesión actual.
================================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from io import BytesIO
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

# Importar generador PDF
try:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.units import inch, cm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak,
        Table, TableStyle, KeepTogether
    )
    from reportlab.lib.colors import HexColor, white, black, lightgrey
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    from PIL import Image as PILImage
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# ==================================================================================
# CONFIGURACIÓN
# ==================================================================================

class ConfigPDFStreamlit:
    """Configuración para PDF desde Streamlit"""

    COLOR_PRIMARY = HexColor("#1F77B4")
    COLOR_SECONDARY = HexColor("#FF7F0E")
    COLOR_ACCENT = HexColor("#2CA02C")
    COLOR_GRAY = HexColor("#7F7F7F")
    COLOR_LIGHT_GRAY = HexColor("#E8E8E8")

    PAGE_WIDTH, PAGE_HEIGHT = A4
    MARGIN = 0.75 * inch
    CONTENT_WIDTH = PAGE_WIDTH - (2 * MARGIN)

    CHART_DPI = 150


# ==================================================================================
# UTILIDADES
# ==================================================================================

def formatear_numero_argentino(numero, decimales=0):
    """Formatea números al estilo argentino"""
    if pd.isna(numero):
        return "N/A"

    numero_redondeado = round(numero, decimales)

    if decimales > 0:
        parte_entera = int(numero_redondeado)
        parte_decimal = int((numero_redondeado - parte_entera) * (10 ** decimales))
        parte_decimal_str = f"{parte_decimal:0{decimales}d}"
    else:
        parte_entera = int(numero_redondeado)
        parte_decimal_str = ""

    parte_entera_formateada = f"{parte_entera:,}".replace(",", ".")

    if decimales > 0:
        return f"{parte_entera_formateada},{parte_decimal_str}"
    else:
        return parte_entera_formateada


def formatear_moneda_argentina(numero, decimales=0, simbolo="$"):
    """Formatea moneda al estilo argentino"""
    return f"{simbolo}{formatear_numero_argentino(numero, decimales)}"


def exportar_figura_plotly(fig):
    """Exporta una figura Plotly a PNG en memoria"""
    try:
        buffer = BytesIO()
        fig.write_image(
            buffer,
            format='png',
            width=int(ConfigPDFStreamlit.CONTENT_WIDTH * ConfigPDFStreamlit.CHART_DPI / 72),
            height=int(5 * inch * ConfigPDFStreamlit.CHART_DPI / 72),
            scale=1
        )
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.warning(f"⚠️ Error exportando gráfico: {e}")
        return None


# ==================================================================================
# GENERADOR PDF DESDE STREAMLIT
# ==================================================================================

class GeneradorPDFStreamlit:
    """Genera PDF con los gráficos desde Streamlit"""

    def __init__(self, datos, titulo="Informe Ejecutivo"):
        self.datos = datos
        self.titulo = titulo
        self.elementos = []
        self.styles = self._crear_estilos()

    def _crear_estilos(self):
        """Crea estilos personalizados"""
        styles = getSampleStyleSheet()

        styles.add(ParagraphStyle(
            name='TituloInforme',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=ConfigPDFStreamlit.COLOR_PRIMARY,
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=ConfigPDFStreamlit.COLOR_PRIMARY,
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))

        styles.add(ParagraphStyle(
            name='BodyNormal',
            parent=styles['BodyText'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=10,
            leading=12
        ))

        styles.add(ParagraphStyle(
            name='Highlight',
            parent=styles['Normal'],
            fontSize=10,
            textColor=ConfigPDFStreamlit.COLOR_PRIMARY,
            backColor=HexColor("#F0F8FF"),
            borderColor=ConfigPDFStreamlit.COLOR_PRIMARY,
            borderWidth=1,
            borderPadding=5,
            spaceAfter=10,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        return styles

    def agregar_portada(self):
        """Agrega portada"""
        self.elementos.append(Spacer(ConfigPDFStreamlit.CONTENT_WIDTH, 2 * inch))

        titulo = Paragraph(
            "SUPERMERCADO NINO",
            self.styles['TituloInforme']
        )
        self.elementos.append(titulo)

        subtitulo = Paragraph(
            self.titulo,
            self.styles['SectionHeading']
        )
        self.elementos.append(subtitulo)

        self.elementos.append(Spacer(ConfigPDFStreamlit.CONTENT_WIDTH, 1 * inch))

        fecha_texto = Paragraph(
            f"<b>Generado:</b> {datetime.now().strftime('%d/%m/%Y a las %H:%M')}",
            self.styles['BodyNormal']
        )
        self.elementos.append(fecha_texto)

        self.elementos.append(PageBreak())

    def agregar_kpis(self, kpis_dict):
        """Agrega sección de KPIs"""
        titulo = Paragraph("Métricas Principales", self.styles['SectionHeading'])
        self.elementos.append(titulo)

        # Crear tabla de KPIs
        datos_tabla = [['Métrica', 'Valor']]
        for metrica, valor in kpis_dict.items():
            datos_tabla.append([metrica, str(valor)])

        tabla = Table(datos_tabla, colWidths=[3*inch, 2.5*inch])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), ConfigPDFStreamlit.COLOR_PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), ConfigPDFStreamlit.COLOR_LIGHT_GRAY),
            ('GRID', (0, 0), (-1, -1), 1, black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, ConfigPDFStreamlit.COLOR_LIGHT_GRAY]),
        ]))

        self.elementos.append(tabla)
        self.elementos.append(Spacer(ConfigPDFStreamlit.CONTENT_WIDTH, 0.3 * inch))

    def agregar_grafico(self, fig, titulo="Gráfico"):
        """Agrega un gráfico Plotly al PDF"""
        if fig is None:
            return

        # Agregar título
        self.elementos.append(Paragraph(titulo, self.styles['SectionHeading']))

        # Exportar figura a PNG
        buffer = exportar_figura_plotly(fig)

        if buffer:
            try:
                # Guardar temporalmente
                temp_path = Path("/tmp") / f"grafico_{datetime.now().timestamp()}.png"
                with open(temp_path, 'wb') as f:
                    f.write(buffer.getvalue())

                # Agregar imagen
                img = Image(
                    str(temp_path),
                    width=ConfigPDFStreamlit.CONTENT_WIDTH,
                    height=3.5*inch
                )
                self.elementos.append(img)
                self.elementos.append(Spacer(ConfigPDFStreamlit.CONTENT_WIDTH, 0.2 * inch))

            except Exception as e:
                st.warning(f"⚠️ Error agregando gráfico al PDF: {e}")
        else:
            self.elementos.append(Paragraph(
                "⚠️ No se pudo generar el gráfico",
                self.styles['BodyNormal']
            ))

    def agregar_tabla_datos(self, df, titulo="Tabla de Datos"):
        """Agrega una tabla de datos al PDF"""
        if df is None or len(df) == 0:
            return

        self.elementos.append(Paragraph(titulo, self.styles['SectionHeading']))

        # Limitar a primeras 10 filas y 5 columnas
        df_display = df.iloc[:10, :5].copy()

        # Convertir a datos de tabla
        datos_tabla = [list(df_display.columns)]
        for _, row in df_display.iterrows():
            datos_tabla.append([str(v)[:30] for v in row.values])  # Limitar texto

        tabla = Table(datos_tabla, colWidths=[ConfigPDFStreamlit.CONTENT_WIDTH / 5] * 5)
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), ConfigPDFStreamlit.COLOR_PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), ConfigPDFStreamlit.COLOR_LIGHT_GRAY),
            ('GRID', (0, 0), (-1, -1), 0.5, black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, ConfigPDFStreamlit.COLOR_LIGHT_GRAY]),
        ]))

        self.elementos.append(tabla)
        self.elementos.append(Spacer(ConfigPDFStreamlit.CONTENT_WIDTH, 0.3 * inch))

    def agregar_texto(self, texto, es_titulo=False):
        """Agrega párrafo de texto"""
        estilo = self.styles['SectionHeading'] if es_titulo else self.styles['BodyNormal']
        self.elementos.append(Paragraph(texto, estilo))
        self.elementos.append(Spacer(ConfigPDFStreamlit.CONTENT_WIDTH, 0.1 * inch))

    def agregar_salto_pagina(self):
        """Agrega salto de página"""
        self.elementos.append(PageBreak())

    def generar_bytes(self):
        """Genera PDF y retorna como bytes"""
        if not REPORTLAB_AVAILABLE:
            st.error("❌ ReportLab no está instalado. Por favor instala con: pip install reportlab")
            return None

        try:
            # Crear documento en memoria
            buffer = BytesIO()

            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=ConfigPDFStreamlit.MARGIN,
                leftMargin=ConfigPDFStreamlit.MARGIN,
                topMargin=ConfigPDFStreamlit.MARGIN,
                bottomMargin=ConfigPDFStreamlit.MARGIN,
                title="Informe Ejecutivo - Supermercado NINO",
                author="Dashboard Científico",
                subject="Análisis de Rentabilidad"
            )

            # Construir PDF
            doc.build(self.elementos)

            buffer.seek(0)
            return buffer.getvalue()

        except Exception as e:
            st.error(f"❌ Error generando PDF: {e}")
            return None


# ==================================================================================
# FUNCIONES DE INTERFAZ STREAMLIT
# ==================================================================================

def mostrar_boton_descargar_pdf(label="📥 Descargar Informe PDF"):
    """Muestra botón para descargar PDF"""
    if st.button(label, key="descargar_pdf", use_container_width=True):
        return True
    return False


def generar_y_descargar_pdf(datos, titulo="Informe Ejecutivo"):
    """Genera PDF y lo hace disponible para descargar"""
    with st.spinner("⏳ Generando PDF..."):
        generador = GeneradorPDFStreamlit(datos, titulo)

        # Agregar contenido
        generador.agregar_portada()

        # Agregar KPIs si están disponibles
        if 'kpis' in st.session_state:
            generador.agregar_kpis(st.session_state['kpis'])

        # Generar bytes
        pdf_bytes = generador.generar_bytes()

        if pdf_bytes:
            # Crear nombre de archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Informe_NINO_{timestamp}.pdf"

            # Botón de descarga
            st.download_button(
                label="✅ Descargar PDF",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf",
                key="descarga_final"
            )

            st.success(f"✅ PDF generado: {filename}")
        else:
            st.error("❌ Error al generar el PDF")


# ==================================================================================
# EJEMPLO DE USO
# ==================================================================================

def ejemplo_uso():
    """Ejemplo de cómo usar el módulo"""

    # Inicializar sesión
    if 'kpis' not in st.session_state:
        st.session_state.kpis = {
            'Total de Tickets': '15,234',
            'Ventas Totales': '$2.345.678',
            'Rentabilidad': '22.5%',
            'Ticket Promedio': '$154.50'
        }

    st.title("Test PDF Generator")

    # Crear gráfico de ejemplo
    df_test = pd.DataFrame({
        'Mes': ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo'],
        'Ventas': [100, 120, 115, 140, 165]
    })

    fig_test = go.Figure(
        data=[go.Bar(x=df_test['Mes'], y=df_test['Ventas'])],
        layout=dict(
            title="Ventas Mensuales",
            xaxis_title="Mes",
            yaxis_title="Ventas ($)"
        )
    )

    # Mostrar controles
    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("Vista previa de contenido")

    with col2:
        if st.button("🔄 Generar PDF"):
            generador = GeneradorPDFStreamlit({}, "Informe Test")
            generador.agregar_portada()
            generador.agregar_kpis(st.session_state.kpis)
            generador.agregar_grafico(fig_test, "Gráfico Test")
            generador.agregar_tabla_datos(df_test, "Datos Test")

            pdf_bytes = generador.generar_bytes()
            if pdf_bytes:
                st.download_button(
                    label="📥 Descargar PDF",
                    data=pdf_bytes,
                    file_name="test_informe.pdf",
                    mime="application/pdf"
                )

    # Mostrar tabla
    st.plotly_chart(fig_test, use_container_width=True)
    st.dataframe(df_test)


if __name__ == "__main__":
    ejemplo_uso()

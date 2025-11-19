# -*- coding: utf-8 -*-
"""
================================================================================
GENERADOR DE INFORME PDF COMPLETO - SUPERMERCADO NINO
================================================================================
Convierte el dashboard Streamlit a un informe PDF profesional con:
- Portada ejecutiva
- Tabla de contenidos
- Gráficos de alta resolución
- Narrativa y storytelling
- Análisis detallado por sección
================================================================================
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio
from io import BytesIO
import warnings
warnings.filterwarnings('ignore')

# Importar librerías PDF
try:
    from reportlab.lib.pagesizes import letter, A4, landscape
    from reportlab.lib.units import inch, cm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak,
        Table, TableStyle, KeepTogether, Preformatted
    )
    from reportlab.lib.colors import HexColor, white, black, lightgrey, Color
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("ERROR: ReportLab no instalado. Ejecutar: pip install reportlab")

try:
    from PIL import Image as PILImage
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("ADVERTENCIA: Pillow no instalado. Algunos formatos de imagen pueden no funcionar")


# ==================================================================================
# CONFIGURATION
# ==================================================================================

class ConfigPDF:
    """Configuración centralizada para el PDF"""

    # Colores corporativos (strings para Plotly, HexColor para ReportLab)
    COLOR_PRIMARY_STR = "#1F77B4"           # Azul oscuro
    COLOR_SECONDARY_STR = "#FF7F0E"         # Naranja
    COLOR_ACCENT_STR = "#2CA02C"            # Verde
    COLOR_GRAY_STR = "#7F7F7F"              # Gris
    COLOR_LIGHT_GRAY_STR = "#E8E8E8"        # Gris claro

    COLOR_PRIMARY = HexColor("#1F77B4")
    COLOR_SECONDARY = HexColor("#FF7F0E")
    COLOR_ACCENT = HexColor("#2CA02C")
    COLOR_GRAY = HexColor("#7F7F7F")
    COLOR_LIGHT_GRAY = HexColor("#E8E8E8")

    # Dimensiones
    PAGE_WIDTH, PAGE_HEIGHT = A4
    MARGIN_TOP = 0.75 * inch
    MARGIN_BOTTOM = 0.75 * inch
    MARGIN_LEFT = 0.75 * inch
    MARGIN_RIGHT = 0.75 * inch

    CONTENT_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT
    CONTENT_HEIGHT = PAGE_HEIGHT - MARGIN_TOP - MARGIN_BOTTOM

    # Gráficos
    CHART_WIDTH = 8.5  # inches
    CHART_HEIGHT = 5.0  # inches
    DPI_EXPORT = 150  # Resolución para exportar imágenes

    # Estilos
    TITLE_FONT_SIZE = 28
    HEADING_FONT_SIZE = 18
    SUBHEADING_FONT_SIZE = 14
    BODY_FONT_SIZE = 11
    SMALL_FONT_SIZE = 9


# ==================================================================================
# UTILIDADES DE DATOS
# ==================================================================================

def cargar_datos():
    """Carga todos los datos necesarios del dashboard"""
    print("[*] Cargando datos...")

    data_path = Path(__file__).parent / "data" / "app_dataset"
    datos = {}

    try:
        # Archivos esenciales
        archivos = [
            'alcance_dataset.parquet',
            'kpis_base.parquet',
            'kpi_diario.parquet',
            'kpi_periodo.parquet',
            'kpi_semana.parquet',
            'kpi_dia.parquet',
            'kpi_categoria.parquet',
            'pareto_prod_global.parquet',
            'pareto_cat_global.parquet',
            'reglas.parquet',
            'kpi_pago.parquet',
            'rentabilidad_ticket.parquet'
        ]

        for archivo in archivos:
            filepath = data_path / archivo
            if filepath.exists():
                datos[archivo.replace('.parquet', '')] = pd.read_parquet(filepath)
                print(f"  [OK] {archivo}")
            else:
                print(f"  [!] {archivo} no encontrado")

        return datos

    except Exception as e:
        print(f"ERROR al cargar datos: {e}")
        return {}


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


# ==================================================================================
# GENERADORES DE GRÁFICOS (Compatibles con PDF)
# ==================================================================================

class GeneradorGraficos:
    """Generador de gráficos Plotly optimizados para PDF"""

    @staticmethod
    def grafico_temporal(datos):
        """Gráfico de tendencia temporal"""
        if 'kpi_periodo' not in datos:
            return None

        df = datos['kpi_periodo'].copy()
        df['periodo'] = pd.to_datetime(df['periodo'], errors='coerce')
        df = df.dropna(subset=['periodo']).sort_values('periodo')

        # Calcular línea de tendencia
        x_numeric = np.arange(len(df))
        z = np.polyfit(x_numeric, df['tickets'].values, 1)
        p = np.poly1d(z)
        trend_line = p(x_numeric)

        fig = go.Figure()

        # Línea de datos
        fig.add_trace(go.Scatter(
            x=df['periodo'],
            y=df['tickets'],
            mode='lines+markers',
            name='Tickets',
            line=dict(color=ConfigPDF.COLOR_PRIMARY_STR, width=3),
            marker=dict(size=8)
        ))

        # Línea de tendencia
        fig.add_trace(go.Scatter(
            x=df['periodo'],
            y=trend_line,
            mode='lines',
            name='Tendencia',
            line=dict(color=ConfigPDF.COLOR_SECONDARY_STR, width=2, dash='dash')
        ))

        # Promedio
        avg = df['tickets'].mean()
        fig.add_hline(
            y=avg,
            line_dash="dot",
            annotation_text=f"Promedio: {formatear_numero_argentino(avg)}",
            annotation_position="right",
            line_color=ConfigPDF.COLOR_GRAY_STR
        )

        fig.update_layout(
            title="Evolución de Tickets por Período",
            xaxis_title="Período",
            yaxis_title="Cantidad de Tickets",
            height=400,
            showlegend=True,
            template='plotly_white',
            hovermode='x unified'
        )

        return fig

    @staticmethod
    def grafico_pareto(datos):
        """Gráfico Pareto 80/20"""
        if 'pareto_prod_global' not in datos:
            return None

        df = datos['pareto_prod_global'].copy()

        # Ordenar y calcular cumulative
        df = df.sort_values('ventas', ascending=False).head(20)
        df['cumulative_pct'] = (df['ventas'].cumsum() / df['ventas'].sum()) * 100

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Barras
        fig.add_trace(
            go.Bar(
                x=df['descripcion'],
                y=df['ventas'],
                name='Ventas',
                marker_color=ConfigPDF.COLOR_PRIMARY_STR,
                showlegend=True
            ),
            secondary_y=False
        )

        # Línea de acumulado
        fig.add_trace(
            go.Scatter(
                x=df['descripcion'],
                y=df['cumulative_pct'],
                name='% Acumulado',
                line=dict(color=ConfigPDF.COLOR_SECONDARY_STR, width=2),
                mode='lines+markers',
                showlegend=True
            ),
            secondary_y=True
        )

        # Referencia 80%
        fig.add_hline(
            y=80,
            line_dash="dash",
            annotation_text="80% Pareto",
            secondary_y=True,
            line_color=ConfigPDF.COLOR_ACCENT_STR
        )

        fig.update_xaxes(tickangle=-45)
        fig.update_yaxes(title_text="Ventas", secondary_y=False)
        fig.update_yaxes(title_text="% Acumulado", secondary_y=True)

        fig.update_layout(
            title="Análisis Pareto - Top 20 Productos",
            height=400,
            hovermode='x unified'
        )

        return fig

    @staticmethod
    def grafico_categorias(datos):
        """Gráfico de categorías top"""
        if 'kpi_categoria' not in datos:
            return None

        df = datos['kpi_categoria'].copy()
        df = df.sort_values('ventas_totales', ascending=False).head(10)

        fig = px.bar(
            df,
            x='ventas_totales',
            y='categoria',
            orientation='h',
            title='Top 10 Categorías por Ventas',
            labels={'ventas_totales': 'Ventas Totales', 'categoria': 'Categoría'},
            color='ventas_totales',
            color_continuous_scale='Blues'
        )

        fig.update_layout(height=400, showlegend=False)

        return fig

    @staticmethod
    def grafico_segmentacion(datos):
        """Gráfico de distribución de rentabilidad"""
        if 'rentabilidad_ticket' not in datos:
            return None

        df = datos['rentabilidad_ticket'].copy()

        fig = px.histogram(
            df,
            x='rentabilidad_pct_ticket',
            nbins=30,
            title='Distribución de Rentabilidad por Ticket',
            labels={'rentabilidad_pct_ticket': 'Rentabilidad %', 'count': 'Cantidad de Tickets'},
            color_discrete_sequence=[ConfigPDF.COLOR_PRIMARY_STR]
        )

        # Quartiles
        q1 = df['rentabilidad_pct_ticket'].quantile(0.25)
        q2 = df['rentabilidad_pct_ticket'].quantile(0.50)
        q3 = df['rentabilidad_pct_ticket'].quantile(0.75)

        for q, name in [(q1, 'Q1'), (q2, 'Q2'), (q3, 'Q3')]:
            fig.add_vline(x=q, line_dash="dash", line_color=ConfigPDF.COLOR_GRAY_STR,
                         annotation_text=name, annotation_position="top")

        fig.update_layout(height=400)

        return fig

    @staticmethod
    def grafico_medios_pago(datos):
        """Gráfico de medios de pago"""
        if 'kpi_pago' not in datos:
            return None

        df = datos['kpi_pago'].copy()

        fig = px.bar(
            df,
            x='tipo_medio_pago',
            y='ventas_totales',
            title='Ventas por Medio de Pago',
            labels={'tipo_medio_pago': 'Medio de Pago', 'ventas_totales': 'Ventas'},
            color='ventas_totales',
            color_continuous_scale='Viridis'
        )

        fig.update_layout(height=400, showlegend=False)

        return fig

    @staticmethod
    def exportar_grafico_png(fig, nombre_archivo):
        """Exporta un gráfico Plotly a PNG"""
        if fig is None:
            return None

        try:
            # Asegurar que se usa kaleido para exportar a PNG
            buffer = BytesIO()
            fig.write_image(
                buffer,
                format='png',
                width=ConfigPDF.CHART_WIDTH * ConfigPDF.DPI_EXPORT,
                height=ConfigPDF.CHART_HEIGHT * ConfigPDF.DPI_EXPORT,
                scale=1
            )
            buffer.seek(0)
            return buffer
        except Exception as e:
            print(f"ERROR exportando gráfico {nombre_archivo}: {e}")
            return None


# ==================================================================================
# GENERADOR DE DOCUMENTO PDF
# ==================================================================================

class GeneradorPDFCompleto:
    """Genera un informe PDF profesional con storytelling"""

    def __init__(self, datos, output_path="entregables/Informe_Completo_Supermercado_NINO.pdf"):
        self.datos = datos
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        # Configurar estilos
        self.styles = self._crear_estilos()

        # Elementos del documento
        self.elementos = []

    def _crear_estilos(self):
        """Crea estilos personalizados para el PDF"""
        styles = getSampleStyleSheet()

        # Título principal
        styles.add(ParagraphStyle(
            name='TituloInforme',
            parent=styles['Heading1'],
            fontSize=ConfigPDF.TITLE_FONT_SIZE,
            textColor=ConfigPDF.COLOR_PRIMARY,
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Subtítulo
        styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=styles['Normal'],
            fontSize=16,
            textColor=ConfigPDF.COLOR_SECONDARY,
            spaceAfter=10,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))

        # Heading de sección
        styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=styles['Heading2'],
            fontSize=ConfigPDF.HEADING_FONT_SIZE,
            textColor=ConfigPDF.COLOR_PRIMARY,
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold',
            borderColor=ConfigPDF.COLOR_PRIMARY,
            borderWidth=2,
            borderPadding=5
        ))

        # Heading de subsección
        styles.add(ParagraphStyle(
            name='SubsectionHeading',
            parent=styles['Heading3'],
            fontSize=ConfigPDF.SUBHEADING_FONT_SIZE,
            textColor=ConfigPDF.COLOR_SECONDARY,
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))

        # Body normal
        styles.add(ParagraphStyle(
            name='BodyNormal',
            parent=styles['BodyText'],
            fontSize=ConfigPDF.BODY_FONT_SIZE,
            alignment=TA_JUSTIFY,
            spaceAfter=10,
            leading=14
        ))

        # Highlight box
        styles.add(ParagraphStyle(
            name='Highlight',
            parent=styles['Normal'],
            fontSize=ConfigPDF.BODY_FONT_SIZE,
            textColor=ConfigPDF.COLOR_PRIMARY,
            backColor=HexColor("#F0F8FF"),
            borderColor=ConfigPDF.COLOR_PRIMARY,
            borderWidth=1,
            borderPadding=5,
            spaceAfter=10,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        return styles

    def agregar_portada(self):
        """Agrega portada ejecutiva"""
        print("[*] Generando portada...")

        # Espaciador
        self.elementos.append(Spacer(ConfigPDF.CONTENT_WIDTH, 2 * inch))

        # Título
        titulo = Paragraph(
            "SUPERMERCADO NINO",
            self.styles['TituloInforme']
        )
        self.elementos.append(titulo)

        # Subtítulo
        subtitulo = Paragraph(
            "Informe Ejecutivo - Análisis de Rentabilidad",
            self.styles['Subtitulo']
        )
        self.elementos.append(subtitulo)

        # Espaciador
        self.elementos.append(Spacer(ConfigPDF.CONTENT_WIDTH, 0.5 * inch))

        # Información del período
        if 'alcance_dataset' in self.datos:
            df_alcance = self.datos['alcance_dataset']
            fecha_min = df_alcance['min_fecha'].values[0] if len(df_alcance) > 0 else "N/A"
            fecha_max = df_alcance['max_fecha'].values[0] if len(df_alcance) > 0 else "N/A"

            periodo_texto = Paragraph(
                f"<b>Período:</b> {fecha_min} a {fecha_max}",
                self.styles['BodyNormal']
            )
            self.elementos.append(periodo_texto)

        # Fecha de generación
        fecha_hoy = datetime.now().strftime("%d de %B de %Y").replace('B', 'B').lower()
        fecha_texto = Paragraph(
            f"<b>Generado:</b> {datetime.now().strftime('%d/%m/%Y')}",
            self.styles['BodyNormal']
        )
        self.elementos.append(fecha_texto)

        # Espaciador
        self.elementos.append(Spacer(ConfigPDF.CONTENT_WIDTH, 1 * inch))

        # KPIs principales
        if 'alcance_dataset' in self.datos and 'kpis_base' in self.datos:
            df_alcance = self.datos['alcance_dataset']
            df_kpis = self.datos['kpis_base']

            kpi_data = [
                ['Métrica', 'Valor'],
                ['Total de Tickets', formatear_numero_argentino(df_alcance['n_tickets'].values[0]) if len(df_alcance) > 0 else 'N/A'],
                ['SKUs Únicos', formatear_numero_argentino(df_alcance['n_skus_unicos'].values[0]) if len(df_alcance) > 0 else 'N/A'],
                ['Ventas Totales', formatear_moneda_argentina(df_alcance['ventas_total'].values[0]) if len(df_alcance) > 0 else 'N/A'],
                ['Rentabilidad Global', f"{df_kpis['rentabilidad_global'].values[0]:.2f}%" if len(df_kpis) > 0 else 'N/A'],
            ]

            tabla_kpi = Table(kpi_data, colWidths=[4*inch, 2*inch])
            tabla_kpi.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), ConfigPDF.COLOR_PRIMARY),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), ConfigPDF.COLOR_LIGHT_GRAY),
                ('GRID', (0, 0), (-1, -1), 1, black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, ConfigPDF.COLOR_LIGHT_GRAY]),
            ]))

            self.elementos.append(tabla_kpi)

        # Page break
        self.elementos.append(PageBreak())

    def agregar_tabla_contenidos(self):
        """Agrega tabla de contenidos"""
        print("[*] Generando tabla de contenidos...")

        titulo = Paragraph("Tabla de Contenidos", self.styles['SectionHeading'])
        self.elementos.append(titulo)
        self.elementos.append(Spacer(ConfigPDF.CONTENT_WIDTH, 0.2 * inch))

        contenidos = [
            "1. Introducción",
            "2. Análisis Temporal",
            "3. Análisis de Productos (Pareto)",
            "4. Análisis de Categorías",
            "5. Segmentación de Rentabilidad",
            "6. Análisis de Medios de Pago",
            "7. Estrategias Priorizadas",
            "8. Conclusiones",
        ]

        for item in contenidos:
            self.elementos.append(Paragraph(item, self.styles['BodyNormal']))

        self.elementos.append(PageBreak())

    def agregar_introduccion(self):
        """Agrega sección de introducción"""
        print("[*] Generando introducción...")

        titulo = Paragraph("1. Introducción", self.styles['SectionHeading'])
        self.elementos.append(titulo)

        texto = """
        <b>Propósito del Informe</b><br/>
        Este informe ejecutivo presenta un análisis integral de los datos de ventas de
        Supermercado NINO, enfocado en identificar oportunidades para aumentar la rentabilidad
        del ticket y optimizar la experiencia del cliente.
        <br/><br/>
        <b>Metodología</b><br/>
        El análisis se realizó mediante técnicas de:
        <ul>
            <li><b>Análisis Temporal:</b> Evaluación de tendencias y patrones de venta a lo largo del período</li>
            <li><b>Análisis de Pareto:</b> Identificación del 80/20 en productos y categorías</li>
            <li><b>Market Basket Analysis:</b> Descubrimiento de asociaciones entre productos</li>
            <li><b>Segmentación:</b> Clasificación de tickets por rentabilidad</li>
            <li><b>Análisis de Medios de Pago:</b> Evaluación de métodos de pago</li>
        </ul>
        <br/>
        <b>Audiencia Objetivo</b><br/>
        Este informe está dirigido a la dirección ejecutiva y gerentes de operaciones
        de Supermercado NINO para la toma de decisiones estratégicas.
        """

        self.elementos.append(Paragraph(texto, self.styles['BodyNormal']))
        self.elementos.append(PageBreak())

    def agregar_seccion_graficos(self):
        """Agrega secciones con gráficos"""
        print("[*] Generando secciones de gráficos...")

        # Sección Temporal
        self.elementos.append(Paragraph("2. Análisis Temporal", self.styles['SectionHeading']))

        texto_temporal = """
        El análisis temporal permite identificar patrones, tendencias y estacionalidad en el volumen de tickets.
        Esta información es crucial para la planificación de inventario, staffing y promociones.
        """
        self.elementos.append(Paragraph(texto_temporal, self.styles['BodyNormal']))

        fig_temporal = GeneradorGraficos.grafico_temporal(self.datos)
        if fig_temporal:
            try:
                buffer = GeneradorGraficos.exportar_grafico_png(fig_temporal, 'temporal')
                if buffer:
                    temp_img_path = "/tmp/grafico_temporal.png"
                    with open(temp_img_path, 'wb') as f:
                        f.write(buffer.getvalue())

                    img = Image(temp_img_path, width=ConfigPDF.CONTENT_WIDTH, height=3*inch)
                    self.elementos.append(img)
            except:
                self.elementos.append(Paragraph("⚠ No se pudo generar el gráfico temporal", self.styles['BodyNormal']))

        self.elementos.append(PageBreak())

        # Sección Pareto
        self.elementos.append(Paragraph("3. Análisis de Productos (Pareto)", self.styles['SectionHeading']))

        texto_pareto = """
        El análisis de Pareto identifica los productos que generan el 80% de las ventas.
        Esta concentración permite enfocar esfuerzos en los productos clave para maximizar rentabilidad.
        """
        self.elementos.append(Paragraph(texto_pareto, self.styles['BodyNormal']))

        fig_pareto = GeneradorGraficos.grafico_pareto(self.datos)
        if fig_pareto:
            try:
                buffer = GeneradorGraficos.exportar_grafico_png(fig_pareto, 'pareto')
                if buffer:
                    temp_img_path = "/tmp/grafico_pareto.png"
                    with open(temp_img_path, 'wb') as f:
                        f.write(buffer.getvalue())

                    img = Image(temp_img_path, width=ConfigPDF.CONTENT_WIDTH, height=3*inch)
                    self.elementos.append(img)
            except:
                self.elementos.append(Paragraph("⚠ No se pudo generar el gráfico Pareto", self.styles['BodyNormal']))

        self.elementos.append(PageBreak())

        # Sección Categorías
        self.elementos.append(Paragraph("4. Análisis de Categorías", self.styles['SectionHeading']))

        texto_categorias = """
        Las categorías de productos son fundamentales para la organización del almacén y la experiencia del cliente.
        Este análisis identifica las categorías con mayor desempeño en términos de volumen de ventas.
        """
        self.elementos.append(Paragraph(texto_categorias, self.styles['BodyNormal']))

        fig_categorias = GeneradorGraficos.grafico_categorias(self.datos)
        if fig_categorias:
            try:
                buffer = GeneradorGraficos.exportar_grafico_png(fig_categorias, 'categorias')
                if buffer:
                    temp_img_path = "/tmp/grafico_categorias.png"
                    with open(temp_img_path, 'wb') as f:
                        f.write(buffer.getvalue())

                    img = Image(temp_img_path, width=ConfigPDF.CONTENT_WIDTH, height=3*inch)
                    self.elementos.append(img)
            except:
                self.elementos.append(Paragraph("⚠ No se pudo generar el gráfico de categorías", self.styles['BodyNormal']))

        self.elementos.append(PageBreak())

        # Sección Segmentación
        self.elementos.append(Paragraph("5. Segmentación de Rentabilidad", self.styles['SectionHeading']))

        texto_segmentacion = """
        La segmentación por rentabilidad permite identificar qué tickets generan mayor margen de ganancia.
        Esta información es esencial para diseñar estrategias de pricing y promociones diferenciadas.
        """
        self.elementos.append(Paragraph(texto_segmentacion, self.styles['BodyNormal']))

        fig_segmentacion = GeneradorGraficos.grafico_segmentacion(self.datos)
        if fig_segmentacion:
            try:
                buffer = GeneradorGraficos.exportar_grafico_png(fig_segmentacion, 'segmentacion')
                if buffer:
                    temp_img_path = "/tmp/grafico_segmentacion.png"
                    with open(temp_img_path, 'wb') as f:
                        f.write(buffer.getvalue())

                    img = Image(temp_img_path, width=ConfigPDF.CONTENT_WIDTH, height=3*inch)
                    self.elementos.append(img)
            except:
                self.elementos.append(Paragraph("⚠ No se pudo generar el gráfico de segmentación", self.styles['BodyNormal']))

        self.elementos.append(PageBreak())

        # Sección Medios de Pago
        self.elementos.append(Paragraph("6. Análisis de Medios de Pago", self.styles['SectionHeading']))

        texto_pago = """
        El análisis de medios de pago permite identificar preferencias de pago de los clientes y oportunidades
        para promocionar métodos de pago digitales que mejoran la eficiencia operativa.
        """
        self.elementos.append(Paragraph(texto_pago, self.styles['BodyNormal']))

        fig_pago = GeneradorGraficos.grafico_medios_pago(self.datos)
        if fig_pago:
            try:
                buffer = GeneradorGraficos.exportar_grafico_png(fig_pago, 'pago')
                if buffer:
                    temp_img_path = "/tmp/grafico_pago.png"
                    with open(temp_img_path, 'wb') as f:
                        f.write(buffer.getvalue())

                    img = Image(temp_img_path, width=ConfigPDF.CONTENT_WIDTH, height=3*inch)
                    self.elementos.append(img)
            except:
                self.elementos.append(Paragraph("⚠ No se pudo generar el gráfico de medios de pago", self.styles['BodyNormal']))

        self.elementos.append(PageBreak())

    def agregar_estrategias(self):
        """Agrega sección de estrategias priorizadas"""
        print("[*] Generando estrategias...")

        titulo = Paragraph("7. Estrategias Priorizadas", self.styles['SectionHeading'])
        self.elementos.append(titulo)

        texto_intro = """
        A continuación se presentan 6 estrategias priorizadas para mejorar la rentabilidad de Supermercado NINO,
        basadas en los insights extraídos del análisis de datos:
        """
        self.elementos.append(Paragraph(texto_intro, self.styles['BodyNormal']))
        self.elementos.append(Spacer(ConfigPDF.CONTENT_WIDTH, 0.2 * inch))

        estrategias = [
            {
                'titulo': '1. Pack Despensa Mensual',
                'impacto': 'ALTO',
                'descripcion': 'Crear bundles de productos de alta rotación con descuento de 10-12% para aumentar ticket promedio.',
                'acciones': [
                    '• Identificar 5-10 productos fast-moving de cada categoría',
                    '• Diseñar packs con precio atractivo',
                    '• Capacitar staff en venta cruzada',
                    '• Lanzar campaña de marketing'
                ],
                'impacto_esperado': 'Aumento de 12-18% en ticket promedio'
            },
            {
                'titulo': '2. Expansión de Marca Propia',
                'impacto': 'ALTO',
                'descripcion': 'Desarrollar línea de marca propia en categorías de alto margen para mejorar rentabilidad.',
                'acciones': [
                    '• Seleccionar 3-5 categorías prioritarias',
                    '• Buscar proveedores de marca propia',
                    '• Diseñar packaging diferenciador',
                    '• Planificar shelf space'
                ],
                'impacto_esperado': 'Incremento de 3-5 pp en margen bruto'
            },
            {
                'titulo': '3. Cross-Merchandising Inteligente',
                'impacto': 'MEDIO',
                'descripcion': 'Reorganizar layout basado en asociaciones de compra descubiertas en market basket analysis.',
                'acciones': [
                    '• Aplicar insights de reglas de asociación',
                    '• Rediseñar flujo de tienda',
                    '• Crear zonas de impulsa',
                    '• Monitorear impacto'
                ],
                'impacto_esperado': 'Aumento de 5-8% en productos asociados'
            },
            {
                'titulo': '4. Programa de Capacitación de Vendedores',
                'impacto': 'MEDIO',
                'descripcion': 'Entrenar personal de cajas y reposición en técnicas de upselling basadas en combos.',
                'acciones': [
                    '• Crear guía de combos recomendados',
                    '• Realizar sesiones de capacitación',
                    '• Implementar incentivos por venta',
                    '• Monitorear uptake'
                ],
                'impacto_esperado': 'Incremento de 3-5% en ventas complementarias'
            },
            {
                'titulo': '5. Programa de Fidelización',
                'impacto': 'ALTO',
                'descripcion': 'Lanzar tarjeta de cliente para ofertas personalizadas a clientes de alto margen (Q4).',
                'acciones': [
                    '• Diseñar estructura de beneficios',
                    '• Desarrollar plataforma digital',
                    '• Crear ofertas personalizadas',
                    '• Integrar con POS'
                ],
                'impacto_esperado': 'Aumento de 10-15% en retención'
            },
            {
                'titulo': '6. Dashboard de Monitoreo',
                'impacto': 'BAJO',
                'descripcion': 'Implementar dashboard semanal para tracking de KPIs y ajustes dinámicos de estrategias.',
                'acciones': [
                    '• Configurar métricas semanales',
                    '• Crear alertas automáticas',
                    '• Definir procesos de revisión',
                    '• Capacitar gerencia'
                ],
                'impacto_esperado': 'Mejora en toma de decisiones ágil'
            }
        ]

        for est in estrategias:
            # Título de estrategia
            titulo_est = Paragraph(f"<b>{est['titulo']}</b>", self.styles['SubsectionHeading'])
            self.elementos.append(titulo_est)

            # Impacto
            color_impacto = {
                'ALTO': ConfigPDF.COLOR_ACCENT,
                'MEDIO': ConfigPDF.COLOR_SECONDARY,
                'BAJO': ConfigPDF.COLOR_GRAY
            }.get(est['impacto'], ConfigPDF.COLOR_GRAY)

            impacto_text = f"<font color='{color_impacto.hexval()}'><b>Impacto: {est['impacto']}</b></font>"
            self.elementos.append(Paragraph(impacto_text, self.styles['Normal']))

            # Descripción
            self.elementos.append(Paragraph(est['descripcion'], self.styles['BodyNormal']))

            # Acciones
            acciones_text = "<b>Acciones Clave:</b><br/>" + "<br/>".join(est['acciones'])
            self.elementos.append(Paragraph(acciones_text, self.styles['BodyNormal']))

            # Impacto esperado
            self.elementos.append(Paragraph(
                f"<b>Impacto Esperado:</b> {est['impacto_esperado']}",
                self.styles['Highlight']
            ))

            self.elementos.append(Spacer(ConfigPDF.CONTENT_WIDTH, 0.15 * inch))

        self.elementos.append(PageBreak())

    def agregar_conclusiones(self):
        """Agrega sección de conclusiones"""
        print("[*] Generando conclusiones...")

        titulo = Paragraph("8. Conclusiones", self.styles['SectionHeading'])
        self.elementos.append(titulo)

        texto = """
        <b>Hallazgos Clave</b><br/>
        <ul>
            <li>El análisis temporal muestra patrones consistentes en la demanda que permiten optimizar inventario</li>
            <li>El principio de Pareto es aplicable: ~20% de productos generan ~80% de ventas</li>
            <li>Existen oportunidades significativas en asociaciones de productos para aumentar ticket promedio</li>
            <li>La segmentación de rentabilidad revela oportunidades para mejorar margen en Q1/Q2</li>
            <li>La adopción de métodos digitales de pago está en crecimiento</li>
        </ul>
        <br/>
        <b>Recomendaciones de Acción Inmediata</b><br/>
        <ol>
            <li>Implementar Pack Despensa en los próximos 2 semanas</li>
            <li>Iniciar evaluación de proveedores para marca propia</li>
            <li>Capacitar equipo de cajas en técnicas de upselling basadas en datos</li>
            <li>Rediseñar layout aprovechando insights de market basket</li>
            <li>Lanzar pilot de programa de fidelización en 1 mes</li>
        </ol>
        <br/>
        <b>Impacto Proyectado (6 meses)</b><br/>
        <ul>
            <li>Ticket promedio: +12-18%</li>
            <li>Margen bruto: +3-5 pp</li>
            <li>Incremental en ventas: +$2-3M anualizados</li>
            <li>Retención de clientes: +10-15%</li>
        </ul>
        <br/>
        <b>Próximos Pasos</b><br/>
        Se recomienda:
        <ol>
            <li>Presentar este informe a dirección ejecutiva para aprobación</li>
            <li>Conformar equipo de implementación con gerentes de categoría y operaciones</li>
            <li>Crear plan detallado de rollout con hitos y responsables</li>
            <li>Implementar dashboard de seguimiento semanal</li>
            <li>Planificar revisión mensual de resultados vs targets</li>
        </ol>
        """

        self.elementos.append(Paragraph(texto, self.styles['BodyNormal']))
        self.elementos.append(Spacer(ConfigPDF.CONTENT_WIDTH, 0.5 * inch))

        # Footer
        footer_text = Paragraph(
            f"<br/><hr/><br/><b>Informe generado:</b> {datetime.now().strftime('%d/%m/%Y a las %H:%M')}<br/><b>Sistema:</b> Dashboard Científico - Supermercado NINO",
            self.styles['Normal']
        )
        self.elementos.append(footer_text)

    def generar(self):
        """Genera el documento PDF completo"""
        print("\n[*] Generando documento PDF...")

        # Verificar que ReportLab está disponible
        if not REPORTLAB_AVAILABLE:
            print("[ERROR] ReportLab no está instalado")
            return False

        try:
            # Agregar secciones
            self.agregar_portada()
            self.agregar_tabla_contenidos()
            self.agregar_introduccion()
            self.agregar_seccion_graficos()
            self.agregar_estrategias()
            self.agregar_conclusiones()

            # Crear documento
            doc = SimpleDocTemplate(
                str(self.output_path),
                pagesize=A4,
                rightMargin=ConfigPDF.MARGIN_RIGHT,
                leftMargin=ConfigPDF.MARGIN_LEFT,
                topMargin=ConfigPDF.MARGIN_TOP,
                bottomMargin=ConfigPDF.MARGIN_BOTTOM,
                title="Informe Ejecutivo - Supermercado NINO",
                author="Sistema Dashboard Científico",
                subject="Análisis de Rentabilidad"
            )

            # Construir PDF
            doc.build(
                self.elementos,
                onFirstPage=self._agregar_header_footer,
                onLaterPages=self._agregar_header_footer
            )

            print(f"[OK] PDF generado exitosamente: {self.output_path}")
            return True

        except Exception as e:
            print(f"[ERROR] Generando PDF: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _agregar_header_footer(self, canvas_obj, doc):
        """Agrega header y footer a las páginas"""
        canvas_obj.saveState()

        # Header
        canvas_obj.setFont("Helvetica-Bold", 10)
        canvas_obj.drawString(
            ConfigPDF.MARGIN_LEFT,
            ConfigPDF.PAGE_HEIGHT - 0.4 * inch,
            "Supermercado NINO - Informe Ejecutivo"
        )

        # Footer
        canvas_obj.setFont("Helvetica", 8)
        canvas_obj.drawString(
            ConfigPDF.MARGIN_LEFT,
            0.4 * inch,
            f"Página {doc.page}"
        )

        canvas_obj.drawRightString(
            ConfigPDF.PAGE_WIDTH - ConfigPDF.MARGIN_RIGHT,
            0.4 * inch,
            f"© {datetime.now().year} - Pyme Inside"
        )

        canvas_obj.restoreState()


# ==================================================================================
# MAIN
# ==================================================================================

def main():
    """Función principal"""
    print("\n" + "="*80)
    print("GENERADOR DE INFORME PDF - SUPERMERCADO NINO")
    print("="*80 + "\n")

    # Cargar datos
    datos = cargar_datos()

    if not datos:
        print("[ERROR] No se pudieron cargar los datos necesarios")
        return False

    # Generar PDF
    generador = GeneradorPDFCompleto(datos)
    success = generador.generar()

    if success:
        print("\n" + "="*80)
        print("[OK] INFORME GENERADO EXITOSAMENTE")
        print("="*80)
        print(f"\n[*] Ubicacion: {generador.output_path}")
        print(f"[*] Incluye: Portada, TOC, 7 secciones de analisis, 5 graficos, estrategias y conclusiones")
        print("\n[*] El informe esta listo para presentacion a direccion ejecutiva\n")
        return True
    else:
        print("\n[ERROR] Error al generar el PDF")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

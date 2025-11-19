# Generación de Informes PDF - Supermercado NINO

## Descripción

Este proyecto incluye dos soluciones completas para generar informes PDF profesionales a partir del Dashboard Científico de Supermercado NINO:

1. **Script Standalone** (`generar_informe_pdf_completo.py`) - Para generar PDFs desde línea de comandos
2. **Módulo Streamlit** (`pdf_generator_streamlit.py`) - Para integrar descarga de PDFs directamente en el dashboard

---

## Requisitos

### Dependencias principales
```bash
pip install -r requirements.txt
```

**Librerías necesarias:**
- `reportlab>=4.0.0` - Generación de documentos PDF
- `kaleido>=0.2.1` - Exportación de gráficos Plotly a imágenes
- `Pillow>=10.0.0` - Procesamiento de imágenes
- `plotly>=5.17.0` - Visualizaciones (ya incluido)
- `pandas>=2.0.0` - Manipulación de datos (ya incluido)

### Sistema operativo
- Funciona en Windows, macOS y Linux
- Requiere Python 3.7+

---

## OPCIÓN 1: Script Standalone

### Uso

```bash
python generar_informe_pdf_completo.py
```

### Salida

Genera un archivo PDF en:
```
entregables/Informe_Completo_Supermercado_NINO.pdf
```

### Contenido del PDF

El informe generado incluye:

#### **Portada Ejecutiva**
- Título: "SUPERMERCADO NINO"
- Subtítulo: "Informe Ejecutivo - Análisis de Rentabilidad"
- Período de análisis
- 4 KPIs principales en tabla formateada

#### **Tabla de Contenidos**
- 8 secciones principales con navegación

#### **1. Introducción**
- Propósito del informe
- Metodología de análisis
- Audiencia objetivo

#### **2. Análisis Temporal**
- Gráfico de evolución de tickets por período
- Línea de tendencia con pendiente
- Línea de promedio
- Análisis de estacionalidad

#### **3. Análisis de Productos (Pareto)**
- Gráfico Pareto 80/20
- Top 20 productos por ventas
- Línea de acumulado con referencia al 80%
- Insights sobre concentración de ventas

#### **4. Análisis de Categorías**
- Top 10 categorías por ventas
- Gráfico horizontal de barras
- Información de desempeño por categoría

#### **5. Segmentación de Rentabilidad**
- Histograma de distribución de rentabilidad
- Líneas de cuartiles (Q1, Q2, Q3)
- Análisis de variación de margen

#### **6. Análisis de Medios de Pago**
- Gráfico de ventas por método de pago
- Breakdown entre efectivo y digital
- Insights sobre penetración de pagos digitales

#### **7. Estrategias Priorizadas** (6 iniciativas)
1. **Pack Despensa Mensual** (IMPACTO ALTO)
   - Bundle de productos fast-moving con descuento 10-12%
   - Esperado: +12-18% en ticket promedio

2. **Expansión de Marca Propia** (IMPACTO ALTO)
   - Desarrollo de línea de marca propia
   - Esperado: +3-5 pp en margen bruto

3. **Cross-Merchandising Inteligente** (IMPACTO MEDIO)
   - Reorganización de layout basado en market basket
   - Esperado: +5-8% en productos asociados

4. **Programa de Capacitación de Vendedores** (IMPACTO MEDIO)
   - Entrenamiento en upselling
   - Esperado: +3-5% en ventas complementarias

5. **Programa de Fidelización** (IMPACTO ALTO)
   - Tarjeta de cliente con ofertas personalizadas
   - Esperado: +10-15% en retención

6. **Dashboard de Monitoreo** (IMPACTO BAJO)
   - Tracking semanal de KPIs
   - Mejora en toma de decisiones ágil

#### **8. Conclusiones**
- Hallazgos clave
- Recomendaciones de acción inmediata
- Impacto proyectado a 6 meses
- Próximos pasos

### Características de Formato

- **Tamaño de página:** A4 (210x297mm)
- **Márgenes:** 0.75" en todos los lados
- **Colores:**
  - Primario (títulos): #1F77B4 (Azul Plotly)
  - Secundario (acentos): #FF7F0E (Naranja Plotly)
  - Accent (énfasis): #2CA02C (Verde Plotly)

- **Tipografía:**
  - Títulos: Helvetica-Bold 28pt
  - Headings: Helvetica-Bold 18pt
  - Subheadings: Helvetica-Bold 14pt
  - Body: Helvetica 11pt

- **Headers/Footers:**
  - Header izquierda: "Supermercado NINO - Informe Ejecutivo"
  - Footer izquierda: Número de página
  - Footer derecha: "© 2024 - Pyme Inside"

- **Tablas:** Colores alternados (blanco/gris claro) con bordes

### Archivos requeridos

El script espera encontrar los siguientes archivos en `data/app_dataset/`:

```
data/app_dataset/
├── alcance_dataset.parquet          (metadatos de período)
├── kpis_base.parquet                (KPIs globales)
├── kpi_diario.parquet               (agregados diarios)
├── kpi_periodo.parquet              (tendencia mensual)
├── kpi_semana.parquet               (agregados semanales)
├── kpi_dia.parquet                  (breakdowndia de semana)
├── kpi_categoria.parquet            (performance categorías)
├── pareto_prod_global.parquet       (análisis Pareto productos)
├── pareto_cat_global.parquet        (análisis Pareto categorías)
├── reglas.parquet                   (market basket rules)
├── rentabilidad_ticket.parquet      (distribución rentabilidad)
└── (opcional) kpi_pago.parquet      (medios de pago)
```

---

## OPCIÓN 2: Integración en Streamlit

### Uso básico

```python
from pdf_generator_streamlit import GeneradorPDFStreamlit, generar_y_descargar_pdf

# En tu dashboard Streamlit
import streamlit as st

# Botón para generar y descargar PDF
if st.button("Descargar Informe PDF"):
    generar_y_descargar_pdf(datos, titulo="Informe Ejecutivo")
```

### Clases disponibles

#### **GeneradorPDFStreamlit**

```python
generador = GeneradorPDFStreamlit(datos, titulo="Mi Informe")

# Agregar secciones
generador.agregar_portada()
generador.agregar_kpis({
    'Total Tickets': '15,234',
    'Ventas': '$2.3M',
    'Rentabilidad': '22.5%'
})
generador.agregar_grafico(fig, "Título del gráfico")
generador.agregar_tabla_datos(df, "Tabla de Datos")
generador.agregar_texto("Párrafo de texto")
generador.agregar_salto_pagina()

# Generar PDF en bytes
pdf_bytes = generador.generar_bytes()

# Ofrecer descarga
st.download_button(
    label="Descargar PDF",
    data=pdf_bytes,
    file_name="informe.pdf",
    mime="application/pdf"
)
```

#### **Funciones Helper**

```python
# Exportar una figura Plotly a PNG en memoria
buffer = exportar_figura_plotly(fig)

# Formatear números al estilo argentino
numero_formateado = formatear_numero_argentino(1234567, decimales=2)
# Resultado: "1.234.567,00"

# Formatear moneda argentina
moneda_formateada = formatear_moneda_argentina(1234567.89)
# Resultado: "$1.234.567,89"
```

### Ejemplo completo de integración

```python
import streamlit as st
import plotly.express as px
import pandas as pd
from pdf_generator_streamlit import GeneradorPDFStreamlit

st.title("Dashboard con Descarga de PDF")

# Cargar datos
df = pd.DataFrame({
    'Mes': ['Enero', 'Febrero', 'Marzo'],
    'Ventas': [100, 120, 115]
})

# Mostrar gráfico
fig = px.line(df, x='Mes', y='Ventas', title="Tendencia de Ventas")
st.plotly_chart(fig)

# Botón de descarga
if st.button("Descargar como PDF"):
    generador = GeneradorPDFStreamlit({})

    # Agregar contenido
    generador.agregar_portada()
    generador.agregar_kpis({'Total': 'dato1', 'Promedio': 'dato2'})
    generador.agregar_grafico(fig, "Gráfico de Ventas")
    generador.agregar_tabla_datos(df, "Datos Crudos")

    # Generar y descargar
    pdf_bytes = generador.generar_bytes()

    st.download_button(
        label="PDF Listo para Descargar",
        data=pdf_bytes,
        file_name="informe_ventas.pdf",
        mime="application/pdf"
    )
    st.success("PDF generado exitosamente!")
```

---

## Solución de Problemas

### Error: "kaleido package not found"

**Solución:**
```bash
pip install -U kaleido
```

### Error: "ReportLab no está instalado"

**Solución:**
```bash
pip install reportlab
```

### Error: "Color format invalid"

**Causa:** Incompatibilidad entre formatos de color
**Solución:** El código ya está corregido para usar strings hex (#RRGGBB)

### El PDF no incluye gráficos

**Causa:** kaleido no puede exportar a PNG
**Solución:**
- Asegurar que kaleido está instalado
- En Linux: `apt-get install libffi-dev`
- En macOS: `brew install libffi`

### Tamaño de archivo muy grande

**Solución:** Reducir resolución DPI en `ConfigPDF.DPI_EXPORT` (default: 150)

---

## Personalización

### Cambiar colores corporativos

En `generar_informe_pdf_completo.py` o `pdf_generator_streamlit.py`:

```python
class ConfigPDF:
    COLOR_PRIMARY_STR = "#TU_COLOR_HEX"       # Títulos
    COLOR_SECONDARY_STR = "#TU_COLOR_HEX"     # Acentos
    COLOR_ACCENT_STR = "#TU_COLOR_HEX"        # Énfasis
```

### Cambiar tamaño de página

```python
from reportlab.lib.pagesizes import letter, A3, A4

class ConfigPDF:
    PAGE_WIDTH, PAGE_HEIGHT = A3  # Cambiar de A4 a A3
```

### Agregar nuevas secciones

```python
def agregar_seccion_personalizada(self):
    """Agrega sección personalizada"""
    titulo = Paragraph("Mi Sección", self.styles['SectionHeading'])
    self.elementos.append(titulo)

    contenido = Paragraph("Texto del contenido", self.styles['BodyNormal'])
    self.elementos.append(contenido)

    self.elementos.append(PageBreak())
```

---

## Especificaciones técnicas

### Arquitectura

```
generar_informe_pdf_completo.py
├── ConfigPDF (configuración centralizada)
├── GeneradorGraficos (gráficos Plotly)
├── GeneradorPDFCompleto (orquestador)
│   ├── agregar_portada()
│   ├── agregar_tabla_contenidos()
│   ├── agregar_seccion_*()
│   └── generar()
└── main() (punto de entrada)

pdf_generator_streamlit.py
├── ConfigPDFStreamlit (config para Streamlit)
├── GeneradorPDFStreamlit (generación dinámica)
├── Utilidades (exportar_figura, formatear_*)
└── funciones_interfaz (mostrar_boton, generar_y_descargar)
```

### Performance

- Generación del PDF: ~30-60 segundos (sin exportar gráficos a imágenes)
- Tamaño del PDF: ~15KB (solo texto) a ~2MB (con gráficos)
- Memoria: ~50-100MB durante generación

### Compatibilidad

- Python: 3.7+
- Sistemas operativos: Windows, macOS, Linux
- Navegadores: Todos (para descarga en Streamlit)

---

## Próximas mejoras sugeridas

1. **Gráficos interactivos en PDF:** Usar embedPDF con contenido JS
2. **Análisis comparativo:** Agregar comparación período anterior
3. **Alertas automáticas:** Detectar anomalías y marcarlas en rojo
4. **Templates personalizados:** Permitir cambiar layout por cliente
5. **Firma digital:** Agregar firma electrónica del ejecutivo
6. **Enviable por email:** Generar y enviar automáticamente

---

## Soporte

Para reportar bugs o solicitar mejoras, crear un issue en GitHub.

**Autor:** Dashboard Científico - Supermercado NINO
**Última actualización:** Noviembre 2024
**Estado:** Producción

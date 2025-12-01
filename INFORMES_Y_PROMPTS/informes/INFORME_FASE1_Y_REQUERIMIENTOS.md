# Informe de Validación Fase 1 y Requerimientos Técnicos (Fase 2)

## 1. Validación del Estado Actual (Fase 1)

Tras la revisión exhaustiva del repositorio y el cruce con la **"Auditoría Final - Cumplimiento de Objetivos Fase I"**, confirmamos que el desarrollo actual **CUMPLE y SUPERA** los objetivos funcionales planteados para los primeros 3 meses.

### ✅ Logros Consolidados
El "Dashboard Científico" desarrollado en **Streamlit** es una herramienta robusta que ya resuelve la visualización de inteligencia de negocios:
*   **Cobertura Total de KPIs:** Ventas, Tickets, Ticket Promedio, UPT, Paretos y Mapas de Calor están implementados y validados.
*   **Analítica Avanzada:** Se han entregado módulos que exceden el requerimiento básico, como **Clustering de Clientes** (segmentación por poder de compra) y **Market Basket Analysis** (reglas de asociación para combos).
*   **Arquitectura de Datos:** Existe un pipeline ETL (`scripts/pipeline/main_pipeline.py`) bien estructurado que limpia, normaliza y enriquece los datos, generando una "Fuente Única de Verdad" en archivos Parquet.
*   **Reportabilidad:** El sistema de generación de PDFs (`generar_informe_pdf_completo.py`) permite la distribución ejecutiva de la información.

**Conclusión:** La herramienta visual está lista. La discrepancia sobre "Power BI" en los documentos originales ha sido superada por una solución en Python/Streamlit que ofrece mayor flexibilidad para los modelos de Machine Learning implementados.

---

## 2. El "Eslabón Perdido": Automatización Real (Conexión a BD)

Aunque el dashboard funciona perfectamente, la "Auditoría" identifica correctamente que **depende de un archivo CSV estático** (`SERIE_COMPROBANTES_COMPLETOS.csv`).
Para cumplir con la promesa de "Carga Automática" (Semana 4-5 del plan) y eliminar la intervención manual, es imperativo conectar el pipeline directamente al motor de base de datos del sistema **Caribe POS**.

### 📋 Requerimientos para el Área de IT / Proveedor de POS
Necesitamos solicitar una reunión técnica para configurar la extracción automática.

**Preguntas Clave para el Administrador:**
1.  **Motor de Base de Datos:** ¿Sobre qué motor corre Caribe POS?
    *   *Hipótesis:* Comúnmente usan **SQL Server**, **Firebird** o archivos **DBF/FoxPro**. Necesitamos confirmación exacta.
2.  **Credenciales de Lectura:**
    *   Necesitamos un usuario (ej: `dashboard_reader`) con permisos de `SELECT` (solo lectura).
    *   IP del servidor y puerto (ej: 1433 para SQL, 3050 para Firebird).
3.  **Diccionario de Tablas:**
    *   Identificar las tablas que contienen la información del CSV actual:
        *   `ENCABEZADO_TICKET` (Fecha, Hora, Nro, Total).
        *   `DETALLE_TICKET` (Producto, Cantidad, Precio, **Costo**).
        *   `MAESTRO_PRODUCTOS` (Rubro, Marca, Proveedor).

**Objetivo:** Reemplazar la lectura del CSV en `etl_basico.py` por una consulta SQL directa (`pd.read_sql`), programada para correr cada noche automáticamente.

---

## 3. Nuevo Módulo: Sistema de Costeo de Producción

El chat con el cliente solicita explícitamente un *"documento para armar un sistema de costeo de la parte de rotisería, panadería..."*.
**Diagnóstico:** El sistema actual calcula la rentabilidad comercial (Precio Venta - Costo Compra/Lista). Esto sirve para reventa (latas, paquetes), pero **NO sirve para elaboración propia** (Rotisería), donde el costo depende de una **Receta**.

### 🛠️ Requerimientos para Ingeniería de Menú (Fase 2)
Para construir este módulo, necesitamos que el negocio "digitalice" su cocina.

**Información a Solicitar (Plantillas para el Cliente):**
1.  **Definición de "Productos Terminados":** Listado de todo lo que se produce (ej: 1kg Pan Francés, 1 Docena Empanadas).
2.  **Recetas Estándar (Escandallos):**
    *   Para cada producto, listar **Ingredientes** y **Cantidades Netas**.
    *   Ejemplo: *Para 10kg de Pan:* 10kg Harina, 6L Agua, 200g Levadura, 200g Sal.
3.  **Factores de Merma:**
    *   ¿Cuánto se pierde al limpiar la carne o cocinar el pollo? (El costo debe calcularse sobre el peso bruto, no el neto).
4.  **Costos de Insumos:**
    *   Vincular los ingredientes con el precio de compra actual en el sistema.

**Entregable Propuesto:** Un nuevo script de ETL que cruce *Ventas de Rotisería* vs *Recetas* para calcular el **Costo Teórico** y el **Margen Real** de producción, detectando desvíos por desperdicio o robo.

---

## 4. Hoja de Ruta Inmediata

1.  **Validar Dashboard:** Dar por cerrada la Fase 1 visual con la aprobación del dashboard actual.
2.  **Reunión IT (Prioridad Alta):** Conseguir los accesos a Caribe POS para automatizar el ETL.
3.  **Tarea para el Cliente:** Entregar las planillas de Excel para el relevamiento de recetas de Rotisería/Panadería.

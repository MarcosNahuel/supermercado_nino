# Informe de Mejoras y Correcciones: Dashboard Analítico NINO

**Fecha:** 1 de Diciembre, 2025
**Objetivo:** Guía de implementación para el Agente CLI basada en el testeo de usuario y revisión de código.

## 1. 🚨 Correcciones Críticas (Bugs)

### 1.1. Tab "Análisis de Costos (Prototipo)" Sin Datos
**Problema:**
La pestaña muestra el mensaje *"⚠️ No hay datos de productos disponibles para análisis de rentabilidad"*.
Al revisar el código en `dashboard_cientifico.py`, se intenta acceder a `data.get('kpi_productos')` (Línea 2322), pero este dataset **NO se está cargando** en la función `load_all_data` (Líneas 254-277).

**Solución Técnica Sugerida:**
1.  Verificar si `kpi_productos` debería ser el archivo `pareto_prod_global.parquet` (cargado como `pareto_prod`).
2.  **Opción A:** Si es el mismo archivo, asignar `data['kpi_productos'] = data['pareto_prod']` al final de `load_all_data`.
3.  **Opción B:** Si es un archivo distinto, agregarlo a la lista `required_files` en `load_all_data`.
4.  **Opción C (Fallback):** Si es un prototipo simulado, generar un DataFrame sintético en el momento si la clave no existe, para permitir visualizar la demo.

## 2. 🎨 Mejoras de UI/UX (Estética y Navegación)

El usuario mencionó *"no veo que scrolles"*, lo que implica que el contenido importante puede estar quedando oculto "below the fold" o que la navegación vertical es tediosa.

### 2.1. Optimización del Layout Vertical
**Problema:** Páginas muy largas que requieren mucho scroll.
**Acciones:**
*   Utilizar `st.expander` para secciones secundarias (ej. tablas de datos crudos).
*   Dividir métricas en filas más compactas.
*   Evaluar mover filtros globales al Sidebar (`st.sidebar`) para ganar espacio vertical.

### 2.2. Estética "Premium" (CSS Personalizado)
**Problema:** Diseño estándar de Streamlit.
**Acciones:**
*   Implementar tarjetas (Cards) para las métricas principales con sombras suaves (`box-shadow`) y bordes redondeados.
*   Mejorar el contraste de los títulos de las pestañas.
*   **Código CSS sugerido para inyectar:**
    ```css
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
    ```

## 3. 🚀 Mejoras Funcionales

### 3.1. Interactividad en Gráficos
*   Asegurar que todos los gráficos de Plotly tengan `hovermode='x unified'` para facilitar la lectura de valores al pasar el mouse (ya implementado en algunos, estandarizar en todos).

### 3.2. Feedback de Carga
*   Agregar `st.spinner` o mensajes de estado al cambiar entre pestañas pesadas (como Market Basket) para que el usuario sepa que la app está procesando.

---

## Plan de Ejecución Recomendado

1.  **Inmediato:** Resolver el bug de `kpi_productos` en `dashboard_cientifico.py` para habilitar la pestaña de Costos.
2.  **Corto Plazo:** Inyectar el CSS de "Tarjetas" para mejorar la primera impresión visual.
3.  **Corto Plazo:** Revisar el layout de la pestaña "Resumen Ejecutivo" para reducir la altura.

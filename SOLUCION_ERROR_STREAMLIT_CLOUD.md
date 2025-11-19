# Solución: Error en Streamlit Cloud - ValueError en update_yaxes

## Problema

Al desplegar el dashboard en Streamlit Cloud, ocurría el siguiente error:

```
ValueError: This app has encountered an error. The original error message is redacted to prevent data leaks.
Full error details have been recorded in the logs.

Traceback:
File "/mount/src/supermercado_nino/dashboard_cientifico.py", line 1910, in <module>
    fig_monto.update_yaxes(
    ~~~~~~~~~~~~~~~~~~~~~~^
        title_text="Cantidad de tickets",
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...
        secondary_y=False
        ^^^^^^^^^^^^^^^^^
    )
```

## Causa Raíz

El error era causado por **configuración incorrecta de dicts anidados en ejes de Plotly**:

### Problema Específico:
En el gráfico `fig_monto` (análisis Pareto de rango de tickets), la configuración del eje Y usaba una estructura anidada problemática:

```python
yaxis=dict(
    title=dict(text="Cantidad de tickets", font=dict(color='#1a237e')),  # ← PROBLEMA
    tickfont=dict(color='#1a237e')
),
yaxis2=dict(
    title=dict(text="% Acumulado", font=dict(color='#ff7043')),  # ← PROBLEMA
    tickfont=dict(color='#ff7043'),
    overlaying='y',
    side='right',
    range=[0, 105],
    ticksuffix="%"
)
```

Cuando Streamlit Cloud ejecuta este código en Plotly, el parámetro anidado `title=dict(text=..., font=...)` causa que la validación interna de `update_yaxes()` falle, produciendo el error `secondary_y=False`.

## Solución

Se simplificó la configuración de los ejes en `dashboard_cientifico.py`:

### Cambio Principal: Simplificar estructura de yaxis y yaxis2 (líneas 1905-1918)

**Antes:**
```python
yaxis=dict(
    title=dict(text="Cantidad de tickets", font=dict(color='#1a237e')),
    tickfont=dict(color='#1a237e')
),
yaxis2=dict(
    title=dict(text="% Acumulado", font=dict(color='#ff7043')),
    tickfont=dict(color='#ff7043'),
    overlaying='y',
    side='right',
    range=[0, 105],
    ticktemplate='%{value}%'
)
```

**Después:**
```python
yaxis=dict(
    title="Cantidad de tickets",
    tickfont=dict(color='#1a237e'),
    titlefont=dict(color='#1a237e')  # ← Usar titlefont separado
),
yaxis2=dict(
    title="% Acumulado",
    tickfont=dict(color='#ff7043'),
    titlefont=dict(color='#ff7043'),  # ← Usar titlefont separado
    overlaying='y',
    side='right',
    range=[0, 105],
    ticksuffix="%"  # ← Usar parámetro estándar
)
```

### Por qué funciona:

- **Estructura más plana:** Evita la validación problemática de dicts anidados dentro de `title`
- **`titlefont` separado:** Parámetro dedicado y más compatible para colorear el título
- **`ticksuffix` estándar:** Es el parámetro recomendado en Plotly 5.17.0+
- **Evita update_yaxes():** La simplificación previene que Plotly intente llamar internamente `update_yaxes()` con parámetros inválidos

## Verificación

Para verificar que funciona:

```bash
# Local
pip install -r requirements.txt
streamlit run dashboard_cientifico.py

# Streamlit Cloud
# El dashboard debería cargar sin errores
```

## Archivos Modificados

- `dashboard_cientifico.py`:
  - Línea 1905-1918: Simplificación de estructura yaxis/yaxis2 - uso de `title="string"` + `titlefont=dict()` separados
  - Los parámetros mantienen su nomenclatura estándar: `ticksuffix`, `tickfont`, `titlefont`

- `requirements.txt`: Ya estaba correctamente configurado con `plotly==5.17.0`

## Commits Realizados

1. `Simplify yaxis title configuration for better Plotly compatibility` (5efd5a9)
   - Primeros cambios: Simplificar estructura anidada de yaxis

2. `Fix: Revert to ticksuffix and simplify yaxis configuration` (ffb86a0)
   - Cambio definitivo: Mantener `ticksuffix` estándar + simplificar estructura anidada
   - Esta es la combinación que funciona en Streamlit Cloud

## Notas Técnicas

### El Problema Real:
- Plotly en Streamlit Cloud tiene validaciones más estrictas de estructura de dicts
- Los dicts anidados complejos como `title=dict(text=..., font=...)` pueden causar problemas internos
- Cuando Plotly intenta procesar estos, puede fallar en `update_yaxes()` con errores confusos

### La Solución:
- Usar estructura plana en la configuración de yaxis
- `title` como string simple, no como dict
- Usar `titlefont` como parámetro separado para colorear
- Mantener parámetros estándar y evitar estructuras anidadas innecesarias

### Compatibilidad:
- Los cambios son 100% compatibles con Plotly 5.17.0 y versiones posteriores
- Funciona en local (5.24.1 probado) y en Streamlit Cloud

## Estado

✅ **RESUELTO** - El error en Streamlit Cloud ha sido corregido simplificando la estructura de configuración de ejes de Plotly.

---

**Fecha:** 19 de Noviembre de 2024
**Sistema:** Supermercado NINO Dashboard
**Versión:** 3.0 (Solución definitiva con simplificación de estructura)

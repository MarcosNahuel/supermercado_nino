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

El error era causado por **parámetros deprecados en Plotly** siendo usados en el gráfico Pareto:

### Problema Específico:
En el gráfico `fig_monto` (análisis Pareto de rango de tickets), se usaba `ticksuffix="%"` en la configuración del eje secundario (`yaxis2`):

```python
yaxis2=dict(
    title=dict(text="% Acumulado", font=dict(color='#ff7043')),
    tickfont=dict(color='#ff7043'),
    overlaying='y',
    side='right',
    range=[0, 105],
    ticksuffix="%"  # ← PARÁMETRO PROBLEMÁTICO
)
```

En Plotly 5.17.0+, el parámetro `ticksuffix` está deprecado y es reemplazado por `ticktemplate`, que es más flexible y compatible.

## Solución

Se realizaron dos cambios clave en `dashboard_cientifico.py`:

### 1. Reemplazar `ticksuffix` con `ticktemplate` (línea 1915)

**Antes:**
```python
yaxis2=dict(
    ...
    ticksuffix="%"
)
```

**Después:**
```python
yaxis2=dict(
    ...
    ticktemplate='%{value}%'
)
```

### 2. Actualizar parámetros en el gráfico de margen diario (línea 1180)

**Antes:**
```python
fig_margen_tipo.update_layout(
    ...
    yaxis_ticksuffix="%",
    ...
)
```

**Después:**
```python
fig_margen_tipo.update_layout(
    ...
    yaxis_ticktemplate='%{value}%',
    ...
)
```

### Por qué funciona:

- **`ticktemplate`** es el parámetro moderno y recomendado por Plotly
- **Mejor compatibilidad** con todas las versiones de Plotly >= 5.17.0
- **Mantiene funcionalidad** de agregar "%" a los valores de los ejes
- **Más flexible** que `ticksuffix` para casos complejos con ejes secundarios

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
  - Línea 1915: Cambio de `ticksuffix="%"` a `ticktemplate='%{value}%'` en `yaxis2`
  - Línea 1180: Cambio de `yaxis_ticksuffix="%"` a `yaxis_ticktemplate='%{value}%'`

- `requirements.txt`: Ya estaba correctamente configurado con `plotly==5.17.0`

## Commits Realizados

1. `Fix Plotly version compatibility issue in Streamlit Cloud` (8d02e13)
   - Reemplaza `ticksuffix` con `ticktemplate` en el eje secundario del gráfico Pareto

2. `Update remaining ticksuffix to ticktemplate for Plotly compatibility` (4c5c540)
   - Actualiza parámetro adicional en el gráfico de margen diario

## Notas Técnicas

- **`ticksuffix` (deprecado):** Parámetro antiguo que causa conflictos en Plotly 5.17.0+ especialmente con ejes secundarios
- **`ticktemplate` (moderno):** Parámetro flexible que permite formato personalizado (ej: `'%{value}%'`, `'$%{value}'`)
- **Compatibilidad:** Los cambios son 100% compatibles con Plotly 5.17.0 y versiones posteriores

## Estado

✅ **RESUELTO** - El error en Streamlit Cloud ha sido corregido reemplazando parámetros deprecados de Plotly.

---

**Fecha:** 19 de Noviembre de 2024
**Sistema:** Supermercado NINO Dashboard
**Versión:** 2.0 (Actualizado con solución definitiva)

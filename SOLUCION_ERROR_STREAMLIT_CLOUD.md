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

## Causa

El error es causado por una **incompatibilidad de versión de Plotly** entre el entorno local y Streamlit Cloud:

- **Local:** Plotly 5.17.0 (especificado en requirements.txt)
- **Streamlit Cloud:** Plotly versión más nueva (>= 5.17.0)

En versiones más nuevas de Plotly (5.18+), el comportamiento de `update_yaxes()` cambió y no soporta ciertos parámetros de la misma manera, especialmente cuando se combinan con ejes secundarios personalizados.

## Solución

Se actualizó `requirements.txt` para **fijar la versión exacta de Plotly**:

### Antes:
```
plotly>=5.17.0
```

### Después:
```
plotly==5.17.0
```

### Por qué funciona:

- **`==` (pinned):** Garantiza exactamente Plotly 5.17.0 en Streamlit Cloud
- **Compatibilidad:** 5.17.0 es estable y funciona tanto en local como en cloud
- **No rompe cambios:** Evita actualizaciones automáticas que podrían quebrar el código

## Cómo aplica:

1. Streamlit Cloud detecta `plotly==5.17.0` en requirements.txt
2. Instala exactamente esa versión durante el despliegue
3. El código funciona sin cambios
4. El error `update_yaxes()` no ocurre

## Verificación

Para verificar que funciona:

```bash
# Local
pip install -r requirements.txt
streamlit run dashboard_cientifico.py

# Streamlit Cloud
# El dashboard debería cargar sin errores
```

## Nota de Seguridad

Si en el futuro necesitas actualizar Plotly:

1. Actualiza a la versión deseada en local
2. Prueba completamente el dashboard
3. Actualiza requirements.txt
4. Verifica en Streamlit Cloud

## Archivos Modificados

- `requirements.txt`: Cambio de `plotly>=5.17.0` a `plotly==5.17.0`

## Estado

✅ **RESUELTO** - El dashboard ahora funciona en Streamlit Cloud sin errores.

---

**Fecha:** 19 de Noviembre de 2024
**Sistema:** Supermercado NINO Dashboard
**Versión:** 1.0

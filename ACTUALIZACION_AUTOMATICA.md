# Actualización Automática de Métricas

Este documento explica cómo actualizar automáticamente todas las métricas del dashboard cuando actualizas el archivo CSV central.

## 📋 Flujo de Actualización

Cuando actualizas `data/raw/SERIE_COMPROBANTES_COMPLETOS.csv` (por ejemplo, cambios en medios de pago, nuevas transacciones, etc.), necesitas regenerar todos los datos procesados para que el dashboard refleje los cambios.

## 🚀 Uso Rápido

### Opción 1: Usando el script de Python (Recomendado)

```bash
python actualizar_metricas.py
```

### Opción 2: Usando el script .bat (Windows - Doble clic)

Simplemente haz doble clic en:
```
actualizar_metricas.bat
```

## 🔧 Qué hace el script automáticamente

El script ejecuta 3 pasos en secuencia:

### 1️⃣ Pipeline de Procesamiento de Datos
- Lee `SERIE_COMPROBANTES_COMPLETOS.csv`
- Ejecuta ETL (limpieza y enriquecimiento)
- Calcula KPIs (incluyendo medios de pago)
- Genera Market Basket Analysis
- Calcula análisis de Pareto
- Ejecuta clustering de tickets
- Genera pronósticos semanales
- **Duración estimada:** 1-2 horas (dependiendo del volumen de datos)

### 2️⃣ Copia de Archivos Procesados
- Copia automáticamente todos los archivos .parquet de `data/processed/` a `data/app_dataset/`
- Copia archivos de predicciones de `data/predictivos/` a `data/app_dataset/`
- **Duración estimada:** < 1 minuto

### 3️⃣ Entrenamiento de Modelos ML
- Entrena modelos de predicción de tickets
- Ejecuta simuladores de estrategias (combos, marca propia, cross-merchandising, etc.)
- Genera estimaciones de ROI
- Guarda resultados en `data/ml_results/`
- **Duración estimada:** 10-20 segundos

## 📊 Archivos que se actualizan

Los siguientes archivos se regeneran con datos actualizados:

### KPIs y Métricas
- `kpi_medio_pago.parquet` ⭐ (contiene cambios de medios de pago)
- `kpi_categoria.parquet`
- `kpi_dia.parquet`
- `kpi_tipo_dia.parquet`

### Análisis Avanzado
- `tickets.parquet` (todos los tickets procesados)
- `detalle_lineas.parquet` (líneas de detalle)
- `reglas.parquet` (reglas de asociación Market Basket)
- `combos_recomendados.parquet` (combos sugeridos)

### Pareto
- `pareto_categoria.parquet`
- `pareto_producto.parquet`

### Clustering y Predicciones
- `clusters_tickets.parquet`
- `ventas_semanales_categoria.parquet`
- `prediccion_ventas_semanal.parquet`

### Modelos ML
- `strategy_roi_summary.parquet`
- `strategy_roi_details.json`

## ✅ Ver los Cambios en el Dashboard

Una vez que el script termine:

1. **Si el dashboard ya está corriendo:**
   - Ve al navegador donde está abierto (`http://localhost:8501`)
   - Presiona la tecla `R` o `F5` para recargar
   - Los nuevos datos se cargarán automáticamente

2. **Si el dashboard NO está corriendo:**
   ```bash
   streamlit run final/streamlit_app/dashboard_cientifico.py
   ```

## ⏱️ Tiempo Total Estimado

- **Datos pequeños** (< 1M registros): 15-30 minutos
- **Datos medianos** (1-3M registros): 1-1.5 horas ⭐ (tu caso actual)
- **Datos grandes** (> 3M registros): 2+ horas

## 🔍 Verificación de Cambios

Para verificar que los cambios de medios de pago se aplicaron correctamente:

1. Abre el dashboard
2. Ve a la sección de **KPIs por Medio de Pago**
3. Verifica que los valores reflejen tus cambios recientes

## 🛠️ Proceso Manual (Si prefieres ejecutar paso por paso)

Si necesitas más control, puedes ejecutar cada paso manualmente:

```bash
# Paso 1: Procesar datos
python -m scripts.pipeline.main_pipeline

# Paso 2: Copiar archivos (PowerShell)
Copy-Item -Path "data\processed\*.parquet" -Destination "data\app_dataset\" -Force

# Paso 3: Entrenar modelos ML
python scripts/train_ml_models.py

# Paso 4: Iniciar/recargar dashboard
streamlit run final/streamlit_app/dashboard_cientifico.py
```

## 🐛 Solución de Problemas

### Error: "No module named 'src'"
**Solución:** Ejecuta desde la raíz del proyecto
```bash
cd "d:\OneDrive\GitHub\supermercado_nino definitivo claude"
python actualizar_metricas.py
```

### Error: "File not found: SERIE_COMPROBANTES_COMPLETOS.csv"
**Solución:** Verifica que el archivo existe en `data/raw/`
```bash
ls data/raw/SERIE_COMPROBANTES_COMPLETOS.csv
```

### El dashboard no muestra los cambios
**Solución:** Fuerza la recarga completa
1. En el navegador, presiona `Ctrl + Shift + R` (Windows) o `Cmd + Shift + R` (Mac)
2. O reinicia el servidor Streamlit (Ctrl+C y vuelve a ejecutar)

## 📝 Logs y Debugging

El script muestra el progreso en tiempo real. Si algo falla:

1. Lee el mensaje de error cuidadosamente
2. Verifica que todos los archivos CSV estén en `data/raw/`
3. Verifica que tienes espacio en disco suficiente
4. Verifica que no hay otros procesos usando los archivos

## 🔄 Frecuencia de Actualización Recomendada

- **Cambios en medios de pago:** Inmediatamente después de actualizar el CSV
- **Nuevas transacciones diarias:** Semanal o mensual
- **Cambios en catálogo de productos:** Cuando sea necesario

## 📞 Soporte

Si encuentras problemas:
1. Verifica los logs del script
2. Asegúrate de tener todas las dependencias instaladas (`pip install -r requirements.txt`)
3. Contacta al equipo de desarrollo en contacto@pymeinside.com

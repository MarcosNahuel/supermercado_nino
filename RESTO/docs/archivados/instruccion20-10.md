# Instrucciones para Mejoras en el Código e Informes del Proyecto Analytics Supermercado NINO

## Objetivo
Optimizar los informes y análisis del proyecto actual, incluyendo modelos predictivos, sin usar datos personales de clientes. Se enfocará en:
1. Modularizar el pipeline para mantenimiento eficiente.
2. Incorporar feriados junto con fines de semana en análisis temporales.
3. Calcular y estandarizar KPIs clave.
4. Añadir modelos predictivos sobre ventas e inventario.
5. Documentar todas las salidas.

---

## 1. Estructura Modular del Pipeline

### Objetivo:
Dividir `pipeline_estrategias.py` en scripts modulares.

### Sugerido:
- `/src/data_prep/etl_basico.py` → Carga, limpieza y estandarización de datos.
- `/src/features/kpis_basicos.py` → KPIs por ticket, día, semana, mes.
- `/src/features/market_basket.py` → Reglas Apriori + combos sugeridos.
- `/src/features/clustering_tickets.py` → Clustering de tickets (KMeans).
- `/src/features/pareto_margen.py` → Análisis ABC de productos y categorías.
- `/src/features/predictivos_ventas.py` → Modelos ARIMA o Prophet para ventas por categoría.
- `/src/utils/load_data.py` → Carga de feriados y funciones de fechas especiales.
- `main_pipeline.py` → Orquestador de todos los pasos.

---

## 2. Incorporación de Feriados a los KPIs Temporales

### Archivo fuente:
`D:\OneDrive\GitHub\supermercado_nino definitivo claude\data\raw\FERIADOS_2024_2025.csv`

### Formato esperado:
```csv
fecha,descripcion
2024-12-25,Navidad
2025-01-01,Año Nuevo
...```

### Instrucciones:
1. Cargar CSV con `parse_dates=['fecha']`.
2. En `etl_basico.py`, crear columna `tipo_dia`:
```python
df['es_fin_de_semana'] = df['fecha'].dt.dayofweek >= 5
df['es_feriado'] = df['fecha'].isin(feriados['fecha'])
df['tipo_dia'] = np.select([
    df['es_feriado'], df['es_fin_de_semana']
], ['FERIADO', 'FDS'], default='HABIL')
```
3. Agregar esta variable a las agregaciones por fecha y categoría.

---

## 3. Estandarización de KPIs y Agregaciones

### KPIs base:
- `ticket_promedio = ventas_totales / tickets`
- `upt = unidades_totales / tickets`
- `margen_pct = margen_total / ventas_totales`

### Dimensiones:
- Día, semana, mes, tipo_dia (HABIL/FDS/FERIADO), medio de pago, categoría

### Guardar en:
```bash
/data/processed/kpi_dia.parquet
/data/processed/kpi_tipo_dia.parquet
/data/processed/kpi_categoria.parquet
```

---

## 4. Modelos Predictivos (sin datos de cliente)

### Objetivo:
Pronosticar demanda por categoría usando modelos clásicos de series de tiempo.

### Datos necesarios:
- Ventas semanales por categoría (`ventas_semanales_categoria.parquet`)

### Métodos sugeridos:
- `ARIMA` (para series estables)
- `Prophet` (para manejo de feriados y estacionalidad)

### Instrucciones:
1. Para cada categoría top 10 por volumen, construir una serie semanal.
2. Entrenar modelo (ej. ARIMA(p,d,q) con selección por AIC).
3. Incluir feriados como exógenas si se usa Prophet.
4. Generar predicción para 4–8 semanas siguientes.
5. Guardar salidas en:
```bash
/data/predictivos/prediccion_ventas_semanal.parquet
```
6. Agregar visualización por categoría (últimas semanas + forecast).

---

## 5. Validación de Datos e Informes

### Script `validacion_informes.py`:
- Validar que suma mensual = total anual.
- Validar rango lógico de ticket promedio ($25k–$30k).
- Verificar que FDS y feriados estén bien categorizados.

### Documento `DOCUMENTACION_ANALISIS.md`:
- Explicación de KPIs y predicciones.
- Glosario de campos y tipos de día.
- Supuestos y fuentes de entrada/salida.

---

## Notas Finales
- Los modelos predictivos no incluyen clustering ni comportamiento de cliente.
- Automatizaciones y alertas se verán en una fase futura.
- Esta estructura permitirá integrar dashboards e informes estratégicos fácilmente.

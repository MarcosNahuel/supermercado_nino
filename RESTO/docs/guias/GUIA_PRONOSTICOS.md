# Guía de Pronósticos de Ventas - Supermercado NINO

## Introducción

Este documento explica en términos simples cómo funciona el sistema de pronósticos de ventas semanales y cómo interpretar sus resultados, diseñado para personas **sin conocimientos técnicos**.

---

## ¿Por qué hacer pronósticos?

Los pronósticos de ventas nos ayudan a:

1. **Planificar inventario**: Saber cuánto stock ordenar para evitar faltantes o exceso
2. **Asignar recursos**: Programar personal adecuadamente para los días esperados de alta demanda
3. **Evaluar campañas**: Comparar ventas reales vs. esperadas para medir el impacto de promociones
4. **Tomar decisiones**: Anticipar problemas y oportunidades con datos, no intuición

---

## ¿Cómo funciona nuestro modelo?

### Método: Promedio Móvil con Tendencia

Usamos un método **simple y transparente** que cualquier gerente puede entender y verificar:

#### 1. Promedio Móvil (Base)

Calculamos el **promedio de ventas de las últimas 8 semanas** (~2 meses).

**¿Por qué 8 semanas?**
- 8 semanas capturan patrones recientes sin ser demasiado sensibles a picos aislados
- Representa ~2 meses de comportamiento del consumidor
- Es fácil de recordar y comunicar

**Ejemplo:**
```
Semana 1: 1,000 unidades
Semana 2: 1,100 unidades
Semana 3: 950 unidades
Semana 4: 1,050 unidades
Semana 5: 1,200 unidades
Semana 6: 1,150 unidades
Semana 7: 1,100 unidades
Semana 8: 1,050 unidades

Promedio = (1000 + 1100 + 950 + 1050 + 1200 + 1150 + 1100 + 1050) / 8
         = 1,075 unidades/semana
```

#### 2. Tendencia (Ajuste)

Identificamos si las ventas están **creciendo o decreciendo** en el tiempo.

La tendencia se mide como el **cambio promedio por semana**.

**Ejemplo:**
- Si cada semana vendemos ~20 unidades más que la anterior → Tendencia: +20 unid/sem
- Si cada semana vendemos ~15 unidades menos → Tendencia: -15 unid/sem
- Si las ventas son estables → Tendencia: ±0 unid/sem

#### 3. Pronóstico Final

Combinamos el promedio base con la tendencia acumulada:

```
Pronóstico Semana N = Promedio Base + (Tendencia × N)
```

**Ejemplo continuando del anterior:**
- Promedio base: 1,075 unidades/semana
- Tendencia: +20 unidades/semana

**Pronósticos:**
- Semana 1: 1,075 + (20 × 1) = **1,095 unidades**
- Semana 2: 1,075 + (20 × 2) = **1,115 unidades**
- Semana 3: 1,075 + (20 × 3) = **1,135 unidades**
- Semana 4: 1,075 + (20 × 4) = **1,155 unidades**

---

## Intervalos de Confianza

### ¿Qué son?

Un rango donde esperamos que caigan las ventas reales con **80% de probabilidad**.

### ¿Por qué 80%?

- 80% es un balance entre confianza y utilidad práctica
- Significa que 8 de cada 10 veces, las ventas reales estarán dentro del rango
- Un intervalo muy amplio (95%, 99%) sería demasiado conservador
- Un intervalo muy estrecho (50%) sería arriesgado

### ¿Cómo se calcula?

Basado en la **variabilidad histórica** (desviación estándar) de las ventas:

```
Límite Inferior = Pronóstico - 1.28 × Desviación Estándar × Factor Horizonte
Límite Superior = Pronóstico + 1.28 × Desviación Estándar × Factor Horizonte
```

**Nota:** El factor de horizonte hace que el intervalo se amplíe para semanas más lejanas (mayor incertidumbre).

### Ejemplo Visual

```
Pronóstico Semana 1: 1,095 unidades (rango: 900 - 1,290)
Pronóstico Semana 4: 1,155 unidades (rango: 850 - 1,460)
```

Observa que el rango de la semana 4 es **más amplio** porque predecir el futuro lejano es más incierto.

---

## Interpretación Práctica

### Caso de Estudio: Categoría "Lacteos"

**Datos del modelo:**
- Promedio base: 5,000 litros/semana
- Tendencia: +50 litros/semana
- Desviación estándar: 400 litros

**Pronósticos generados:**

| Semana | Pronóstico Central | Límite Inferior (80%) | Límite Superior (80%) |
|--------|--------------------|-----------------------|-----------------------|
| 1      | 5,050 litros       | 4,500 litros          | 5,600 litros          |
| 2      | 5,100 litros       | 4,450 litros          | 5,750 litros          |
| 3      | 5,150 litros       | 4,400 litros          | 5,900 litros          |
| 4      | 5,200 litros       | 4,350 litros          | 6,050 litros          |

**¿Qué nos dice esto?**

1. **Crecimiento Sostenido**: Las ventas de lácteos están creciendo ~50 litros por semana
2. **Pronóstico Próxima Semana**: Esperamos vender 5,050 litros (probablemente entre 4,500-5,600)
3. **Planificación de Inventario**:
   - Escenario conservador: Ordenar 4,500 litros
   - Escenario normal: Ordenar 5,050 litros
   - Escenario optimista: Ordenar 5,600 litros
4. **Incertidumbre Creciente**: A 4 semanas, el rango es ±850 litros (vs. ±550 la semana 1)

---

## Preguntas Frecuentes

### 1. ¿Por qué no usar modelos más complejos como ARIMA?

**Respuesta corta:** ARIMA es una "caja negra" difícil de explicar y auditar.

**Respuesta larga:**

| Aspecto | Promedio Móvil + Tendencia | ARIMA |
|---------|----------------------------|-------|
| **Interpretabilidad** | "Promedio últimas 8 semanas + crecimiento de 20 unid/sem" | "Modelo ARIMA(1,1,2) con parámetros autorregresivos..." |
| **Auditabilidad** | Calculas a mano con Excel | Requiere software estadístico especializado |
| **Explicación a gerentes** | ✅ Fácil en 2 minutos | ❌ Requiere curso de estadística |
| **Precisión (series cortas)** | Similar | Similar (ARIMA no mejora significativamente) |
| **Mantenimiento** | Cualquiera entiende el código | Solo especialistas pueden modificarlo |

Para series de tiempo cortas (<2 años), **ARIMA no ofrece ventajas prácticas** y añade complejidad innecesaria.

### 2. ¿Qué tan precisos son los pronósticos?

**Depende del horizonte:**

- **Semana 1-2**: Muy precisos (error típico ~10-15%)
- **Semana 3-4**: Precisos (error típico ~15-20%)
- **Semana 5-8**: Menos precisos pero útiles (error típico ~20-30%)

**Factores que afectan la precisión:**
- Estabilidad de la demanda (productos estables → pronósticos mejores)
- Eventos especiales (feriados, promociones)
- Cambios bruscos en el mercado

### 3. ¿Qué hacer cuando las ventas reales quedan fuera del rango?

**Es normal que ocurra el 20% de las veces** (recordar que es intervalo del 80%).

**Si ocurre ocasionalmente:**
- Analizar causas (¿hubo promoción? ¿faltante de stock? ¿clima?)
- Documentar aprendizajes
- Considerar ajustar parámetros si persiste

**Si ocurre frecuentemente:**
- Revisar ventana del promedio móvil (¿8 semanas es adecuado?)
- Buscar factores externos no capturados (estacionalidad, competencia)
- Considerar segmentar más (ej: pronosticar por categoría Y tienda)

### 4. ¿Cada cuánto se actualizan los pronósticos?

**Recomendación:** Semanalmente

Cada semana nueva:
1. Se incorpora la venta real de la última semana
2. Se recalcula el promedio móvil de 8 semanas
3. Se actualiza la tendencia
4. Se generan nuevos pronósticos

Esto garantiza que el modelo siempre usa los datos más recientes.

### 5. ¿Puedo cambiar la ventana de 8 semanas?

Sí. Edita el parámetro `ventana_promedio` en `main_pipeline.py`:

```python
generate_forecasts(
    ventas_df,
    output_dir,
    ventana_promedio=12  # Cambiar a 12 semanas (~3 meses)
)
```

**Ventanas más cortas (4-6 semanas):**
- ✅ Reaccionan más rápido a cambios
- ❌ Más sensibles a picos aislados

**Ventanas más largas (12-16 semanas):**
- ✅ Más estables y suavizadas
- ❌ Lentas para detectar nuevas tendencias

---

## Uso en la Toma de Decisiones

### Ejemplo 1: Planificación de Compras

**Situación:**
- Pronóstico próxima semana: 500 unidades (rango: 400-600)
- Stock actual: 250 unidades

**Decisión:**
- **Conservadora**: Ordenar 150 unidades (total 400)
- **Normal**: Ordenar 250 unidades (total 500)
- **Optimista**: Ordenar 350 unidades (total 600)

### Ejemplo 2: Evaluación de Campaña

**Situación:**
- Pronóstico semana de campaña: 1,000 unidades (rango: 850-1,150)
- Ventas reales durante campaña: 1,350 unidades

**Análisis:**
- **Impacto neto**: +350 unidades (+35% sobre pronóstico base)
- **Conclusión**: La campaña fue exitosa (ventas superaron límite superior)
- **ROI**: Calcular costo de campaña vs. ventas incrementales

### Ejemplo 3: Asignación de Personal

**Situación:**
- Pronóstico tickets próxima semana: 8,000 (rango: 7,200-8,800)
- Capacidad por cajero: 200 tickets/día

**Decisión:**
- **Mínimo**: 7,200 tickets ÷ 200 = 36 cajeros-día (ej: 6 cajeros × 6 días)
- **Óptimo**: 8,000 tickets ÷ 200 = 40 cajeros-día
- **Máximo**: 8,800 tickets ÷ 200 = 44 cajeros-día

Programar 40 cajeros-día con 4 adicionales en pool flexible.

---

## Limitaciones del Modelo

### Lo que el modelo NO puede predecir:

1. **Eventos imprevistos**: Cortes de luz, pandemias, desastres naturales
2. **Cambios drásticos de mercado**: Nueva competencia cercana, crisis económica
3. **Promociones extraordinarias**: Descuentos masivos nunca antes vistos
4. **Estacionalidad compleja**: Si vendes juguetes, Navidad requiere modelo especial

### Mitigación:

- Usar juicio humano junto con pronósticos
- Ajustar manualmente en situaciones especiales
- Monitorear desviaciones y aprender de errores
- Complementar con análisis cualitativo

---

## Glosario de Términos

- **Promedio Móvil**: Promedio de las últimas N observaciones (8 semanas en nuestro caso)
- **Tendencia**: Cambio promedio por período (ej: +20 unidades/semana)
- **Desviación Estándar**: Medida de cuánto varían las ventas alrededor del promedio
- **Intervalo de Confianza**: Rango donde esperamos que caigan las ventas reales
- **Horizonte de Pronóstico**: Cuánto tiempo hacia el futuro estamos prediciendo
- **Pronóstico Central**: El valor más probable (línea central en gráficos)
- **Límites Inferior/Superior**: Bordes del intervalo de confianza (banda sombreada)

---

## Recursos Adicionales

- **Código fuente**: `src/features/predictivos_ventas_simple.py`
- **Pipeline de ejecución**: `main_pipeline.py` (línea 86-87)
- **Visualización**: Dashboard Streamlit, Tab "Pronósticos"
- **Datos generados**: `data/predictivos/prediccion_ventas_semanal.parquet`
- **Metadata de modelos**: `data/predictivos/prediccion_ventas_semanal_modelos.parquet`

---

## Contacto para Soporte

Si tienes dudas sobre cómo interpretar un pronóstico o necesitas ajustar parámetros:

- Email: contacto@pymeinside.com
- Documentación técnica: Ver README.md y código fuente con comentarios extensos

---

**Última actualización:** Octubre 2025
**Versión del modelo:** 2.0 (Promedio Móvil + Tendencia)

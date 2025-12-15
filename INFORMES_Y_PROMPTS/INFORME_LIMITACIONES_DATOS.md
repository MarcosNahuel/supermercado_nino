# Informe de Limitaciones de Datos - Supermercado NINO

## Resumen Ejecutivo

Este documento detalla las limitaciones actuales del dataset disponible y las oportunidades que se desbloquearían al incorporar datos adicionales. El objetivo es guiar decisiones de inversión en sistemas de captura de datos.

---

## 1. Limitaciones Actuales

### 1.1 Ausencia de ID de Cliente Único

**Estado actual:** Los tickets no tienen un identificador de cliente asociado.

**Impacto:**
- No podemos medir **retención de clientes** (cuántos vuelven)
- No podemos calcular **Customer Lifetime Value (CLV)** - valor del cliente en el tiempo
- No podemos hacer **análisis RFM** (Recencia, Frecuencia, Monto)
- No podemos identificar clientes de alto valor individualmente
- No podemos personalizar promociones por cliente
- No podemos medir efectividad de programas de fidelización

**Análisis que se desbloquean con ID de cliente:**
| Análisis | Valor para el negocio |
|----------|----------------------|
| RFM Segmentation | Identificar clientes en riesgo de abandono |
| Cohorte Analysis | Medir retención por mes de primer compra |
| Customer Journey | Entender evolución de compra del cliente |
| Churn Prediction | Predecir qué clientes van a abandonar |
| CLV Calculation | Priorizar clientes por valor futuro |
| Personalización | Ofertas 1:1 basadas en historial |

**Solución recomendada:**
- Implementar programa de fidelización (tarjeta física o app)
- Registrar DNI o teléfono en cada transacción
- Inversión estimada: Sistema de fidelización básico

---

### 1.2 Ausencia de Datos de Inventario

**Estado actual:** No hay información de stock, quiebres ni merma.

**Impacto:**
- No podemos medir **quiebres de stock** (ventas perdidas)
- No podemos calcular **rotación de inventario** por producto
- No podemos implementar **"Hora NINO"** (descuentos por vencimiento)
- No podemos optimizar niveles de stock
- No podemos medir merma ni desperdicios

**Análisis que se desbloquean con datos de inventario:**
| Análisis | Valor para el negocio |
|----------|----------------------|
| Stock Optimization | Reducir capital inmovilizado |
| Quiebre Detection | Recuperar ventas perdidas (estimado 3-5%) |
| Merma Analysis | Identificar categorías con mayor pérdida |
| Rotación por SKU | Priorizar productos de alta rotación |
| Alertas de Vencimiento | Reducir desperdicios con "Hora NINO" |
| Reposición Automática | Pedidos basados en demanda real |

**Solución recomendada:**
- Integrar sistema de inventario con POS
- Registrar movimientos de stock en tiempo real
- Implementar sistema de alertas de vencimiento

---

### 1.3 Ausencia de Costos Reales por Producto

**Estado actual:** Solo tenemos % de margen aproximado por categoría, no costo real por SKU.

**Impacto:**
- El margen calculado es una **aproximación**, no el real
- No podemos hacer análisis de **contribución por producto**
- No podemos identificar productos con **margen negativo**
- No podemos simular impacto de cambios de precio con precisión
- No podemos negociar con proveedores basados en datos

**Análisis que se desbloquean con costos reales:**
| Análisis | Valor para el negocio |
|----------|----------------------|
| Margen Real por SKU | Identificar productos que pierden dinero |
| Pricing Optimization | Ajustar precios para maximizar margen |
| Negociación Proveedores | Argumentar con datos precisos |
| Simulación What-If | Modelar escenarios de precio-costo |
| Descuentos Inteligentes | Saber cuánto descuento es sostenible |

**Solución recomendada:**
- Integrar lista de precios de compra del sistema contable
- Actualizar costos cada vez que llega mercadería
- Considerar costos logísticos por categoría

---

### 1.4 Datos de Marca Incompletos

**Estado actual:** 99% de productos figuran como "SIN MARCA" (productos a granel/peso).

**Impacto:**
- No podemos hacer análisis de **participación por marca**
- No podemos identificar **marcas más rentables**
- No podemos comparar **marca propia vs. terceros**
- Limitación para análisis de surtido

**Nota:** Esta limitación es estructural del tipo de negocio (carnicería, verdulería, panadería tienen productos a granel).

---

## 2. Datos Disponibles y Bien Aprovechados

A pesar de las limitaciones, el dataset actual permite análisis valiosos:

| Dato Disponible | Análisis Habilitado | Estado |
|-----------------|---------------------|--------|
| Fecha/hora de ticket | Estacionalidad, patrones temporales | Implementado |
| Monto por ticket | Segmentación por valor, Tribu Premium | Implementado |
| Items por ticket | UPT, análisis de canasta | Implementado |
| Categoría de producto | Pareto, mix de categorías | Implementado |
| Medio de pago | Análisis de pagos, oportunidades bancarias | Implementado |
| Emisor de tarjeta | Priorización de acuerdos bancarios | Implementado |
| Productos por ticket | Market Basket Analysis, combos | Implementado |
| Margen aproximado | Rentabilidad por ticket/categoría | Implementado |
| Feriados marcados | Efecto de feriados en ventas | Implementado |

---

## 3. Roadmap de Mejora de Datos

### Fase 1: Quick Wins (1-3 meses)
- [ ] Implementar registro de DNI/teléfono en caja (voluntario)
- [ ] Crear tarjeta de fidelización básica
- [ ] Integrar lista de costos por categoría

### Fase 2: Infraestructura (3-6 meses)
- [ ] Integrar sistema de inventario con POS
- [ ] Implementar alertas de stock bajo
- [ ] Desarrollar app de fidelización móvil

### Fase 3: Optimización (6-12 meses)
- [ ] Implementar costos reales por SKU
- [ ] Sistema de predicción de demanda automatizado
- [ ] Dashboard de alertas en tiempo real

---

## 4. Estimación de Valor Desbloqueado

| Mejora de Datos | Análisis Nuevo | Impacto Estimado |
|-----------------|----------------|------------------|
| ID de Cliente | Retención, CLV | +5-10% en ventas a clientes fieles |
| Datos de Stock | Reducir quiebres | Recuperar 3-5% ventas perdidas |
| Costos Reales | Pricing óptimo | +1-3% margen bruto |
| Alertas Merma | "Hora NINO" | Reducir 20-30% desperdicios |

**Impacto total estimado:** Potencial de +10-15% en rentabilidad

---

## 5. Conclusión

El dataset actual permite análisis sofisticados de comportamiento de compra, pero la **ausencia de ID de cliente** es la limitación más crítica. Un programa de fidelización simple desbloquearía análisis de alto valor como:

1. **Predicción de abandono** - Identificar clientes en riesgo
2. **Personalización** - Ofertas basadas en historial
3. **Medición de impacto** - Saber si las estrategias funcionan

**Recomendación principal:** Priorizar implementación de sistema de fidelización con identificación de cliente.

---

*Documento generado: Diciembre 2025*
*Dashboard Científico - Supermercado NINO*

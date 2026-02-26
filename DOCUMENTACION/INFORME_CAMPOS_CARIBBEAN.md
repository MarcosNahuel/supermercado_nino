# INFORME DE REQUERIMIENTOS TÉCNICOS
## Sistema Caribbean Desktop - Supermercado Don Nino

**Fecha:** 16 de Enero 2026
**Destinatario:** Técnico de Sistema Caribbean
**Solicitante:** Supermercado Don Nino / PymeInside
**Prioridad:** ALTA

---

## RESUMEN EJECUTIVO

El supermercado ha implementado un sistema de Business Intelligence que analiza los datos de ventas para optimizar la rentabilidad. Para potenciar este sistema y habilitar funcionalidades críticas de **fidelización de clientes**, se requiere que Caribbean habilite/exporte campos adicionales en los reportes de ventas.

---

## 1. CAMPOS ACTUALES (YA DISPONIBLES)

Actualmente recibimos los siguientes campos en la exportación de comprobantes:

| # | Campo | Descripción | Estado |
|---|-------|-------------|--------|
| 1 | Fecha | Fecha de la transacción | ✅ OK |
| 2 | Comprobante | Número de ticket/factura | ✅ OK |
| 3 | Código | Código interno del producto | ✅ OK |
| 4 | Código barras | EAN del producto | ✅ OK |
| 5 | Marca | Marca del producto | ✅ OK |
| 6 | Departamento | Categoría/rubro | ✅ OK |
| 7 | Nombre | Descripción del producto | ✅ OK |
| 8 | Cantidad | Unidades vendidas | ✅ OK |
| 9 | Importe | Monto total de la línea | ✅ OK |
| 10 | Unitario | Precio unitario | ✅ OK |
| 11 | TIPO FACTURA | Tipo de comprobante (FA, FB, etc.) | ✅ OK |
| 12 | Tipo medio de pago | Efectivo/Tarjeta/etc. | ✅ OK |
| 13 | Emisor tarjeta | Visa, Mastercard, etc. | ✅ OK |
| 14 | RENTABILIDAD | Factor de margen | ✅ OK |
| 15 | mARGEN DE RENTABILIDAD | Porcentaje de margen | ✅ OK |

**Archivo separado con horarios:**

| # | Campo | Descripción | Estado |
|---|-------|-------------|--------|
| 1 | Fecha | Fecha de transacción | ✅ OK |
| 2 | Hora | Hora de la transacción | ✅ OK |
| 3 | Comprobante | Número de ticket | ✅ OK |
| 4 | Cliente | ID/Nombre de cliente | ⚠️ VACÍO |
| 5 | Importe | Monto total | ✅ OK |

---

## 2. CAMPOS REQUERIDOS - PRIORIDAD CRÍTICA

Estos campos son **INDISPENSABLES** para implementar el programa de fidelización y análisis de clientes:

### 2.1 Identificación de Cliente

| # | Campo Requerido | Descripción | Uso |
|---|-----------------|-------------|-----|
| **1** | **ID_CLIENTE** | Código único del cliente en Caribbean | Vincular transacciones al mismo cliente |
| **2** | **DNI_CLIENTE** | Documento de identidad | Identificación única |
| **3** | **NOMBRE_CLIENTE** | Nombre completo | Comunicación personalizada |
| **4** | **TELEFONO_CLIENTE** | Número de celular | WhatsApp para ofertas |
| **5** | **EMAIL_CLIENTE** | Correo electrónico (opcional) | Marketing digital |

> **JUSTIFICACIÓN:** Actualmente el campo "Cliente" existe pero está **vacío en el 100% de los registros**. Esto impide identificar a los clientes Premium (15.6% de transacciones que generan 52.1% de la ganancia) y cualquier acción de fidelización.

### 2.2 Unificación de Archivo de Exportación

| # | Campo Requerido | Descripción | Uso |
|---|-----------------|-------------|-----|
| **6** | **HORA** | Hora de la transacción (HH:MM:SS) | Incluir en el archivo principal |

> **JUSTIFICACIÓN:** Actualmente la hora está en un archivo separado. Se requiere unificar en un solo archivo de exportación para simplificar el proceso.

---

## 3. CAMPOS REQUERIDOS - PRIORIDAD ALTA

Estos campos mejorarían significativamente el análisis operativo:

### 3.1 Información de Punto de Venta

| # | Campo Requerido | Descripción | Uso |
|---|-----------------|-------------|-----|
| **7** | **CODIGO_CAJA** | Número de caja donde se realizó la venta | Análisis de productividad |
| **8** | **CODIGO_CAJERO** | ID del empleado que atendió | Seguimiento de ventas por empleado |
| **9** | **TURNO** | Turno de la transacción (mañana/tarde/noche) | Análisis operativo |

### 3.2 Información Adicional del Producto

| # | Campo Requerido | Descripción | Uso |
|---|-----------------|-------------|-----|
| **10** | **PROVEEDOR** | Código/nombre del proveedor | Análisis de proveedores |
| **11** | **COSTO_PRODUCTO** | Costo de adquisición | Cálculo preciso de márgenes |

---

## 4. CAMPOS REQUERIDOS - PRIORIDAD MEDIA

Campos opcionales que agregarían valor al análisis:

| # | Campo | Descripción | Uso |
|---|-------|-------------|-----|
| **12** | DESCUENTO_LINEA | Descuento aplicado al ítem | Análisis de promociones |
| **13** | DESCUENTO_TICKET | Descuento total del ticket | Impacto de promos |
| **14** | PRECIO_LISTA | Precio sin descuento | Comparar con precio final |
| **15** | STOCK_ACTUAL | Stock al momento de venta | Alertas de reposición |
| **16** | UBICACION_GONDOLA | Ubicación física del producto | Optimización de layout |

---

## 5. FORMATO DE EXPORTACIÓN REQUERIDO

### 5.1 Especificaciones Técnicas

| Parámetro | Valor Requerido |
|-----------|-----------------|
| **Formato** | CSV (separado por punto y coma) |
| **Encoding** | UTF-8 |
| **Delimitador** | Punto y coma (;) |
| **Decimal** | Coma (,) o Punto (.) - indicar cuál |
| **Fecha** | Formato ISO: YYYY-MM-DD |
| **Hora** | Formato 24h: HH:MM:SS |
| **Encabezados** | Primera fila con nombres de columnas |

### 5.2 Estructura Propuesta del Archivo Unificado

```
Fecha;Hora;Comprobante;ID_Cliente;DNI_Cliente;Nombre_Cliente;Telefono_Cliente;Codigo_Caja;Codigo_Cajero;Codigo;Codigo_Barras;Marca;Departamento;Nombre;Cantidad;Importe;Unitario;Tipo_Factura;Tipo_Medio_Pago;Emisor_Tarjeta;Rentabilidad;Margen_Rentabilidad
```

---

## 6. PRIORIZACIÓN POR IMPACTO DE NEGOCIO

### ETAPA 1 - INMEDIATA (1-2 semanas)

Habilitar estos campos es **CRÍTICO** para la estrategia de fidelización:

| Campo | Impacto |
|-------|---------|
| **ID_CLIENTE** | Permite identificar clientes recurrentes |
| **TELEFONO_CLIENTE** | Habilita comunicación vía WhatsApp |
| **HORA** (en archivo principal) | Simplifica el proceso de análisis |

> **Sin estos campos, es imposible implementar el programa de fidelización que proteja a los clientes Premium (52% de la ganancia).**

### ETAPA 2 - CORTO PLAZO (1 mes)

| Campo | Impacto |
|-------|---------|
| DNI_CLIENTE | Identificación única y verificable |
| NOMBRE_CLIENTE | Comunicación personalizada |
| CODIGO_CAJA | Análisis de productividad por caja |
| CODIGO_CAJERO | Incentivos y capacitación |

### ETAPA 3 - MEDIANO PLAZO (2-3 meses)

| Campo | Impacto |
|-------|---------|
| EMAIL_CLIENTE | Marketing digital |
| PROVEEDOR | Análisis de supply chain |
| COSTO_PRODUCTO | Márgenes precisos |
| DESCUENTO_LINEA | Efectividad de promociones |

---

## 7. PREGUNTAS PARA EL TÉCNICO

1. **¿El campo "Cliente" ya existe en Caribbean pero no se está capturando?**
   - El archivo de horarios tiene la columna "Cliente" pero está vacía.

2. **¿Se puede configurar Caribbean para solicitar DNI/teléfono en caja?**
   - ¿Es un campo obligatorio u opcional?
   - ¿Existe búsqueda de cliente por teléfono?

3. **¿Caribbean tiene módulo de clientes/fidelización integrado?**
   - Si existe, ¿cómo se activa?
   - ¿Tiene acumulación de puntos?

4. **¿Se pueden unificar ambos archivos de exportación?**
   - Actualmente hay uno con detalles y otro con horarios.

5. **¿Cuál es el proceso para agregar campos a la exportación?**
   - ¿Requiere actualización de versión?
   - ¿Es configurable desde el sistema?

6. **¿Existe documentación de la estructura de datos de Caribbean?**
   - Manual técnico de tablas/campos disponibles.

---

## 8. CONTACTO PARA COORDINACIÓN

**Supermercado Don Nino**
- Responsable del proyecto: [Completar]
- Email: [Completar]
- Teléfono: [Completar]

**PymeInside - Equipo de BI**
- Soporte técnico para integración de datos

---

## ANEXO: RESUMEN DE CAMPOS

### Tabla Consolidada

| # | Campo | Prioridad | Disponible | Requerido |
|---|-------|-----------|------------|-----------|
| 1 | Fecha | - | ✅ | ✅ |
| 2 | Hora | CRÍTICA | ⚠️ Separado | ✅ Unificar |
| 3 | Comprobante | - | ✅ | ✅ |
| 4 | **ID_CLIENTE** | **CRÍTICA** | ❌ | ✅ |
| 5 | **DNI_CLIENTE** | **CRÍTICA** | ❌ | ✅ |
| 6 | **NOMBRE_CLIENTE** | ALTA | ❌ | ✅ |
| 7 | **TELEFONO_CLIENTE** | **CRÍTICA** | ❌ | ✅ |
| 8 | EMAIL_CLIENTE | MEDIA | ❌ | Opcional |
| 9 | CODIGO_CAJA | ALTA | ❌ | ✅ |
| 10 | CODIGO_CAJERO | ALTA | ❌ | ✅ |
| 11 | Código | - | ✅ | ✅ |
| 12 | Código barras | - | ✅ | ✅ |
| 13 | Marca | - | ✅ | ✅ |
| 14 | Departamento | - | ✅ | ✅ |
| 15 | Nombre | - | ✅ | ✅ |
| 16 | Cantidad | - | ✅ | ✅ |
| 17 | Importe | - | ✅ | ✅ |
| 18 | Unitario | - | ✅ | ✅ |
| 19 | Tipo Factura | - | ✅ | ✅ |
| 20 | Tipo medio pago | - | ✅ | ✅ |
| 21 | Emisor tarjeta | - | ✅ | ✅ |
| 22 | Rentabilidad | - | ✅ | ✅ |
| 23 | Margen | - | ✅ | ✅ |
| 24 | PROVEEDOR | MEDIA | ❌ | Opcional |
| 25 | COSTO_PRODUCTO | MEDIA | ❌ | Opcional |
| 26 | DESCUENTO_LINEA | MEDIA | ❌ | Opcional |

---

**Leyenda:**
- ✅ Disponible y funcionando
- ⚠️ Parcialmente disponible
- ❌ No disponible actualmente

---

*Documento generado para coordinación técnica con Caribbean Desktop*
*Supermercado Don Nino - Proyecto de Business Intelligence*

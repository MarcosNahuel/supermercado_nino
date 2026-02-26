# Solicitud de Datos - Sistema Caribbean
**Supermercado Don Nino**
**Fecha:** 16/01/2026

---

## 1. VENTAS - Detalle de Comprobantes

| Campo | Descripción |
|-------|-------------|
| Fecha | Fecha de la transacción (YYYY-MM-DD) |
| Hora | Hora exacta (HH:MM:SS) |
| Comprobante | Número de ticket/factura |
| Tipo Comprobante | FA, FB, NC, ND, etc. |
| SKU | Código interno del producto |
| Código Barras | EAN/UPC del producto |
| Descripción | Nombre del producto |
| Departamento | Categoría/rubro |
| Marca | Marca del producto |
| Cantidad | Unidades vendidas |
| Precio Unitario | Precio de venta unitario |
| Descuento Linea % | Porcentaje de descuento aplicado al ítem |
| Descuento Linea $ | Monto de descuento aplicado al ítem |
| Importe Bruto | Precio x Cantidad (sin descuento) |
| Importe Neto | Monto final de la línea (con descuento) |
| Descuento Ticket % | Descuento general del ticket |
| Descuento Ticket $ | Monto descuento general del ticket |
| Motivo Descuento | Código/descripción del motivo |
| Medio de Pago | Efectivo, Débito, Crédito, QR, etc. |
| Emisor Tarjeta | Visa, Mastercard, etc. |
| Cuotas | Cantidad de cuotas (si aplica) |
| ID Cliente | Código único del cliente |
| DNI Cliente | Documento del cliente |
| Nombre Cliente | Nombre completo |
| Teléfono Cliente | Número de contacto |
| Código Caja | Número de caja |
| Código Cajero | ID del empleado |

---

## 2. STOCK - Inventario Actual

| Campo | Descripción |
|-------|-------------|
| Fecha Consulta | Fecha del corte de inventario |
| Hora Consulta | Hora del corte |
| SKU | Código interno del producto |
| Código Barras | EAN/UPC |
| Descripción | Nombre del producto |
| Departamento | Categoría/rubro |
| Marca | Marca del producto |
| Stock Actual | Unidades disponibles |
| Stock Mínimo | Punto de reposición |
| Stock Máximo | Tope de inventario |
| Unidad Medida | Unidad, Kg, Lt, etc. |
| Ubicación | Depósito/góndola/sector |
| Proveedor Principal | Código/nombre proveedor |
| Fecha Último Ingreso | Última recepción de mercadería |
| Fecha Última Venta | Última venta del producto |

---

## 3. MOVIMIENTOS DE STOCK

| Campo | Descripción |
|-------|-------------|
| Fecha | Fecha del movimiento |
| Hora | Hora exacta del movimiento |
| SKU | Código del producto |
| Código Barras | EAN/UPC |
| Descripción | Nombre del producto |
| Departamento | Categoría |
| Tipo Movimiento | Entrada / Salida / Ajuste |
| Motivo | Compra, Venta, Merma, Transferencia, Ajuste, etc. |
| Cantidad | Unidades del movimiento (+/-) |
| Stock Anterior | Stock antes del movimiento |
| Stock Posterior | Stock después del movimiento |
| Documento Referencia | Remito, Factura, Ticket, etc. |
| Número Documento | Número del documento |
| Proveedor | Código/nombre (si es entrada) |
| Lote | Número de lote (si aplica) |
| Fecha Vencimiento | Vencimiento del lote |
| Costo Unitario | Costo del movimiento |
| Usuario | Quién registró el movimiento |

---

## 4. BAJAS / MERMAS (Salidas No Venta)

| Campo | Descripción |
|-------|-------------|
| Fecha | Fecha de la baja |
| Hora | Hora exacta |
| SKU | Código del producto |
| Código Barras | EAN/UPC |
| Descripción | Nombre del producto |
| Departamento | Categoría |
| Cantidad | Unidades dadas de baja |
| Motivo Baja | Vencimiento, Rotura, Deterioro, Hurto, Error, etc. |
| Costo Unitario | Costo del producto |
| Costo Total | Pérdida total |
| Lote | Número de lote |
| Fecha Vencimiento | Si es por vencimiento |
| Documento Baja | Número de comprobante interno |
| Usuario | Quién registró |
| Autorizado Por | Supervisor que autorizó |
| Observaciones | Detalle adicional |

---

## 5. PRECIOS - Histórico por SKU

| Campo | Descripción |
|-------|-------------|
| Fecha Desde | Inicio de vigencia del precio |
| Fecha Hasta | Fin de vigencia (vacío si vigente) |
| Hora Cambio | Hora exacta del cambio de precio |
| SKU | Código del producto |
| Código Barras | EAN/UPC |
| Descripción | Nombre del producto |
| Departamento | Categoría |
| Precio Lista | Precio regular |
| Precio Promocional | Precio de oferta (si aplica) |
| Tipo Precio | Regular, Oferta, Liquidación, etc. |
| Motivo Cambio | Actualización, Promoción, Ajuste, etc. |
| Usuario | Quién modificó |

---

## 6. COSTOS - Histórico por SKU (si existe)

| Campo | Descripción |
|-------|-------------|
| Fecha | Fecha del costo |
| SKU | Código del producto |
| Código Barras | EAN/UPC |
| Descripción | Nombre |
| Costo Unitario | Costo de adquisición |
| Costo Promedio | Costo promedio ponderado |
| Proveedor | Código/nombre |
| Documento | Factura de compra |
| Número Documento | Número de factura |

---

## 7. MAESTRO DE PRODUCTOS

| Campo | Descripción |
|-------|-------------|
| SKU | Código interno único |
| Código Barras | EAN/UPC |
| Descripción | Nombre del producto |
| Descripción Corta | Nombre abreviado |
| Departamento | Categoría principal |
| Subdepartamento | Subcategoría |
| Marca | Marca del producto |
| Proveedor Principal | Código/nombre |
| Unidad Medida | Unidad, Kg, Lt, etc. |
| Contenido Neto | Peso/volumen |
| IVA | Tasa de IVA aplicable |
| Días Vida Útil | Para productos perecederos |
| Stock Mínimo | Punto de reposición |
| Stock Máximo | Tope de inventario |
| Activo | Sí/No |
| Fecha Alta | Fecha de creación |
| Fecha Baja | Si está inactivo |

---

## 8. MAESTRO DE CLIENTES (si existe)

| Campo | Descripción |
|-------|-------------|
| ID Cliente | Código único |
| DNI/CUIT | Documento |
| Nombre | Nombre completo / Razón social |
| Teléfono | Número de contacto |
| Email | Correo electrónico |
| Dirección | Domicilio |
| Fecha Alta | Fecha de registro |
| Fecha Última Compra | Última transacción |
| Categoría Cliente | VIP, Regular, Mayorista, etc. |

---

## Notas Técnicas

- **Vinculación:** Todos los datos se vinculan por **SKU** y **Fecha/Hora**
- **Formato Fecha:** YYYY-MM-DD
- **Formato Hora:** HH:MM:SS (24 horas)
- **Formato Archivo:** CSV con separador punto y coma (;)
- **Encoding:** UTF-8
- **Frecuencia:** Diaria o según se acuerde

---

## Resumen de Tablas Solicitadas

| # | Tabla | Prioridad |
|---|-------|-----------|
| 1 | Ventas - Detalle Comprobantes | Alta |
| 2 | Stock - Inventario Actual | Alta |
| 3 | Movimientos de Stock | Alta |
| 4 | Bajas / Mermas | Alta |
| 5 | Precios - Histórico | Alta |
| 6 | Costos - Histórico | Media (si existe) |
| 7 | Maestro de Productos | Alta |
| 8 | Maestro de Clientes | Media (si existe) |

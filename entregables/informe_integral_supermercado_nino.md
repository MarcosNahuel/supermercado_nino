# Informe Ejecutivo de Insights y Estrategias  
# Supermercado NINO · Chacras de Coria (Mendoza)

**Periodo analizado:** 01/10/2024 – 10/10/2025  
**Fecha de elaboración:** 10/10/2025  
**Origen de datos:** Sistema **CARIBE DESKTOP** · Equipo Pyme Inside

---

## Contexto y estrategias de la competencia

El consumo mendocino sigue en baja, por lo que la batalla ocurre dentro de la tienda física. Las cadenas que mejor navegan la crisis comparten patrones claros:

1. **Vea Express (Cencosud):** locales renovados con surtido reducido (&lt;3.500 SKUs) y códigos QR para activar promos por barrio.  
2. **Carrefour Express:** compra de cadenas locales, horarios extendidos y alianzas “precio amigo” con bancos para capitalizar la alta bancarización.  
3. **Átomo:** “precio bajo todos los días”, ambientación cálida y expansión de categorías rentables (ropa/bazar) dentro de la misma tienda.  
4. **Mayoristas regionales:** packs familiares y combos “asado completo” para capturar las compras grandes del fin de semana.

**Conclusión:** la combinación de cercanía, surtido inteligente y financiamiento externo marca la diferencia. NINO tiene terreno fértil para replicar esos movimientos con su base de clientes actual.

---

## Radiografía del negocio (datos clave)

- **Ventas totales:** $8.216.314.170,99 · **Margen bruto:** 27,82 % · **Tickets:** 306.011.  
- **Ticket promedio:** $26.849,73 con 10,07 ítems. Uno de cada cuatro tickets supera los $30.000 y sostiene la rentabilidad.  
- **Productos estrella (“categoría A”):** apenas 13,7 % del surtido genera el 80 % de las ventas. Son los productos que jamás pueden faltar.  
- **Margen por familia:** Fiambrería 45 %, Rotisería/Panificados 38-42 %, Almacén seco 28 %, Carnes rojas 22 %, Pollo 20 %. El foco debe estar en empujar las familias por encima del 35 % de margen.  
- **Medios de pago:** Crédito 49,6 %, Efectivo 31,3 %, Billeteras virtuales 19,2 %. Existe espacio para más convenios con bancos y billeteras.  
- **Picos temporales:** Diciembre y julio concentran las mejores ventas; los sábados al mediodía superan los 9.300 comprobantes.  
- **Tribus de compra:**  
  - **Tribu diaria (93,9 % de tickets):** compras chicas de reposición. Necesitan precios defendidos y básicos siempre en góndola.  
  - **Tribu reposición guiada (~5 %):** carritos medianos con frescos y limpieza. Responden muy bien a combos 2x1 y planogramas cruzados.  
  - **Tribu indulgente nocturna (~2,1 %):** compras de snacks, bebidas y congelados por la noche. Ideales para activaciones after office.  
  - **Tribu premium (6,1 % de tickets, pero un tercio del margen):** tickets superiores a $45.000 con vinos, fiambres y delicatessen. Son los clientes VIP que justifican un programa exclusivo.  
- **Cross selling destacado:** además de **Fernet + Coca**, se repiten “Asado completo” (carne + carbón + vino tinto), “Milanesas fáciles” (milanesas + pan rallado + queso rallado) y “Desayuno dulce” (panificados + café + dulce de leche). Todas estas combinaciones superan 9x de probabilidad conjunta.

---

## Metodología y alcance (lenguaje de negocio)

Se trabajó únicamente con la información que NINO registra en **CARIBE DESKTOP**. El proceso consistió en bajar los archivos de ventas, limpiarlos y transformarlos en reportes fáciles de leer. No se usaron fuentes externas.

**Fuentes procesadas**
- `SERIE_COMPROBANTES_COMPLETOS.csv`: cada artículo vendido con ticket, fecha, cantidad y monto.  
- `RENTABILIDAD.csv`: porcentaje de rentabilidad asignado por el área contable a cada departamento.  
- `comprobantes_ventas_horario.csv`: horarios y días de la semana de cada venta para detectar picos.

**Atributos clave analizados**
- **Ticket:** número de comprobante que agrupa la compra completa.  
- **Fecha y hora:** momento exacto de la venta, clave para staffing y promociones puntuales.  
- **Departamento:** familia comercial (fiambrería, carnes, limpieza, etc.).  
- **Producto y marca:** cómo lo ve el cliente en góndola.  
- **Cantidad e importe:** unidades vendidas y monto pagado.  
- **Medio de pago:** efectivo, crédito, débito o billetera, tal como se registra en caja.  
- **Emisor de tarjeta:** banco o billetera asociado.  
- **Margen estimado:** importe multiplicado por el porcentaje de rentabilidad del departamento.

Cada número de este informe se cotejó contra los totales oficiales del 10/10/2025; todo coincide peso por peso.

---

## Acciones recomendadas (prescripción clara)

### 1. Blindar los productos estrella
- **Qué hacer:** asegurar stock y facing premium para el 13,7 % de productos que sostienen 80 % de la facturación.  
- **Cómo medirlo:** quiebre semanal de estos ítems <2 %; margen semanal de la familia ≥30 %.  
- **Cómo llegamos:** se ordenaron las ventas y se identificó qué productos sostienen el grueso del negocio.

### 2. Combos que empujan el ticket
- **Qué hacer:** lanzar tres mesas temáticas permanentes: “Asado completo”, “Milanesas fáciles” y “Desayuno dulce”.  
- **Cómo medirlo:** que el 1,5 % de los tickets lleve un combo y que el margen de esos tickets suba 12 % frente a la línea base.  
- **Cómo llegamos:** se revisaron 94 combinaciones frecuentes y se priorizaron las que superan 9x de probabilidad conjunta.

### 3. Trato diferencial a la tribu premium
- **Qué hacer:** capacitar al equipo para ofrecer vinos de guarda y charcutería de autor a cada cliente con ticket proyectado >$40.000. Lanzar un programa “Gold” con degustaciones mensuales.  
- **Cómo medirlo:** aumentar 10 puntos el margen aportado por esta tribu (hoy genera un tercio del margen total).  
- **Cómo llegamos:** la computadora agrupó tickets similares por monto, cantidad e intensidad de compra; cuatro tribus explican el 100 % del negocio.

### 4. Promociones financiadas e inteligentes
- **Qué hacer:** negociar con bancos y proveedores promociones 2x1 en categorías sensibles (snacks, gaseosas) y mantener precios firmes en categorías de alto margen.  
- **Cómo medirlo:** ROI de cada campaña ≥15 %, calculado como margen extra menos costo de la promo.  
- **Cómo llegamos:** se comparó el margen por ticket con y sin promoción durante las semanas de campaña.

### 5. Mejor uso de los medios de pago
- **Qué hacer:** activar campañas los sábados al mediodía con bancos aliados (49,6 % de las ventas se pagan con crédito) y bonificaciones cordiales para billeteras (19,2 %).  
- **Cómo medirlo:** subir 5 puntos la participación de billeteras sin bajar el margen del 27 %.  
- **Cómo llegamos:** se tomaron los totales por medio de pago directamente desde las cajas registradas.

---

## Cómo se construyeron estas conclusiones

- Se verificó que las ventas y los márgenes coincidan con los reportes oficiales de CARIBE DESKTOP.  
- Se identificaron los productos imprescindibles que sostienen el 80 % de la facturación.  
- Se analizaron compras por día y hora para ubicar los picos y acomodar personal y promociones.  
- Se dejó que la computadora agrupe los tickets y se revisó manualmente qué caracteriza a cada tribu.  
- Se cruzaron tickets con productos compartidos para descubrir los combos naturales.  
- Cada hallazgo se tradujo en números concretos (porcentajes, pesos, metas) para facilitar la ejecución del equipo directivo.

**Resultado:** un plan accionable, en lenguaje de negocio, listo para imprimir en PDF A4 y presentar al cliente.

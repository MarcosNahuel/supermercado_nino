Va, Nahuel! Aca tenes el **resumen en texto** de las modificaciones que hay que aplicar al dashboard (agnostico a herramienta).

# Modificaciones a aplicar

1. Analisis temporal y tendencia

- Reemplazar "distribucion y utilidad por ticket" por **distribucion de ventas por ticket**.
- Agregar **linea de tendencia** con **pendiente** (slope) visible.
- Habilitar vistas **Mensual / Quincenal / Semanal**.
- Incorporar **UPT semanal** (unidades por ticket).

2. Heatmap de demanda

- Ya esta habilitado el mapa de calor Dia x Hora; solo validar que siga cargando correctamente (antes no renderizaba).

3. Pareto por categoria (no global)

- Construir **Paretos separados** para **Carnes, Almacen, Lacteos y Limpieza** con corte 80/20.
- **Eliminar** el Pareto global Top10 y la **tabla final** redundante.

4. Market Basket Analysis (reglas de asociacion)

- Mantener vista general (support, confidence, lift).
- Crear una **segunda vista excluyendo Carniceria** (filtro fijo).

5. Segmentacion por monto de ticket

- Armar **histograma de 16 bins** de **$2.500** (0 a $37.500; el ultimo agrupa "> $37.500").
- Calcular **cuartiles** (Q1, Q2, Q3) y etiquetar cada ticket en **Bajo / Medio / Alto / Premium**.
- Para cada cuartil, mostrar **histograma del margen**.
- Agregar **KPI de rotacion** para cruzar **margen vs rotacion** (si hay costo/stock; si no, dejar placeholder).

6. Medios de pago (normalizacion + analisis)

- Normalizar metodos en: **Efectivo / Debito / Credito / Billetera**.
- Separar **Efectivo** vs **Digitales** (Debito+Credito+Billetera).
- Incluir **histogramas de montos** por metodo y **histograma de margen** por metodo.
- Validar que **Debito** quede correctamente tipificado y visible.

7. Nomenclatura y limpieza de UX

- Renombrar **SKU -> Codigo de producto**.
- Cambiar textos confusos ("utilidad por ticket") por **"venta por ticket"**.
- Remover elementos de prueba o tablas residuales.

8. Rendimiento y aceptacion

- Con filtro del **ultimo mes**, cada vista debe cargar en **< 3 s**.
- El **heatmap** debe reflejar picos horarios consistentes con el total diario.
- Deben existir **dos pestanas de MBA** (General y **Sin Carniceria**).
- Deben existir **4 Paretos por categoria** (sin Pareto global).
- Debe verse el **histograma 16 bins** y las **4 segmentaciones por cuartil** con **margen por cuartil**.
- **Metodos de pago** claramente separados y **Debito** presente.

9. Entregables

- Dashboard actualizado.
- **Diccionario de metricas/KPIs** y **README breve** de navegacion/uso.

# PROMPT — Agente de Codificación (Data Scientist + Analyst)

**Objetivo:** con los datos disponibles de tickets por ítem (fecha, comprobante, departamento, producto, cantidad, unitario, importe) y el mapeo de **% de rentabilidad por Departamento**, construir un **pipeline reproducible en Python** y una **aplicación Streamlit** que:

1. calcule y exponga KPIs y métricas accionables (existentes + nuevas que sean posibles con estos datos),
2. **modele la rentabilidad por ticket** y su **desviación**, con **series cíclicas** (anual, mensual, semanal y diaria),
3. realice **Pareto de productos** (global y cíclico),
4. analice **medios de pago** (cuando están presentes: 01/02/2025–07/10/2025),
5. produzca un **informe narrativo** (bullets) con hallazgos y **estrategias respaldadas por los números**,
6. mantenga un **cuaderno de anotaciones** en Markdown con todo lo aprendido y decidido.

> **Regla clave:** solo calcular KPIs/estrategias **respaldables** con estos datos. Nada fuera del alcance (sin conjeturas).

---

## 0) Contexto y paths (Windows)

- Informe a leer primero:
  `D:\OneDrive\GitHub\supermercado_nino - copia\NUEVO ANALISIS COMPLETO\Estrategias de Analítica para Supermercados Medianos en Mendoza (Rentabilidad del Ticket Promedio).md`
- Datos crudos:
  `D:\OneDrive\GitHub\supermercado_nino - copia\data\raw\SERIE_COMPROBANTES_COMPLETOS3.csv`
- Tabla de % rentabilidad por departamento (aproximada): **CSV** con columnas: `Departamento, Clasificación, % Rentabilidad`.
  (Si no fuese CSV, convertí a CSV y usá ese archivo).
- **Período con medios de pago**: del **01/02/2025** al **07/10/2025**: campos “Tipo medio de pago” y “Emisor tarjeta”. **Vacíos = Efectivo**.

> Si corrés fuera de ese path, detectá automáticamente una ruta equivalente del repo.

---

## 1) Setup del proyecto

- Crear estructura:

  ```
  /app
    ├─ streamlit_app.py
    ├─ components/          (gráficos/funciones)
    ├─ assets/              (logos, css opcional)
  /data
    ├─ raw/                 (CSV original)
    ├─ processed/           (salidas limpias y KPIs)
  /reports
    ├─ cuaderno_agente.md   (memoria viva del agente)
    ├─ resumen_bullets.md   (hallazgos y estrategias)
  /config
    └─ settings.yaml        (parámetros generales)
  /notebooks (opcional)
  /README.md
  requirements.txt
  ```

- `requirements.txt` mínimo:
  `pandas numpy python-dateutil streamlit plotly statsmodels scikit-learn`
- Registrar **todo** lo que hagas en `/reports/cuaderno_agente.md` (puede reescribirse/append cada paso).

---

## 2) Lectura del informe y del repositorio (Memoria)

1. **Abrí y leé** el informe en la ruta indicada. Extraé: objetivos, KPIs clave, estrategias sugeridas.

   - Guardá **resumen** (bullets) en `/reports/cuaderno_agente.md` sección `# Informe base – resumen`.

2. **Revisá el repositorio** (si disponible localmente): listá scripts previos, qué KPIs calculan, y oportunidades de mejora.

   - Anotá hallazgos en el cuaderno.

3. Dejá preparado un **checklist** de KPIs a generar **sólo con estos datos** (sección `# Backlog de KPIs posibles`).

---

## 3) Ingesta y normalización de datos

- Cargar `SERIE_COMPROBANTES_COMPLETOS3.csv` con atención a **separador** (`;`) y **decimal** (`,`).

  - Intentá `encoding='utf-8'`; si hay mojibake (e.g., `Ã³`), probá `latin1`.

- Estandarizá columnas a `snake_case` (ejemplo):

  ```
  Fecha -> fecha (datetime)
  Comprobante -> ticket_id (string)
  Código -> producto_id (string)
  Código barras -> codigo_barras (string)
  Marca -> marca (string)
  Departamento -> departamento (string)
  Nombre -> producto (string)
  Cantidad -> cantidad (float)
  Importe -> importe_total (float)
  Unitario -> precio_unitario (float)
  TIPO FACTURA -> tipo_factura (string)
  Tipo medio de pago -> medio_pago (string)
  Emisor tarjeta -> emisor (string)
  ```

- Normalizaciones:

  - **Fechas** a `datetime` (día/mes/año si corresponde).
  - **Blanks/NaN en `medio_pago` ⇒ "EFECTIVO"**.
  - Mapear variantes:

    - `Tarjeta de crédito` ⇒ `CREDITO`, `Visa débito` ⇒ `DEBITO` (estandarizar), `Billetera Vitual` ⇒ `BILLETERA`.
    - `emisor`: normalizar (`VISA`, `MASTERCARD`, etc.).

  - **Strings**: `.str.strip().str.upper()`; corregir acentos si fuera necesario.

- **Data Quality** (anotar al cuaderno):

  - % filas con nulos por columna clave.
  - Chequear `importe_total ≈ cantidad * precio_unitario` (tolerancia ±0,01).
  - Duplicados por línea (no eliminar salvo fraude obvio; registrá conteo).

---

## 4) Costeo estimado por línea y rentabilidad

> Solo con los datos disponibles **no hay costo real**; usar el **% Rentabilidad por Departamento** (aproximado) para estimar margen.

- Cargar tabla de **rentabilidad por departamento**.

  - Estandarizar `Departamento` y mapear `% Rentabilidad` a `rentabilidad_pct` numérico (e.g., `"28%" → 28.0`).

- **Join** por `departamento` para obtener `rentabilidad_pct` de cada línea.
- Calcular:

  - `margen_linea_est = importe_total * (rentabilidad_pct/100)`
  - `costo_linea_est = importe_total - margen_linea_est`

- **Calidad**: indicador `tiene_rentabilidad` (=1 si se mapeó; 0 si no). Registrar cobertura por departamento.

---

## 5) Agregación por ticket y features temporales

- **Ticket (comprobante) = transacción**: agrupar por `ticket_id`:

  - `monto_total_ticket = sum(importe_total)`
  - `costo_total_ticket = sum(costo_linea_est)`
  - `rentabilidad_ticket = sum(margen_linea_est)`
  - `items_ticket = sum(cantidad)`
  - `skus_ticket = nunique(producto_id)`
  - `fecha` (min/first), `hora` (si disponible)
  - `medio_pago_ticket`: **modo más frecuente** dentro del ticket (o `EFECTIVO` si todos NaN).
  - `emisor_principal` (si aplica)

- Derivadas:

  - `rentabilidad_pct_ticket = rentabilidad_ticket / monto_total_ticket` (manejar división por cero).
  - Calendario: `anio`, `mes`, `dia`, `semana_iso` (`YYYY-Www`), `mes_str` (`YYYY-MM`), `weekday`, `hora` (si hay).

- Exportar tablas **procesadas** a `/data/processed/`:

  - `items.csv` (líneas) y `tickets.csv` (agregado por ticket).
  - Guardar un **diccionario de datos** (CSV) con descripción de campos.

---

## 6) KPIs obligatorios (con estos datos)

> Todo debe poder **filtrarse** por rango de fechas y, cuando existan, por **medio de pago** y **emisor**.

1. **Rentabilidad por ticket (AR$)**

   - Media, mediana, **desviación estándar**, p25/p75.
   - **Series cíclicas** de **rentabilidad por ticket**:

     - **Anual** (por `anio`)
     - **Mensual** (`YYYY-MM`)
     - **Semanal** (`semana_iso`)
     - **Diaria** (`fecha`/`YYYY-MM-DD`)

   - Además, **ciclos promedios**:

     - **Mes del año** (promedio por `1..12`)
     - **Día de semana** (Mon..Sun)
     - **Hora del día** (si hay hora)

2. **Ticket promedio (AR$)** y **UPT** (unidades por ticket) por esos mismos ciclos.
3. **Pareto de productos (80/20)**

   - Global: ranking por ventas y por margen_est.
   - **Cíclico**: Pareto por `YYYY-MM` y por **día de semana** (siempre top N=20).
   - Clasificación ABC (A: 0–80%; B: 80–95%; C: 95–100%).

4. **KPIs por Departamento** (derivables):

   - Ventas, margen_est, **margen % estimado**, tickets, UPT.

5. **Medios de pago** _(solo 01/02/2025–07/10/2025)_:

   - % de **ventas** y % de **tickets** por `medio_pago` y por `emisor`.
   - **Ticket promedio** y **rentabilidad por ticket** por `medio_pago`.
   - Ciclo semanal/mensual por `medio_pago` (identificar días de mayor uso de tarjetas/billeteras).
   - Nota: filas sin `medio_pago` ⇒ `EFECTIVO`.

6. **Calidad de estimación**:

   - % de líneas con `rentabilidad_pct` mapeada.
   - Lista de departamentos sin mapeo (si existiera).

> **Importante:** Toda métrica debe indicar explícitamente que es **estimada** (por uso de % por Departamento).

---

## 7) Visualizaciones (Streamlit)

**Página 1 — Overview**

- KPIs grandes (desde–hasta): Ventas totales, Tickets, **Ticket Promedio**, **Rentabilidad promedio por ticket**, **Desv.Std**.
- Serie temporal de **rentabilidad por ticket** (línea) con selector de ciclo (**diaria/semanal/mensual**).
- Distribución (histograma o boxplot) de rentabilidad por ticket.

**Página 2 — Ciclos (Anual/Mensual/Semanal/Diario)**

- 4 tabs: **Anual**, **Mensual**, **Semanal**, **Diario**.
- Cada tab: gráficos de **rentabilidad por ticket**, **ticket promedio** y **UPT** para ese ciclo.
- (Opcional) descomposición estacional simple si hay suficiente data (statsmodels).

**Página 3 — Pareto & ABC**

- Tabla y barras **Top 20** productos por ventas y por margen_est.
- ABC global y **ABC por mes** (selector `YYYY-MM`) y **por día de semana**.

**Página 4 — Departamentos**

- Tabla: ventas, margen_est, margen %, tickets, UPT por departamento.
- Barras apiladas: contribución de departamentos a **margen_est**.

**Página 5 — Medios de Pago (2025-02-01 a 2025-10-07)**

- % ventas y % tickets por **EFECTIVO / CREDITO / DEBITO / BILLETERA**.
- Ticket promedio y **rentabilidad/ticket** por medio de pago.
- **Ciclo semanal** por medio de pago (para detectar dónde conviene poner promos bancarias).
- Tabla por **emisor** (Visa, Mastercard, etc.) con % de ventas/tickets.

**Página 6 — Descargas & Diccionario**

- Botones para descargar CSV de KPIs y **diccionario de datos**.
- Nota clara: “márgenes **estimados** por mapeo de departamento”.

**Filtros globales (sidebar)**

- Rango de fechas, Departamento(s), Medio de pago (cuando haya), Emisor.

---

## 8) Informe narrativo + estrategias respaldadas

- Generar `/reports/resumen_bullets.md` con:

  1. **Bullets** del informe leído al inicio (tu propio resumen, no copy/paste).
  2. **Hallazgos** del análisis real (con cifras):

     - p.ej., “La rentabilidad media por ticket en el período fue $X con σ=$Y; fines de semana +Z% vs. días hábiles; el top 20 de productos explica W% de ventas y V% de margen_est; con tarjeta el ticket es N% mayor/menor que efectivo”, etc.

  3. **Estrategias respaldadas por datos** (solo plausibles con esta info):

     - **Gestión ABC en A** (evitar quiebres, facing premium) → respaldar con Pareto;
     - **Combos/cross-selling** con productos que co-ocurren en tickets altos (si detectás asociaciones simples por ticket-id, sin MBA formal);
     - **Promos por medio de pago** en días valle donde el uso de tarjetas/billeteras sea natural, **sin destruir margen** (apoyarte en ticket/margen por medio de pago);
     - **Rebalanceo de espacio por Departamento** con mejor margen_est (mostrar impacto esperado a partir de su contribución actual al margen_est).

- Cada bullet debe referenciar **qué métrica/tabla** del dashboard lo sustenta.

---

## 9) Memoria del agente (obligatorio)

- Mantener `/reports/cuaderno_agente.md` como **cuaderno vivo**. Debe registrar:

  - Lecturas iniciales (informe, repo).
  - Decisiones de limpieza/normalización y por qué.
  - Supuestos (e.g., “Vacío en medio_pago = EFECTIVO”).
  - Coberturas y limitaciones (p.ej., “márgenes estimados por % dep.”).
  - Cambios introducidos durante el análisis (paso 4 del usuario): métricas nuevas si detectaste una necesidad tras releer el informe.
  - Tareas cumplidas (checklist).

- Al finalizar, **resumen final** con links a artefactos generados y capturas del dashboard (si posible).

---

## 10) Validaciones, calidad y entregables

- **Validaciones**:

  - Totales de ventas por día/mes iguales entre items y tickets.
  - `monto_total_ticket ≈ Σ importe_total (líneas)`
  - Si hay horas, validar que “ciclo diario” no esté vacío.
  - Cobertura de `rentabilidad_pct` > **90%** de líneas. Listar faltantes si los hay.

- **Entregables mínimos**:

  - `/app/streamlit_app.py` (app completa, sin secretos).
  - `/data/processed/` con: `items.csv`, `tickets.csv`, `kpi_ciclos_*.csv`, `pareto_global.csv`, `pareto_mensual.csv`, `pareto_semana.csv`, `kpi_medios_pago.csv`, `data_dictionary.csv`.
  - `/reports/cuaderno_agente.md` (memoria) y `/reports/resumen_bullets.md`.
  - `/README.md` con **cómo correr** el pipeline y la app.

---

## 11) Notas técnicas (implementación sugerida)

- **Lectura CSV**: `pd.read_csv(..., sep=';', decimal=',', encoding='utf-8', low_memory=False)` con fallback `latin1`.
- **Ciclos**:

  - anual: `tickets.groupby('anio')`
  - mensual: `tickets.groupby('mes_str')` (`YYYY-MM`)
  - semanal: `tickets.groupby('semana_iso')`
  - diario: `tickets.groupby('fecha')`
  - “promedios estacionales”: agrupar por `month(fecha)`, por `weekday`, por `hour`.

- **Pareto**: por producto (`producto_id`, `producto`): ventas, margen_est, % acumulado, ABC. Repetir por `mes_str` y por `weekday`.
- **Medios de pago**: filtrar `fecha ∈ [2025-02-01, 2025-10-07]`. Mapear blanks=EFECTIVO; tabla de `% ventas` y `% tickets` por `medio_pago` y `emisor`.
- **Gráficos**: usar **Plotly** para interactividad (líneas, barras, box).
- **Caché**: `@st.cache_data` para lecturas pesadas.
- **Descargas**: `st.download_button` para CSVs.

---

## 12) Cierre

- **Releer el informe inicial** y, a la luz de los resultados, **agregar** cualquier **métrica complementaria** que sí sea posible con estos datos (ej.: _ticket promedio por departamento_, _participación de top-20 productos en margen_est por mes_, _participación de medios de pago en días valle/pico_).
- Actualizar el **cuaderno** con estas decisiones.
- En el **resumen final**, **vincular cada estrategia** propuesta con **1–2 KPIs** del dashboard y su **línea base** para seguimiento (_before/after_).

---

### Criterios de éxito

- El dashboard muestra **rentabilidad por ticket**, **desviación**, y **series cíclicas** (anual, mensual, semanal, diaria).
- El **Pareto de productos** está disponible **global y por ciclos**.
- Existen vistas y tablas por **medios de pago** (en su período disponible).
- El **informe narrativo** y el **cuaderno** documentan hallazgos y **estrategias soportadas por métricas**.
- Todo el trabajo es **reproducible** y **ejecutable** con `streamlit run app/streamlit_app.py`.

---

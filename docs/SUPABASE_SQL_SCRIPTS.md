# SQL Scripts para Limpiar y Repoblar Supabase

Este documento reúne los comandos SQL más comunes que usamos para dejar la base limpia y volver a cargar los datasets procesados. Todo el SQL puede ejecutarse desde el **SQL Editor** del dashboard de Supabase.

> ⚠️ Ajusta `<PROJECT_REF>` por el identificador de tu proyecto y actualiza las URLs de `COPY` según dónde subas los CSV (Storage público, S3 propio, etc.). Si prefieres seguir usando los scripts en Python (`scripts/clean_supabase.py` y `scripts/migrate_to_supabase.py`), estos comandos no son necesarios.

---

## 1. Limpiar Tablas Existentes

```sql
-- Desactiva temporalmente los triggers si tienes foreign keys (opcional)
-- ALTER TABLE items_ventas DISABLE TRIGGER ALL;

TRUNCATE TABLE
    items_ventas,
    tickets,
    reglas_asociacion,
    perfiles_clusters,
    pareto_productos,
    kpi_dia_semana,
    kpi_categoria,
    kpi_periodo
RESTART IDENTITY CASCADE;

-- Reactiva los triggers si los desactivaste
-- ALTER TABLE items_ventas ENABLE TRIGGER ALL;
```

---

## 2. Recrear el Esquema (por si necesitas redefinir tablas)

```sql
CREATE TABLE IF NOT EXISTS kpi_periodo (
    id SERIAL PRIMARY KEY,
    periodo VARCHAR(7) NOT NULL,
    ventas NUMERIC(15, 2),
    margen NUMERIC(15, 2),
    tickets INTEGER,
    ticket_promedio NUMERIC(15, 2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS kpi_categoria (
    id SERIAL PRIMARY KEY,
    categoria VARCHAR(100) NOT NULL,
    rentabilidad_pct NUMERIC(6, 2),
    ventas NUMERIC(15, 2),
    margen NUMERIC(15, 2),
    unidades NUMERIC(15, 3),
    tickets INTEGER,
    pct_ventas NUMERIC(6, 2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS kpi_dia_semana (
    id SERIAL PRIMARY KEY,
    dia_semana VARCHAR(20) NOT NULL,
    ventas NUMERIC(15, 2),
    tickets INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pareto_productos (
    id SERIAL PRIMARY KEY,
    producto_id VARCHAR(50) NOT NULL,
    descripcion VARCHAR(200),
    categoria VARCHAR(100),
    ventas NUMERIC(15, 2),
    unidades NUMERIC(15, 3),
    margen NUMERIC(15, 2),
    ventas_acumuladas NUMERIC(15, 2),
    pct_acumulado NUMERIC(6, 2),
    clasificacion_abc VARCHAR(1),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS perfiles_clusters (
    id SERIAL PRIMARY KEY,
    cluster INTEGER NOT NULL,
    cantidad_tickets INTEGER,
    ticket_promedio NUMERIC(15, 2),
    items_promedio NUMERIC(6, 2),
    margen_promedio NUMERIC(15, 2),
    pct_fin_semana NUMERIC(6, 2),
    pct_tickets NUMERIC(6, 2),
    etiqueta VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS reglas_asociacion (
    id SERIAL PRIMARY KEY,
    antecedents TEXT,
    consequents TEXT,
    support NUMERIC(12, 6),
    confidence NUMERIC(12, 6),
    lift NUMERIC(12, 6),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    ticket_id VARCHAR(50) NOT NULL UNIQUE,
    monto_total_ticket NUMERIC(15, 2),
    items_ticket INTEGER,
    margen_ticket NUMERIC(15, 2),
    fecha TIMESTAMP,
    periodo VARCHAR(7),
    dia_semana VARCHAR(20),
    es_fin_semana BOOLEAN,
    cluster INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS items_ventas (
    id SERIAL PRIMARY KEY,
    fecha TIMESTAMP,
    ticket_id VARCHAR(50),
    producto_id VARCHAR(50),
    categoria VARCHAR(100),
    descripcion VARCHAR(200),
    cantidad NUMERIC(12, 3),
    importe_total NUMERIC(15, 2),
    precio_unitario NUMERIC(15, 2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tickets_fecha ON tickets(fecha);
CREATE INDEX IF NOT EXISTS idx_tickets_id ON tickets(ticket_id);
CREATE INDEX IF NOT EXISTS idx_items_ticket ON items_ventas(ticket_id);
CREATE INDEX IF NOT EXISTS idx_items_categoria ON items_ventas(categoria);
CREATE INDEX IF NOT EXISTS idx_items_fecha ON items_ventas(fecha);
CREATE INDEX IF NOT EXISTS idx_pareto_clasificacion ON pareto_productos(clasificacion_abc);
```

---

## 3. Cargar Datos desde CSV con `COPY`

1. Sube cada CSV procesado de `data/processed/FASE1_OUTPUT` a Supabase Storage (por ejemplo, bucket público `analytics`).
2. Usa las rutas públicas del bucket en los comandos `COPY`.

```sql
-- KPIs por período
COPY kpi_periodo (periodo, ventas, margen, tickets, ticket_promedio)
FROM 'https://<PROJECT_REF>.supabase.co/storage/v1/object/public/analytics/03_KPI_PERIODO.csv'
WITH (FORMAT csv, DELIMITER ';', HEADER true, ENCODING 'UTF8');

-- KPIs por categoría
COPY kpi_categoria (categoria, rentabilidad_pct, ventas, margen, unidades, tickets, pct_ventas)
FROM 'https://<PROJECT_REF>.supabase.co/storage/v1/object/public/analytics/04_KPI_CATEGORIA.csv'
WITH (FORMAT csv, DELIMITER ';', HEADER true, ENCODING 'UTF8');

-- KPIs por día
COPY kpi_dia_semana (dia_semana, ventas, tickets)
FROM 'https://<PROJECT_REF>.supabase.co/storage/v1/object/public/analytics/08_KPI_DIA_SEMANA.csv'
WITH (FORMAT csv, DELIMITER ';', HEADER true, ENCODING 'UTF8');

-- Pareto de productos
COPY pareto_productos (producto_id, descripcion, categoria, ventas, unidades, margen, ventas_acumuladas, pct_acumulado, clasificacion_abc)
FROM 'https://<PROJECT_REF>.supabase.co/storage/v1/object/public/analytics/05_PARETO_PRODUCTOS.csv'
WITH (FORMAT csv, DELIMITER ';', HEADER true, ENCODING 'UTF8');

-- Perfiles de clusters
COPY perfiles_clusters (cluster, cantidad_tickets, ticket_promedio, items_promedio, margen_promedio, pct_fin_semana, pct_tickets, etiqueta)
FROM 'https://<PROJECT_REF>.supabase.co/storage/v1/object/public/analytics/07_PERFILES_CLUSTERS.csv'
WITH (FORMAT csv, DELIMITER ';', HEADER true, ENCODING 'UTF8');

-- Reglas de asociación (opcional)
COPY reglas_asociacion (antecedents, consequents, support, confidence, lift)
FROM 'https://<PROJECT_REF>.supabase.co/storage/v1/object/public/analytics/06_REGLAS_ASOCIACION.csv'
WITH (FORMAT csv, DELIMITER ';', HEADER true, ENCODING 'UTF8');

-- Tickets (resumen)
COPY tickets (ticket_id, monto_total_ticket, items_ticket, margen_ticket, fecha, periodo, dia_semana, es_fin_semana, cluster)
FROM 'https://<PROJECT_REF>.supabase.co/storage/v1/object/public/analytics/02_TICKETS.csv'
WITH (FORMAT csv, DELIMITER ';', HEADER true, ENCODING 'UTF8');

-- Items de ventas (solo si necesitas todo el detalle)
COPY items_ventas (fecha, ticket_id, producto_id, categoria, descripcion, cantidad, importe_total, precio_unitario)
FROM 'https://<PROJECT_REF>.supabase.co/storage/v1/object/public/analytics/01_ITEMS_VENTAS.csv'
WITH (FORMAT csv, DELIMITER ';', HEADER true, ENCODING 'UTF8');
```

> 💡 Si tus CSV usan coma decimal (`,`), convierte previamente la columna o usa `REPLACE` en una vista intermedia antes de insertar.

---

## 4. Validaciones Rápidas

```sql
SELECT COUNT(*) AS total_periodos FROM kpi_periodo;
SELECT COUNT(*) AS total_categorias FROM kpi_categoria;
SELECT COUNT(*) AS total_dias FROM kpi_dia_semana;
SELECT COUNT(*) AS total_pareto FROM pareto_productos;
SELECT COUNT(*) AS total_clusters FROM perfiles_clusters;
SELECT COUNT(*) AS total_tickets FROM tickets;
```

Cuando todos los conteos sean mayores a cero podrás consumirlos desde clientes externos o reactivar la integración en el dashboard. Por defecto, `app_streamlit_supabase.py` utiliza `data/app_dataset/`; si deseas volver a Supabase, restaura la lógica de conexión antes de desplegar.

---

**Última actualización:** 12/10/2025

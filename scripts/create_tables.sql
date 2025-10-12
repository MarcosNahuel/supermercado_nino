-- ================================================================================
-- CREAR TABLAS EN SUPABASE
-- Supermercado NINO - Esquema completo de base de datos
-- ================================================================================

-- Tabla de KPIs por período
CREATE TABLE IF NOT EXISTS kpi_periodo (
    id SERIAL PRIMARY KEY,
    periodo VARCHAR(7) NOT NULL,
    ventas DECIMAL(15, 2),
    margen DECIMAL(15, 2),
    tickets INTEGER,
    ticket_promedio DECIMAL(15, 2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de KPIs por categoría
CREATE TABLE IF NOT EXISTS kpi_categoria (
    id SERIAL PRIMARY KEY,
    categoria VARCHAR(100) NOT NULL,
    rentabilidad_pct DECIMAL(5, 2),
    ventas DECIMAL(15, 2),
    margen DECIMAL(15, 2),
    unidades INTEGER,
    tickets INTEGER,
    pct_ventas DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de KPIs por día de semana
CREATE TABLE IF NOT EXISTS kpi_dia_semana (
    id SERIAL PRIMARY KEY,
    dia_semana VARCHAR(20) NOT NULL,
    ventas DECIMAL(15, 2),
    tickets INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de Pareto (productos ABC)
CREATE TABLE IF NOT EXISTS pareto_productos (
    id SERIAL PRIMARY KEY,
    producto_id VARCHAR(50) NOT NULL,
    descripcion VARCHAR(200),
    categoria VARCHAR(100),
    ventas DECIMAL(15, 2),
    unidades INTEGER,
    margen DECIMAL(15, 2),
    ventas_acumuladas DECIMAL(15, 2),
    pct_acumulado DECIMAL(5, 2),
    clasificacion_abc VARCHAR(1),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de perfiles de clusters
CREATE TABLE IF NOT EXISTS perfiles_clusters (
    id SERIAL PRIMARY KEY,
    cluster INTEGER NOT NULL,
    cantidad_tickets INTEGER,
    ticket_promedio DECIMAL(15, 2),
    items_promedio DECIMAL(5, 2),
    margen_promedio DECIMAL(15, 2),
    pct_fin_semana DECIMAL(5, 2),
    pct_tickets DECIMAL(5, 2),
    etiqueta VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de reglas de asociación
CREATE TABLE IF NOT EXISTS reglas_asociacion (
    id SERIAL PRIMARY KEY,
    antecedents TEXT,
    consequents TEXT,
    support DECIMAL(10, 6),
    confidence DECIMAL(10, 6),
    lift DECIMAL(10, 4),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de tickets (resumen)
CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    ticket_id VARCHAR(50) NOT NULL UNIQUE,
    monto_total_ticket DECIMAL(15, 2),
    items_ticket INTEGER,
    margen_ticket DECIMAL(15, 2),
    fecha TIMESTAMP,
    periodo VARCHAR(7),
    dia_semana VARCHAR(20),
    es_fin_semana BOOLEAN,
    cluster INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de items de ventas (más pesada)
CREATE TABLE IF NOT EXISTS items_ventas (
    id SERIAL PRIMARY KEY,
    fecha TIMESTAMP,
    ticket_id VARCHAR(50),
    producto_id VARCHAR(50),
    categoria VARCHAR(100),
    descripcion VARCHAR(200),
    cantidad DECIMAL(10, 3),
    importe_total DECIMAL(15, 2),
    precio_unitario DECIMAL(15, 2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_tickets_fecha ON tickets(fecha);
CREATE INDEX IF NOT EXISTS idx_tickets_id ON tickets(ticket_id);
CREATE INDEX IF NOT EXISTS idx_items_ticket ON items_ventas(ticket_id);
CREATE INDEX IF NOT EXISTS idx_items_categoria ON items_ventas(categoria);
CREATE INDEX IF NOT EXISTS idx_items_fecha ON items_ventas(fecha);
CREATE INDEX IF NOT EXISTS idx_pareto_clasificacion ON pareto_productos(clasificacion_abc);

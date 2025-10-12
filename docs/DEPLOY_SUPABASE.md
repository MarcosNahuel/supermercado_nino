si# 🚀 Guía Completa de Deploy con Supabase

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Problema Original](#problema-original)
3. [Solución con Supabase](#solución-con-supabase)
4. [Configuración Inicial](#configuración-inicial)
5. [Migración de Datos](#migración-de-datos)
6. [Deploy en Streamlit Cloud](#deploy-en-streamlit-cloud)
7. [Mantenimiento](#mantenimiento)

---

## 🎯 Introducción

Esta guía documenta la solución implementada para superar las limitaciones de tamaño de GitHub (100MB) al deployar el dashboard de Supermercado NINO.

### Archivos Actualizados en Esta Solución

- ✅ `FASE1_ANALISIS_COMPLETO.py` - Actualizado para usar `SERIE_COMPROBANTES_COMPLETOS2.csv`
- ✅ `app_streamlit_supabase.py` - Nueva versión con soporte para Supabase
- ✅ `scripts/migrate_to_supabase.py` - Script de migración de datos
- ✅ `requirements.txt` - Dependencias actualizadas
- ✅ `.env` y `.env.example` - Configuración de credenciales
- ✅ `.gitignore` - Excluye archivos sensibles

---

## ⚠️ Problema Original

### Situación

- **Archivo CSV:** `SERIE_COMPROBANTES_COMPLETOS2.csv`
- **Tamaño:** 378 MB (2,944,660 registros)
- **Límite de GitHub:** 100 MB por archivo
- **Resultado:** Imposible subir el dataset al repositorio

### Intentos Previos

- ❌ Git LFS (Git Large File Storage) - Requiere pago para ancho de banda
- ❌ Compresión - Archivo sigue siendo muy grande
- ❌ GitHub Releases - Mismo límite de 100 MB

---

## ✅ Solución con Supabase

### Por Qué Supabase

1. **Base de Datos PostgreSQL en la Nube:** Gratuita hasta 500MB
2. **API REST Automática:** Acceso inmediato a los datos
3. **Sin Límites de Tamaño de Archivo:** Los datos están en una base de datos
4. **Integración Simple con Streamlit:** SDK de Python oficial
5. **Gratuito para Proyectos Pequeños:** Perfecto para dashboards PYME

### Arquitectura de la Solución

```
┌─────────────────────┐
│   CSV Local (378MB) │
│                     │
└──────────┬──────────┘
           │
           │ migrate_to_supabase.py
           ▼
    ┌─────────────────┐
    │   Supabase DB   │
    │  (PostgreSQL)   │
    └─────────┬───────┘
              │
              │ Supabase API
              ▼
       ┌──────────────┐
       │  Streamlit   │
       │  Cloud App   │
       └──────────────┘
```

---

## 🔧 Configuración Inicial

### 1. Crear Cuenta en Supabase

1. Ve a [https://supabase.com](https://supabase.com)
2. Registra una cuenta gratuita
3. Crea un nuevo proyecto:
   - Nombre: `supermercado-nino`
   - Base de datos: (genera una contraseña fuerte)
   - Región: South America (más cercano)

### 2. Obtener Credenciales

En el Dashboard de Supabase:

1. Ve a **Settings** > **API**
2. Copia:
   - **Project URL:** `https://xxxxx.supabase.co`
   - **anon public key:** `eyJhbGciOiJIUzI1NiI...`

### 3. Configurar Variables de Entorno

#### Opción A: Archivo .env (desarrollo local)

Crea `.env` en la raíz del proyecto:

```bash
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-anon-key-aqui
```

#### Opción B: Streamlit Secrets (producción)

En Streamlit Cloud, ve a **Settings** > **Secrets** y agrega:

```toml
SUPABASE_URL = "https://tu-proyecto.supabase.co"
SUPABASE_KEY = "tu-anon-key-aqui"
```

### 4. Instalar Dependencias

```bash
pip install -r requirements.txt
```

Asegúrate de que `requirements.txt` incluya:

```
supabase>=2.0.0
python-dotenv>=1.0.0
tqdm>=4.66.0
```

---

## 📊 Migración de Datos

### Paso 1: Crear Tablas en Supabase

En el **SQL Editor** de Supabase, ejecuta:

```sql
-- Tabla de KPIs por período
CREATE TABLE kpi_periodo (
    id SERIAL PRIMARY KEY,
    periodo VARCHAR(7) NOT NULL,
    ventas DECIMAL(15, 2),
    margen DECIMAL(15, 2),
    tickets INTEGER,
    ticket_promedio DECIMAL(15, 2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de KPIs por categoría
CREATE TABLE kpi_categoria (
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
CREATE TABLE kpi_dia_semana (
    id SERIAL PRIMARY KEY,
    dia_semana VARCHAR(20) NOT NULL,
    ventas DECIMAL(15, 2),
    tickets INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de Pareto (productos ABC)
CREATE TABLE pareto_productos (
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
CREATE TABLE perfiles_clusters (
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
CREATE TABLE reglas_asociacion (
    id SERIAL PRIMARY KEY,
    antecedents TEXT,
    consequents TEXT,
    support DECIMAL(10, 6),
    confidence DECIMAL(10, 6),
    lift DECIMAL(10, 4),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de tickets (resumen)
CREATE TABLE tickets (
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

-- Tabla de items de ventas (más pesada - opcional)
CREATE TABLE items_ventas (
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
CREATE INDEX idx_tickets_fecha ON tickets(fecha);
CREATE INDEX idx_tickets_id ON tickets(ticket_id);
CREATE INDEX idx_items_ticket ON items_ventas(ticket_id);
CREATE INDEX idx_items_categoria ON items_ventas(categoria);
CREATE INDEX idx_items_fecha ON items_ventas(fecha);
CREATE INDEX idx_pareto_clasificacion ON pareto_productos(clasificacion_abc);
```

### Paso 2: Ejecutar Script de Migración

```bash
python scripts/migrate_to_supabase.py
```

#### Qué Hace el Script

1. **Lee credenciales** desde `.env`
2. **Conecta a Supabase**
3. **Migra tablas ligeras** (KPIs, Pareto, Clusters)
4. **Migra tickets** en chunks de 1,000 registros
5. **Migra items** en chunks de 500 registros (modo demo: primeros 100k)
6. **Muestra progreso** con barra de tqdm

#### Notas Importantes

- ⏱️ **Tiempo estimado:** 30-60 minutos para migración completa
- 💾 **Modo demo:** Por defecto migra solo 100k items (quita el límite para full migration)
- 🔄 **Re-ejecutable:** Puedes detener y reanudar (si las tablas están vacías)
- ❌ **Duplicados:** Si la tabla ya tiene datos, fallará (elimina registros primero)

### Paso 3: Verificar Datos

1. Ve al **Table Editor** en Supabase Dashboard
2. Verifica que las tablas tengan datos:
   - `kpi_periodo`: ~13 registros (meses)
   - `kpi_categoria`: ~45 registros (categorías)
   - `pareto_productos`: ~10,000 registros (productos)
   - `tickets`: ~306,000 registros
   - `items_ventas`: ~100,000 registros (modo demo) o ~3M (full)

---

## ☁️ Deploy en Streamlit Cloud

### Paso 1: Preparar Repositorio

#### 1. Asegúrate de que `.gitignore` excluye archivos sensibles:

```gitignore
# Environment variables
.env
.env.local
.streamlit/secrets.toml

# Data files
data/raw/
*.csv
!data/sample/**
```

#### 2. Commit y push de cambios:

```bash
git add .
git commit -m "Implementa integración con Supabase para deploy sin límites de tamaño"
git push origin main
```

### Paso 2: Deploy en Streamlit Cloud

1. Ve a [https://streamlit.io/cloud](https://streamlit.io/cloud)
2. Haz clic en **New app**
3. Selecciona tu repositorio: `MarcosNahuel/supermercado_nino`
4. **Main file path:** `app_streamlit_supabase.py`
5. **Python version:** 3.10 (recomendado)

### Paso 3: Configurar Secrets

En **Advanced settings** > **Secrets**:

```toml
SUPABASE_URL = "https://yebiszzkrgapfqwngbwj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InllYmlzenprcmdhcGZxd25nYndqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzkxMDM1ODEsImV4cCI6MjA1NDY3OTU4MX0.4iQFcFwQaH5NDV3op0AUxWxkFjNXVCL0degCThMiU8E"
```

### Paso 4: Deploy

- Haz clic en **Deploy!**
- Espera 3-5 minutos
- ✅ La app estará disponible en: `https://tu-app.streamlit.app`

---

## 🔄 Mantenimiento

### Actualizar Datos

Cuando tengas nuevos datos:

1. **Actualiza el CSV local** con los datos nuevos
2. **Borra tablas en Supabase** (SQL Editor):

```sql
TRUNCATE TABLE kpi_periodo, kpi_categoria, kpi_dia_semana,
              pareto_productos, perfiles_clusters, reglas_asociacion,
              tickets, items_ventas CASCADE;
```

3. **Re-ejecuta la migración:**

```bash
python scripts/migrate_to_supabase.py
```

4. **Reinicia la app en Streamlit Cloud** (se recarga automáticamente tras 1 hora de cache)

### Monitoreo

#### En Supabase Dashboard:

- **Database** > **Database**: Ver uso de almacenamiento
- **API**: Ver requests y límites
- **Logs**: Depurar errores

#### Límites del Plan Gratuito:

- 📊 **Almacenamiento:** 500 MB
- 🔌 **API Calls:** 50,000 requests/mes
- 👥 **Usuarios activos:** Ilimitados (anon key)

### Optimización

Si alcanzas límites, considera:

1. **Implementar paginación** en queries grandes
2. **Aumentar cache TTL** en Streamlit (de 1 hora a 24 horas)
3. **Eliminar columnas innecesarias** (reduce tamaño de DB)
4. **Agregar más índices** para queries frecuentes
5. **Upgrade a plan Pro** ($25/mes - 8GB storage)

---

## 🎯 Resultados

### Antes (Sin Supabase)

❌ CSV de 378MB no se podía subir a GitHub
❌ Imposible deployar en Streamlit Cloud
❌ Alternativas (Git LFS) eran costosas o complejas

### Después (Con Supabase)

✅ Datos alojados en Supabase (gratis)
✅ Repositorio limpio (solo código, sin CSVs grandes)
✅ Deploy exitoso en Streamlit Cloud
✅ App carga datos desde la nube en <2 segundos
✅ Escalable y mantenible

---

## 📞 Soporte

Si tienes problemas:

1. **Revisa logs en Supabase Dashboard:** Settings > Logs
2. **Verifica credenciales:** Asegúrate de que SUPABASE_URL y SUPABASE_KEY sean correctos
3. **Chequea límites:** Database > Database Usage
4. **Consulta documentación:** [https://supabase.com/docs](https://supabase.com/docs)

---

## 📚 Referencias

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Python Client](https://github.com/supabase-community/supabase-py)
- [Streamlit Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [PostgreSQL Best Practices](https://wiki.postgresql.org/wiki/Don%27t_Do_This)

---

**Autor:** pymeinside.com
**Fecha:** Octubre 2025
**Versión:** 2.0
**Proyecto:** Supermercado NINO - Dashboard de Análisis de Ventas

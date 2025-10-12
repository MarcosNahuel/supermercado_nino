# 🚀 Guía Completa de Deploy en Streamlit Cloud

## 📋 Resumen de la Arquitectura

**Problema:** Archivos CSV demasiado grandes (1.1GB) exceden el límite de GitHub (100MB)

**Solución:**
- 📦 **Datos:** Supabase Cloud (PostgreSQL gratis)
- 🌐 **App:** Streamlit Cloud (hosting gratis)
- 💻 **Código:** GitHub (solo código, sin datos)

---

## ✅ Pre-requisitos Completados

- [x] `.gitignore` configurado para excluir archivos grandes
- [x] `app_streamlit_supabase.py` listo (carga desde Supabase)
- [x] `requirements.txt` actualizado con `supabase` y `python-dotenv`
- [x] Configuración de Supabase en `.env` (no se sube a Git)

---

## 🗂️ PASO 1: Limpiar y Migrar Datos a Supabase

### 1.1 Borrar Datos Antiguos en Supabase Dashboard

1. Ve a: https://supabase.com/dashboard/project/yebiszzkrgapfqwngbwj/editor

2. Para cada tabla grande, haz click derecho → **"Truncate table"**:
   - `items_ventas`
   - `tickets`

3. Las demás tablas ya fueron limpiadas automáticamente

### 1.2 Ejecutar Migración Completa

```bash
# Desde la raíz del proyecto
python scripts/migrate_to_supabase.py
```

**Tiempo estimado:** 15-20 minutos (migrará ~3M registros)

**Progreso esperado:**
- ✅ KPIs (instantáneo)
- ✅ Tickets (5 min)
- ✅ Items de ventas (10-15 min)

### 1.3 Verificar Migración

Ejecuta queries en Supabase SQL Editor:

```sql
-- Verificar totales
SELECT
  'kpi_periodo' as tabla, COUNT(*) as registros FROM kpi_periodo
UNION ALL
SELECT 'kpi_categoria', COUNT(*) FROM kpi_categoria
UNION ALL
SELECT 'tickets', COUNT(*) FROM tickets
UNION ALL
SELECT 'items_ventas', COUNT(*) FROM items_ventas;
```

**Resultados esperados:**
- kpi_periodo: **13**
- kpi_categoria: **48**
- kpi_dia_semana: **7**
- pareto_productos: **10,372**
- tickets: **306,011**
- items_ventas: **~2,944,659**

---

## 📤 PASO 2: Subir Código a GitHub

### 2.1 Verificar que NO se suben archivos grandes

```bash
# Verificar archivos modificados
git status

# IMPORTANTE: NO deberías ver ningún .csv grande
# Solo deberías ver archivos .py, .md, .toml
```

### 2.2 Commit y Push

```bash
git add .
git commit -m "Preparar app para deploy en Streamlit Cloud con Supabase"
git push origin main
```

### 2.3 Verificar tamaño del repo

```bash
# El repo NO debe exceder 100MB
git count-objects -vH
```

---

## 🌐 PASO 3: Deploy en Streamlit Cloud

### 3.1 Crear App en Streamlit Cloud

1. Ve a: https://share.streamlit.io/
2. Click en **"New app"**
3. Conecta tu cuenta de GitHub si aún no lo has hecho

### 3.2 Configurar el Deploy

- **Repository:** `MarcosNahuel/supermercado_nino`
- **Branch:** `main`
- **Main file path:** `app_streamlit_supabase.py` ⚠️ **IMPORTANTE: usar la versión Supabase**
- **Python version:** 3.10

### 3.3 Configurar Secrets (Variables de Entorno)

En Streamlit Cloud, click en **"Advanced settings"** → **"Secrets"**

Copia y pega esto:

```toml
SUPABASE_URL = "https://yebiszzkrgapfqwngbwj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InllYmlzenprcmdhcGZxd25nYndqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzkxMDM1ODEsImV4cCI6MjA1NDY3OTU4MX0.4iQFcFwQaH5NDV3op0AUxWxkFjNXVCL0degCThMiU8E"
```

### 3.4 Deploy

1. Click en **"Deploy!"**
2. Espera 2-3 minutos mientras instala dependencias
3. Tu app estará disponible en: `https://[tu-nombre-app].streamlit.app`

---

## ✅ PASO 4: Verificar Funcionamiento

Una vez deployada, verifica:

### 4.1 Checks de Funcionamiento

✅ La app carga sin errores
✅ Sidebar muestra "✅ Conectado a Supabase"
✅ KPIs muestran datos correctos:
- Total Ventas: **~$8.2M**
- Tickets: **306,011**
- Margen: **~28%**

✅ Todas las secciones cargan:
- 🏠 Resumen Ejecutivo
- 📈 Análisis Pareto
- 🛒 Market Basket
- 👥 Segmentación
- 💰 Rentabilidad
- 📅 Análisis Temporal

### 4.2 Si hay errores

**Error: "No se pudieron cargar los datos"**
- Verifica que los secrets están correctamente configurados
- Revisa los logs en Streamlit Cloud

**Error: "Tabla no existe"**
- Ejecuta nuevamente la migración a Supabase
- Verifica en Supabase Dashboard que las tablas existen

---

## 🎨 PASO 5: Personalizar tu App (Opcional)

### 5.1 Cambiar URL de la app

En Streamlit Cloud → Settings → **"General"** → Cambiar app name

### 5.2 Agregar dominio personalizado

Streamlit Cloud → Settings → **"Domain"** → Agregar tu dominio

---

## 📊 Métricas Esperadas del Dashboard

Una vez deployado, tu dashboard mostrará:

### KPIs Globales
- 💰 Total Ventas: **$8,216,314,170.99**
- 💎 Margen: **$2,318,614,454.34 (28.22%)**
- 📝 Tickets: **306,011**
- 🛒 Ticket Promedio: **$26,849.73**
- 📦 Items/Ticket: **10.1 unidades**
- 📈 Productos: **10,372 SKUs**

### Análisis Pareto
- 🏆 Productos A: **1,389 (13.4%)** → generan **80%** de ventas
- 📊 Productos B: **2,688 (25.9%)** → generan **15%** de ventas
- 📉 Productos C: **6,295 (60.7%)** → generan **5%** de ventas

### Market Basket
- 🔝 Regla estrella: **FERNET + COCA COLA** (Lift **33.69x**)
- 📈 95 reglas de asociación detectadas

---

## 🔧 Mantenimiento y Actualización

### Actualizar Datos

Si quieres actualizar los datos en el futuro:

```bash
# 1. Procesar nuevos datos localmente
python FASE1_ANALISIS_COMPLETO.py

# 2. Limpiar Supabase (opcional si quieres reemplazar)
python scripts/clean_supabase.py

# 3. Migrar nuevos datos
python scripts/migrate_to_supabase.py

# 4. Reiniciar app en Streamlit Cloud (para limpiar cache)
# Streamlit Cloud → ⋮ → "Reboot app"
```

### Actualizar Código

```bash
# 1. Hacer cambios en app_streamlit_supabase.py
git add app_streamlit_supabase.py
git commit -m "Actualizar dashboard"
git push origin main

# 2. Streamlit Cloud detectará los cambios y redesplegará automáticamente
```

---

## 🆘 Solución de Problemas

### Error: "Repository too large"

Si ves este error al hacer push:

```bash
# Verificar archivos grandes
git ls-files --cached | xargs ls -lh | sort -k5 -rh | head -20

# Si hay CSVs grandes, agregarlos al .gitignore
echo "ruta/al/archivo.csv" >> .gitignore
git rm --cached ruta/al/archivo.csv
git commit -m "Remover archivo grande"
git push
```

### Error: "Rate limit exceeded" en Supabase

Durante la migración, si ves este error:

```bash
# El script ya tiene rate limiting (sleep de 0.1s)
# Si persiste, edita scripts/migrate_to_supabase.py:
# Línea 83: time.sleep(0.1) → time.sleep(0.5)
```

### App muy lenta

Si la app carga lento:

1. **Reducir muestra de datos en app_streamlit_supabase.py:**
   ```python
   # Línea 266: Cambiar limit
   data['tickets'] = pd.DataFrame(_supabase_client.table('tickets').select('*').limit(5000).execute().data)
   ```

2. **Crear índices en Supabase:**
   ```sql
   CREATE INDEX idx_items_ticket ON items_ventas(ticket_id);
   CREATE INDEX idx_items_categoria ON items_ventas(categoria);
   CREATE INDEX idx_items_fecha ON items_ventas(fecha);
   ```

---

## 📚 Recursos

- 📖 [Documentación Streamlit Cloud](https://docs.streamlit.io/streamlit-community-cloud)
- 📖 [Documentación Supabase](https://supabase.com/docs)
- 🌐 [Supabase Dashboard](https://supabase.com/dashboard/project/yebiszzkrgapfqwngbwj)
- 🚀 [Streamlit Cloud Apps](https://share.streamlit.io/)

---

## 🎉 ¡Listo!

Tu dashboard estará disponible públicamente en:
```
https://[tu-app-name].streamlit.app
```

Podrás compartirlo con clientes, stakeholders, o usarlo para presentaciones sin necesidad de instalar nada.

**Desarrollado por:** [pymeinside.com](https://pymeinside.com)
**Cliente:** Supermercado NINO
**Versión:** 2.0 (Octubre 2025)

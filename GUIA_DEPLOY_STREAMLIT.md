# Guía para Deploy en Streamlit Cloud

## Acceso a la Aplicación Local

**La aplicación ya está corriendo localmente en:**
- Local: http://localhost:8501
- Red: http://192.168.0.101:8501

## Datos Actualizados

✅ Las métricas ahora reflejan los datos de `SERIE_COMPROBANTES_COMPLETOS2.csv`:
- 📊 Total Ventas: **$8,216,314,170.99**
- 💎 Margen: **$2,318,614,454.34 (28.22%)**
- 📝 Tickets: **306,011**
- 🛒 Ticket Promedio: **$26,849.73**
- 📦 Items/Ticket: **10.1 unidades**
- 📈 Productos: **10,372 SKUs**
- 🎯 Pareto: **13.4%** de productos generan **80%** de ventas

## Deploy en Streamlit Cloud (GRATIS)

### Opción 1: Deploy con Datos de Muestra (Recomendado para compartir públicamente)

**Ventaja:** Deploy rápido sin problemas de tamaño de archivos.

#### Paso 1: Preparar el repositorio

```bash
# Asegúrate de que los cambios estén en Git
git status
git add .
git commit -m "Actualizar dashboard con datos procesados"
git push origin main
```

#### Paso 2: Crear cuenta en Streamlit Cloud

1. Ve a https://share.streamlit.io/
2. Inicia sesión con tu cuenta de GitHub
3. Haz clic en "New app"

#### Paso 3: Configurar el deploy

- **Repository:** `MarcosNahuel/supermercado_nino`
- **Branch:** `main`
- **Main file path:** `app_streamlit.py`

#### Paso 4: Configurar archivos de muestra

Como los archivos procesados son grandes (2.9M registros), usa los datos de muestra:

1. Crea la carpeta `data/sample/FASE1_OUTPUT_SAMPLE/`
2. Copia una muestra de los archivos procesados (primeras 10,000 filas de cada CSV)
3. La aplicación detectará automáticamente que está usando datos de muestra

#### Paso 5: Deploy

Haz clic en "Deploy" y espera 2-5 minutos. Tu app estará disponible en:
`https://[tu-nombre-app].streamlit.app`

---

### Opción 2: Deploy con Supabase (Datos Completos)

**Ventaja:** Todos los datos completos disponibles en la nube.

#### Paso 1: Crear proyecto en Supabase

1. Ve a https://supabase.com y crea una cuenta
2. Crea un nuevo proyecto
3. Copia tu URL y tu `anon` key

#### Paso 2: Migrar datos a Supabase

```bash
# Crear archivo .env con tus credenciales
echo "SUPABASE_URL=https://tu-proyecto.supabase.co" > .env
echo "SUPABASE_KEY=tu-anon-key-aqui" >> .env

# Ejecutar migración
python scripts/migrate_to_supabase.py
```

#### Paso 3: Deploy en Streamlit Cloud

1. Ve a https://share.streamlit.io/
2. Crea nueva app apuntando a `app_streamlit_supabase.py`
3. En "Advanced settings" > "Secrets", agrega:

```toml
SUPABASE_URL = "https://tu-proyecto.supabase.co"
SUPABASE_KEY = "tu-anon-key-aqui"
```

4. Haz clic en "Deploy"

Tu app estará disponible con todos los datos completos.

---

### Opción 3: Deploy Local con Túnel (Para pruebas rápidas)

Si solo quieres compartir temporalmente:

```bash
# Instalar localtunnel
npm install -g localtunnel

# En otra terminal, crear túnel
lt --port 8501

# Te dará una URL pública temporal como:
# https://xxxx.loca.lt
```

---

## Verificar Deploy

Una vez deployada, verifica:

✅ La página carga sin errores
✅ Los KPIs muestran las métricas correctas
✅ Los gráficos se renderizan correctamente
✅ Los filtros funcionan
✅ Las diferentes secciones cargan bien

## Compartir la Aplicación

Una vez deployada en Streamlit Cloud, simplemente comparte el link:

```
https://tu-app.streamlit.app
```

## Solución de Problemas

### Error: "File too large"

**Solución:** Usa datos de muestra o migra a Supabase (Opción 2)

### Error: "Module not found"

**Solución:** Verifica que `requirements.txt` incluya todas las dependencias

### La app no carga datos

**Solución:**
- Verifica que exista la carpeta `data/processed/FASE1_OUTPUT/` con los archivos CSV
- O usa la carpeta de muestra `data/sample/FASE1_OUTPUT_SAMPLE/`

### Error de memoria en Streamlit Cloud

**Solución:**
- Reduce el tamaño de los datos usando muestreo
- O migra a Supabase para datos en la nube

---

## Recursos Adicionales

- 📖 [Documentación de Streamlit Cloud](https://docs.streamlit.io/streamlit-community-cloud)
- 📖 [Guía de Deploy con Supabase](docs/DEPLOY_SUPABASE.md)
- 🌐 [Streamlit Community Forum](https://discuss.streamlit.io/)

---

**Desarrollado por:** pymeinside.com
**Cliente:** Supermercado NINO
**Versión:** 2.0 (Octubre 2025)

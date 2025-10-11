# 🏷️ Guía: GitHub Releases

## 🎯 Ventajas
- ✅ **2GB por archivo** (gratis)
- ✅ Integrado con Git
- ✅ Control de versiones
- ✅ Público o privado
- ✅ URL directa de descarga

## 📋 Pasos para Crear Release

### 1. Preparar el Archivo

```bash
# Si aún no está comprimido:
python scripts/comprimir_datos.py

# Verifica el tamaño
ls -lh datos/SERIE_COMPROBANTES_COMPLETOS.csv.gz
# Debe ser ~20MB (menor a 2GB)
```

### 2. Crear Release en GitHub Web

1. Ve a tu repositorio en GitHub
2. Click en **"Releases"** (barra lateral derecha)
3. Click en **"Create a new release"**

### 3. Configurar Release

**Tag version:** `v1.0-data`
**Release title:** `Datos de Análisis v1.0`
**Description:**
```markdown
# Datos de Análisis - Supermercado NINO

Contiene:
- SERIE_COMPROBANTES_COMPLETOS.csv.gz (20.65 MB)
- Período: Octubre 2024 - Septiembre 2025
- 2,305,235 registros

## Uso
```bash
python scripts/descargar_github_release.py
```
```

### 4. Subir Archivo como Asset

1. En la sección **"Attach binaries"**
2. Arrastra o selecciona: `SERIE_COMPROBANTES_COMPLETOS.csv.gz`
3. Click **"Publish release"**

### 5. Obtener URL de Descarga

La URL será:
```
https://github.com/MarcosNahuel/supermercado_nino/releases/download/v1.0-data/SERIE_COMPROBANTES_COMPLETOS.csv.gz
```

### 6. Configurar Script de Descarga

Edita `scripts/descargar_github_release.py`:

```python
GITHUB_USER = "MarcosNahuel"
GITHUB_REPO = "supermercado_nino"
RELEASE_TAG = "v1.0-data"
FILE_NAME = "SERIE_COMPROBANTES_COMPLETOS.csv.gz"
```

### 7. Descargar Automáticamente

```bash
python scripts/descargar_github_release.py
```

## 🔄 Integración con Streamlit

Agregar a `app_streamlit.py`:

```python
from pathlib import Path
import subprocess
import streamlit as st

def download_data_if_needed():
    """Descarga datos desde GitHub Release si no existen."""
    data_file = Path("datos/SERIE_COMPROBANTES_COMPLETOS.csv")
    
    if not data_file.exists():
        with st.spinner("📥 Descargando datos desde GitHub Release..."):
            subprocess.run(["python", "scripts/descargar_github_release.py"])
        
        if data_file.exists():
            st.success("✅ Datos descargados correctamente")
            st.rerun()
        else:
            st.warning("⚠️ Usando datos de muestra")

# Ejecutar al inicio
download_data_if_needed()
```

## 📊 Límites de GitHub Releases

| Límite | Valor |
|--------|-------|
| Tamaño máximo por archivo | 2 GB |
| Número de archivos por release | Ilimitado |
| Tamaño total del release | Ilimitado |
| Ancho de banda | Ilimitado* |

*Sin límites documentados para releases públicos

## 🚀 Ventajas vs Google Drive

| Característica | GitHub Releases | Google Drive |
|---------------|-----------------|--------------|
| **Tamaño max archivo** | 2GB | Ilimitado (15GB cuenta gratis) |
| **Integración Git** | ✅ Nativa | ❌ Externa |
| **Versionado** | ✅ Automático | ❌ Manual |
| **Privacidad** | ✅ Sigue repo | ⚠️ Requiere config |
| **Velocidad descarga** | ⚡ Muy rápida | ⚡ Muy rápida |
| **API pública** | ✅ Simple | ⚠️ Requiere auth |

## 💡 Casos de Uso Recomendados

### Usa GitHub Releases si:
- ✅ Datos versionados (cambios frecuentes)
- ✅ Proyecto open source
- ✅ Archivos < 2GB
- ✅ Quieres todo en un solo lugar

### Usa Google Drive si:
- ✅ Archivos > 2GB
- ✅ Colaboración con no-programadores
- ✅ Necesitas más espacio (15GB gratis)
- ✅ Datos privados compartidos

## 🔧 Comandos Útiles

### Crear Release desde CLI (gh CLI)

```bash
# Instalar GitHub CLI: https://cli.github.com/

# Autenticar
gh auth login

# Crear release con archivo
gh release create v1.0-data \
  datos/SERIE_COMPROBANTES_COMPLETOS.csv.gz \
  --title "Datos de Análisis v1.0" \
  --notes "Datos procesados del período 2024-2025"

# Listar releases
gh release list

# Descargar asset
gh release download v1.0-data \
  --pattern "*.csv.gz" \
  --dir datos/
```

## 📝 Ejemplo Completo

```python
# auto_download.py
import requests
from pathlib import Path

def download_from_github_release():
    url = "https://github.com/MarcosNahuel/supermercado_nino/releases/download/v1.0-data/SERIE_COMPROBANTES_COMPLETOS.csv.gz"
    output = Path("datos/SERIE_COMPROBANTES_COMPLETOS.csv.gz")
    
    if not output.exists():
        print("Descargando datos...")
        response = requests.get(url, stream=True)
        with open(output, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("✅ Descarga completa")
    else:
        print("✅ Datos ya disponibles")

if __name__ == "__main__":
    download_from_github_release()
```

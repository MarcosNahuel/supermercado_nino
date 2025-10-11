# 📦 Guía: Almacenamiento en Google Drive

## 🎯 Ventajas
- ✅ **15GB gratis** (suficiente para todos tus datos)
- ✅ Fácil de configurar
- ✅ Funciona en Streamlit Cloud
- ✅ Compartible con el equipo

## 📋 Pasos Completos

### 1. Subir Archivo a Google Drive

1. Ve a [drive.google.com](https://drive.google.com)
2. Sube `SERIE_COMPROBANTES_COMPLETOS.csv` (o la versión .gz)
3. Click derecho en el archivo → **Obtener enlace**
4. Cambia a: **"Cualquiera con el enlace"**
5. Copia el enlace completo

**Ejemplo de URL:**
```
https://drive.google.com/file/d/1xYz_ABC123def456GHI789jkl/view?usp=sharing
```

**Tu File ID es:** `1xYz_ABC123def456GHI789jkl` (la parte del medio)

### 2. Configurar Script de Descarga

Edita `scripts/descargar_google_drive.py`:

```python
# Línea 17: Reemplaza con tu File ID
GOOGLE_DRIVE_FILE_ID = "1xYz_ABC123def456GHI789jkl"
```

### 3. Instalar Dependencia

```bash
pip install gdown
```

Agregar a `requirements.txt`:
```
gdown>=4.7.1
```

### 4. Descargar Localmente

```bash
python scripts/descargar_google_drive.py
```

### 5. Integrar con Streamlit

Agregar al inicio de `app_streamlit.py`:

```python
import os
from pathlib import Path

# Auto-descargar datos si no existen
def setup_data():
    data_file = Path("datos/SERIE_COMPROBANTES_COMPLETOS.csv")
    
    if not data_file.exists():
        st.info("📥 Descargando datos desde Google Drive...")
        import subprocess
        subprocess.run([
            "python", 
            "scripts/descargar_google_drive.py"
        ])
        st.rerun()

# Ejecutar al inicio
setup_data()
```

### 6. Deploy en Streamlit Cloud

1. Sube el código a GitHub (sin el CSV grande)
2. Configura Streamlit Cloud
3. Los datos se descargarán automáticamente al iniciar

## 🔒 Seguridad

### Opción A: Enlace Público
- **Pros**: Simple, funciona directamente
- **Contras**: Cualquiera con el enlace puede descargar

### Opción B: Con Credenciales (Recomendado para producción)

1. Crear Service Account en Google Cloud
2. Compartir archivo con el email del service account
3. Usar PyDrive o google-drive-api

```python
# Ejemplo con credenciales
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SERVICE_ACCOUNT_FILE = 'credentials.json'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('drive', 'v3', credentials=credentials)
```

## 📊 Límites de Google Drive

| Plan | Almacenamiento | Transferencia | Costo |
|------|----------------|---------------|-------|
| **Gratis** | 15 GB | Ilimitada* | $0 |
| **Google One 100GB** | 100 GB | Ilimitada* | $1.99/mes |
| **Google One 200GB** | 200 GB | Ilimitada* | $2.99/mes |

*Límite de 750GB/día por usuario

## 🚀 Alternativas Rápidas

### OneDrive (si ya lo usas)
```python
# Similar a Google Drive, pero con OneDrive API
# Límite: 5GB gratis
```

### Dropbox
```python
import dropbox
# Límite: 2GB gratis
```

## 💡 Recomendación Final

**Para tu proyecto:**
1. Usar `.csv.gz` comprimido (20MB) → ✅ **Cabe en GitHub**
2. Google Drive como backup
3. Datos de muestra en el repo

**Ventajas de este enfoque:**
- No dependes de servicios externos
- Funciona offline
- Deploy más rápido

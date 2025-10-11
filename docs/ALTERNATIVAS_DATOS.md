# Alternativas para Datos Grandes

## 1. Google Drive (15GB Gratis)

### Subir archivo a Google Drive
1. Sube `SERIE_COMPROBANTES_COMPLETOS.csv` a Google Drive
2. Haz clic derecho → "Obtener enlace" → "Cualquiera con el enlace"
3. Copia el ID del archivo del enlace

### Código para descargar en Streamlit
```python
import gdown
import os

# ID del archivo de Google Drive
FILE_ID = "TU_FILE_ID_AQUI"
OUTPUT_PATH = "datos/SERIE_COMPROBANTES_COMPLETOS.csv"

if not os.path.exists(OUTPUT_PATH):
    url = f"https://drive.google.com/uc?id={FILE_ID}"
    gdown.download(url, OUTPUT_PATH, quiet=False)
```

Agregar a `requirements.txt`:
```
gdown>=4.7.1
```

---

## 2. GitHub Releases (Hasta 2GB por archivo)

### Subir como Release Asset
```bash
# 1. Crear release en GitHub web
# 2. Subir archivo como asset del release
# 3. Obtener URL de descarga
```

### Código para descargar
```python
import requests
import os

RELEASE_URL = "https://github.com/USER/REPO/releases/download/v1.0/SERIE_COMPROBANTES_COMPLETOS.csv"
OUTPUT_PATH = "datos/SERIE_COMPROBANTES_COMPLETOS.csv"

if not os.path.exists(OUTPUT_PATH):
    response = requests.get(RELEASE_URL, stream=True)
    with open(OUTPUT_PATH, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
```

---

## 3. Comprimir el Archivo

### Comprimir con gzip (puede reducir 70-90%)
```python
import gzip
import shutil

# Comprimir
with open('SERIE_COMPROBANTES_COMPLETOS.csv', 'rb') as f_in:
    with gzip.open('SERIE_COMPROBANTES_COMPLETOS.csv.gz', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

# Leer comprimido directamente
import pandas as pd
df = pd.read_csv('SERIE_COMPROBANTES_COMPLETOS.csv.gz', 
                 compression='gzip', sep=';', encoding='utf-8')
```

**Tamaño estimado comprimido**: ~30-100MB (puede entrar en GitHub)

---

## 4. Dividir el Archivo

### Dividir en chunks más pequeños
```python
import pandas as pd

# Leer y dividir
df = pd.read_csv('SERIE_COMPROBANTES_COMPLETOS.csv', sep=';')
chunk_size = 500_000  # Filas por chunk

for i, chunk in enumerate(df.groupby(df.index // chunk_size)):
    chunk[1].to_csv(f'datos/comprobantes_parte_{i+1}.csv', sep=';', index=False)

# Leer y combinar
import glob
files = sorted(glob.glob('datos/comprobantes_parte_*.csv'))
df = pd.concat([pd.read_csv(f, sep=';') for f in files], ignore_index=True)
```

---

## 5. Usar Solo Datos de Muestra en GitHub

### Estructura Recomendada
```
├── FASE1_OUTPUT_SAMPLE/  # En GitHub (datos de ejemplo)
├── datos/                # En .gitignore (datos reales, solo local)
└── docs/COMO_OBTENER_DATOS_COMPLETOS.md
```

### Para Streamlit Cloud
- Usa datos de muestra (FASE1_OUTPUT_SAMPLE/)
- Agrega nota: "Demo con datos sintéticos"
- Para producción: Conecta base de datos remota

---

## Recomendación por Caso de Uso

| Caso | Solución Recomendada |
|------|---------------------|
| **Solo desarrollo local** | Mantener en `datos/` (gitignored) |
| **Compartir con equipo** | Google Drive + script descarga |
| **Streamlit Cloud** | Usar datos de muestra O Google Drive |
| **Producción real** | Base de datos (PostgreSQL, MySQL) |
| **GitHub público** | GitHub Releases + descarga automática |

---

## Mejor Opción: Comprimir + GitHub Releases

1. **Comprimir** el archivo a .gz (~30-50MB)
2. **Subirlo** como GitHub Release
3. **Descargarlo** automáticamente en primera ejecución
4. Mantener **datos de muestra** para demos rápidos

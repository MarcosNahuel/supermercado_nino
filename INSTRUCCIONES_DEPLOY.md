# 🚀 Instrucciones para Subir a GitHub y Deploy

## ✅ Archivo Comprimido Creado

El archivo grande ha sido comprimido:
- **Original**: `SERIE_COMPROBANTES_COMPLETOS.csv` (337 MB) ❌ No cabe en GitHub
- **Comprimido**: `SERIE_COMPROBANTES_COMPLETOS.csv.gz` (20.65 MB) ✅ Sí cabe en GitHub

## 📋 Pasos para Subir a GitHub

### 1. Verificar archivos ignorados
```bash
# El .gitignore ya está configurado para:
# ✅ Ignorar archivos .csv grandes
# ✅ Permitir archivos .csv.gz
# ✅ Incluir FASE1_OUTPUT_SAMPLE/ (datos de muestra)
```

### 2. Agregar cambios
```bash
git add .
git status  # Verificar que NO aparezcan archivos grandes
```

### 3. Commit
```bash
git commit -m "Reorganizar proyecto y comprimir datos (20MB)"
```

### 4. Push a GitHub
```bash
git push origin main
```

## 🔧 Configurar Dashboard para Leer Archivos Comprimidos

El dashboard ya está configurado para buscar datos en múltiples ubicaciones:
1. `data/processed/FASE1_OUTPUT/` (nuevo estándar)
2. `FASE1_OUTPUT/` (legacy)
3. `data/sample/FASE1_OUTPUT_SAMPLE/` (muestra)
4. `FASE1_OUTPUT_SAMPLE/` (legacy muestra)

### Para usar datos comprimidos localmente:

```python
# Pandas lee archivos .gz automáticamente
import pandas as pd
df = pd.read_csv('datos/SERIE_COMPROBANTES_COMPLETOS.csv.gz', 
                 sep=';', encoding='utf-8')
```

## 🌐 Deploy en Streamlit Cloud

### Opción A: Usar Datos de Muestra (Recomendado)
```
✅ Ya incluidos en el repositorio
✅ Funcionan automáticamente
✅ Ideal para demos
```

### Opción B: Descargar Datos Comprimidos al Iniciar
Agregar al inicio de `app_streamlit.py`:

```python
import gzip
import shutil
from pathlib import Path

# Descomprimir si existe versión .gz
gz_file = Path("datos/SERIE_COMPROBANTES_COMPLETOS.csv.gz")
csv_file = Path("datos/SERIE_COMPROBANTES_COMPLETOS.csv")

if gz_file.exists() and not csv_file.exists():
    with st.spinner('Descomprimiendo datos...'):
        with gzip.open(gz_file, 'rb') as f_in:
            with open(csv_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
```

## 📊 Estructura Final del Repositorio

```
supermercado_nino/
├── .streamlit/                    # Config Streamlit
├── data/
│   ├── raw/                      # Datos originales (gitignored)
│   ├── processed/                # Datos procesados (gitignored)
│   └── sample/                   # Datos de muestra (incluidos)
├── datos/                        # Carpeta legacy
│   ├── README.md
│   ├── RENTABILIDAD.csv          # ✅ Incluido (pequeño)
│   └── *.csv.gz                  # ✅ Comprimidos permitidos
├── docs/                         # Documentación
│   ├── ALTERNATIVAS_DATOS.md
│   ├── CONCLUSIONES_ESTRATEGIAS_FINALES.md
│   └── RESUMEN_PROYECTO_FINAL.md
├── scripts/                      # Scripts auxiliares
│   ├── analisis/
│   └── validaciones/
├── FASE1_OUTPUT_SAMPLE/          # ✅ Datos de muestra (incluidos)
├── FASE1_ANALISIS_COMPLETO.py    # Script principal
├── app_streamlit.py              # Dashboard
├── requirements.txt
├── .gitignore
└── README.md
```

## ⚠️ Archivos NO Incluidos en GitHub

Estos archivos están en `.gitignore` (solo local):
- `FASE1_OUTPUT/` - Datos procesados completos (~400MB)
- `data/raw/SERIE_COMPROBANTES_COMPLETOS.csv` (337MB)
- `comprobantes completos/` - Carpeta temporal eliminada

## ✅ Archivos SÍ Incluidos

- `FASE1_OUTPUT_SAMPLE/` - Datos de muestra (~5KB)
- `datos/SERIE_COMPROBANTES_COMPLETOS.csv.gz` (20MB) - Opcional
- `datos/RENTABILIDAD.csv` (1.4KB)
- Todo el código Python y configuración

## 🎯 Siguiente Paso

```bash
# Ejecuta estos comandos:
git add .
git commit -m "feat: Reorganizar repositorio y comprimir datos"
git push origin main
```

Luego ve a [share.streamlit.io](https://share.streamlit.io) y despliega tu app.

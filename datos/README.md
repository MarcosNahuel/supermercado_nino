# 📁 Carpeta de Datos

## ⚠️ Archivos Grandes No Incluidos

El archivo `SERIE_COMPROBANTES_COMPLETOS.csv` (**353 MB**) NO está en GitHub debido al límite de tamaño (100MB).

## 🔧 Opciones para Obtener Datos Completos

### **Opción 1: Comprimir y Subir** (Recomendada)

```bash
# 1. Comprimir el archivo
python scripts/comprimir_datos.py

# 2. Verificar tamaño
# Si <100MB, puedes subirlo a GitHub como .csv.gz

# 3. El dashboard leerá automáticamente archivos .gz
```

### **Opción 2: Usar Datos de Muestra**

El repositorio incluye `FASE1_OUTPUT_SAMPLE/` con datos sintéticos para pruebas:
- ✅ Incluido en GitHub
- ✅ Ideal para Streamlit Cloud
- ✅ Funciona inmediatamente sin configuración

### **Opción 3: Descargar de Release**

```bash
# Descargar desde GitHub Releases (si está disponible)
wget https://github.com/MarcosNahuel/supermercado_nino/releases/download/v1.0/SERIE_COMPROBANTES_COMPLETOS.csv.gz
gunzip SERIE_COMPROBANTES_COMPLETOS.csv.gz
```

### **Opción 4: Google Drive** (Para colaboración)

1. Subir archivo a Google Drive
2. Obtener enlace compartido
3. Usar script de descarga automática (ver `docs/ALTERNATIVAS_DATOS.md`)

## 📊 Estructura de Datos

```
datos/
├── README.md                           # Este archivo
├── SERIE_COMPROBANTES_COMPLETOS.csv   # ❌ No en GitHub (353MB)
├── SERIE_COMPROBANTES_COMPLETOS.csv.gz # ✅ Versión comprimida (opcional)
└── RENTABILIDAD.csv                    # ✅ Incluido (pequeño)
```

## 🚀 Para Desarrollo Local

Si tienes el archivo CSV completo:
1. Colócalo en esta carpeta (`datos/`)
2. El `.gitignore` ya lo excluye automáticamente
3. El dashboard lo detectará y usará

## 📖 Más Información

- **Comprimir datos**: Ver `scripts/comprimir_datos.py`
- **Alternativas completas**: Ver `docs/ALTERNATIVAS_DATOS.md`
- **Configurar Git LFS**: Ver `docs/SETUP_GIT_LFS.md`

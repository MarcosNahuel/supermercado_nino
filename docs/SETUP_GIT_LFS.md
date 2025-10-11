# Configurar Git LFS para Archivos Grandes

## Instalación

### Windows
```bash
# Descargar de: https://git-lfs.github.com/
# O con chocolatey:
choco install git-lfs
```

### Configuración
```bash
# Inicializar Git LFS
git lfs install

# Rastrear archivos CSV grandes
git lfs track "datos/*.csv"
git lfs track "comprobantes completos/*.csv"

# Agregar .gitattributes
git add .gitattributes

# Commit y push
git add .
git commit -m "Configure Git LFS for large CSV files"
git push
```

## Costo
- **Gratis**: 1GB almacenamiento + 1GB transferencia/mes
- **Pago**: $5/mes por 50GB adicionales

## Nota
Git LFS es ideal si necesitas versionar el archivo grande.

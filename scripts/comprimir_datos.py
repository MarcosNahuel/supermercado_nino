#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para comprimir archivos CSV grandes con gzip
Reduce tamaño típicamente en 70-90%
"""

import gzip
import shutil
from pathlib import Path

def comprimir_archivo(archivo_entrada, archivo_salida=None):
    """Comprime un archivo CSV con gzip."""
    archivo_entrada = Path(archivo_entrada)
    
    if archivo_salida is None:
        archivo_salida = archivo_entrada.with_suffix(archivo_entrada.suffix + '.gz')
    else:
        archivo_salida = Path(archivo_salida)
    
    print(f"📦 Comprimiendo: {archivo_entrada}")
    print(f"   Tamaño original: {archivo_entrada.stat().st_size / 1024 / 1024:.2f} MB")
    
    with open(archivo_entrada, 'rb') as f_in:
        with gzip.open(archivo_salida, 'wb', compresslevel=9) as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    tamano_comprimido = archivo_salida.stat().st_size / 1024 / 1024
    tamano_original = archivo_entrada.stat().st_size / 1024 / 1024
    reduccion = ((tamano_original - tamano_comprimido) / tamano_original) * 100
    
    print(f"✅ Comprimido: {archivo_salida}")
    print(f"   Tamaño comprimido: {tamano_comprimido:.2f} MB")
    print(f"   Reducción: {reduccion:.1f}%")
    
    if tamano_comprimido < 100:
        print(f"✅ ¡Archivo comprimido cabe en GitHub! (<100MB)")
    else:
        print(f"⚠️  Archivo aún supera 100MB, considera GitHub Releases o LFS")
    
    return archivo_salida

if __name__ == "__main__":
    # Comprimir archivo de comprobantes
    archivo = Path("datos/SERIE_COMPROBANTES_COMPLETOS.csv")
    
    if archivo.exists():
        comprimir_archivo(archivo)
    else:
        # Buscar en carpeta alternativa
        archivo_alt = Path("comprobantes completos/SERIE_COMPROBANTES_COMPLETOS.csv")
        if archivo_alt.exists():
            comprimir_archivo(archivo_alt)
        else:
            print("❌ No se encontró el archivo SERIE_COMPROBANTES_COMPLETOS.csv")
            print("   Búsqueda en:")
            print(f"   - {archivo}")
            print(f"   - {archivo_alt}")

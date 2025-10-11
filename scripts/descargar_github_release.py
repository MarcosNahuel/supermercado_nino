#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para descargar archivo desde GitHub Releases
Uso: Crear release en GitHub y subir archivo como asset
"""

import requests
from pathlib import Path
import sys

# =============================================================================
# CONFIGURACIÓN
# =============================================================================
GITHUB_USER = "MarcosNahuel"
GITHUB_REPO = "supermercado_nino"
RELEASE_TAG = "v1.0-data"  # Tag del release
FILE_NAME = "SERIE_COMPROBANTES_COMPLETOS.csv.gz"

# Construir URL de descarga
RELEASE_URL = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/releases/download/{RELEASE_TAG}/{FILE_NAME}"

OUTPUT_DIR = Path("datos")
OUTPUT_FILE = OUTPUT_DIR / FILE_NAME

# =============================================================================
# FUNCIONES
# =============================================================================
def descargar_desde_github_release(url, output_path, chunk_size=8192):
    """Descarga archivo desde GitHub Release."""
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Verificar si ya existe
    if output_path.exists():
        print(f"✅ Archivo ya existe: {output_path}")
        size_mb = output_path.stat().st_size / 1024 / 1024
        print(f"   Tamaño: {size_mb:.2f} MB")
        return output_path
    
    print(f"📥 Descargando desde GitHub Release...")
    print(f"   URL: {url}")
    print(f"   Destino: {output_path}")
    
    try:
        # Realizar solicitud con streaming
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Obtener tamaño total
        total_size = int(response.headers.get('content-length', 0))
        print(f"   Tamaño: {total_size / 1024 / 1024:.2f} MB")
        
        # Descargar en chunks
        downloaded = 0
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\r   Progreso: {progress:.1f}% ", end='')
        
        print("\n✅ Descarga completa")
        
        # Descomprimir si es .gz
        if output_path.suffix == '.gz':
            print("📦 Descomprimiendo archivo...")
            import gzip
            import shutil
            
            output_csv = output_path.with_suffix('')
            with gzip.open(output_path, 'rb') as f_in:
                with open(output_csv, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            print(f"✅ Descomprimido: {output_csv}")
            return output_csv
        
        return output_path
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"\n❌ Error 404: Release no encontrado")
            print(f"\n💡 Verifica:")
            print(f"   1. Usuario: {GITHUB_USER}")
            print(f"   2. Repositorio: {GITHUB_REPO}")
            print(f"   3. Tag: {RELEASE_TAG}")
            print(f"   4. Archivo: {FILE_NAME}")
            print(f"\n📋 CREAR RELEASE:")
            print(f"   1. Ve a: https://github.com/{GITHUB_USER}/{GITHUB_REPO}/releases")
            print(f"   2. Click 'Create a new release'")
            print(f"   3. Tag: {RELEASE_TAG}")
            print(f"   4. Sube {FILE_NAME} como asset")
        else:
            print(f"\n❌ Error HTTP: {e}")
        return None
        
    except Exception as e:
        print(f"\n❌ Error en descarga: {e}")
        return None

# =============================================================================
# EJECUCIÓN PRINCIPAL
# =============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("DESCARGA DE DATOS DESDE GITHUB RELEASE")
    print("=" * 70)
    
    resultado = descargar_desde_github_release(RELEASE_URL, OUTPUT_FILE)
    
    if resultado:
        print(f"\n✅ ÉXITO: Datos listos para usar")
        print(f"   Ejecuta: streamlit run app_streamlit.py")
    else:
        print(f"\n❌ ERROR: No se pudo descargar el archivo")
        print(f"\n💡 ALTERNATIVAS:")
        print(f"   1. Descarga manual: {RELEASE_URL}")
        print(f"   2. Usa datos de muestra: FASE1_OUTPUT_SAMPLE/")

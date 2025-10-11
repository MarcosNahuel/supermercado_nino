#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para descargar archivo desde Google Drive
Uso: Subir SERIE_COMPROBANTES_COMPLETOS.csv a Google Drive y usar este script
"""

import gdown
import os
from pathlib import Path

# =============================================================================
# CONFIGURACIÓN
# =============================================================================
# Reemplaza con tu File ID de Google Drive
# Para obtenerlo: Click derecho en archivo > Obtener enlace > Copiar ID del URL
# URL ejemplo: https://drive.google.com/file/d/1ABC123xyz_FILE_ID_AQUI/view?usp=sharing
GOOGLE_DRIVE_FILE_ID = "TU_FILE_ID_AQUI"

# Ruta donde guardar el archivo
OUTPUT_DIR = Path("datos")
OUTPUT_FILE = OUTPUT_DIR / "SERIE_COMPROBANTES_COMPLETOS.csv"

# =============================================================================
# FUNCIONES
# =============================================================================
def descargar_desde_google_drive(file_id, output_path):
    """Descarga archivo desde Google Drive."""
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Verificar si ya existe
    if output_path.exists():
        print(f"✅ Archivo ya existe: {output_path}")
        respuesta = input("¿Descargar nuevamente? (s/n): ")
        if respuesta.lower() != 's':
            return output_path
    
    # Construir URL de descarga
    url = f"https://drive.google.com/uc?id={file_id}"
    
    print(f"📥 Descargando desde Google Drive...")
    print(f"   URL: {url}")
    print(f"   Destino: {output_path}")
    
    try:
        gdown.download(url, str(output_path), quiet=False)
        
        # Verificar descarga
        if output_path.exists():
            size_mb = output_path.stat().st_size / 1024 / 1024
            print(f"✅ Descarga completa: {size_mb:.2f} MB")
            return output_path
        else:
            print("❌ Error: El archivo no se descargó correctamente")
            return None
            
    except Exception as e:
        print(f"❌ Error en descarga: {e}")
        print("\n💡 Verifica que:")
        print("   1. El File ID sea correcto")
        print("   2. El archivo tenga permisos de 'Cualquiera con el enlace'")
        print("   3. Tengas instalado gdown: pip install gdown")
        return None

def descargar_archivo_grande(file_id, output_path):
    """Descarga archivos grandes con soporte de chunks."""
    import requests
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # URL para archivos grandes
    url = "https://drive.google.com/uc?export=download"
    
    session = requests.Session()
    
    print(f"📥 Descargando archivo grande desde Google Drive...")
    
    # Primera solicitud para obtener el token de confirmación
    response = session.get(url, params={'id': file_id}, stream=True)
    
    # Buscar el token de confirmación
    token = None
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            token = value
            break
    
    # Segunda solicitud con el token
    if token:
        params = {'id': file_id, 'confirm': token}
        response = session.get(url, params=params, stream=True)
    
    # Guardar el archivo en chunks
    CHUNK_SIZE = 32768
    total_size = int(response.headers.get('content-length', 0))
    
    print(f"   Tamaño: {total_size / 1024 / 1024:.2f} MB")
    
    downloaded = 0
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                progress = (downloaded / total_size) * 100 if total_size > 0 else 0
                print(f"\r   Progreso: {progress:.1f}%", end='')
    
    print(f"\n✅ Descarga completa: {output_path}")
    return output_path

# =============================================================================
# EJECUCIÓN PRINCIPAL
# =============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("DESCARGA DE DATOS DESDE GOOGLE DRIVE")
    print("=" * 70)
    
    # Verificar configuración
    if GOOGLE_DRIVE_FILE_ID == "TU_FILE_ID_AQUI":
        print("⚠️  Necesitas configurar el File ID de Google Drive")
        print("\n📋 PASOS PARA CONFIGURAR:")
        print("1. Sube el archivo CSV a Google Drive")
        print("2. Click derecho → Obtener enlace")
        print("3. Configura 'Cualquiera con el enlace'")
        print("4. Copia el ID del URL:")
        print("   https://drive.google.com/file/d/[COPIA_ESTE_ID]/view")
        print("5. Pega el ID en este script (línea 17)")
        exit(1)
    
    # Intentar descarga
    resultado = descargar_desde_google_drive(GOOGLE_DRIVE_FILE_ID, OUTPUT_FILE)
    
    if resultado:
        print(f"\n✅ ÉXITO: Datos listos para usar")
        print(f"   Ejecuta: streamlit run app_streamlit.py")
    else:
        print(f"\n❌ ERROR: No se pudo descargar el archivo")
        print(f"   Intenta la descarga manual desde Google Drive")

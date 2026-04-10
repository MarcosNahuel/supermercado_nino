"""Configuracion de fuentes de datos competitivas."""
from pathlib import Path

# Directorios
DATA_DIR = Path("data/competitive")
SEPA_RAW_DIR = DATA_DIR / "sepa_raw"
SEPA_PROCESSED_DIR = DATA_DIR / "sepa_processed"
VTEX_PROMOS_DIR = DATA_DIR / "vtex_promos"
INSIGHTS_DIR = DATA_DIR / "insights"

# SEPA
SEPA_DATASET_URL = "https://datos.produccion.gob.ar/dataset/sepa-precios"
SEPA_API_BASE = "https://datos.produccion.gob.ar/api/3/action/package_show?id=sepa-precios"

# Cadenas VTEX
VTEX_CHAINS = {
    "carrefour": {
        "name": "Carrefour",
        "domain": "www.carrefour.com.ar",
        "vtex_account": "carrefourar",
    },
    "changomas": {
        "name": "Changomas / Mas Online",
        "domain": "www.masonline.com.ar",
        "vtex_account": "maboraonline",
    },
    "jumbo": {
        "name": "Jumbo",
        "domain": "www.jumbo.com.ar",
        "vtex_account": "jumbocencosud",
    },
    "disco": {
        "name": "Disco",
        "domain": "www.disco.com.ar",
        "vtex_account": "discocencosud",
    },
    "vea": {
        "name": "Vea",
        "domain": "www.veadigital.com.ar",
        "vtex_account": "veacencosud",
    },
}

# Provincias de interes (Mendoza primero, luego expandir)
PROVINCIAS_INTERES = ["MENDOZA"]

# Categorias prioritarias para comparacion
CATEGORIAS_PRIORITARIAS = [
    "BEBIDAS",
    "LACTEOS",
    "CARNES",
    "PANADERIA",
    "LIMPIEZA",
    "PERFUMERIA",
    "ALMACEN",
    "FIAMBRERIA",
    "VERDULERIA",
    "CONGELADOS",
]

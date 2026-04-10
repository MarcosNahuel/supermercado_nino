"""Scraper de promociones de cadenas VTEX (Carrefour, Changomas, Jumbo, Disco, Vea).

Usa la API publica VTEX Intelligent Search para obtener productos con precios
y promociones activas. No requiere autenticacion.
"""
import time
import logging
from typing import Any

import pandas as pd
import requests

from src.competitive.config import VTEX_CHAINS, CATEGORIAS_PRIORITARIAS, VTEX_PROMOS_DIR

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 15
DELAY_BETWEEN_REQUESTS = 2.0  # Segundos entre requests para no saturar


def search_vtex_products(
    vtex_account: str,
    domain: str,
    query: str,
    page: int = 0,
    count: int = 50,
) -> dict:
    """Busca productos via VTEX catalog_system API (endpoint legacy estable).

    Args:
        vtex_account: Cuenta VTEX (ej: "carrefourar"). Actualmente no usado,
            se mantiene por compat con firma previa.
        domain: Dominio de la tienda (ej: "www.carrefour.com.ar").
        query: Termino de busqueda (ej: "leche", "bebidas").
        page: Pagina de resultados (0-indexed).
        count: Cantidad de resultados por pagina.

    Returns:
        Dict normalizado con clave "products" (lista).
    """
    _from = page * count
    _to = _from + count - 1
    url = (
        f"https://{domain}/api/catalog_system/pub/products/search/"
        f"{query}?_from={_from}&_to={_to}"
    )

    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (compatible; NINO-Intel/1.0)",
    }

    resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()

    # VTEX legacy retorna array directo; normalizar a {"products": [...]}
    if isinstance(data, list):
        return {"products": data}
    return data


def _extract_teaser_name(teaser: dict) -> str:
    """Extrae nombre de teaser manejando formato legacy (.NET) y moderno."""
    if not isinstance(teaser, dict):
        return ""
    # Formato moderno (lowercase)
    if "name" in teaser:
        return str(teaser.get("name", ""))
    # Formato legacy .NET: "<Name>k__BackingField"
    for key, val in teaser.items():
        if "Name" in key and isinstance(val, str):
            return val
    return ""


def extract_promos_from_response(
    data: dict,
    chain_key: str,
) -> list[dict]:
    """Extrae productos con info de precios y promos de la respuesta VTEX.

    Args:
        data: Respuesta JSON de VTEX.
        chain_key: Clave de cadena en VTEX_CHAINS.

    Returns:
        Lista de dicts con producto, precios y promo.
    """
    chain_name = VTEX_CHAINS.get(chain_key, {}).get("name", chain_key.upper())
    products = []

    for product in data.get("products", []):
        for item in product.get("items", []):
            ean = item.get("ean", "")
            if not ean:
                continue

            for seller in item.get("sellers", []):
                offer = seller.get("commertialOffer", {})
                precio_lista = offer.get("ListPrice", 0)
                precio_venta = offer.get("Price", 0)
                disponible = offer.get("AvailableQuantity", 0)

                if precio_lista <= 0 or disponible <= 0:
                    continue

                # Calcular descuento
                descuento_pct = 0.0
                if precio_lista > 0 and precio_venta < precio_lista:
                    descuento_pct = round(
                        (1 - precio_venta / precio_lista) * 100, 1
                    )

                # Extraer promos/teasers (legacy usa "Teasers" mayuscula)
                teasers = offer.get("teasers") or offer.get("Teasers") or []
                promo_nombres = [
                    name for name in (_extract_teaser_name(t) for t in teasers) if name
                ]

                categories = product.get("categories", [""])
                categoria = categories[0].strip("/").split("/")[0] if categories else ""

                products.append({
                    "ean": str(ean).strip(),
                    "descripcion": product.get("productName", ""),
                    "marca": product.get("brand", ""),
                    "categoria_vtex": categoria,
                    "cadena": chain_name.upper(),
                    "cadena_key": chain_key,
                    "precio_lista": precio_lista,
                    "precio_venta": precio_venta,
                    "descuento_pct": descuento_pct,
                    "tiene_promo": descuento_pct > 0 or len(promo_nombres) > 0,
                    "promo_nombre": " | ".join(promo_nombres) if promo_nombres else "",
                })

    return products


def scrape_chain_promos(
    chain_key: str,
    categorias: list[str] | None = None,
) -> pd.DataFrame:
    """Scrapea promos de una cadena VTEX buscando por categorias.

    Args:
        chain_key: Clave de la cadena (ej: "carrefour").
        categorias: Lista de categorias a buscar. Default: CATEGORIAS_PRIORITARIAS.

    Returns:
        DataFrame con todos los productos encontrados y sus promos.
    """
    chain = VTEX_CHAINS[chain_key]
    categorias = categorias or CATEGORIAS_PRIORITARIAS
    all_products = []

    for cat in categorias:
        try:
            data = search_vtex_products(
                vtex_account=chain["vtex_account"],
                domain=chain["domain"],
                query=cat,
            )
            products = extract_promos_from_response(data, chain_key)
            all_products.extend(products)
            logger.info(f"  {chain['name']} / {cat}: {len(products)} productos")
            time.sleep(DELAY_BETWEEN_REQUESTS)
        except Exception as e:
            logger.warning(f"  {chain['name']} / {cat}: ERROR {e}")

    df = pd.DataFrame(all_products)
    if not df.empty:
        df = df.drop_duplicates(subset=["ean", "cadena"], keep="first")

    logger.info(f"{chain['name']}: {len(df)} productos totales")
    return df


def scrape_all_chains(
    chains: list[str] | None = None,
    categorias: list[str] | None = None,
) -> pd.DataFrame:
    """Scrapea promos de todas las cadenas VTEX.

    Args:
        chains: Lista de claves de cadena. None = todas.
        categorias: Categorias a buscar.

    Returns:
        DataFrame consolidado con promos de todas las cadenas.
    """
    chains = chains or list(VTEX_CHAINS.keys())
    frames = []

    for chain_key in chains:
        logger.info(f"Scrapeando {VTEX_CHAINS[chain_key]['name']}...")
        df = scrape_chain_promos(chain_key, categorias)
        if not df.empty:
            frames.append(df)

    if not frames:
        return pd.DataFrame()

    result = pd.concat(frames, ignore_index=True)

    # Guardar JSON con timestamp
    VTEX_PROMOS_DIR.mkdir(parents=True, exist_ok=True)
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d")
    result.to_parquet(VTEX_PROMOS_DIR / f"promos_{timestamp}.parquet", index=False)
    result.to_parquet(VTEX_PROMOS_DIR / "promos_latest.parquet", index=False)

    logger.info(
        f"Total: {len(result):,} productos, "
        f"{result['tiene_promo'].sum():,} con promo activa"
    )
    return result

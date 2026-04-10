"""Tests para scraper VTEX de promociones."""
import pytest
import json
from unittest.mock import patch, MagicMock

from src.competitive.vtex_scraper import (
    search_vtex_products,
    extract_promos_from_response,
    scrape_chain_promos,
    scrape_all_chains,
)


@pytest.fixture
def vtex_search_response():
    """Respuesta simulada de VTEX Intelligent Search."""
    return {
        "products": [
            {
                "productId": "12345",
                "productName": "Coca Cola 2.25L",
                "brand": "Coca Cola",
                "categories": ["/Bebidas/Gaseosas/"],
                "items": [
                    {
                        "itemId": "12345-1",
                        "ean": "7790002345678",
                        "name": "Coca Cola 2.25L",
                        "sellers": [
                            {
                                "sellerId": "1",
                                "commertialOffer": {
                                    "Price": 1890.00,
                                    "ListPrice": 2100.00,
                                    "AvailableQuantity": 100,
                                    "teasers": [
                                        {
                                            "name": "2da unidad al 50%",
                                            "conditions": {
                                                "minimumQuantity": 2
                                            },
                                        }
                                    ],
                                },
                            }
                        ],
                    }
                ],
            },
            {
                "productId": "67890",
                "productName": "Leche Entera La Serenisima 1L",
                "brand": "La Serenisima",
                "categories": ["/Lacteos/Leches/"],
                "items": [
                    {
                        "itemId": "67890-1",
                        "ean": "7790001234567",
                        "name": "Leche Entera 1L",
                        "sellers": [
                            {
                                "sellerId": "1",
                                "commertialOffer": {
                                    "Price": 1250.50,
                                    "ListPrice": 1250.50,
                                    "AvailableQuantity": 50,
                                    "teasers": [],
                                },
                            }
                        ],
                    }
                ],
            },
        ],
    }


def test_extract_promos_parses_products(vtex_search_response):
    """Debe extraer productos con precios y promos."""
    products = extract_promos_from_response(vtex_search_response, "carrefour")
    assert len(products) == 2

    coca = next(p for p in products if p["ean"] == "7790002345678")
    assert coca["precio_lista"] == 2100.00
    assert coca["precio_venta"] == 1890.00
    assert coca["descuento_pct"] == pytest.approx(10.0, abs=0.1)
    assert coca["tiene_promo"] is True
    assert "2da unidad al 50%" in coca["promo_nombre"]


def test_extract_promos_no_promo(vtex_search_response):
    """Producto sin promo debe tener tiene_promo=False."""
    products = extract_promos_from_response(vtex_search_response, "carrefour")
    leche = next(p for p in products if p["ean"] == "7790001234567")
    assert leche["tiene_promo"] is False
    assert leche["descuento_pct"] == 0.0


def test_search_vtex_products_makes_correct_request():
    """Debe construir URL VTEX correctamente."""
    with patch("src.competitive.vtex_scraper.requests.get") as mock_get:
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"products": []}
        )
        search_vtex_products("carrefourar", "www.carrefour.com.ar", "leche")

        call_url = mock_get.call_args[0][0]
        assert "carrefour.com.ar" in call_url
        assert "leche" in call_url


def test_scrape_chain_promos_returns_dataframe(vtex_search_response):
    """Debe retornar DataFrame con promos de una cadena."""
    with patch("src.competitive.vtex_scraper.search_vtex_products") as mock_search:
        mock_search.return_value = vtex_search_response
        df = scrape_chain_promos("carrefour")
        assert len(df) > 0
        assert "cadena" in df.columns
        assert "ean" in df.columns
        assert "tiene_promo" in df.columns

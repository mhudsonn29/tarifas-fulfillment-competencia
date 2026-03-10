"""Scraper para Mercado Libre Full con Playwright."""

import logging
from typing import Any
from base import BaseScraper
from config import URLS
from parser import parse_mercadolibre

logger = logging.getLogger(__name__)

# Solo usamos colecta para la comparacion de fulfillment
URL_COLECTA = URLS["mercadolibre"]["colecta"]


class MercadoLibreScraper(BaseScraper):
    """Scraper para tarifas de Mercado Libre Full."""

    def __init__(self):
        super().__init__("MercadoLibre")

    def scrape(self) -> dict[str, Any]:
        """Extrae tarifas de colecta de MercadoLibre (relevante para comparacion)."""
        result = {"marketplace": "MercadoLibre", "url": URL_COLECTA, "success": False, "tarifas": [], "error": None}

        try:
            soup = self.fetch_page(URL_COLECTA)

            if not soup:
                result["error"] = "No se pudo obtener la página"
                return result

            tablas = [t["data"] for t in self.extract_tables(soup)]
            logger.info(f"[MercadoLibre] {len(tablas)} tablas encontradas")

            if not tablas:
                result["error"] = "No se encontraron tablas en la página"
                return result

            tarifas = parse_mercadolibre(tablas)

            if tarifas:
                result["success"] = True
                result["tarifas"] = tarifas
            else:
                result["error"] = "No se pudieron parsear las tarifas"

        except Exception as e:
            logger.error(f"[MercadoLibre] Error inesperado: {e}")
            result["error"] = str(e)

        return result


def scrape_mercadolibre() -> dict[str, Any]:
    scraper = MercadoLibreScraper()
    try:
        return scraper.scrape()
    finally:
        scraper.close()

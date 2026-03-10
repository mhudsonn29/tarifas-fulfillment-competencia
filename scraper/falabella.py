"""Scraper para Fulfillment by Falabella con Playwright."""

import logging
from typing import Any
from base import BaseScraper
from config import URLS
from parser import parse_falabella

logger = logging.getLogger(__name__)
URL = URLS["falabella"]["tarifas"]


class FalabellaScraper(BaseScraper):
    """Scraper para tarifas de Fulfillment by Falabella Chile."""

    def __init__(self):
        super().__init__("Falabella")

    def scrape(self) -> dict[str, Any]:
        """Extrae tarifas de Falabella y retorna lista estandarizada."""
        result = {"marketplace": "Falabella", "url": URL, "success": False, "tarifas": [], "error": None}

        try:
            # Salesforce Community renderiza con JS - Playwright es clave acá
            soup = self.fetch_page(URL, wait_selector="table")

            if not soup:
                result["error"] = "No se pudo obtener la página"
                return result

            tablas = [t["data"] for t in self.extract_tables(soup)]
            logger.info(f"[Falabella] {len(tablas)} tablas encontradas")

            if not tablas:
                result["error"] = "No se encontraron tablas en la página"
                return result

            tarifas = parse_falabella(tablas)

            if tarifas:
                result["success"] = True
                result["tarifas"] = tarifas
            else:
                result["error"] = "No se pudieron parsear las tarifas de las tablas"

        except Exception as e:
            logger.error(f"[Falabella] Error inesperado: {e}")
            result["error"] = str(e)

        return result


def scrape_falabella() -> dict[str, Any]:
    scraper = FalabellaScraper()
    try:
        return scraper.scrape()
    finally:
        scraper.close()

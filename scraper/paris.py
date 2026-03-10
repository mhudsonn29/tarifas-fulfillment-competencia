"""Scraper para Fulfillment by Paris con Playwright."""

import logging
from typing import Any
from base import BaseScraper
from config import URLS
from parser import parse_paris

logger = logging.getLogger(__name__)


class ParisScraper(BaseScraper):
    """Scraper para tarifas de Fulfillment by Paris (Cencosud)."""

    def __init__(self):
        super().__init__("Paris")

    def scrape(self) -> dict[str, Any]:
        """Extrae tarifas de Paris y retorna lista estandarizada."""
        result = {"marketplace": "Paris", "success": False, "tarifas": [], "error": None}

        tablas_totales = []

        for key, url in URLS["paris"].items():
            try:
                soup = self.fetch_page(url)
                if soup:
                    tablas = [t["data"] for t in self.extract_tables(soup)]
                    logger.info(f"[Paris] {key}: {len(tablas)} tablas")
                    tablas_totales.extend(tablas)
                else:
                    logger.warning(f"[Paris] No se pudo obtener {url}")
            except Exception as e:
                logger.error(f"[Paris] Error en {url}: {e}")

        if not tablas_totales:
            result["error"] = "No se encontraron tablas en ninguna página de Paris"
            return result

        tarifas = parse_paris(tablas_totales)

        if tarifas:
            result["success"] = True
            result["tarifas"] = tarifas
        else:
            result["error"] = "No se pudieron parsear las tarifas"

        return result


def scrape_paris() -> dict[str, Any]:
    scraper = ParisScraper()
    try:
        return scraper.scrape()
    finally:
        scraper.close()

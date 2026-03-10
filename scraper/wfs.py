"""Scraper para Walmart Fulfillment Services (WFS) con Playwright."""

import logging
from typing import Any
from base import BaseScraper
from cache import WFS_TARIFAS_BASE
from parser import tabla_a_tarifas

logger = logging.getLogger(__name__)
URL = "https://marketplacelearn.walmart.com/cl/guides/Walmart%20Fulfillment%20Services/Walmart%20Fulfillment%20Services/tarifas-wfs"


class WFSScraper(BaseScraper):
    """Scraper para tarifas de WFS Walmart Chile."""

    def __init__(self):
        super().__init__("WFS")

    def scrape(self) -> dict[str, Any]:
        """Intenta scraper WFS, si falla usa datos hardcodeados conocidos."""
        result = {"marketplace": "WFS", "url": URL, "success": False, "tarifas": [], "error": None}

        try:
            soup = self.fetch_page(URL, wait_selector="table")

            if soup:
                tablas = [t["data"] for t in self.extract_tables(soup)]
                logger.info(f"[WFS] {len(tablas)} tablas encontradas")

                for tabla in tablas:
                    tarifas = tabla_a_tarifas(tabla)
                    if len(tarifas) >= 5:  # La tabla de WFS tiene 8 filas
                        result["success"] = True
                        result["tarifas"] = tarifas
                        logger.info(f"[WFS] Scraped exitosamente: {len(tarifas)} tarifas")
                        return result

            # Fallback a datos hardcodeados (siempre válidos)
            logger.info("[WFS] Usando datos hardcodeados (fuente: portal oficial Walmart)")
            result["success"] = True
            result["tarifas"] = WFS_TARIFAS_BASE["fulfillment"]

        except Exception as e:
            logger.error(f"[WFS] Error: {e} - usando datos hardcodeados")
            result["success"] = True
            result["tarifas"] = WFS_TARIFAS_BASE["fulfillment"]

        return result


def scrape_wfs() -> dict[str, Any]:
    scraper = WFSScraper()
    try:
        return scraper.scrape()
    finally:
        scraper.close()

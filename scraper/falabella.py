"""Scraper para Fulfillment by Falabella."""

import logging
from typing import Any
from base import BaseScraper
from config import URLS

logger = logging.getLogger(__name__)


class FalabellaScraper(BaseScraper):
    """Scraper para tarifas de Fulfillment by Falabella Chile."""
    
    def __init__(self):
        super().__init__("Falabella")
        self.url = URLS["falabella"]["tarifas"]
    
    def scrape(self) -> dict[str, Any]:
        """Extrae todas las tarifas de Falabella."""
        soup = self.fetch_page(self.url)
        
        result = {
            "marketplace": "Falabella",
            "url": self.url,
            "success": False,
            "tarifas": {},
            "todas_las_tablas": []
        }
        
        if not soup:
            result["error"] = "No se pudo obtener la página"
            return result
        
        result["success"] = True
        
        # Extraer todas las tablas de la página
        tables = self.extract_tables(soup)
        result["todas_las_tablas"] = [t["data"] for t in tables]
        
        logger.info(f"[Falabella] Se encontraron {len(tables)} tablas")
        
        return result


def scrape_falabella() -> dict[str, Any]:
    """Función helper para ejecutar el scraper."""
    scraper = FalabellaScraper()
    result = scraper.scrape()
    scraper._close_browser()
    return result

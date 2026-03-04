"""Scraper para Fulfillment by Paris (Cencosud)."""

import logging
from typing import Any
from base import BaseScraper
from config import URLS

logger = logging.getLogger(__name__)


class ParisScraper(BaseScraper):
    """Scraper para tarifas de Fulfillment by Paris."""
    
    def __init__(self):
        super().__init__("Paris")
        self.urls = URLS["paris"]
    
    def scrape(self) -> dict[str, Any]:
        """Extrae todas las tarifas de Paris."""
        result = {
            "marketplace": "Paris",
            "success": True,
            "tarifas": {}
        }
        
        # Scrape costos logísticos
        result["tarifas"]["despacho"] = self._scrape_costos_logisticos()
        
        # Scrape fulfillment
        result["tarifas"]["fulfillment"] = self._scrape_fulfillment()
        
        # Verificar si obtuvo datos
        despacho_ok = len(result["tarifas"]["despacho"].get("todas_las_tablas", [])) > 0
        fulfillment_ok = len(result["tarifas"]["fulfillment"].get("todas_las_tablas", [])) > 0
        result["success"] = despacho_ok or fulfillment_ok
        
        return result
    
    def _scrape_costos_logisticos(self) -> dict[str, Any]:
        """Extrae las tablas de costos de despacho a domicilio."""
        url = self.urls["costos_logisticos"]
        soup = self.fetch_page(url)
        
        data = {
            "titulo": "Costos de Despacho a Domicilio",
            "url": url,
            "todas_las_tablas": [],
            "tiene_datos": False
        }
        
        if not soup:
            data["error"] = "No se pudo obtener la página"
            return data
        
        tables = self.extract_tables(soup)
        data["todas_las_tablas"] = [t["data"] for t in tables]
        data["tiene_datos"] = len(tables) > 0
        
        logger.info(f"[Paris] Costos Logísticos: {len(tables)} tablas")
        
        return data
    
    def _scrape_fulfillment(self) -> dict[str, Any]:
        """Extrae costos de almacenamiento y retiro."""
        url = self.urls["fulfillment"]
        soup = self.fetch_page(url)
        
        data = {
            "titulo": "Fulfillment by Paris",
            "url": url,
            "todas_las_tablas": [],
            "texto_relevante": [],
            "tiene_datos": False
        }
        
        if not soup:
            data["error"] = "No se pudo obtener la página"
            return data
        
        tables = self.extract_tables(soup)
        data["todas_las_tablas"] = [t["data"] for t in tables]
        data["tiene_datos"] = len(tables) > 0
        
        # Extraer texto con precios
        for p in soup.find_all(['p', 'li']):
            text = p.get_text(strip=True)
            indicators = ['$', 'costo', 'tarifa', 'almacen', 'retiro', '%']
            if any(ind in text.lower() for ind in indicators):
                if 15 < len(text) < 300:
                    data["texto_relevante"].append(text)
        
        logger.info(f"[Paris] Fulfillment: {len(tables)} tablas")
        
        return data


def scrape_paris() -> dict[str, Any]:
    """Función helper para ejecutar el scraper."""
    scraper = ParisScraper()
    result = scraper.scrape()
    scraper._close_browser()
    return result

"""Scraper para Fulfillment by Paris (Cencosud)."""

from typing import Any
from base import BaseScraper, logger
from config import URLS


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
        
        # Scrape costos logísticos (tablas de despacho)
        result["tarifas"]["despacho"] = self._scrape_costos_logisticos()
        
        # Scrape fulfillment (almacenamiento y retiro)
        result["tarifas"]["fulfillment"] = self._scrape_fulfillment()
        
        # Paris es exitoso si al menos obtuvo algunas tablas
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
            "tabla_menor_49990": [],
            "tabla_mayor_49990": [],
            "todas_las_tablas": [],
            "tiene_datos": False
        }
        
        if not soup:
            data["error"] = "No se pudo obtener la página"
            return data
        
        # Extraer todas las tablas
        tables = self.extract_tables(soup)
        data["todas_las_tablas"] = [t["data"] for t in tables]
        data["tiene_datos"] = len(tables) > 0
        
        # Identificar las tablas específicas
        if len(tables) >= 2:
            data["tabla_menor_49990"] = tables[0]["data"] if tables else []
            data["tabla_mayor_49990"] = tables[1]["data"] if len(tables) > 1 else []
        elif len(tables) == 1:
            data["tabla_menor_49990"] = tables[0]["data"]
        
        logger.info(f"[Paris] Costos Logísticos: {len(tables)} tablas encontradas")
        
        return data
    
    def _scrape_fulfillment(self) -> dict[str, Any]:
        """Extrae costos de almacenamiento y retiro."""
        url = self.urls["fulfillment"]
        soup = self.fetch_page(url)
        
        data = {
            "titulo": "Fulfillment by Paris (Almacenamiento y Retiro)",
            "url": url,
            "almacenamiento": [],
            "retiro": [],
            "todas_las_tablas": [],
            "texto_relevante": [],
            "tiene_datos": False
        }
        
        if not soup:
            data["error"] = "No se pudo obtener la página"
            return data
        
        # Extraer tablas
        tables = self.extract_tables(soup)
        data["todas_las_tablas"] = [t["data"] for t in tables]
        data["tiene_datos"] = len(tables) > 0
        
        # Buscar secciones específicas por encabezados
        for heading in soup.find_all(['h2', 'h3', 'h4', 'strong', 'b', 'p']):
            heading_text = heading.get_text(strip=True).lower()
            
            if 'almacenamiento' in heading_text and not data["almacenamiento"]:
                next_table = heading.find_next('table')
                if next_table:
                    data["almacenamiento"] = self._parse_table(next_table)
            
            if 'retiro' in heading_text and not data["retiro"]:
                next_table = heading.find_next('table')
                if next_table:
                    data["retiro"] = self._parse_table(next_table)
        
        # Extraer texto con precios
        for p in soup.find_all(['p', 'li']):
            text = p.get_text(strip=True)
            indicators = ['$', 'costo', 'tarifa', 'almacen', 'retiro', '%', 'clp']
            if any(ind in text.lower() for ind in indicators):
                if len(text) > 15 and len(text) < 500:
                    data["texto_relevante"].append(text)
        
        logger.info(f"[Paris] Fulfillment: {len(tables)} tablas encontradas")
        
        return data


def scrape_paris() -> dict[str, Any]:
    """Función helper para ejecutar el scraper."""
    scraper = ParisScraper()
    return scraper.scrape()

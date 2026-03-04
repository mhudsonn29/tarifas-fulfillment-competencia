"""Scraper para Fulfillment by Falabella."""

from typing import Any
from base import BaseScraper, logger
from config import URLS


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
            "tarifas": {}
        }
        
        if not soup:
            result["error"] = "No se pudo obtener la página"
            return result
        
        result["success"] = True
        
        # Extraer todas las tablas de la página
        tables = self.extract_tables(soup)
        
        # Mapear las tarifas que necesitamos
        tarifas_map = {
            "retiro_tren_logistico": {
                "titulo": "Tarifa de Retiro - Tren Logístico",
                "keywords": ["retiro", "tren logístico", "retiro de productos"]
            },
            "servicio_etiquetado": {
                "titulo": "Servicio de Etiquetado",
                "keywords": ["etiquetado", "servicio opcional"]
            },
            "almacenamiento_diario": {
                "titulo": "Almacenamiento Diario",
                "keywords": ["almacenamiento diario", "tarifa diaria"]
            },
            "almacenamiento_prolongado": {
                "titulo": "Almacenamiento Prolongado",
                "keywords": ["almacenamiento prolongado", "prolongado"]
            },
            "cofinanciamiento_logistico": {
                "titulo": "Cofinanciamiento Logístico (Despacho)",
                "keywords": ["cofinanciamiento", "despacho", "logístico"]
            },
            "retiro_anticipado": {
                "titulo": "Retiro Anticipado desde Bodega",
                "keywords": ["retiro anticipado", "bodega"]
            }
        }
        
        # Buscar secciones específicas
        for key, config in tarifas_map.items():
            section_data = self._extract_section(soup, tables, config["keywords"])
            result["tarifas"][key] = {
                "titulo": config["titulo"],
                "datos": section_data
            }
        
        # También guardar todas las tablas encontradas
        result["todas_las_tablas"] = [t["data"] for t in tables]
        
        logger.info(f"[Falabella] Se encontraron {len(tables)} tablas")
        
        return result
    
    def _extract_section(self, soup, tables: list, keywords: list) -> list:
        """Extrae una sección específica basada en keywords."""
        # Buscar encabezados que contengan las keywords
        for heading_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'strong', 'b', 'p']:
            headings = soup.find_all(heading_tag)
            for heading in headings:
                heading_text = heading.get_text(strip=True).lower()
                if any(kw.lower() in heading_text for kw in keywords):
                    # Buscar la tabla más cercana después de este heading
                    next_table = heading.find_next('table')
                    if next_table:
                        return self._parse_table(next_table)
        
        return []


def scrape_falabella() -> dict[str, Any]:
    """Función helper para ejecutar el scraper."""
    scraper = FalabellaScraper()
    return scraper.scrape()

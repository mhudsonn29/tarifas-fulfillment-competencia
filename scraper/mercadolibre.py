"""Scraper para Mercado Libre Full."""

from typing import Any
from base import BaseScraper, logger
from config import URLS


class MercadoLibreScraper(BaseScraper):
    """Scraper para tarifas de Mercado Libre Full."""
    
    def __init__(self):
        super().__init__("MercadoLibre")
        self.urls = URLS["mercadolibre"]
    
    def scrape(self) -> dict[str, Any]:
        """Extrae todas las tarifas de Mercado Libre Full."""
        result = {
            "marketplace": "Mercado Libre",
            "success": True,
            "tarifas": {}
        }
        
        # Scrape de cada URL
        tarifas_config = [
            ("colecta", "Costos por Colecta", self.urls["colecta"]),
            ("incumplimiento", "Cargos por Incumplimiento", self.urls["incumplimiento"]),
            ("almacenamiento", "Almacenamiento Diario", self.urls["almacenamiento"]),
            ("stock_antiguo", "Stock Antiguo", self.urls["stock_antiguo"]),
            ("retiro_descarte", "Retiro o Descarte", self.urls["retiro_descarte"])
        ]
        
        for key, nombre, url in tarifas_config:
            result["tarifas"][key] = self._scrape_url(url, nombre)
        
        # Verificar si alguno falló
        if any(t.get("error") for t in result["tarifas"].values()):
            result["success"] = False
        
        return result
    
    def _scrape_url(self, url: str, nombre: str) -> dict[str, Any]:
        """Scrape de una URL específica de ayuda de Mercado Libre."""
        soup = self.fetch_page(url)
        
        data = {
            "titulo": nombre,
            "url": url,
            "tablas": [],
            "texto_relevante": []
        }
        
        if not soup:
            data["error"] = f"No se pudo obtener la página"
            return data
        
        # Extraer tablas
        tables = self.extract_tables(soup)
        data["tablas"] = [t["data"] for t in tables]
        
        # Extraer contenido de la página de ayuda
        # Mercado Libre usa divs específicos para el contenido
        article = (
            soup.find('article') or 
            soup.find('div', class_='content') or 
            soup.find('main') or
            soup.find('div', {'id': 'content'})
        )
        
        if article:
            # Buscar párrafos con información de precios
            paragraphs = article.find_all(['p', 'li'])
            for p in paragraphs:
                text = p.get_text(strip=True)
                # Filtrar texto que contenga precios o tarifas
                indicators = ['$', 'clp', 'costo', 'tarifa', 'cargo', 'precio', '%']
                if any(ind in text.lower() for ind in indicators):
                    if len(text) > 10:  # Evitar textos muy cortos
                        data["texto_relevante"].append(text)
        
        logger.info(f"[MercadoLibre] {nombre}: {len(data['tablas'])} tablas, {len(data['texto_relevante'])} textos")
        
        return data


def scrape_mercadolibre() -> dict[str, Any]:
    """Función helper para ejecutar el scraper."""
    scraper = MercadoLibreScraper()
    return scraper.scrape()

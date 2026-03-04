"""Scraper para Mercado Libre Full."""

import logging
from typing import Any
from base import BaseScraper
from config import URLS

logger = logging.getLogger(__name__)


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
        
        # Extraer contenido relevante
        article = (
            soup.find('article') or 
            soup.find('div', class_='content') or 
            soup.find('main') or
            soup.find('body')
        )
        
        if article:
            paragraphs = article.find_all(['p', 'li'])
            for p in paragraphs:
                text = p.get_text(strip=True)
                indicators = ['$', 'clp', 'costo', 'tarifa', 'cargo', 'precio', '%']
                if any(ind in text.lower() for ind in indicators):
                    if 10 < len(text) < 300:
                        data["texto_relevante"].append(text)
        
        logger.info(f"[MercadoLibre] {nombre}: {len(data['tablas'])} tablas")
        
        return data


def scrape_mercadolibre() -> dict[str, Any]:
    """Función helper para ejecutar el scraper."""
    scraper = MercadoLibreScraper()
    result = scraper.scrape()
    scraper._close_browser()
    return result

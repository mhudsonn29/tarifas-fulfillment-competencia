"""Base scraper con funcionalidad común."""

import requests
from bs4 import BeautifulSoup
from typing import Any
import logging
import time
import random

from config import HEADERS

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BaseScraper:
    """Clase base para scrapers de marketplaces."""
    
    def __init__(self, marketplace_name: str):
        self.marketplace_name = marketplace_name
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
    
    def fetch_page(self, url: str, retries: int = 3) -> BeautifulSoup | None:
        """Obtiene y parsea una pagina web con reintentos."""
        for attempt in range(retries):
            try:
                # Pequeño delay aleatorio para evitar rate limiting
                time.sleep(random.uniform(1, 3))
                
                logger.info(f"[{self.marketplace_name}] Obteniendo: {url}")
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                return BeautifulSoup(response.content, 'lxml')
                
            except requests.RequestException as e:
                logger.warning(f"[{self.marketplace_name}] Intento {attempt + 1}/{retries} falló: {e}")
                if attempt < retries - 1:
                    time.sleep(5)  # Esperar antes de reintentar
                else:
                    logger.error(f"[{self.marketplace_name}] Error definitivo al obtener {url}")
                    return None
        return None
    
    def extract_tables(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        """Extrae todas las tablas de una página."""
        tables_data = []
        tables = soup.find_all('table')
        
        for idx, table in enumerate(tables):
            table_data = self._parse_table(table)
            if table_data:
                tables_data.append({
                    'index': idx,
                    'data': table_data
                })
        
        return tables_data
    
    def _parse_table(self, table) -> list[list[str]]:
        """Parsea una tabla HTML a lista de listas."""
        rows = []
        for tr in table.find_all('tr'):
            cells = []
            for cell in tr.find_all(['th', 'td']):
                text = cell.get_text(strip=True)
                cells.append(text)
            if cells:
                rows.append(cells)
        return rows
    
    def scrape(self) -> dict[str, Any]:
        """Método principal de scraping. Debe ser implementado por subclases."""
        raise NotImplementedError("Subclases deben implementar scrape()")

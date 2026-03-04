"""Base scraper con funcionalidad común."""

import requests
from bs4 import BeautifulSoup
from typing import Any
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-CL,es;q=0.9,en;q=0.8",
}


class BaseScraper:
    """Clase base para scrapers de marketplaces."""
    
    def __init__(self, marketplace_name: str):
        self.marketplace_name = marketplace_name
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
    
    def fetch_page(self, url: str, retries: int = 2) -> BeautifulSoup | None:
        """Obtiene y parsea una pagina web."""
        for attempt in range(retries):
            try:
                time.sleep(1)
                logger.info(f"[{self.marketplace_name}] Obteniendo: {url}")
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'lxml')
            except Exception as e:
                logger.warning(f"[{self.marketplace_name}] Intento {attempt + 1} falló: {e}")
                if attempt < retries - 1:
                    time.sleep(2)
        return None
    
    def extract_tables(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        """Extrae todas las tablas de una página."""
        tables_data = []
        tables = soup.find_all('table')
        
        for idx, table in enumerate(tables):
            table_data = self._parse_table(table)
            if table_data:
                tables_data.append({'index': idx, 'data': table_data})
        
        return tables_data
    
    def _parse_table(self, table) -> list[list[str]]:
        """Parsea una tabla HTML a lista de listas."""
        rows = []
        for tr in table.find_all('tr'):
            cells = [cell.get_text(strip=True) for cell in tr.find_all(['th', 'td'])]
            if cells:
                rows.append(cells)
        return rows
    
    def _close_browser(self):
        """Compatibilidad - no hace nada en requests."""
        pass
    
    def scrape(self) -> dict[str, Any]:
        raise NotImplementedError("Subclases deben implementar scrape()")

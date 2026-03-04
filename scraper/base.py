"""Base scraper con Playwright para evitar bloqueos."""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from typing import Any
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BaseScraper:
    """Clase base para scrapers de marketplaces usando Playwright."""
    
    def __init__(self, marketplace_name: str):
        self.marketplace_name = marketplace_name
        self.browser = None
        self.page = None
    
    def _init_browser(self):
        """Inicializa el navegador Playwright."""
        if not self.browser:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=True)
            self.page = self.browser.new_page()
            # Configurar user agent para parecer un navegador real
            self.page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'es-CL,es;q=0.9,en;q=0.8',
            })
    
    def _close_browser(self):
        """Cierra el navegador."""
        if self.browser:
            self.browser.close()
            self.playwright.stop()
            self.browser = None
            self.page = None
    
    def fetch_page(self, url: str, wait_time: int = 3) -> BeautifulSoup | None:
        """Obtiene y parsea una pagina web usando Playwright."""
        try:
            self._init_browser()
            
            logger.info(f"[{self.marketplace_name}] Navegando a: {url}")
            self.page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Esperar un poco para que cargue el contenido dinámico
            time.sleep(wait_time)
            
            # Obtener el HTML de la página
            html = self.page.content()
            
            return BeautifulSoup(html, 'lxml')
            
        except Exception as e:
            logger.error(f"[{self.marketplace_name}] Error al obtener {url}: {e}")
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
    
    def __del__(self):
        """Limpieza al destruir el objeto."""
        self._close_browser()

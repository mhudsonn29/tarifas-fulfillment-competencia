"""Base scraper con Playwright para páginas con JS."""

import logging
import time
from typing import Any
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, Page, Browser

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BaseScraper:
    """Scraper base con Playwright - maneja JS y páginas dinámicas."""

    def __init__(self, marketplace_name: str):
        self.marketplace_name = marketplace_name
        self._playwright = None
        self._browser: Browser | None = None

    def _get_browser(self) -> Browser:
        """Inicializa y retorna el browser (lazy)."""
        if not self._browser:
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )
        return self._browser

    def fetch_page(self, url: str, wait_selector: str = None, retries: int = 2) -> BeautifulSoup | None:
        """Obtiene una página con Playwright y retorna BeautifulSoup."""
        browser = self._get_browser()

        for attempt in range(retries):
            page: Page = None
            try:
                logger.info(f"[{self.marketplace_name}] Abriendo: {url}")
                page = browser.new_page(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                page.set_extra_http_headers({"Accept-Language": "es-CL,es;q=0.9"})
                page.goto(url, wait_until="networkidle", timeout=30000)

                if wait_selector:
                    page.wait_for_selector(wait_selector, timeout=10000)

                # Scroll para cargar lazy content
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1)

                content = page.content()
                return BeautifulSoup(content, "lxml")

            except Exception as e:
                logger.warning(f"[{self.marketplace_name}] Intento {attempt + 1} falló: {e}")
                if attempt < retries - 1:
                    time.sleep(3)
            finally:
                if page:
                    page.close()

        return None

    def extract_tables(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        """Extrae todas las tablas HTML como listas de listas."""
        tables_data = []
        for idx, table in enumerate(soup.find_all("table")):
            rows = self._parse_table(table)
            if rows:
                tables_data.append({"index": idx, "data": rows})
        return tables_data

    def _parse_table(self, table) -> list[list[str]]:
        """Parsea una tabla HTML a lista de listas."""
        rows = []
        for tr in table.find_all("tr"):
            cells = [cell.get_text(strip=True) for cell in tr.find_all(["th", "td"])]
            if cells:
                rows.append(cells)
        return rows

    def close(self):
        """Cierra el browser y Playwright."""
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()

    # Compatibilidad con código anterior
    def _close_browser(self):
        self.close()

    def scrape(self) -> dict[str, Any]:
        raise NotImplementedError("Subclases deben implementar scrape()")

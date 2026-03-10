"""Script de debug: guarda el HTML real de cada pagina para analizar su estructura."""

import os
import sys
import time

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from playwright.sync_api import sync_playwright

DEBUG_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "debug_html"
)

URLS = {
    "falabella": "https://ayudaseller.falabella.com/s/article/Tarifas-Fulfillment-by-Falabella-Chile?language=es#a01",
    "mercadolibre": "https://www.mercadolibre.cl/ayuda/33736",
    "paris": "https://ayuda.marketplace.paris.cl/2023/09/20/que-es-fulfillment/",
}


def dump_page(name: str, url: str, page):
    """Navega a la URL y guarda el HTML completo."""
    print(f"\n-> Abriendo {name}: {url}")
    try:
        page.goto(url, wait_until="networkidle", timeout=30000)
        time.sleep(2)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)
        html = page.content()
        path = os.path.join(DEBUG_DIR, f"{name}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"   OK - {len(html)} chars guardados en {path}")
    except Exception as e:
        print(f"   ERROR: {e}")


def run():
    os.makedirs(DEBUG_DIR, exist_ok=True)
    print("=" * 60)
    print("DEBUG: Guardando HTML de paginas de tarifas")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page.set_extra_http_headers({"Accept-Language": "es-CL,es;q=0.9"})

        for name, url in URLS.items():
            dump_page(name, url, page)

        browser.close()

    print("\n=" * 60)
    print("DEBUG COMPLETADO")
    print("=" * 60)


if __name__ == "__main__":
    run()

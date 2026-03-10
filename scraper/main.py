#!/usr/bin/env python3
"""Orquestador principal: scraping + cache + generacion HTML."""

import sys
import os
from datetime import datetime

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from falabella import scrape_falabella
from paris import scrape_paris
from mercadolibre import scrape_mercadolibre
from wfs import scrape_wfs
from cache import load_cache, save_cache, update_platform
from html_generator import generate_html

DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")


def run_scraper(name: str, fn) -> tuple[bool, list, str | None]:
    """Ejecuta un scraper y retorna (success, tarifas, error)."""
    print(f"\n-> Scraping {name}...")
    try:
        result = fn()
        success = result.get("success", False)
        tarifas = result.get("tarifas", [])
        error = result.get("error")
        status = "OK" if success else f"FALLO: {error}"
        print(f"   [{name}] {status} | {len(tarifas)} tarifas")
        return success, tarifas, error
    except Exception as e:
        print(f"   [{name}] ERROR: {e}")
        return False, [], str(e)


def run():
    print("=" * 60)
    print(f"SCRAPING TARIFAS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    cache = load_cache()

    # Ejecutar todos los scrapers
    scrapers = [
        ("wfs",          scrape_wfs),
        ("falabella",    scrape_falabella),
        ("paris",        scrape_paris),
        ("mercadolibre", scrape_mercadolibre),
    ]

    for platform, fn in scrapers:
        success, tarifas, error = run_scraper(platform, fn)
        cache = update_platform(cache, platform, tarifas, success, error)

    save_cache(cache)

    # Generar HTML con datos actualizados
    print("\nGenerando pagina HTML...")
    os.makedirs(DOCS_DIR, exist_ok=True)
    html_path = generate_html(cache, output_dir=DOCS_DIR)
    print(f"HTML generado: {html_path}")

    print("\n" + "=" * 60)
    print("COMPLETADO")
    print("=" * 60)


if __name__ == "__main__":
    run()

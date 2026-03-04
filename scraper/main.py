#!/usr/bin/env python3
"""Script principal para ejecutar el scraping de tarifas de fulfillment."""

import sys
import os
import json
from datetime import datetime

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from falabella import scrape_falabella
from mercadolibre import scrape_mercadolibre
from paris import scrape_paris
from html_generator import generate_html


def run_scraping():
    """Ejecuta el scraping de todos los marketplaces y genera el HTML."""
    print("=" * 60)
    print(f"SCRAPING DE TARIFAS FULFILLMENT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    results = {}
    
    # Scrape Falabella
    print("\n[1/3] Scrapeando Falabella...")
    try:
        results['falabella'] = scrape_falabella()
        status = "✅" if results['falabella'].get('success') else "⚠️"
        print(f"      {status} Falabella completado")
    except Exception as e:
        print(f"      ❌ Error en Falabella: {e}")
        results['falabella'] = {"success": False, "error": str(e), "tarifas": {}}
    
    # Scrape Mercado Libre
    print("\n[2/3] Scrapeando Mercado Libre...")
    try:
        results['mercadolibre'] = scrape_mercadolibre()
        status = "✅" if results['mercadolibre'].get('success') else "⚠️"
        print(f"      {status} Mercado Libre completado")
    except Exception as e:
        print(f"      ❌ Error en Mercado Libre: {e}")
        results['mercadolibre'] = {"success": False, "error": str(e), "tarifas": {}}
    
    # Scrape Paris
    print("\n[3/3] Scrapeando Paris...")
    try:
        results['paris'] = scrape_paris()
        status = "✅" if results['paris'].get('success') else "⚠️"
        print(f"      {status} Paris completado")
    except Exception as e:
        print(f"      ❌ Error en Paris: {e}")
        results['paris'] = {"success": False, "error": str(e), "tarifas": {}}
    
    # Guardar JSON con los datos crudos (para debug)
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs')
    os.makedirs(docs_dir, exist_ok=True)
    
    json_path = os.path.join(docs_dir, 'datos.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Datos JSON guardados en: {json_path}")
    
    # Generar HTML
    print("\nGenerando página HTML...")
    try:
        html_path = generate_html(
            falabella_data=results['falabella'],
            mercadolibre_data=results['mercadolibre'],
            paris_data=results['paris'],
            output_dir=docs_dir
        )
        print(f"✅ HTML generado: {html_path}")
    except Exception as e:
        print(f"❌ Error generando HTML: {e}")
        raise
    
    print("\n" + "=" * 60)
    print("✅ SCRAPING COMPLETADO")
    print("=" * 60)
    
    # Resumen
    total_success = sum(1 for r in results.values() if r.get('success'))
    print(f"\nResumen: {total_success}/3 marketplaces obtenidos correctamente")
    
    return html_path


if __name__ == "__main__":
    run_scraping()

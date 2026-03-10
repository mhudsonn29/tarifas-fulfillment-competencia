#!/usr/bin/env python3
"""Script principal para generar la página de tarifas de fulfillment."""

import sys
import os
from datetime import datetime

# Fix encoding for Windows terminals
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from html_generator import generate_html


def run():
    """Genera la página HTML con los links a las tarifas."""
    print("=" * 60)
    print(f"GENERANDO PAGINA TARIFAS FULFILLMENT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs')
    os.makedirs(docs_dir, exist_ok=True)
    
    print("\nGenerando página HTML...")
    html_path = generate_html(output_dir=docs_dir)
    print(f"✅ HTML generado: {html_path}")
    
    print("\n" + "=" * 60)
    print("✅ GENERACION COMPLETADA")
    print("=" * 60)
    
    return html_path


if __name__ == "__main__":
    run()

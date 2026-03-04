"""Configuración de URLs y datos a extraer de cada marketplace."""

URLS = {
    "falabella": {
        "tarifas": "https://ayudaseller.falabella.com/s/article/Tarifas-Fulfillment-by-Falabella-Chile?language=es#a01"
    },
    "mercadolibre": {
        "colecta": "https://www.mercadolibre.cl/ayuda/33736",
        "incumplimiento": "https://www.mercadolibre.cl/ayuda/19758",
        "almacenamiento": "https://www.mercadolibre.cl/ayuda/24253",
        "stock_antiguo": "https://www.mercadolibre.cl/ayuda/15373",
        "retiro_descarte": "https://www.mercadolibre.cl/ayuda/16645"
    },
    "paris": {
        "costos_logisticos": "https://ayuda.marketplace.paris.cl/2023/03/23/costos-logisticos/",
        "fulfillment": "https://ayuda.marketplace.paris.cl/2023/09/20/que-es-fulfillment/"
    }
}

# Headers para simular un navegador real
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "es-CL,es;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
}

# Nombres legibles para mostrar
MARKETPLACE_NAMES = {
    "falabella": "Falabella",
    "mercadolibre": "Mercado Libre",
    "paris": "Paris"
}

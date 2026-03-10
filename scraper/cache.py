"""Manejo de cache JSON con fallback de últimos datos válidos."""

import json
import os
import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

CACHE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "tarifas_cache.json"
)

# Datos base WFS (hardcoded - fuente: portal oficial Walmart)
WFS_TARIFAS_BASE = {
    "fulfillment": [
        {"talla": "XS", "peso_min": 0,   "peso_max": 2,   "costo": 2000},
        {"talla": "S1", "peso_min": 2,   "peso_max": 4,   "costo": 2500},
        {"talla": "S2", "peso_min": 4,   "peso_max": 6,   "costo": 3990},
        {"talla": "S3", "peso_min": 6,   "peso_max": 15,  "costo": 4250},
        {"talla": "M1", "peso_min": 15,  "peso_max": 25,  "costo": 5590},
        {"talla": "M2", "peso_min": 25,  "peso_max": 50,  "costo": 6290},
        {"talla": "L",  "peso_min": 50,  "peso_max": 400, "costo": 6990},
        {"talla": "XL", "peso_min": 400, "peso_max": 9999, "costo": 18990}
    ]
}


def load_cache() -> dict[str, Any]:
    """Carga el cache desde disco. Si no existe, retorna estructura vacía."""
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error leyendo cache: {e}")
    return _empty_cache()


def save_cache(data: dict[str, Any]) -> None:
    """Guarda el cache en disco."""
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"Cache guardado en {CACHE_PATH}")


def update_platform(cache: dict, platform: str, tarifas: list[dict], success: bool, error: str = None) -> dict:
    """Actualiza los datos de una plataforma en el cache."""
    now = datetime.utcnow().isoformat()

    if success and tarifas:
        cache["platforms"][platform] = {
            "tarifas": tarifas,
            "last_success": now,
            "last_attempt": now,
            "success": True,
            "error": None
        }
        logger.info(f"[{platform}] Cache actualizado exitosamente")
    else:
        # Mantener tarifas anteriores, solo actualizar estado
        existing = cache["platforms"].get(platform, {})
        cache["platforms"][platform] = {
            "tarifas": existing.get("tarifas", []),
            "last_success": existing.get("last_success"),
            "last_attempt": now,
            "success": False,
            "error": error or "Error desconocido"
        }
        logger.warning(f"[{platform}] Scraping falló, manteniendo datos anteriores")

    cache["last_run"] = now
    return cache


def _empty_cache() -> dict[str, Any]:
    """Retorna estructura de cache inicial con datos WFS precargados."""
    now = datetime.utcnow().isoformat()
    return {
        "last_run": None,
        "platforms": {
            "wfs": {
                "tarifas": WFS_TARIFAS_BASE["fulfillment"],
                "last_success": now,
                "last_attempt": now,
                "success": True,
                "error": None
            },
            "falabella": {
                "tarifas": [],
                "last_success": None,
                "last_attempt": None,
                "success": False,
                "error": "Sin datos aún"
            },
            "paris": {
                "tarifas": [],
                "last_success": None,
                "last_attempt": None,
                "success": False,
                "error": "Sin datos aún"
            },
            "mercadolibre": {
                "tarifas": [],
                "last_success": None,
                "last_attempt": None,
                "success": False,
                "error": "Sin datos aún"
            }
        }
    }

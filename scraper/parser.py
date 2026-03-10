"""Parser de tablas de tarifas: extrae peso y costo en formato estandar."""

import re
import logging
from typing import Any

logger = logging.getLogger(__name__)


def parse_precio(texto: str) -> int | None:
    """Extrae el precio en CLP de un string como '$3.990' o '3990'."""
    if not texto:
        return None
    # Eliminar signos, puntos de miles y espacios
    limpio = re.sub(r"[$\s]", "", texto)
    limpio = re.sub(r"\.(\d{3})", r"\1", limpio)  # 3.990 -> 3990
    match = re.search(r"(\d+)", limpio)
    if match:
        return int(match.group(1))
    return None


def parse_peso(texto: str) -> float | None:
    """Extrae el peso en kg de un string como '< 2', '2 - 4', '50 kg', etc."""
    if not texto:
        return None
    texto = texto.lower().replace(",", ".").replace("kg", "").strip()
    match = re.search(r"([\d.]+)", texto)
    if match:
        return float(match.group(1))
    return None


def detectar_columna_peso(headers: list[str]) -> int | None:
    """Detecta qué columna contiene el peso/talla."""
    keywords = ["kg", "peso", "talla", "tamaño", "rango", "volum", "size"]
    for i, h in enumerate(headers):
        if any(k in h.lower() for k in keywords):
            return i
    return None


def detectar_columna_precio(headers: list[str]) -> int | None:
    """Detecta qué columna contiene el precio."""
    keywords = ["costo", "precio", "tarifa", "valor", "$", "cobro", "seller"]
    for i, h in enumerate(headers):
        if any(k in h.lower() for k in keywords):
            return i
    return None


def tabla_a_tarifas(tabla: list[list[str]], peso_min_col: int = None,
                   peso_max_col: int = None, precio_col: int = None) -> list[dict]:
    """Convierte una tabla raw en lista de tarifas {peso_min, peso_max, costo}."""
    if not tabla or len(tabla) < 2:
        return []

    headers = [h.lower() for h in tabla[0]]
    tarifas = []

    # Auto-detectar columnas si no se especifican
    if precio_col is None:
        precio_col = detectar_columna_precio(headers)
    if precio_col is None:
        logger.warning("No se encontró columna de precio")
        return []

    for row in tabla[1:]:
        if len(row) <= precio_col:
            continue
        precio = parse_precio(row[precio_col])
        if not precio:
            continue

        tarifa = {"costo": precio, "talla": None, "peso_min": 0, "peso_max": 9999}

        # Intentar extraer rango de peso de las columnas disponibles
        pesos_en_fila = []
        for i, celda in enumerate(row):
            if i == precio_col:
                continue
            p = parse_peso(celda)
            if p is not None:
                pesos_en_fila.append(p)

        if len(pesos_en_fila) == 1:
            tarifa["peso_max"] = pesos_en_fila[0]
        elif len(pesos_en_fila) >= 2:
            tarifa["peso_min"] = pesos_en_fila[0]
            tarifa["peso_max"] = pesos_en_fila[1]

        # Talla: primera columna si no parece un número
        if row[0] and not re.match(r'^[\d$.,<>\s]+$', row[0]):
            tarifa["talla"] = row[0].strip()

        tarifas.append(tarifa)

    return tarifas


def parse_falabella(tablas: list[list[list[str]]]) -> list[dict]:
    """Parsea tablas de Falabella al formato estandar."""
    for tabla in tablas:
        tarifas = tabla_a_tarifas(tabla)
        if tarifas:
            logger.info(f"[Falabella] {len(tarifas)} tarifas parseadas")
            return tarifas
    return []


def parse_paris(tablas: list[list[list[str]]]) -> list[dict]:
    """Parsea tablas de Paris al formato estandar."""
    for tabla in tablas:
        tarifas = tabla_a_tarifas(tabla)
        if tarifas:
            logger.info(f"[Paris] {len(tarifas)} tarifas parseadas")
            return tarifas
    return []


def parse_mercadolibre(tablas: list[list[list[str]]]) -> list[dict]:
    """Parsea tablas de MercadoLibre (usa la de colecta como comparacion)."""
    for tabla in tablas:
        tarifas = tabla_a_tarifas(tabla)
        if tarifas:
            logger.info(f"[MercadoLibre] {len(tarifas)} tarifas parseadas")
            return tarifas
    return []

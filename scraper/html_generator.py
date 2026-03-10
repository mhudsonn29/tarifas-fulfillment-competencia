"""Generador de pagina HTML con calculadora y comparador de tarifas."""

import os
import json
from datetime import datetime
from typing import Any


PLATFORMS_META = {
    "wfs":          {"nombre": "Walmart WFS",    "color": "#0053e2", "emoji": "🔷"},
    "falabella":    {"nombre": "Falabella",       "color": "#009e60", "emoji": "🟢"},
    "paris":        {"nombre": "Paris",           "color": "#2563eb", "emoji": "🔵"},
    "mercadolibre": {"nombre": "Mercado Libre",   "color": "#d97706", "emoji": "🟡"},
}

LINKS = {
    "wfs":          "https://marketplacelearn.walmart.com/cl/guides/Walmart%20Fulfillment%20Services/Walmart%20Fulfillment%20Services/tarifas-wfs",
    "falabella":    "https://ayudaseller.falabella.com/s/article/Tarifas-Fulfillment-by-Falabella-Chile?language=es#a01",
    "paris":        "https://ayuda.marketplace.paris.cl/2023/09/20/que-es-fulfillment/",
    "mercadolibre": "https://www.mercadolibre.cl/ayuda/33736",
}


def _format_fecha(iso: str | None) -> str:
    if not iso:
        return "nunca"
    try:
        dt = datetime.fromisoformat(iso)
        return dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return iso


def _build_status_banners(platforms: dict) -> str:
    """Genera los banners de advertencia para plataformas con error."""
    banners = []
    for key, data in platforms.items():
        if not data.get("success") and data.get("last_success") is None:
            continue  # Primera vez sin datos - no mostrar banner todavia
        if not data.get("success"):
            meta = PLATFORMS_META[key]
            fecha = _format_fecha(data.get("last_success"))
            banners.append(f"""
            <div class="flex items-start gap-3 p-4 mb-3 rounded-lg border border-red-300 bg-red-50">
                <span class="text-xl">⚠️</span>
                <div>
                    <p class="font-semibold text-red-700">{meta['nombre']}: no se pudo actualizar</p>
                    <p class="text-sm text-red-600">Ultimo dato valido: {fecha} — {data.get('error', 'Error desconocido')}</p>
                </div>
            </div>""")
    return "\n".join(banners)


def _build_links_section(platforms: dict) -> str:
    """Genera la seccion de links a las paginas oficiales."""
    cards = []
    for key, meta in PLATFORMS_META.items():
        data = platforms.get(key, {})
        fecha = _format_fecha(data.get("last_success"))
        status_badge = (
            '<span class="text-xs px-2 py-1 rounded-full bg-green-100 text-green-700 font-medium">✅ Actualizado</span>'
            if data.get("success")
            else '<span class="text-xs px-2 py-1 rounded-full bg-red-100 text-red-700 font-medium">⚠️ Sin actualizar</span>'
        )
        cards.append(f"""
            <div class="bg-white rounded-xl shadow p-5 border-t-4" style="border-color:{meta['color']}">
                <div class="flex justify-between items-start mb-3">
                    <h3 class="text-lg font-bold" style="color:{meta['color']}">{meta['emoji']} {meta['nombre']}</h3>
                    {status_badge}
                </div>
                <p class="text-xs text-gray-400 mb-4">Ultima actualizacion: {fecha}</p>
                <a href="{LINKS[key]}" target="_blank"
                   class="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-white text-sm font-medium transition hover:opacity-90"
                   style="background-color:{meta['color']}">
                    🔗 Ver tarifas oficiales
                </a>
            </div>""")
    return "\n".join(cards)


def _build_js_data(platforms: dict) -> str:
    """Serializa las tarifas como objeto JS para la calculadora."""
    js_data = {}
    for key, meta in PLATFORMS_META.items():
        data = platforms.get(key, {})
        js_data[key] = {
            "nombre": meta["nombre"],
            "color": meta["color"],
            "tarifas": data.get("tarifas", []),
            "disponible": bool(data.get("tarifas"))
        }
    return json.dumps(js_data, ensure_ascii=False)


def _build_calculator_js() -> str:
    """Retorna el JS de la calculadora."""
    return """
    function getCosto(tarifas, peso) {
        if (!tarifas || tarifas.length === 0) return null;
        for (const t of tarifas) {
            const min = t.peso_min ?? 0;
            const max = t.peso_max ?? 9999;
            if (peso >= min && peso < max) return t;
        }
        // Si supera el maximo, usar el ultimo tramo
        return tarifas[tarifas.length - 1];
    }

    function formatPrecio(n) {
        return '$' + n.toLocaleString('es-CL');
    }

    function calcular() {
        const peso = parseFloat(document.getElementById('peso-input').value);
        if (isNaN(peso) || peso <= 0) {
            document.getElementById('resultado').innerHTML =
                '<p class="text-red-500 font-medium">⚠️ Ingresa un peso valido (mayor a 0 kg)</p>';
            return;
        }

        const resultados = [];
        for (const [key, plat] of Object.entries(TARIFAS_DATA)) {
            if (!plat.disponible) {
                resultados.push({ key, nombre: plat.nombre, color: plat.color,
                    costo: null, talla: null, disponible: false });
                continue;
            }
            const t = getCosto(plat.tarifas, peso);
            resultados.push({
                key, nombre: plat.nombre, color: plat.color,
                costo: t ? t.costo : null,
                talla: t ? (t.talla || '-') : null,
                disponible: true
            });
        }

        // Ordenar por costo (null al final)
        resultados.sort((a, b) => {
            if (a.costo === null) return 1;
            if (b.costo === null) return -1;
            return a.costo - b.costo;
        });

        const minCosto = resultados.find(r => r.costo !== null)?.costo;

        let html = `
            <h3 class="text-lg font-bold text-gray-700 mb-4">
                Resultados para <span class="text-blue-700">${peso} kg</span>
            </h3>
            <div class="overflow-x-auto">
            <table class="w-full text-sm border-collapse rounded-xl overflow-hidden shadow">
                <thead>
                    <tr class="text-white" style="background-color:#0053e2">
                        <th class="px-4 py-3 text-left">#</th>
                        <th class="px-4 py-3 text-left">Plataforma</th>
                        <th class="px-4 py-3 text-left">Talla</th>
                        <th class="px-4 py-3 text-left">Costo Fulfillment</th>
                        <th class="px-4 py-3 text-left"></th>
                    </tr>
                </thead>
                <tbody>`;

        resultados.forEach((r, i) => {
            const esGanador = r.costo !== null && r.costo === minCosto;
            const bg = esGanador ? 'background-color:#f0fdf4; font-weight:bold;' : (i % 2 === 0 ? 'background-color:#f8fafc;' : '');
            const costoTxt = r.costo !== null ? formatPrecio(r.costo) : '<span class="text-gray-400">Sin datos</span>';
            const badge = esGanador ? '<span class="ml-2 px-2 py-0.5 rounded-full text-xs bg-green-600 text-white">🏆 Mas rentable</span>' : '';

            html += `
                <tr style="${bg}">
                    <td class="px-4 py-3 text-gray-400">${r.costo !== null ? i + 1 : '-'}</td>
                    <td class="px-4 py-3 font-semibold" style="color:${r.color}">${r.nombre}</td>
                    <td class="px-4 py-3">${r.talla || '-'}</td>
                    <td class="px-4 py-3">${costoTxt}${badge}</td>
                    <td class="px-4 py-3"></td>
                </tr>`;
        });

        html += '</tbody></table></div>';

        if (minCosto) {
            const ganador = resultados.find(r => r.costo === minCosto);
            html += `<div class="mt-4 p-4 rounded-xl border-2 border-green-400 bg-green-50">
                <p class="font-bold text-green-800">🏆 Para un producto de ${peso} kg, la opcion mas rentable es <span style="color:${ganador.color}">${ganador.nombre}</span> con un costo de ${formatPrecio(minCosto)}</p>
            </div>`;
        }

        document.getElementById('resultado').innerHTML = html;
    }

    document.getElementById('peso-input').addEventListener('keydown', function(e) {
        if (e.key === 'Enter') calcular();
    });
    """


def generate_html(cache: dict[str, Any], output_dir: str = "docs") -> str:
    """Genera el index.html completo con comparador y calculadora."""
    os.makedirs(output_dir, exist_ok=True)

    platforms = cache.get("platforms", {})
    last_run = _format_fecha(cache.get("last_run"))
    status_banners = _build_status_banners(platforms)
    links_section = _build_links_section(platforms)
    js_data = _build_js_data(platforms)
    calculator_js = _build_calculator_js()

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comparador Tarifas Fulfillment - Chile</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 min-h-screen">

    <!-- HEADER -->
    <header class="text-white py-6 shadow-lg" style="background-color:#0053e2">
        <div class="container mx-auto px-4">
            <h1 class="text-3xl font-bold">📦 Comparador Tarifas Fulfillment</h1>
            <p class="mt-1 text-blue-200 text-sm">Walmart WFS · Falabella · Paris · Mercado Libre</p>
            <p class="mt-1 text-blue-300 text-xs">Ultima actualizacion: {last_run}</p>
        </div>
    </header>

    <main class="container mx-auto px-4 py-8 max-w-5xl">

        <!-- BANNERS DE ERROR -->
        {'<div class="mb-6">' + status_banners + '</div>' if status_banners.strip() else ''}

        <!-- CALCULADORA -->
        <section class="bg-white rounded-2xl shadow-md p-6 mb-8 border-t-4" style="border-color:#ffc220">
            <h2 class="text-2xl font-bold text-gray-800 mb-1">🧮 Calculadora por peso</h2>
            <p class="text-gray-500 text-sm mb-5">Ingresa el peso de tu producto y te mostramos cual plataforma te conviene mas</p>

            <div class="flex gap-3 items-center flex-wrap">
                <input
                    id="peso-input"
                    type="number"
                    min="0.1"
                    step="0.1"
                    placeholder="Ej: 2.5"
                    class="border-2 border-gray-300 rounded-xl px-4 py-3 text-lg w-40 focus:outline-none focus:border-blue-500"
                />
                <span class="text-gray-600 font-medium">kg</span>
                <button
                    onclick="calcular()"
                    class="px-6 py-3 rounded-xl text-white font-bold text-base transition hover:opacity-90"
                    style="background-color:#0053e2">
                    Comparar ➜
                </button>
            </div>

            <div id="resultado" class="mt-6"></div>
        </section>

        <!-- LINKS TARIFAS OFICIALES -->
        <section class="mb-8">
            <h2 class="text-xl font-bold text-gray-700 mb-4">🔗 Tarifas oficiales por plataforma</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                {links_section}
            </div>
        </section>

    </main>

    <footer class="py-6" style="background-color:#001e6c">
        <div class="container mx-auto px-4 text-center">
            <p class="text-blue-200">🐶 Generado automaticamente por Code Puppy para WFS Chile</p>
            <p class="text-blue-400 text-xs mt-1">Actualizado cada 24 horas via GitHub Actions</p>
        </div>
    </footer>

    <script>
        const TARIFAS_DATA = {js_data};
        {calculator_js}
    </script>
</body>
</html>"""

    output_path = os.path.join(output_dir, "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path

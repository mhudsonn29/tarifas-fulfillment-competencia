"""Generador de página HTML con las tarifas."""

import os
from datetime import datetime
from typing import Any
from jinja2 import Template


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tarifas Fulfillment - Competencia Chile</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .table-container { overflow-x: auto; }
        table { border-collapse: collapse; width: 100%; }
        th, td { padding: 8px 12px; text-align: left; border: 1px solid #e5e7eb; }
        th { background-color: #f3f4f6; font-weight: 600; }
        tr:nth-child(even) { background-color: #f9fafb; }
        tr:hover { background-color: #f0f9ff; }
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <header class="bg-blue-700 text-white py-6 shadow-lg">
        <div class="container mx-auto px-4">
            <h1 class="text-3xl font-bold">📦 Tarifas Fulfillment - Competencia</h1>
            <p class="mt-2 text-blue-100">Actualizado: {{ updated_at }}</p>
        </div>
    </header>

    <main class="container mx-auto px-4 py-8">
        <!-- Status Banner -->
        <div class="mb-8 p-4 rounded-lg bg-green-100 border border-green-300">
            <p class="font-medium">✅ Datos actualizados - Se actualiza automáticamente cada 48 horas</p>
        </div>

        <!-- FALABELLA -->
        <section class="mb-12 bg-white rounded-lg shadow-md p-6">
            <h2 class="text-2xl font-bold text-green-700 mb-4 flex items-center">
                <span class="mr-2">🟢</span> Falabella
            </h2>
            
            <div class="mb-4">
                <a href="https://ayudaseller.falabella.com/s/article/Tarifas-Fulfillment-by-Falabella-Chile?language=es#a01" 
                   target="_blank" 
                   class="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition">
                    🔗 Ver tarifas en Falabella
                </a>
            </div>
            
            {% if falabella.todas_las_tablas and falabella.todas_las_tablas|length > 0 %}
            <div class="mt-4">
                <h3 class="text-lg font-semibold text-gray-700 mb-3">📊 Tablas extraídas automáticamente:</h3>
                {% for tabla in falabella.todas_las_tablas %}
                <div class="mb-4 table-container">
                    <table class="text-sm">
                        {% for row in tabla %}
                        <tr>
                            {% for cell in row %}
                            {% if loop.parent.first %}
                            <th class="bg-green-50">{{ cell }}</th>
                            {% else %}
                            <td>{{ cell }}</td>
                            {% endif %}
                            {% endfor %}
                        </tr>
                        {% endfor %}
                    </table>
                </div>
                {% endfor %}
            </div>
            {% else %}
            <p class="text-sm text-gray-500 mt-2">Haz clic en el botón para ver las tarifas de retiro, etiquetado, almacenamiento, cofinanciamiento y más.</p>
            {% endif %}
        </section>

        <!-- MERCADO LIBRE -->
        <section class="mb-12 bg-white rounded-lg shadow-md p-6">
            <h2 class="text-2xl font-bold text-yellow-600 mb-4 flex items-center">
                <span class="mr-2">🟡</span> Mercado Libre
            </h2>
            
            <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {% for key, tarifa in mercadolibre.tarifas.items() %}
                <div class="p-4 bg-gray-50 rounded">
                    <h3 class="font-semibold text-gray-700 mb-2">{{ tarifa.titulo }}</h3>
                    <a href="{{ tarifa.url }}" target="_blank" 
                       class="inline-flex items-center px-4 py-2 bg-yellow-500 text-gray-900 rounded-lg hover:bg-yellow-600 transition font-medium">
                        🔗 Ver tarifas
                    </a>
                    
                    {% if tarifa.tablas and tarifa.tablas|length > 0 %}
                    <div class="mt-3">
                        {% for tabla in tarifa.tablas %}
                        <div class="table-container mb-2">
                            <table class="text-xs">
                                {% for row in tabla %}
                                <tr>
                                    {% for cell in row %}
                                    {% if loop.parent.first %}
                                    <th class="bg-yellow-50">{{ cell }}</th>
                                    {% else %}
                                    <td>{{ cell }}</td>
                                    {% endif %}
                                    {% endfor %}
                                </tr>
                                {% endfor %}
                            </table>
                        </div>
                        {% endfor %}
                    </div>
                    {% endif %}
                    
                    {% if tarifa.texto_relevante and tarifa.texto_relevante|length > 0 %}
                    <ul class="mt-2 text-xs text-gray-600 list-disc list-inside">
                        {% for texto in tarifa.texto_relevante[:3] %}
                        <li>{{ texto[:100] }}{% if texto|length > 100 %}...{% endif %}</li>
                        {% endfor %}
                    </ul>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
        </section>

        <!-- PARIS -->
        <section class="mb-12 bg-white rounded-lg shadow-md p-6">
            <h2 class="text-2xl font-bold text-blue-600 mb-4 flex items-center">
                <span class="mr-2">🔵</span> Paris
            </h2>
            
            <!-- Costos Logísticos -->
            <div class="mb-6 p-4 bg-gray-50 rounded">
                <h3 class="text-lg font-semibold text-gray-700 mb-3">Costos de Despacho a Domicilio</h3>
                <a href="https://ayuda.marketplace.paris.cl/2023/03/23/costos-logisticos/" 
                   target="_blank" 
                   class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
                    🔗 Ver tarifas de despacho
                </a>
                
                {% if paris.tarifas.despacho.todas_las_tablas and paris.tarifas.despacho.todas_las_tablas|length > 0 %}
                <div class="mt-4">
                    {% for tabla in paris.tarifas.despacho.todas_las_tablas %}
                    <div class="mb-4 table-container">
                        <table class="text-sm">
                            {% for row in tabla %}
                            <tr>
                                {% for cell in row %}
                                {% if loop.parent.first %}
                                <th class="bg-blue-50">{{ cell }}</th>
                                {% else %}
                                <td>{{ cell }}</td>
                                {% endif %}
                                {% endfor %}
                            </tr>
                            {% endfor %}
                        </table>
                    </div>
                    {% endfor %}
                </div>
                {% else %}
                <p class="text-sm text-gray-500 mt-2">Incluye tablas de costos para despachos menores y mayores a $49.990</p>
                {% endif %}
            </div>
            
            <!-- Fulfillment -->
            <div class="mb-6 p-4 bg-gray-50 rounded">
                <h3 class="text-lg font-semibold text-gray-700 mb-3">Fulfillment by Paris (Almacenamiento y Retiro)</h3>
                <a href="https://ayuda.marketplace.paris.cl/2023/09/20/que-es-fulfillment/" 
                   target="_blank" 
                   class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
                    🔗 Ver tarifas de almacenamiento y retiro
                </a>
                
                {% if paris.tarifas.fulfillment.todas_las_tablas and paris.tarifas.fulfillment.todas_las_tablas|length > 0 %}
                <div class="mt-4">
                    {% for tabla in paris.tarifas.fulfillment.todas_las_tablas %}
                    <div class="mb-4 table-container">
                        <table class="text-sm">
                            {% for row in tabla %}
                            <tr>
                                {% for cell in row %}
                                {% if loop.parent.first %}
                                <th class="bg-blue-50">{{ cell }}</th>
                                {% else %}
                                <td>{{ cell }}</td>
                                {% endif %}
                                {% endfor %}
                            </tr>
                            {% endfor %}
                        </table>
                    </div>
                    {% endfor %}
                </div>
                {% else %}
                <p class="text-sm text-gray-500 mt-2">Incluye costos de almacenamiento y retiro de productos</p>
                {% endif %}
            </div>
        </section>
    </main>

    <footer class="bg-gray-800 text-white py-6">
        <div class="container mx-auto px-4 text-center">
            <p>🐶 Generado automáticamente por Code Puppy para WFS Chile</p>
            <p class="text-sm text-gray-400 mt-1">Se actualiza cada 48 horas vía GitHub Actions</p>
        </div>
    </footer>
</body>
</html>
"""


def generate_html(
    falabella_data: dict[str, Any],
    mercadolibre_data: dict[str, Any],
    paris_data: dict[str, Any],
    output_dir: str = "docs"
) -> str:
    """Genera el archivo HTML con las tarifas."""
    
    # Crear directorio de salida
    os.makedirs(output_dir, exist_ok=True)
    
    # Renderizar template
    template = Template(HTML_TEMPLATE)
    html_content = template.render(
        updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        falabella=falabella_data,
        mercadolibre=mercadolibre_data,
        paris=paris_data
    )
    
    # Guardar archivo
    output_path = os.path.join(output_dir, "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return output_path

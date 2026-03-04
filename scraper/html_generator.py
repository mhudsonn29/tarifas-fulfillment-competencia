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
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        walmart: {
                            blue: '#0071dc',
                            yellow: '#ffc220',
                        }
                    }
                }
            }
        }
    </script>
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
    <header class="bg-walmart-blue text-white py-6 shadow-lg">
        <div class="container mx-auto px-4">
            <h1 class="text-3xl font-bold">📦 Tarifas Fulfillment - Competencia</h1>
            <p class="mt-2 text-blue-100">Actualizado: {{ updated_at }}</p>
        </div>
    </header>

    <main class="container mx-auto px-4 py-8">
        <!-- Status Banner -->
        <div class="mb-8 p-4 rounded-lg {% if all_success %}bg-green-100 border border-green-300{% else %}bg-yellow-100 border border-yellow-300{% endif %}">
            <p class="font-medium">
                {% if all_success %}
                    ✅ Todos los datos se obtuvieron correctamente
                {% else %}
                    ⚠️ Algunos datos no pudieron ser obtenidos. Revisa los detalles abajo.
                {% endif %}
            </p>
        </div>

        <!-- Falabella -->
        <section class="mb-12 bg-white rounded-lg shadow-md p-6">
            <h2 class="text-2xl font-bold text-green-700 mb-4 flex items-center">
                <span class="mr-2">🟢</span> Falabella
                {% if not falabella.success %}<span class="ml-2 text-sm text-red-500">(Error al obtener datos)</span>{% endif %}
            </h2>
            <p class="text-sm text-gray-500 mb-4">
                <a href="{{ falabella.url }}" target="_blank" class="hover:underline">🔗 Ver fuente original</a>
            </p>
            
            {% for key, tarifa in falabella.tarifas.items() %}
                {% if tarifa.datos and tarifa.datos|length > 0 %}
                <div class="mb-6">
                    <h3 class="text-lg font-semibold text-gray-700 mb-2">{{ tarifa.titulo }}</h3>
                    <div class="table-container">
                        <table>
                            {% for row in tarifa.datos %}
                            <tr>
                                {% for cell in row %}
                                {% if loop.first and loop.parent.first %}
                                <th>{{ cell }}</th>
                                {% else %}
                                <td>{{ cell }}</td>
                                {% endif %}
                                {% endfor %}
                            </tr>
                            {% endfor %}
                        </table>
                    </div>
                </div>
                {% endif %}
            {% endfor %}
            
            {% if falabella.todas_las_tablas %}
            <details class="mt-4">
                <summary class="cursor-pointer text-blue-600 hover:underline">Ver todas las tablas encontradas ({{ falabella.todas_las_tablas|length }})</summary>
                {% for tabla in falabella.todas_las_tablas %}
                <div class="mt-4 table-container">
                    <p class="text-sm text-gray-500 mb-1">Tabla {{ loop.index }}</p>
                    <table class="text-sm">
                        {% for row in tabla %}
                        <tr>
                            {% for cell in row %}
                            <td>{{ cell }}</td>
                            {% endfor %}
                        </tr>
                        {% endfor %}
                    </table>
                </div>
                {% endfor %}
            </details>
            {% endif %}
        </section>

        <!-- Mercado Libre -->
        <section class="mb-12 bg-white rounded-lg shadow-md p-6">
            <h2 class="text-2xl font-bold text-yellow-600 mb-4 flex items-center">
                <span class="mr-2">🟡</span> Mercado Libre
                {% if not mercadolibre.success %}<span class="ml-2 text-sm text-red-500">(Error al obtener datos)</span>{% endif %}
            </h2>
            
            {% for key, tarifa in mercadolibre.tarifas.items() %}
            <div class="mb-6 p-4 bg-gray-50 rounded">
                <h3 class="text-lg font-semibold text-gray-700 mb-2">{{ tarifa.titulo }}</h3>
                <p class="text-sm text-gray-500 mb-2">
                    <a href="{{ tarifa.url }}" target="_blank" class="hover:underline">🔗 Ver fuente</a>
                </p>
                
                {% if tarifa.error %}
                <p class="text-red-500">❌ {{ tarifa.error }}</p>
                {% else %}
                    {% if tarifa.tablas %}
                        {% for tabla in tarifa.tablas %}
                        <div class="table-container mb-2">
                            <table class="text-sm">
                                {% for row in tabla %}
                                <tr>
                                    {% for cell in row %}
                                    {% if loop.first and loop.parent.first %}
                                    <th>{{ cell }}</th>
                                    {% else %}
                                    <td>{{ cell }}</td>
                                    {% endif %}
                                    {% endfor %}
                                </tr>
                                {% endfor %}
                            </table>
                        </div>
                        {% endfor %}
                    {% endif %}
                    
                    {% if tarifa.texto_relevante %}
                    <div class="mt-2">
                        <p class="text-sm font-medium text-gray-600">Información relevante:</p>
                        <ul class="list-disc list-inside text-sm text-gray-700">
                            {% for texto in tarifa.texto_relevante[:10] %}
                            <li>{{ texto }}</li>
                            {% endfor %}
                        </ul>
                    </div>
                    {% endif %}
                {% endif %}
            </div>
            {% endfor %}
        </section>

        <!-- Paris -->
        <section class="mb-12 bg-white rounded-lg shadow-md p-6">
            <h2 class="text-2xl font-bold text-red-600 mb-4 flex items-center">
                <span class="mr-2">🔴</span> Paris
                {% if paris.success %}
                <span class="ml-2 text-sm text-green-500">(✅ Datos obtenidos)</span>
                {% endif %}
            </h2>
            
            <!-- Despacho -->
            {% set despacho = paris.tarifas.despacho %}
            <div class="mb-6 p-4 bg-gray-50 rounded">
                <h3 class="text-lg font-semibold text-gray-700 mb-2">{{ despacho.titulo }}</h3>
                <p class="text-sm text-gray-500 mb-2">
                    <a href="{{ despacho.url }}" target="_blank" class="text-blue-600 hover:underline">🔗 Ver fuente original</a>
                </p>
                
                {% if despacho.error %}
                <p class="text-red-500">❌ {{ despacho.error }}</p>
                {% elif despacho.tiene_datos or despacho.todas_las_tablas %}
                    {# Mostrar tablas específicas si las encontró #}
                    {% if despacho.tabla_menor_49990 %}
                    <div class="mb-4">
                        <p class="font-medium text-gray-600 mb-1">📦 Despacho &lt; $49.990:</p>
                        <div class="table-container">
                            <table class="text-sm">
                                {% for row in despacho.tabla_menor_49990 %}
                                <tr>
                                    {% for cell in row %}
                                    {% if loop.parent.first %}
                                    <th class="bg-red-50">{{ cell }}</th>
                                    {% else %}
                                    <td>{{ cell }}</td>
                                    {% endif %}
                                    {% endfor %}
                                </tr>
                                {% endfor %}
                            </table>
                        </div>
                    </div>
                    {% endif %}
                    
                    {% if despacho.tabla_mayor_49990 %}
                    <div class="mb-4">
                        <p class="font-medium text-gray-600 mb-1">📦 Despacho &ge; $49.990:</p>
                        <div class="table-container">
                            <table class="text-sm">
                                {% for row in despacho.tabla_mayor_49990 %}
                                <tr>
                                    {% for cell in row %}
                                    {% if loop.parent.first %}
                                    <th class="bg-red-50">{{ cell }}</th>
                                    {% else %}
                                    <td>{{ cell }}</td>
                                    {% endif %}
                                    {% endfor %}
                                </tr>
                                {% endfor %}
                            </table>
                        </div>
                    </div>
                    {% endif %}
                    
                    {# Si no encontró las tablas específicas, mostrar todas #}
                    {% if not despacho.tabla_menor_49990 and not despacho.tabla_mayor_49990 and despacho.todas_las_tablas %}
                    <p class="text-sm text-gray-500 mb-2">Tablas encontradas:</p>
                    {% for tabla in despacho.todas_las_tablas %}
                    <div class="mb-4 table-container">
                        <table class="text-sm">
                            {% for row in tabla %}
                            <tr>
                                {% for cell in row %}
                                {% if loop.parent.first %}
                                <th class="bg-red-50">{{ cell }}</th>
                                {% else %}
                                <td>{{ cell }}</td>
                                {% endif %}
                                {% endfor %}
                            </tr>
                            {% endfor %}
                        </table>
                    </div>
                    {% endfor %}
                    {% endif %}
                {% else %}
                <p class="text-gray-500">No se encontraron tablas en esta sección.</p>
                {% endif %}
            </div>
            
            <!-- Fulfillment -->
            {% set fulfillment = paris.tarifas.fulfillment %}
            <div class="mb-6 p-4 bg-gray-50 rounded">
                <h3 class="text-lg font-semibold text-gray-700 mb-2">{{ fulfillment.titulo }}</h3>
                <p class="text-sm text-gray-500 mb-2">
                    <a href="{{ fulfillment.url }}" target="_blank" class="text-blue-600 hover:underline">🔗 Ver fuente original</a>
                </p>
                
                {% if fulfillment.error %}
                <p class="text-red-500">❌ {{ fulfillment.error }}</p>
                {% elif fulfillment.tiene_datos or fulfillment.todas_las_tablas %}
                    {# Mostrar secciones específicas si las encontró #}
                    {% if fulfillment.almacenamiento %}
                    <div class="mb-4">
                        <p class="font-medium text-gray-600 mb-1">📦 Almacenamiento:</p>
                        <div class="table-container">
                            <table class="text-sm">
                                {% for row in fulfillment.almacenamiento %}
                                <tr>
                                    {% for cell in row %}
                                    {% if loop.parent.first %}
                                    <th class="bg-red-50">{{ cell }}</th>
                                    {% else %}
                                    <td>{{ cell }}</td>
                                    {% endif %}
                                    {% endfor %}
                                </tr>
                                {% endfor %}
                            </table>
                        </div>
                    </div>
                    {% endif %}
                    
                    {% if fulfillment.retiro %}
                    <div class="mb-4">
                        <p class="font-medium text-gray-600 mb-1">📦 Retiro:</p>
                        <div class="table-container">
                            <table class="text-sm">
                                {% for row in fulfillment.retiro %}
                                <tr>
                                    {% for cell in row %}
                                    {% if loop.parent.first %}
                                    <th class="bg-red-50">{{ cell }}</th>
                                    {% else %}
                                    <td>{{ cell }}</td>
                                    {% endif %}
                                    {% endfor %}
                                </tr>
                                {% endfor %}
                            </table>
                        </div>
                    </div>
                    {% endif %}
                    
                    {# Si no encontró secciones específicas, mostrar todas las tablas #}
                    {% if not fulfillment.almacenamiento and not fulfillment.retiro and fulfillment.todas_las_tablas %}
                    <p class="text-sm text-gray-500 mb-2">Tablas encontradas:</p>
                    {% for tabla in fulfillment.todas_las_tablas %}
                    <div class="mb-4 table-container">
                        <table class="text-sm">
                            {% for row in tabla %}
                            <tr>
                                {% for cell in row %}
                                {% if loop.parent.first %}
                                <th class="bg-red-50">{{ cell }}</th>
                                {% else %}
                                <td>{{ cell }}</td>
                                {% endif %}
                                {% endfor %}
                            </tr>
                            {% endfor %}
                        </table>
                    </div>
                    {% endfor %}
                    {% endif %}
                    
                    {# Texto relevante #}
                    {% if fulfillment.texto_relevante %}
                    <div class="mt-4 p-3 bg-yellow-50 rounded border border-yellow-200">
                        <p class="text-sm font-medium text-gray-700 mb-2">📝 Información adicional:</p>
                        <ul class="list-disc list-inside text-sm text-gray-600 space-y-1">
                            {% for texto in fulfillment.texto_relevante[:10] %}
                            <li>{{ texto }}</li>
                            {% endfor %}
                        </ul>
                    </div>
                    {% endif %}
                {% else %}
                <p class="text-gray-500">No se encontraron tablas en esta sección.</p>
                {% endif %}
            </div>
        </section>
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
    
    # Determinar si todo fue exitoso
    all_success = (
        falabella_data.get("success", False) and
        mercadolibre_data.get("success", False) and
        paris_data.get("success", False)
    )
    
    # Renderizar template
    template = Template(HTML_TEMPLATE)
    html_content = template.render(
        updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        all_success=all_success,
        falabella=falabella_data,
        mercadolibre=mercadolibre_data,
        paris=paris_data
    )
    
    # Guardar archivo
    output_path = os.path.join(output_dir, "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return output_path

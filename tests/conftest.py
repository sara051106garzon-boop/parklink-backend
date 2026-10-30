# tests/conftest.py
"""
Configuración raíz de la suite de pruebas de ParkLink.

Responsabilidades de este archivo:

1. Dejar el paquete ``app`` importable sin importar desde qué carpeta se lance
   ``pytest``.
2. Etiquetar automáticamente cada prueba como ``unit`` o ``integration``
   según la carpeta en la que viva, para poder ejecutar subconjuntos:

       pytest -m unit
       pytest -m integration

Los fixtures que necesitan Flask (``flask_app`` y ``client``) viven en
``tests/integration/conftest.py`` para que las pruebas unitarias nunca
importen la aplicación ni toquen la base de datos.
"""

import sys
from pathlib import Path

import pytest

# Raíz del proyecto: la carpeta que contiene el paquete `app`.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def pytest_collection_modifyitems(items):
    """Marca cada prueba como `unit` o `integration` según su ubicación."""
    for item in items:
        partes = Path(str(item.fspath)).parts
        if "integration" in partes:
            item.add_marker(pytest.mark.integration)
        elif "unit" in partes:
            item.add_marker(pytest.mark.unit)

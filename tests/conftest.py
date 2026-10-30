# tests/conftest.py
"""
Configuración raíz de la suite de pruebas de ParkLink.

Responsabilidades de este archivo:

1. Dejar el paquete ``app`` importable sin importar desde qué carpeta se lance
   ``pytest``.
2. Ofrecer los fixtures de Flask (``flask_app`` y ``client``) a toda la suite.
   Son perezosos: solo se ejecutan si una prueba los pide, así que las pruebas
   unitarias nunca construyen la aplicación.
3. Etiquetar automáticamente cada prueba como ``unit`` o ``integration`` según
   su carpeta:

       pytest -m unit
       pytest -m integration

Estructura: ``tests/<persona>/unit`` y ``tests/<persona>/integration``.
"""

import sys
from pathlib import Path

import pytest

# Raíz del proyecto: la carpeta que contiene el paquete `app`.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def pytest_collection_modifyitems(items):
    """Marca cada prueba como `integration` o `unit` según su carpeta."""
    for item in items:
        partes = Path(str(item.fspath)).parts
        if "integration" in partes:
            item.add_marker(pytest.mark.integration)
        else:
            item.add_marker(pytest.mark.unit)


@pytest.fixture(scope="module")
def flask_app():
    """
    Crea la aplicación una sola vez por archivo de prueba.

    ``socketio`` se configura con ``async_mode="gevent"``; gevent es el motor de
    producción y no interviene en estas pruebas. Se sustituye ``init_app`` por
    un no-op para no levantar un servidor de WebSockets.
    """
    import app as app_module

    init_app_original = app_module.socketio.init_app
    app_module.socketio.init_app = lambda *args, **kwargs: None
    try:
        aplicacion = app_module.create_app()
    finally:
        app_module.socketio.init_app = init_app_original

    aplicacion.config.update(TESTING=True)
    return aplicacion


@pytest.fixture()
def client(flask_app):
    """Cliente HTTP de Flask para invocar las rutas sin abrir un puerto."""
    return flask_app.test_client()

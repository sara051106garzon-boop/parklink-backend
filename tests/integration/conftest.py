# tests/integration/conftest.py
"""
Fixtures compartidos por las pruebas de integración.

Una prueba de integración SÍ construye la aplicación Flask y usa su
``test_client`` para llamar a las rutas, pero nunca abre un puerto real ni
depende de una base de datos MySQL levantada.
"""

import sys
from pathlib import Path

import pytest

# Permite ejecutar `pytest` directamente desde esta carpeta.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import app as app_module


@pytest.fixture(scope="module")
def flask_app():
    """
    Crea la aplicación una sola vez por archivo de prueba.

    ``socketio`` se configura con ``async_mode="gevent"``; gevent es el motor de
    producción y no interviene en estas pruebas. Se sustituye ``init_app`` por
    un no-op para no levantar un servidor de WebSockets.
    """
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

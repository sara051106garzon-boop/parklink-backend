# tests/conftest.py
"""
Configuración común para las pruebas unitarias de ParkLink.

Centraliza la preparación de la aplicación Flask y del cliente HTTP para que
cada caso de prueba pueda vivir en su propio archivo sin repetir código.
"""

import sys
from pathlib import Path

import pytest

# Permite ejecutar `pytest` desde la raíz del repositorio o desde Back-End.
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import app as app_module


@pytest.fixture(scope="module")
def flask_app():
    """
    Crea la aplicación una sola vez por archivo de prueba.

    SocketIO se configura con async_mode="gevent"; gevent es el motor de
    producción y no interviene en estas pruebas unitarias. Se sustituye
    init_app por un no-op para no levantar un servidor de WebSockets.
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

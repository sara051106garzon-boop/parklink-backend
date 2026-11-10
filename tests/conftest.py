# tests/conftest.py
"""
Configuración raíz de la suite de pruebas de ParkLink.

Responsabilidades de este archivo:
1. Dejar el paquete ``app`` importable sin importar desde qué carpeta se lance ``pytest``.
2. Ofrecer los fixtures de Flask (``flask_app``, ``client``, ``cliente_con_bd`` y ``app_con_contexto_de_prueba``).
3. Etiquetar automáticamente cada prueba como ``unit``, ``integration`` o ``e2e`` según su carpeta.
"""

import sys
from pathlib import Path

import pytest

# Raíz del proyecto: la carpeta que contiene el paquete `app`.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Importa todos los modelos para que queden registrados en el metadata
# antes de llamar a db.create_all() (añadido del conftest de tu compañero).
import app.models  # noqa: F401

# URI alternativa para las pruebas que necesitan una base real. Es SQLite en
# memoria: se crea al pedir el fixture `cliente_con_bd` y desaparece al final.
TEST_DATABASE_URI = "sqlite://"


def pytest_collection_modifyitems(items):
    """Marca cada prueba como `e2e`, `integration` o `unit` según su carpeta."""
    for item in items:
        partes = Path(str(item.fspath)).parts
        if "e2e" in partes:
            item.add_marker(pytest.mark.e2e)
        elif "integration" in partes:
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


@pytest.fixture
def app_con_contexto_de_prueba():
    """Crea una app de prueba con una base de datos SQLite en memoria.

    Útil para pruebas de servicios y repositorios que necesitan contexto de
    Flask y tablas reales sin abrir puertos ni tocar MySQL.
    """
    import app as app_module
    from app.database.database import db

    # gevent (async_mode de producción) no está instalado en el entorno de
    # pruebas: se neutraliza init_app igual que hace el fixture `flask_app`.
    init_app_original = app_module.socketio.init_app
    app_module.socketio.init_app = lambda *args, **kwargs: None
    try:
        aplicacion = app_module.create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": TEST_DATABASE_URI,
            "SQLALCHEMY_ENGINE_OPTIONS": {},
            "SECRET_KEY": "test-secret-key",
            "JWT_SECRET_KEY": "test-jwt-secret-key",
        })
    finally:
        app_module.socketio.init_app = init_app_original

    with aplicacion.app_context():
        db.create_all()
        try:
            yield aplicacion
        finally:
            db.session.remove()
            db.drop_all()


@pytest.fixture()
def cliente_con_bd(flask_app):
    """
    Cliente HTTP sobre una base de datos SQLite **en memoria**.
    Sirve para las pruebas de integración que recorren todo el flujo real.
    """
    from app.config.settings import Config
    from app.database.database import db

    aplicacion = flask_app
    sqlalchemy = aplicacion.extensions["sqlalchemy"]

    uri_original = Config.SQLALCHEMY_DATABASE_URI
    opciones_originales = Config.SQLALCHEMY_ENGINE_OPTIONS
    uri_app_original = aplicacion.config["SQLALCHEMY_DATABASE_URI"]
    opciones_app_originales = aplicacion.config["SQLALCHEMY_ENGINE_OPTIONS"]

    def _reconstruir_engine(uri, opciones):
        db.session.remove()
        motores = sqlalchemy._app_engines[aplicacion]
        motor_anterior = motores.get(None)

        opciones_engine = dict(opciones)
        opciones_engine["url"] = uri
        sqlalchemy._apply_driver_defaults(opciones_engine, aplicacion)
        motores[None] = sqlalchemy._make_engine(None, opciones_engine, aplicacion)

        if motor_anterior is not None:
            motor_anterior.dispose()

    def _apuntar_a_sqlite():
        Config.SQLALCHEMY_DATABASE_URI = TEST_DATABASE_URI
        Config.SQLALCHEMY_ENGINE_OPTIONS = {}
        aplicacion.config["SQLALCHEMY_DATABASE_URI"] = TEST_DATABASE_URI
        aplicacion.config["SQLALCHEMY_ENGINE_OPTIONS"] = {}
        _reconstruir_engine(TEST_DATABASE_URI, {})

    def _restaurar_config():
        Config.SQLALCHEMY_DATABASE_URI = uri_original
        Config.SQLALCHEMY_ENGINE_OPTIONS = opciones_originales
        aplicacion.config["SQLALCHEMY_DATABASE_URI"] = uri_app_original
        aplicacion.config["SQLALCHEMY_ENGINE_OPTIONS"] = opciones_app_originales
        _reconstruir_engine(uri_app_original, opciones_app_originales)

    with aplicacion.app_context():
        _apuntar_a_sqlite()
        db.create_all()
        try:
            yield aplicacion.test_client()
        finally:
            db.session.remove()
            db.drop_all()
            _restaurar_config()
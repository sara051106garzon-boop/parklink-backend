# tests/diego/conftest.py
"""
Fixtures propias de las pruebas de Diego.

El archivo ``tests/conftest.py`` (raíz) es el de todo el equipo: define
``flask_app``, ``client`` y ``cliente_con_bd``, y marca cada prueba como
``unit``, ``integration`` o ``e2e`` según su carpeta. Aquí solo se agregan los
fixtures extra que usan las pruebas de Diego:

1. ``app`` / ``db_session`` / ``test_database``: app Flask sobre SQLite en
   memoria con todas las tablas creadas (patrón Arrange-Act-Assert sobre BD).
2. ``app_context``: contexto de aplicación activo para llamar servicios.
3. Tokens y cabeceras JWT por rol (admin, usuario, vigilante).
4. Mocks de entidades del módulo Administrador (celdas).
"""

import pytest
from sqlalchemy import event
from unittest.mock import MagicMock

from flask_jwt_extended import create_access_token

from app import create_app
from app.database.database import db as _db


def _construir_app_de_prueba():
    """Crea la aplicación Flask apuntando a SQLite en memoria, sin WebSockets."""
    import app as app_module

    # ``socketio`` se inicializa con ``async_mode="gevent"``; se neutraliza para
    # no levantar un servidor de WebSockets (mismo criterio que la raíz).
    init_app_original = app_module.socketio.init_app
    app_module.socketio.init_app = lambda *args, **kwargs: None
    try:
        return create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_ENGINE_OPTIONS": {},
            "SECRET_KEY": "test-secret-key",
            "JWT_SECRET_KEY": "clave_secreta_para_testing_parklink",
            "WTF_CSRF_ENABLED": False,
        })
    finally:
        app_module.socketio.init_app = init_app_original


# ── 1. FIXTURE DE APLICACIÓN FLASK EN MODO TESTING ─────────────────────────
@pytest.fixture(scope="session")
def app():
    """
    Instancia la aplicación Flask configurada para el entorno de pruebas (Testing).
    """
    _app = _construir_app_de_prueba()

    with _app.app_context():
        if _db.engine.dialect.name == "sqlite":
            @event.listens_for(_db.engine, "connect")
            def enable_sqlite_foreign_keys(connection, _):
                cursor = connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

    with _app.app_context():
        yield _app


@pytest.fixture
def test_database(app):
    """Crea un esquema aislado para las pruebas que ejercitan la base de datos."""
    with app.app_context():
        if _db.engine.dialect.name != "sqlite":
            pytest.fail("test_database must never run against a non-SQLite database")
        _db.drop_all()
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def db_session(test_database, app):
    """Sesión de SQLAlchemy aislada (SQLite en memoria) para las pruebas de integración."""
    with app.app_context():
        yield _db.session
        _db.session.rollback()


@pytest.fixture(autouse=True)
def prevent_pymysql_connections(monkeypatch):
    """Impide que una prueba se conecte por accidente a MySQL con PyMySQL."""
    import pymysql

    def reject_connection(*args, **kwargs):
        pytest.fail("PyMySQL connections are disabled in pytest")

    monkeypatch.setattr(pymysql, "connect", reject_connection)


# ── 2. FIXTURE DEL CLIENTE HTTP DE PRUEBAS ─────────────────────────────────
@pytest.fixture(scope="function")
def client_de_diego(app):
    """
    Cliente HTTP de pruebas sobre la app de SQLite en memoria (fixture ``app``).

    El ``client`` global no se redefine: es el de la raíz del equipo y no
    consulta la base de datos.
    """
    return app.test_client()


# ── 3. FIXTURE DE CONTEXTO DE APLICACIÓN ──────────────────────────────────
@pytest.fixture(scope="function")
def app_context(app):
    """
    Pone a disposición el contexto de aplicación activo para ejecutar servicios y modelos.
    """
    with app.app_context():
        yield app


# ── 4. FIXTURE TOKEN JWT DE ADMINISTRADOR ──────────────────────────────────
@pytest.fixture(scope="function")
def token_admin(app):
    """
    Genera un Token JWT válido simulando la identidad corporativa de un Administrador.
    """
    with app.app_context():
        return create_access_token(identity="1")


# ── 5. FIXTURE HEADERS DE AUTENTICACIÓN ADMIN ─────────────────────────────
@pytest.fixture(scope="function")
def headers_admin_legacy(token_admin):
    """
    Proporciona los encabezados HTTP con la cabecera Bearer Token para rutas protegidas.
    """
    return {
        "Authorization": f"Bearer {token_admin}",
        "Content-Type": "application/json"
    }


# ── 6. FIXTURES MOCK DE ENTIDADES DEL MÓDULO ADMINISTRADOR ────────────────
@pytest.fixture
def mock_celda_libre():
    """
    Retorna un objeto Celda mockeado en estado disponible/libre.
    """
    celda = MagicMock()
    celda.id = 1
    celda.codigo_celda = "P1-01"
    celda.tipo_celda = "carro"
    celda.planta = 1
    celda.estado = "libre"
    celda.ocupada = False
    celda.placa = None
    celda.usuario = None
    celda.marca = None
    celda.modelo = None
    celda.color_hex = None
    celda.hora_ingreso = None
    return celda


@pytest.fixture
def mock_celda_ocupada():
    """
    Retorna un objeto Celda mockeado en estado ocupado con vehículo asignado.
    """
    celda = MagicMock()
    celda.id = 2
    celda.codigo_celda = "P1-02"
    celda.tipo_celda = "carro"
    celda.planta = 1
    celda.estado = "ocupado"
    celda.ocupada = True
    celda.placa = "ABC-123"
    celda.usuario = "Diego Plazas"
    celda.marca = "Toyota"
    celda.modelo = "Corolla"
    celda.color_hex = "#2563eb"
    celda.hora_ingreso = "08:30 AM"
    return celda


@pytest.fixture
def mock_celda_reservada():
    """
    Retorna un objeto Celda mockeado en estado reservado.
    """
    celda = MagicMock()
    celda.id = 3
    celda.codigo_celda = "P1-03"
    celda.tipo_celda = "carro"
    celda.planta = 1
    celda.estado = "reservado"
    celda.ocupada = True
    celda.placa = None
    celda.usuario = "Usuario Reserva"
    celda.marca = None
    celda.modelo = None
    celda.color_hex = None
    celda.hora_ingreso = "Reserva Activa"
    return celda


# ── 7. TOKENS Y CABECERAS JWT POR ROL ─────────────────────────────────────
@pytest.fixture(scope="function")
def token_usuario(app):
    with app.app_context():
        return create_access_token(identity="2")


@pytest.fixture(scope="function")
def token_vigilante(app):
    with app.app_context():
        return create_access_token(identity="1")


@pytest.fixture(scope="function")
def headers_admin(token_admin):
    return {
        "Authorization": f"Bearer {token_admin}",
        "Content-Type": "application/json"
    }


@pytest.fixture(scope="function")
def headers_usuario(token_usuario):
    return {
        "Authorization": f"Bearer {token_usuario}",
        "Content-Type": "application/json"
    }


@pytest.fixture(scope="function")
def headers_vigilante(token_vigilante):
    return {
        "Authorization": f"Bearer {token_vigilante}",
        "Content-Type": "application/json"
    }

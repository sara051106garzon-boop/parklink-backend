"""
ParkLink - Configuración Global de Fixtures para Pruebas Unitarias.
Ubicación: tests/conftest.py
Módulo: Administrador & Control de Celdas
"""

import pytest
from sqlalchemy import event
from unittest.mock import MagicMock
from unittest.mock import patch
from flask_jwt_extended import create_access_token

from app import create_app
from app.database.database import db as _db


# ── 1. FIXTURE DE APLICACIÓN FLASK EN MODO TESTING ─────────────────────────
@pytest.fixture(scope="session")
def app():
    """
    Instancia la aplicación Flask configurada para el entorno de pruebas (Testing).
    """
    _app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_ENGINE_OPTIONS": {},
        "JWT_SECRET_KEY": "clave_secreta_para_testing_parklink",
        "WTF_CSRF_ENABLED": False
    })

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
    """Creates an isolated schema for tests that exercise database behavior."""
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
    """Provides the isolated in-memory SQLAlchemy session for integration tests."""
    with app.app_context():
        yield _db.session
        _db.session.rollback()


@pytest.fixture(autouse=True)
def prevent_pymysql_connections(monkeypatch):
    import pymysql

    def reject_connection(*args, **kwargs):
        pytest.fail("PyMySQL connections are disabled in pytest")

    monkeypatch.setattr(pymysql, "connect", reject_connection)


# ── 2. FIXTURE DEL CLIENTE HTTP DE PRUEBAS ─────────────────────────────────
@pytest.fixture(scope="function")
def client(app):
    """
    Proporciona un cliente de pruebas de Flask para simular peticiones HTTP a la API.
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
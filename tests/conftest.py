"""
ParkLink - Configuración Global de Fixtures para Pruebas Unitarias.
Ubicación: tests/conftest.py
Módulo: Administrador & Control de Celdas
"""

import pytest
from unittest.mock import MagicMock
from flask_jwt_extended import create_access_token

from app import create_app
from app.database.database import db as _db


# ── 1. FIXTURE DE APLICACIÓN FLASK EN MODO TESTING ─────────────────────────
@pytest.fixture(scope="session")
def app():
    """
    Instancia la aplicación Flask configurada para el entorno de pruebas (Testing).
    """
    _app = create_app()
    _app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "clave_secreta_para_testing_parklink",
        "WTF_CSRF_ENABLED": False
    })

    with _app.app_context():
        yield _app


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
        identity = {
            "id": 1,
            "correo": "admin@parklink.com",
            "rol": "ADMINISTRADOR",
            "nombre": "Diego Plazas"
        }
        return create_access_token(identity=identity)


# ── 5. FIXTURE HEADERS DE AUTENTICACIÓN ADMIN ─────────────────────────────
@pytest.fixture(scope="function")
def headers_admin(token_admin):
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
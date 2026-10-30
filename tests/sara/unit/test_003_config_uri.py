# tests/unit/test_003_config_uri.py
"""UNIT 003 · Config · URI de conexión a la base de datos."""

from app.config.settings import Config


def test_uri_de_base_de_datos_usa_el_driver_pymysql():
    """La cadena de conexión debe usar MySQL mediante PyMySQL."""
    # Arrange
    prefijo_esperado = "mysql+pymysql://"

    # Act
    uri_configurada = Config.SQLALCHEMY_DATABASE_URI

    # Assert
    assert uri_configurada.startswith(prefijo_esperado)

# tests/unit/test_002_config_jwt.py
"""UNIT 002 · Config · Duración del token JWT."""

from datetime import timedelta

from app.config.settings import Config


def test_jwt_access_token_expira_en_ocho_horas():
    """La sesión de un usuario debe durar exactamente 8 horas."""
    # Arrange
    duracion_esperada = timedelta(hours=8)

    # Act
    duracion_configurada = Config.JWT_ACCESS_TOKEN_EXPIRES

    # Assert
    assert duracion_configurada == duracion_esperada

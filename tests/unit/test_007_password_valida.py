# tests/unit/test_007_password_valida.py
"""UNIT 007 · AuthService · Contraseña con longitud correcta."""

from app.services.auth_service import AuthService


def test_validar_password_acepta_una_contrasena_de_ocho_caracteres():
    """Ocho caracteres es la longitud mínima permitida."""
    # Arrange
    password = "12345678"

    # Act
    es_valido, mensaje_error = AuthService.validar_password(password)

    # Assert
    assert es_valido is True
    assert mensaje_error is None

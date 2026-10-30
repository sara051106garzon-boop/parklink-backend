# tests/unit/test_006_password_corta.py
"""UNIT 006 · AuthService · Contraseña demasiado corta."""

from app.services.auth_service import AuthService


def test_validar_password_rechaza_una_contrasena_de_siete_caracteres():
    """La contraseña debe tener al menos 8 caracteres."""
    # Arrange
    password = "1234567"

    # Act
    es_valido, mensaje_error = AuthService.validar_password(password)

    # Assert
    assert es_valido is False
    assert mensaje_error == "La contraseña debe tener un mínimo de 8 caracteres."

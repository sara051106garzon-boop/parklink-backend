# tests/unit/test_005_correo_invalido.py
"""UNIT 005 · AuthService · Correo sin formato válido."""

from app.services.auth_service import AuthService


def test_validar_formato_correo_rechaza_un_correo_sin_arroba():
    """Un texto sin arroba ni dominio no puede ser un correo válido."""
    # Arrange
    correo = "correo-sin-arroba"

    # Act
    es_valido = AuthService.validar_formato_correo(correo)

    # Assert
    assert es_valido is False

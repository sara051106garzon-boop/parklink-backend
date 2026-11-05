# tests/unit/test_004_correo_valido.py
"""UNIT 004 · AuthService · Correo con formato válido."""

from app.services.auth_service import AuthService


def test_validar_formato_correo_acepta_un_correo_correcto():
    """Un correo con usuario, arroba y dominio debe ser aceptado."""
    # Arrange preparcion
    correo = "sara.parklink@correo.com"

    # Act ejecucion
    es_valido = AuthService.validar_formato_correo(correo)

    # Assert
    assert es_valido is True

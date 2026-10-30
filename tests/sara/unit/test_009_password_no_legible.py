# tests/unit/test_009_password_no_legible.py
"""UNIT 009 · Usuario.password · La contraseña no se puede leer."""

import pytest

from app.models.usuario import Usuario


def test_leer_el_atributo_password_lanza_attribute_error():
    """El getter de password debe impedir exponer la contraseña."""
    # Arrange
    usuario = Usuario()

    # Act / Assert
    with pytest.raises(AttributeError, match="no es un atributo legible"):
        _ = usuario.password

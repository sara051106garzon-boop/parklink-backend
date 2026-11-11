"""UNIT 046 · usuario_service.cambiar_password · No permite reutilizar la misma contraseña."""

from unittest.mock import MagicMock, patch

from app.services.usuario_service import cambiar_password


@patch("app.services.usuario_service.db")
@patch("app.services.usuario_service.Usuario")
@patch("app.services.usuario_service.get_jwt_identity", return_value="1")
def test_cambiar_password_rechaza_si_la_nueva_es_igual_a_la_actual(
    mock_identidad, mock_usuario, mock_db
):
    """Si la nueva contraseña verifica contra el hash actual, responde 400."""
    # Arrange
    usuario_falso = MagicMock()
    usuario_falso.verificar_password.return_value = True  # actual y nueva coinciden con el hash
    mock_usuario.query.get.return_value = usuario_falso

    # Act
    respuesta, codigo = cambiar_password("Parklink2026*", "Parklink2026*")

    # Assert
    assert (codigo, respuesta["error"]) == (
        400,
        "La nueva contraseña no puede ser igual a la actual",
    )

"""UNIT 041 · AuthService · Una contraseña de más de 72 bytes se rechaza sin tocar la BD."""

from unittest.mock import patch

from app.services.auth_service import AuthService


def test_registrar_usuario_con_clave_de_mas_de_72_bytes_devuelve_error_controlado(app_context):
    """Bcrypt corta a 72 bytes: el servicio debe validarlo antes de consultar usuarios."""
    # Arrange
    password_extensa = "a" * 100
    datos_registro = {
        "nombre": "Ana Pérez",
        "correo": "ana@empresa.com",
        "password": password_extensa
    }

    with patch("app.models.usuario.Usuario.query") as mock_query:
        mock_query.filter_by.return_value.first.return_value = None

        # Act
        usuario, mensaje_error = AuthService.registrar_usuario(
            datos_registro["nombre"],
            datos_registro["correo"],
            datos_registro["password"]
        )

        # Assert
        assert usuario is None
        assert "La contraseña supera la longitud máxima permitida" in mensaje_error
        mock_query.filter_by.assert_not_called()

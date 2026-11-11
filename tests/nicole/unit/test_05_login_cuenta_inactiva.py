"""UNIT 044 · AuthService.login · Una cuenta inactiva no puede iniciar sesión."""

from unittest.mock import MagicMock, patch

from app.services.auth_service import AuthService


@patch("app.services.auth_service.Usuario")
def test_login_rechaza_cuenta_inactiva_aunque_la_contrasena_sea_correcta(mock_usuario):
    """Con credenciales válidas pero activo=False, el login devuelve el aviso de cuenta inactiva."""
    # Arrange
    usuario_falso = MagicMock()
    usuario_falso.activo = False
    usuario_falso.verificar_password.return_value = True
    mock_usuario.query.filter_by.return_value.first.return_value = usuario_falso

    # Act
    usuario, error = AuthService.login("ana@empresa.com", "Parklink2026*")

    # Assert
    assert (usuario, error) == (None, "Esta cuenta está inactiva. Contacta al administrador.")

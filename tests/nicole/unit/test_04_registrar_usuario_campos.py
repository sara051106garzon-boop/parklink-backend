"""UNIT 043 · AuthService.registrar_usuario · Rechaza el registro si falta algún campo."""

from app.services.auth_service import AuthService


def test_registrar_usuario_rechaza_si_falta_la_contrasena():
    """Sin contraseña no se crea el usuario y se informa que todos los campos son obligatorios."""
    # Arrange
    nombre = "Ana Pérez"
    correo = "ana@empresa.com"
    password = ""

    # Act
    usuario, error = AuthService.registrar_usuario(nombre, correo, password)

    # Assert
    assert (usuario, error) == (None, "Todos los campos son obligatorios.")

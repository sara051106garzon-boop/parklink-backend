"""INTEGRATION 050 · AuthService.registrar_usuario + login · Registro con rol por correo y acceso posterior.

Usa SQLite en memoria (``app_con_contexto_de_prueba``): el usuario se guarda de
verdad, con hash Bcrypt, y luego se autentica contra la misma base.
"""

from app.models.usuario import RolEnum, Usuario
from app.services.auth_service import AuthService


def test_registrar_usuario_con_correo_admin_guarda_rol_administrador_y_permite_login(
    app_con_contexto_de_prueba,
):
    """Un correo de administración se registra como ADMINISTRADOR y puede iniciar sesión."""
    # Arrange
    app_con_contexto_de_prueba.config["EMAIL_ADMIN_EXACTOS"] = ["jefe@parklink.com"]
    password = "Parklink2026*"

    # Act
    nuevo, error_registro = AuthService.registrar_usuario("  Jefe Parklink ", "JEFE@parklink.com", password)
    autenticado, error_login = AuthService.login("jefe@parklink.com", password)

    # Assert
    guardado = Usuario.query.filter_by(correo="jefe@parklink.com").first()
    assert error_registro is None and error_login is None
    assert guardado.rol == RolEnum.ADMINISTRADOR
    assert guardado.nombre_completo == "Jefe Parklink"
    assert guardado.password_hash != password
    assert autenticado.id == nuevo.id

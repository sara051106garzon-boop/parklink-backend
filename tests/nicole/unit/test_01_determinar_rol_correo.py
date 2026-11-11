"""UNIT 040 · AuthService.determinar_rol_por_correo · Correo de administración -> ADMINISTRADOR."""

from types import SimpleNamespace
from unittest.mock import patch

from app.models.usuario import RolEnum
from app.services.auth_service import AuthService

# ``current_app`` es un proxy de Flask: con ``new=`` mock no intenta inspeccionarlo
# (hacerlo sin contexto de aplicación lanza "Working outside of application context").
CONFIG_FALSA = SimpleNamespace(config={
    "EMAIL_VIGILANTE_DOMINIO": "@vigilancia.com",
    "EMAIL_ADMIN_EXACTOS": ["jefe@parklink.com"],
})


@patch("app.services.auth_service.current_app", new=CONFIG_FALSA)
def test_determinar_rol_asigna_administrador_si_el_correo_esta_en_la_lista():
    """Un correo igual a uno de EMAIL_ADMIN_EXACTOS recibe el rol ADMINISTRADOR."""
    # Arrange
    correo = "  JEFE@Parklink.com "

    # Act
    rol = AuthService.determinar_rol_por_correo(correo)

    # Assert
    assert rol == RolEnum.ADMINISTRADOR
# tests/unit/test_001_roles_enum.py
"""UNIT 001 · RolEnum · Los tres roles del sistema."""

from app.models.usuario import RolEnum


def test_rol_enum_define_exactamente_tres_roles():
    """RolEnum solo debe contener usuario, vigilante y administrador."""
    # Arrange
    roles_esperados = {"usuario", "vigilante", "administrador"}

    # Act
    roles_obtenidos = {rol.value for rol in RolEnum}

    # Assert
    assert roles_obtenidos == roles_esperados

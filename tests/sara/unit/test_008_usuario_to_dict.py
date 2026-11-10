# tests/unit/test_008_usuario_to_dict.py
"""UNIT 008 · Usuario.to_dict · Serialización para el frontend."""

from datetime import datetime

from app.models.usuario import RolEnum, Usuario


def test_usuario_to_dict_devuelve_rol_en_texto_y_fecha_formateada():
    """to_dict debe convertir el rol a texto y formatear created_at."""
    # Arrange
    usuario = Usuario(
        nombre_completo="Sara Prueba",
        correo="sara@correo.com",
        rol=RolEnum.VIGILANTE,
        activo=True,
        created_at=datetime(2026, 10, 29, 14, 30, 0),
    )

    # Act
    datos = usuario.to_dict()

    # Assert
    assert datos == {
        "id": None,
        "nombre_completo": "Sara Prueba",
        "correo": "sara@correo.com",
        "rol": "vigilante",
        "activo": True,
        "created_at": "2026-10-29 14:30:00",
    }

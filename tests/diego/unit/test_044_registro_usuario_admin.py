"""UNIT 044 · Admin · Solo un administrador puede registrar usuarios, y no se crea ninguno."""

from app.database.database import db
from app.models.usuario import RolEnum, Usuario


def test_registrar_usuario_deniega_a_usuario_comun(client_de_diego, headers_usuario, test_database):
    """Un usuario con rol USUARIO recibe 403 y la tabla queda igual."""
    # Arrange
    payload_nuevo_usuario = {
        "nombre": "Carlos Pérez",
        "correo": "carlos@parklink.com",
        "password": "Password123!",
        "rol": "VIGILANTE"
    }

    db.session.add(Usuario(
        id=2,
        nombre_completo="Usuario de prueba",
        correo="usuario@parklink.com",
        password_hash="hash-de-prueba",
        rol=RolEnum.USUARIO,
        activo=True
    ))
    db.session.commit()
    cantidad_usuarios = Usuario.query.count()

    # Act
    response = client_de_diego.post(
        "/api/admin/registrar-usuario",
        json=payload_nuevo_usuario,
        headers=headers_usuario
    )

    # Assert
    assert response.status_code == 403
    assert Usuario.query.count() == cantidad_usuarios

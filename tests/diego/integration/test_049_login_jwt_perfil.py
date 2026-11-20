"""Integración del login con creación de JWT y serialización del perfil."""

from flask_jwt_extended import decode_token

from app.models.usuario import RolEnum, Usuario


def test_login_emite_jwt_y_devuelve_perfil(client_de_diego, app, db_session):
    """INT 049 | Severidad: Alta. Login activo debe devolver un JWT utilizable."""
    # Arrange
    with app.app_context():
        usuario = Usuario(
            nombre_completo="Ana Pérez",
            correo="ana@parklink.com",
            rol=RolEnum.USUARIO,
            activo=True,
        )
        usuario.password = "ClaveSegura123!"
        db_session.add(usuario)
        db_session.commit()
        usuario_id = usuario.id

    payload = {"correo": "ana@parklink.com", "contrasena": "ClaveSegura123!"}

    # Act
    response = client_de_diego.post("/api/auth/login", json=payload)

    # Assert
    assert response.status_code == 200
    data = response.get_json()
    assert data["access_token"]
    assert data["usuario"]["id"] == usuario_id
    assert data["usuario"]["correo"] == payload["correo"]
    assert data["usuario"]["nombre_completo"] == "Ana Pérez"
    assert data["usuario"]["rol"] == "usuario"
    with app.app_context():
        claims = decode_token(data["access_token"])
    assert claims["sub"] == str(usuario_id)

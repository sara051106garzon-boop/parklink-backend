from app.database.database import db
from app.models.usuario import RolEnum, Usuario


def test_registrar_usuario_deniega_a_usuario_comun(client, headers_usuario, test_database):
    # --- ARRANGE ---
    headers = {
        "Authorization": "Bearer token_usuario_sin_permiso_admin",
        "Content-Type": "application/json"
    }
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
    headers = headers_usuario

    # --- ACT ---
    response = client.post(
        "/api/admin/registrar-usuario",
        json=payload_nuevo_usuario,
        headers=headers
    )

    # --- ASSERT ---
    assert response.status_code == 403
    assert Usuario.query.count() == cantidad_usuarios
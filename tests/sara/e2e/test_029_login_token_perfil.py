# tests/sara/e2e/test_029_login_token_perfil.py
"""
E2E 029 · Login + JWT · El token devuelve el perfil del usuario.

Usa el fixture ``cliente_con_bd``: base SQLite en memoria con tablas reales,
así cubre todo el camino login → token → consulta a la base → perfil.
"""

from app.database.database import db
from app.models.usuario import RolEnum, Usuario


def _crear_usuario(correo, password, rol, nombre="Sara Prueba"):
    """Siembra un usuario real (con hash Bcrypt) en la base de prueba."""
    usuario = Usuario(nombre_completo=nombre, correo=correo, rol=rol, activo=True)
    usuario.password = password
    db.session.add(usuario)
    db.session.commit()
    return usuario


def _iniciar_sesion(cliente, correo, password):
    """Hace login real y devuelve las cabeceras Authorization con el token."""
    respuesta = cliente.post(
        "/api/auth/login",
        json={"correo": correo, "password": password},
    )
    token = respuesta.get_json()["token"]
    return {"Authorization": f"Bearer {token}"}


def test_login_valido_devuelve_token_que_abre_el_perfil(cliente_con_bd):
    """Con credenciales correctas el token debe dar acceso al perfil propio."""
    # Arrange
    password = "Parklink2026*"
    usuario = _crear_usuario("sara@parklink.com", password, RolEnum.USUARIO)

    # Act
    respuesta_login = cliente_con_bd.post(
        "/api/auth/login",
        json={"correo": "SARA@Parklink.com", "password": password},
    )
    cuerpo_login = respuesta_login.get_json()
    cabeceras = {"Authorization": f"Bearer {cuerpo_login['token']}"}
    respuesta_perfil = cliente_con_bd.get("/api/auth/perfil", headers=cabeceras)

    # Assert
    assert respuesta_login.status_code == 200
    assert cuerpo_login["mensaje"] == "Autenticación exitosa."
    assert cuerpo_login["usuario"]["correo"] == "sara@parklink.com"
    assert cuerpo_login["usuario"]["rol"] == "usuario"
    assert "password_hash" not in cuerpo_login["usuario"]

    assert respuesta_perfil.status_code == 200
    assert respuesta_perfil.get_json()["usuario"]["id"] == usuario.id
    assert respuesta_perfil.get_json()["usuario"]["correo"] == "sara@parklink.com"

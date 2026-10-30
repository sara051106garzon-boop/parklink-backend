# tests/test_023_jwt_token_expirado.py
"""UNIT 023 · jwt.expired_token_loader · Token vencido."""

from datetime import timedelta

from flask_jwt_extended import create_access_token


def test_jwt_token_expirado_devuelve_401_token_expired(flask_app, client):
    """Un token emitido con expiración negativa responde 401 token_expired."""
    # Arrange
    with flask_app.app_context():
        token_expirado = create_access_token(
            identity="1",
            expires_delta=timedelta(hours=-1),
        )
    cabeceras = {"Authorization": f"Bearer {token_expirado}"}

    # Act
    respuesta = client.get("/api/auth/perfil", headers=cabeceras)
    cuerpo = respuesta.get_json()

    # Assert
    assert respuesta.status_code == 401
    assert cuerpo["error"] == "token_expired"

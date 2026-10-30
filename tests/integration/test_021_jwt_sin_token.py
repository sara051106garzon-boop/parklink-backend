# tests/test_021_jwt_sin_token.py
"""UNIT 021 · jwt.unauthorized_loader · Petición sin token."""


def test_jwt_sin_token_devuelve_401_authorization_required(client):
    """Una ruta protegida sin cabecera Authorization responde 401."""
    # Arrange
    ruta_protegida = "/api/auth/perfil"

    # Act
    respuesta = client.get(ruta_protegida)
    cuerpo = respuesta.get_json()

    # Assert
    assert respuesta.status_code == 401
    assert cuerpo["error"] == "authorization_required"

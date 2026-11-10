# tests/sara/integration/test_026_jwt_sin_token.py
"""INTEGRATION 026 · Ruta protegida · Entrar sin token da 401."""


def test_perfil_sin_token_devuelve_401_authorization_required(client):
    """GET /api/auth/perfil sin cabecera Authorization debe rechazar con 401."""
    # Arrange
    ruta_protegida = "/api/auth/perfil"

    # Act
    respuesta = client.get(ruta_protegida)
    cuerpo = respuesta.get_json()

    # Assert
    assert respuesta.status_code == 401
    assert cuerpo["error"] == "authorization_required"

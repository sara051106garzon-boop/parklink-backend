# tests/sara/integration/test_027_jwt_corrupto.py
"""INTEGRATION 027 · Ruta protegida · Un token inválido da 401."""


def test_perfil_con_token_corrupto_devuelve_401_invalid_token(client):
    """Un token que no es un JWT real debe rechazarse con 401."""
    # Arrange
    cabeceras = {"Authorization": "Bearer esto-no-es-un-token"}

    # Act
    respuesta = client.get("/api/auth/perfil", headers=cabeceras)
    cuerpo = respuesta.get_json()

    # Assert
    assert respuesta.status_code == 401
    assert cuerpo["error"] == "invalid_token"

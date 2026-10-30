# tests/test_022_jwt_token_corrupto.py
"""UNIT 022 · jwt.invalid_token_loader · Token mal formado."""


def test_jwt_token_corrupto_devuelve_401_invalid_token(client):
    """Un token con estructura inválida responde 401 invalid_token."""
    # Arrange
    cabeceras = {"Authorization": "Bearer abc.def.ghi"}

    # Act
    respuesta = client.get("/api/auth/perfil", headers=cabeceras)
    cuerpo = respuesta.get_json()

    # Assert
    assert respuesta.status_code == 401
    assert cuerpo["error"] == "invalid_token"

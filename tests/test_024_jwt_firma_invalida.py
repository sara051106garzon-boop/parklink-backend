# tests/test_024_jwt_firma_invalida.py
"""UNIT 024 · JWTManager · Firma inválida."""

import jwt as pyjwt


def test_jwt_token_firmado_con_otra_clave_es_rechazado(flask_app, client):
    """Un token forjado con otra clave responde 401 invalid_token."""
    # Arrange
    clave_no_autorizada = "clave-de-prueba-no-autorizada-para-parklink-2026"
    token_forjado = pyjwt.encode(
        {
            "sub": "1",
            "type": "access",
            "iat": 1_700_000_000,
            "exp": 4_000_000_000,
        },
        clave_no_autorizada,
        algorithm="HS256",
    )
    assert clave_no_autorizada != flask_app.config["JWT_SECRET_KEY"]

    # Act
    respuesta = client.get(
        "/api/auth/perfil",
        headers={"Authorization": f"Bearer {token_forjado}"},
    )
    cuerpo = respuesta.get_json()

    # Assert
    assert respuesta.status_code == 401
    assert cuerpo["error"] == "invalid_token"

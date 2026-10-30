# tests/test_020_cors_rechazado.py
"""UNIT 020 · CORS · Origen no permitido."""


def test_cors_rechaza_origen_no_autorizado(client):
    """Un origen ajeno no recibe la cabecera Access-Control-Allow-Origin."""
    # Arrange
    origen_no_autorizado = "http://sitio-malicioso.com"
    cabeceras = {
        "Origin": origen_no_autorizado,
        "Access-Control-Request-Method": "POST",
    }

    # Act
    respuesta = client.options("/api/auth/login", headers=cabeceras)

    # Assert
    assert "Access-Control-Allow-Origin" not in respuesta.headers

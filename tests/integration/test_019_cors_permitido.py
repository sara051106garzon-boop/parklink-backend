# tests/test_019_cors_permitido.py
"""UNIT 019 · CORS · Origen permitido http://localhost:5173."""


def test_cors_permite_origen_del_frontend_en_rutas_api(client):
    """El preflight del frontend autorizado recibe las cabeceras CORS."""
    # Arrange
    origen_permitido = "http://localhost:5173"
    cabeceras = {
        "Origin": origen_permitido,
        "Access-Control-Request-Method": "POST",
    }

    # Act
    respuesta = client.options("/api/auth/login", headers=cabeceras)

    # Assert
    assert respuesta.status_code == 200
    assert respuesta.headers.get("Access-Control-Allow-Origin") == origen_permitido
    assert respuesta.headers.get("Access-Control-Allow-Credentials") == "true"

# tests/sara/integration/test_025_health.py
"""INTEGRATION 025 · GET /health · La app responde que está en línea."""


def test_health_responde_200_con_datos_del_proyecto(client):
    """GET /health debe responder 200 y decir que ParkLink está online."""
    # Arrange
    ruta = "/health"

    # Act
    respuesta = client.get(ruta)
    cuerpo = respuesta.get_json()

    # Assert
    assert respuesta.status_code == 200
    assert cuerpo["status"] == "online"
    assert cuerpo["project"] == "ParkLink"

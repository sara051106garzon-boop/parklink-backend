# tests/test_016_health.py
"""UNIT 016 · GET /health · Ruta de salud."""


def test_health_check_responde_online(client):
    """GET /health responde 200 con los datos base del proyecto."""
    # Arrange
    ruta = "/health"

    # Act
    respuesta = client.get(ruta)
    cuerpo = respuesta.get_json()

    # Assert
    assert respuesta.status_code == 200
    assert cuerpo["status"] == "online"
    assert cuerpo["project"] == "ParkLink"
    assert cuerpo["version"] == "1.0.0"

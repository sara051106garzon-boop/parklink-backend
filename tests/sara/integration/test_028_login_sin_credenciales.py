# tests/sara/integration/test_028_login_sin_credenciales.py
"""INTEGRATION 028 · POST /api/auth/login · Sin datos responde 400."""


def test_login_sin_datos_devuelve_400_con_mensaje(client):
    """Un login vacío debe rechazarse con 400 antes de consultar la base."""
    # Arrange
    ruta = "/api/auth/login"

    # Act
    respuesta = client.post(ruta)
    cuerpo = respuesta.get_json()

    # Assert
    assert respuesta.status_code == 400
    assert cuerpo["mensaje"] == "No se proporcionaron credenciales."

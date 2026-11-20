"""UNIT 046 · Seguridad · Una ruta protegida sin token responde 401."""


def test_historial_accesos_sin_token_devuelve_401(client):
    """El historial de accesos exige autenticación JWT."""
    # Arrange
    headers_vacios = {
        "Content-Type": "application/json"
    }

    # Act
    response = client.get(
        "/api/admin/historial",
        headers=headers_vacios
    )

    # Assert
    assert response.status_code == 401
    datos = response.get_json()
    assert "msg" in datos or "mensaje" in datos

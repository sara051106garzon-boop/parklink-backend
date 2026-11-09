def test_historial_accesos_sin_token_devuelve_401(client):
    # --- ARRANGE ---
    headers_vacios = {
        "Content-Type": "application/json"
    }

    # --- ACT ---
    response = client.get(
        "/api/admin/historial",
        headers=headers_vacios
    )

    # --- ASSERT ---
    assert response.status_code == 401
    datos = response.get_json()
    assert "msg" in datos or "mensaje" in datos
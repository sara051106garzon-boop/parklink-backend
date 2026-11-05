def test_historial_accesos_sin_token_devuelve_401(client):
    # --- ARRANGE (Preparar) ---
    headers_vacios = {
        "Content-Type": "application/json"
    }

    # --- ACT (Actuar) ---
    response = client.get(
        "/api/admin/historial",
        headers=headers_vacios
    )

    # --- ASSERT (Afirmar) ---
    assert response.status_code == 401
    datos = response.get_json()
    assert "msg" in datos or "mensaje" in datos
    assert "token" in str(datos).lower()
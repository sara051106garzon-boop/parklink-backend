def test_registrar_usuario_deniega_a_usuario_comun(client, token_usuario_comun):
    # --- ARRANGE (Preparar) ---
    headers = {
        "Authorization": f"Bearer {token_usuario_comun}",
        "Content-Type": "application/json"
    }
    payload_nuevo_usuario = {
        "nombre": "Carlos Pérez",
        "correo": "carlos@parklink.com",
        "password": "Password123!",
        "rol": "VIGILANTE"
    }

    # --- ACT (Actuar) ---
    response = client.post(
        "/api/admin/registrar-usuario",
        json=payload_nuevo_usuario,
        headers=headers
    )

    # --- ASSERT (Afirmar) ---
    assert response.status_code == 403
    datos = response.get_json()
    assert "mensaje" in datos
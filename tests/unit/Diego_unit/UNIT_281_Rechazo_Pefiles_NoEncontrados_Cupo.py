def test_validar_cupo_rechaza_perfil_no_valido(client, headers_admin):
    # --- ARRANGE (Preparar) ---
    payload_validacion = {
        "placa": "XYZ-999",
        "tipo_usuario": "visitante",
        "planta": 1
    }

    # --- ACT (Actuar) ---
    response = client.post(
        "/api/admin/ingresos/validar-cupo",
        json=payload_validacion,
        headers=headers_admin
    )

    # --- ASSERT (Afirmar) ---
    assert response.status_code == 400
    datos = response.get_json()
    assert "perfil" in datos.get("mensaje", "").lower()